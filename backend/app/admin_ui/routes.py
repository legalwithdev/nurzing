"""Server-rendered admin dashboard.

Cookie-based sign-in (phone + OTP, admin numbers only), then plain HTML pages so
the team can work without a separate frontend build.
"""
from __future__ import annotations

import datetime as dt
import os

import jwt
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import analytics, audit, ledger
from ..config import settings
from ..db import get_db
from ..invoices import InvoiceDoc, InvoiceLine, invoice_number, render_pdf
from ..models import (ApplicationStatus, Booking, BookingStatus, Document, Professional,
                      ProfessionalApplication, Refund, RefundStatus, User, UserRole)
from ..notifications import enqueue
from ..security import decode_token, hash_otp, new_otp, otp_expiry
from ..models import OtpCode
from ..sms import get_sms
from ..tier import tier_for
from ..rates import quote_detailed
from . import views

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

COOKIE = "nz_admin"


def money(paise: int | None) -> str:
    if not paise:
        return "Rs. 0"
    rupees = int(paise) / 100
    whole = f"{int(rupees):,}".replace(",", "")
    parts = []
    head, tail = whole[:-3], whole[-3:]
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    grouped = ",".join(parts + [tail]) if parts else tail
    return f"Rs. {grouped}"


templates.env.filters["money"] = money

router = APIRouter(prefix="/admin", include_in_schema=False)


def _admin_from_request(request: Request, db: Session) -> User | None:
    token = request.cookies.get(COOKIE)
    if not token:
        return None
    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        return None
    user = db.get(User, int(payload.get("sub", 0)))
    if user is None:
        return None
    if user.role != UserRole.admin and user.phone not in settings.admin_list:
        return None
    return user


def require_admin_page(request: Request, db: Session = Depends(get_db)) -> User:
    user = _admin_from_request(request, db)
    if user is None:
        raise HTTPException(status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": "/admin/login"})
    return user


def _ctx(request: Request, page: str, **kw) -> dict:
    return {"request": request, "page": page, "money": money, **kw}


# ---------------------------------------------------------------- auth
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, stage: str = "phone", phone: str = "", error: str = ""):
    return templates.TemplateResponse(request, "login.html", _ctx(request, "login", stage=stage, phone=phone, error=error))


@router.post("/login")
def login_submit(request: Request, phone: str = Form(...), code: str = Form(""),
                 db: Session = Depends(get_db)):
    phone = phone.strip()
    if phone not in settings.admin_list:
        return templates.TemplateResponse(request, "login.html", _ctx(request, "login", stage="phone", phone=phone,
                 error="This number is not an admin number."), status_code=403)

    if not code:
        otp = new_otp()
        db.add(OtpCode(phone=phone, code_hash=hash_otp(phone, otp), expires_at=otp_expiry()))
        db.commit()
        get_sms().send_otp(phone, otp)
        return templates.TemplateResponse(request, "login.html", _ctx(request, "login", stage="otp", phone=phone, error=""))

    row = db.scalars(select(OtpCode).where(OtpCode.phone == phone, OtpCode.used.is_(False))
                     .order_by(OtpCode.created_at.desc()).limit(1)).first()
    now = dt.datetime.now(dt.timezone.utc)
    ok = False
    if row is not None:
        exp = row.expires_at if row.expires_at.tzinfo else row.expires_at.replace(tzinfo=dt.timezone.utc)
        ok = exp >= now and row.code_hash == hash_otp(phone, code)
    if not ok:
        return templates.TemplateResponse(request, "login.html", _ctx(request, "login", stage="otp", phone=phone, error="Wrong or expired OTP."),
            status_code=400)

    row.used = True
    user = db.scalars(select(User).where(User.phone == phone)).first()
    if user is None:
        user = User(phone=phone, role=UserRole.admin)
        db.add(user)
    user.role = UserRole.admin
    db.commit()
    db.refresh(user)

    from ..security import create_token
    resp = RedirectResponse("/admin", status_code=303)
    resp.set_cookie(COOKIE, create_token(user.id, "admin"), httponly=True, samesite="lax",
                    max_age=settings.jwt_ttl_minutes * 60,
                    secure=not settings.database_url.startswith("sqlite"))
    return resp


@router.get("/logout")
def logout():
    resp = RedirectResponse("/admin/login", status_code=303)
    resp.delete_cookie(COOKIE)
    return resp


# ---------------------------------------------------------------- pages
@router.get("", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), admin: User = Depends(require_admin_page)):
    stats = views.admin_stats(db)
    analytics.recompute(db, days=30)
    bookings = views.recent_bookings(db, limit=10)
    return templates.TemplateResponse(request, "dashboard.html", _ctx(
        request, "dashboard", s=stats, t=analytics.totals(db, 30),
        series=analytics.series(db, 30), bookings=bookings))


@router.get("/bookings", response_class=HTMLResponse)
def bookings_page(request: Request, db: Session = Depends(get_db), admin: User = Depends(require_admin_page)):
    return templates.TemplateResponse(request, "bookings.html", _ctx(
        request, "bookings", rows=views.recent_bookings(db, limit=200),
        statuses=[s.value for s in BookingStatus]))


@router.post("/bookings/{booking_id}/status")
def booking_status(booking_id: int, status_value: str = Form(..., alias="status"),
                   db: Session = Depends(get_db), admin: User = Depends(require_admin_page)):
    b = db.get(Booking, booking_id)
    if b is None:
        raise HTTPException(404, "Booking not found")
    try:
        b.status = BookingStatus(status_value)
    except ValueError:
        raise HTTPException(422, "Unknown status") from None
    if b.status == BookingStatus.cancelled:
        enqueue(db, phone=b.phone, template="booking_cancelled", reference=b.reference)
    audit.record_for_user(db, admin, action="booking.status", entity="booking", entity_id=b.id,
                          detail={"status": b.status.value})
    db.commit()
    return RedirectResponse("/admin/bookings", status_code=303)


