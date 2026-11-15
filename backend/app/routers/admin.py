"""Admin-only operations: stats, professionals, assignment, documents, outbox."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..deps import require_admin
from ..models import (ApplicationStatus, Booking, BookingStatus, Document, OutboxMessage, Payment,
                      PaymentStatus, Professional, ProfessionalApplication, User)
from ..notifications import drain, enqueue
from ..schemas import AdminStats, AssignIn, BookingOut, DocumentOut, ProfessionalOut, ProfessionalUpdate
from ..tier import tier_for
from .bookings import _to_out
from .professionals import to_out

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStats)
def stats(db: Session = Depends(get_db), admin: User = Depends(require_admin)) -> AdminStats:
    pros = list(db.scalars(select(Professional)).all())
    gold = sum(1 for p in pros if tier_for(qualification=p.qualification, reg_type=p.reg_type,
                                           years=p.years, designation=p.designation,
                                           gold_min_years=settings.gold_min_years).gold)
    paid = db.scalar(select(func.coalesce(func.sum(Payment.amount_paise), 0))
                     .where(Payment.status == PaymentStatus.paid)) or 0
    return AdminStats(
        professionals=len(pros),
        active_professionals=sum(1 for p in pros if p.active),
        gold_professionals=gold,
        pending_applications=db.scalar(select(func.count()).select_from(ProfessionalApplication)
                                       .where(ProfessionalApplication.status == ApplicationStatus.pending)) or 0,
        bookings_total=db.scalar(select(func.count()).select_from(Booking)) or 0,
        bookings_requested=db.scalar(select(func.count()).select_from(Booking)
                                     .where(Booking.status == BookingStatus.requested)) or 0,
        revenue_paid_paise=int(paid),
        outbox_pending=db.scalar(select(func.count()).select_from(OutboxMessage)
                                 .where(OutboxMessage.status == "pending")) or 0,
    )


@router.get("/bookings", response_model=list[BookingOut])
def all_bookings(db: Session = Depends(get_db), admin: User = Depends(require_admin)) -> list[BookingOut]:
    rows = db.scalars(select(Booking).order_by(Booking.created_at.desc())).all()
    out = []
    for b in rows:
        p = db.get(Professional, b.professional_id)
        if p:
            out.append(_to_out(b, p))
    return out


@router.patch("/bookings/{booking_id}/status", response_model=BookingOut)
def set_status(booking_id: int, new_status: BookingStatus, db: Session = Depends(get_db),
               admin: User = Depends(require_admin)) -> BookingOut:
    b = db.get(Booking, booking_id)
    if b is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Booking not found")
    b.status = new_status
    p = db.get(Professional, b.professional_id)
    if p is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Professional not found")
    if new_status == BookingStatus.confirmed:
        enqueue(db, phone=b.phone, template="booking_confirmed",
                reference=b.reference, professional=p.name)
    if new_status == BookingStatus.cancelled:
        enqueue(db, phone=b.phone, template="booking_cancelled", reference=b.reference)
    db.commit()
    db.refresh(b)
    return _to_out(b, p)


@router.post("/bookings/{booking_id}/assign", response_model=BookingOut)
def assign(booking_id: int, body: AssignIn, db: Session = Depends(get_db),
           admin: User = Depends(require_admin)) -> BookingOut:
    b = db.get(Booking, booking_id)
    if b is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Booking not found")
    p = db.get(Professional, body.professional_id)
    if p is None or not p.active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Professional not found")
    b.professional_id = p.id
    db.commit()
    db.refresh(b)
    return _to_out(b, p)


@router.get("/professionals", response_model=list[ProfessionalOut])
def list_all(db: Session = Depends(get_db), admin: User = Depends(require_admin)) -> list[ProfessionalOut]:
    return [to_out(p) for p in db.scalars(select(Professional)).all()]


@router.patch("/professionals/{professional_id}", response_model=ProfessionalOut)
def update_professional(professional_id: int, body: ProfessionalUpdate, db: Session = Depends(get_db),
                        admin: User = Depends(require_admin)) -> ProfessionalOut:
    p = db.get(Professional, professional_id)
    if p is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Professional not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(p, field, value)
    db.commit()
    db.refresh(p)
    return to_out(p)


@router.get("/documents/{owner_type}/{owner_id}", response_model=list[DocumentOut])
def list_documents(owner_type: str, owner_id: int, db: Session = Depends(get_db),
                   admin: User = Depends(require_admin)) -> list[DocumentOut]:
    rows = db.scalars(select(Document).where(Document.owner_type == owner_type,
                                             Document.owner_id == owner_id)).all()
    return [DocumentOut(id=d.id, owner_type=d.owner_type, owner_id=d.owner_id, kind=d.kind, url=d.url,
                        content_type=d.content_type, size=d.size, verified=d.verified,
                        uploaded_at=d.uploaded_at) for d in rows]


@router.post("/documents/{document_id}/verify", response_model=DocumentOut)
def verify_document(document_id: int, approve: bool = True, db: Session = Depends(get_db),
                    admin: User = Depends(require_admin)) -> DocumentOut:
    d = db.get(Document, document_id)
    if d is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    d.verified = approve
    db.commit()
    db.refresh(d)
    return DocumentOut(id=d.id, owner_type=d.owner_type, owner_id=d.owner_id, kind=d.kind, url=d.url,
                       content_type=d.content_type, size=d.size, verified=d.verified,
                       uploaded_at=d.uploaded_at)


@router.post("/outbox/drain")
def drain_outbox(limit: int = 50, db: Session = Depends(get_db),
                 admin: User = Depends(require_admin)) -> dict:
    return drain(db, limit=limit)
