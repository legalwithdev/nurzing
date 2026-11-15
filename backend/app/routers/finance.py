"""Invoices, refunds, ledger, analytics and the audit trail."""
from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import analytics, audit, ledger
from ..db import get_db
from ..deps import current_user, require_admin
from ..invoices import InvoiceDoc, InvoiceLine, invoice_number, render_pdf
from ..models import Booking, BookingStatus, Payment, PaymentStatus, Professional, Refund, RefundStatus, User
from ..rates import quote_detailed

router = APIRouter(prefix="/api", tags=["finance"])


# ---------------------------------------------------------------- invoices
@router.get("/bookings/{booking_id}/invoice.pdf")
def booking_invoice(booking_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    b = db.get(Booking, booking_id)
    if b is None or (b.user_id != user.id and user.phone not in ()):
        if b is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Booking not found")
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your booking")
    p = db.get(Professional, b.professional_id)
    q = quote_detailed(care_type=b.care_type, shift=b.shift, days=b.days,
                       city=p.city if p else None, day_rate_paise=p.rate_paise if p else None)
    doc = InvoiceDoc(number=invoice_number(b.reference), issued_on=dt.date.today(),
                     customer_name=user.name or "Customer", customer_phone=b.phone,
                     professional_name=p.name if p else "-",
                     professional_designation=p.designation if p else "-",
                     booking_reference=b.reference, care_type=b.care_type, shift=b.shift,
                     days=b.days,
                     lines=[InvoiceLine(f"{b.care_type} - {b.days} day(s) ({b.shift})", b.amount_paise)],
                     gst_paise=q.gst_paise)
    pdf = render_pdf(doc)
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="{doc.number.replace("/", "-")}.pdf"'})


# ---------------------------------------------------------------- refunds
@router.post("/bookings/{booking_id}/refund", status_code=status.HTTP_201_CREATED)
def request_refund(booking_id: int, reason: str = Query(..., min_length=4, max_length=300),
                   db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict:
    b = db.get(Booking, booking_id)
    if b is None or b.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Booking not found")

    paid = db.scalars(select(Payment).where(Payment.booking_id == b.id,
                                            Payment.status == PaymentStatus.paid)).first()
    if paid is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Nothing has been paid on this booking")

    existing = db.scalars(select(Refund).where(Refund.booking_id == b.id,
                                               Refund.status != RefundStatus.rejected)).first()
    if existing is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "A refund is already open for this booking")

    r = Refund(booking_id=b.id, payment_id=paid.id, amount_paise=paid.amount_paise,
               reason=reason, requested_by=user.id, status=RefundStatus.requested)
    db.add(r)
    audit.record(db, actor=user.phone, action="refund.request", entity="booking",
                 entity_id=b.id, detail={"amount_paise": r.amount_paise})
    db.commit()
    db.refresh(r)
    return {"id": r.id, "status": r.status.value, "amount_paise": r.amount_paise}


@router.get("/admin/refunds")
def list_refunds(db: Session = Depends(get_db), admin: User = Depends(require_admin)) -> list[dict]:
    rows = db.scalars(select(Refund).order_by(Refund.created_at.desc())).all()
    return [{"id": r.id, "booking_id": r.booking_id, "amount_paise": r.amount_paise,
             "reason": r.reason, "status": r.status.value,
             "created_at": r.created_at.isoformat()} for r in rows]


@router.post("/admin/refunds/{refund_id}/decide")
def decide_refund(refund_id: int, approve: bool = True, db: Session = Depends(get_db),
                  admin: User = Depends(require_admin)) -> dict:
    r = db.get(Refund, refund_id)
    if r is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Refund not found")
    if r.status != RefundStatus.requested:
        raise HTTPException(status.HTTP_409_CONFLICT, "Refund already decided")

    if approve:
        r.status = RefundStatus.processed
        r.processed_at = dt.datetime.now(dt.timezone.utc)
        ledger.post_refund(db, booking_id=r.booking_id, payment_id=r.payment_id,
                           amount_paise=r.amount_paise)
        booking = db.get(Booking, r.booking_id)
        if booking is not None:
            booking.status = BookingStatus.cancelled
    else:
        r.status = RefundStatus.rejected
    r.approved_by = admin.phone
    audit.record_for_user(db, admin, action="refund.approve" if approve else "refund.reject",
                          entity="refund", entity_id=r.id, detail={"amount_paise": r.amount_paise})
    db.commit()
    return {"id": r.id, "status": r.status.value}


# ---------------------------------------------------------------- ledger & analytics
@router.get("/admin/ledger")
def get_ledger(db: Session = Depends(get_db), admin: User = Depends(require_admin)) -> dict:
    tb = ledger.trial_balance(db)
    tb["professional_payable_paise"] = ledger.professional_payable(db)
    return tb


@router.get("/admin/analytics")
def get_analytics(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db),
                  admin: User = Depends(require_admin)) -> dict:
    analytics.recompute(db, days=min(days, 90))
    return {"totals": analytics.totals(db, days), "series": analytics.series(db, days)}


@router.get("/admin/audit")
def get_audit(limit: int = Query(100, ge=1, le=500), action: str | None = None,
              db: Session = Depends(get_db), admin: User = Depends(require_admin)) -> list[dict]:
    return [{"id": a.id, "actor": a.actor, "action": a.action, "entity": a.entity,
             "entity_id": a.entity_id, "detail": a.detail, "ip": a.ip,
             "created_at": a.created_at.isoformat()} for a in audit.recent(db, limit, action)]