@router.get("/professionals", response_class=HTMLResponse)
def professionals_page(request: Request, db: Session = Depends(get_db), admin: User = Depends(require_admin_page)):
    rows = []
    for p in db.scalars(select(Professional)).all():
        t = tier_for(qualification=p.qualification, reg_type=p.reg_type, years=p.years,
                     designation=p.designation, gold_min_years=settings.gold_min_years)
        rows.append({"id": p.id, "name": p.name, "designation": p.designation,
                     "qualification": p.qualification, "reg_type": p.reg_type,
                     "reg_verified": p.reg_verified, "tier": t.tier, "gold": t.gold,
                     "rate_paise": p.rate_paise, "active": p.active})
    rows.sort(key=lambda r: (r["tier"], -r["rate_paise"]))
    return templates.TemplateResponse(request, "professionals.html", _ctx(request, "professionals", rows=rows))


@router.post("/professionals/{professional_id}")
def professional_update(professional_id: int, rate_paise: str = Form(""),
                        active: str = Form("1"), db: Session = Depends(get_db),
                        admin: User = Depends(require_admin_page)):
    p = db.get(Professional, professional_id)
    if p is None:
        raise HTTPException(404, "Professional not found")
    if rate_paise.strip():
        try:
            p.rate_paise = max(0, int(rate_paise.strip()))
        except ValueError:
            raise HTTPException(422, "Rate must be a whole number of paise") from None
    p.active = active == "1"
    audit.record_for_user(db, admin, action="professional.update", entity="professional",
                          entity_id=p.id, detail={"rate_paise": p.rate_paise, "active": p.active})
    db.commit()
    return RedirectResponse("/admin/professionals", status_code=303)


@router.get("/applications", response_class=HTMLResponse)
def applications_page(request: Request, db: Session = Depends(get_db), admin: User = Depends(require_admin_page)):
    rows = db.scalars(select(ProfessionalApplication)
                      .order_by(ProfessionalApplication.created_at.desc())).all()
    return templates.TemplateResponse(request, "applications.html", _ctx(request, "applications", rows=rows))


@router.post("/applications/{app_id}/verify")
def application_verify(app_id: int, approve: str = Form("1"), db: Session = Depends(get_db),
                       admin: User = Depends(require_admin_page)):
    a = db.get(ProfessionalApplication, app_id)
    if a is None:
        raise HTTPException(404, "Application not found")
    if a.status != ApplicationStatus.pending:
        return RedirectResponse("/admin/applications", status_code=303)
    ok = approve == "1"
    a.status = ApplicationStatus.verified if ok else ApplicationStatus.rejected
    a.reviewed_by = admin.phone
    a.reviewed_at = dt.datetime.now(dt.timezone.utc)
    if ok:
        slug = f"{a.name.lower().replace(' ', '-')[:24]}-{a.id}"
        db.add(Professional(slug=slug, name=a.name, designation=a.designation,
                            qualification=a.qualification, reg_type=a.reg_type,
                            reg_number=a.reg_number, reg_verified=bool(a.reg_number),
                            years=a.years, city=a.city, area=a.area, rate_paise=0,
                            care_types=a.care_types or [], languages=[], about=a.notes))
    enqueue(db, phone=a.phone,
            template="application_verified" if ok else "application_rejected")
    audit.record_for_user(db, admin, action="application.verify" if ok else "application.reject",
                          entity="application", entity_id=a.id, detail={"name": a.name})
    db.commit()
    return RedirectResponse("/admin/applications", status_code=303)


@router.get("/ledger", response_class=HTMLResponse)
def ledger_page(request: Request, db: Session = Depends(get_db), admin: User = Depends(require_admin_page)):
    return templates.TemplateResponse(request, "ledger.html", _ctx(
        request, "ledger", tb=ledger.trial_balance(db), payable=ledger.professional_payable(db)))


@router.get("/audit", response_class=HTMLResponse)
def audit_page(request: Request, db: Session = Depends(get_db), admin: User = Depends(require_admin_page)):
    return templates.TemplateResponse(request, "audit.html", _ctx(request, "audit", rows=audit.recent(db, 200)))


@router.get("/invoices/{booking_id}.pdf")
def invoice_pdf(booking_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin_page)):
    b = db.get(Booking, booking_id)
    if b is None:
        raise HTTPException(404, "Booking not found")
    p = db.get(Professional, b.professional_id)
    user = db.get(User, b.user_id)
    q = quote_detailed(care_type=b.care_type, shift=b.shift, days=b.days,
                       city=p.city if p else None, day_rate_paise=p.rate_paise if p else None)
    doc = InvoiceDoc(
        number=invoice_number(b.reference), issued_on=dt.date.today(),
        customer_name=(user.name if user and user.name else "Customer"),
        customer_phone=b.phone,
        professional_name=p.name if p else "-",
        professional_designation=p.designation if p else "-",
        booking_reference=b.reference, care_type=b.care_type, shift=b.shift, days=b.days,
        lines=[InvoiceLine(f"{b.care_type} - {b.days} day(s) ({b.shift})", b.amount_paise)],
        gst_paise=q.gst_paise,
    )
    pdf = render_pdf(doc)
    audit.record_for_user(db, admin, action="invoice.download", entity="booking", entity_id=b.id)
    db.commit()
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="{doc.number.replace("/", "-")}.pdf"'})
