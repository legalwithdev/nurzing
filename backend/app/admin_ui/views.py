"""Read helpers for the dashboard."""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import settings
from ..models import (ApplicationStatus, Booking, BookingStatus, OutboxMessage, Payment,
                      PaymentStatus, Professional, ProfessionalApplication)
from ..tier import tier_for


def admin_stats(db: Session) -> dict:
    pros = list(db.scalars(select(Professional)).all())
    gold = sum(1 for p in pros if tier_for(qualification=p.qualification, reg_type=p.reg_type,
                                           years=p.years, designation=p.designation,
                                           gold_min_years=settings.gold_min_years).gold)
    paid = db.scalar(select(func.coalesce(func.sum(Payment.amount_paise), 0))
                     .where(Payment.status == PaymentStatus.paid)) or 0
    return {
        "professionals": len(pros),
        "active_professionals": sum(1 for p in pros if p.active),
        "gold_professionals": gold,
        "pending_applications": db.scalar(
            select(func.count()).select_from(ProfessionalApplication)
            .where(ProfessionalApplication.status == ApplicationStatus.pending)) or 0,
        "bookings_total": db.scalar(select(func.count()).select_from(Booking)) or 0,
        "bookings_requested": db.scalar(select(func.count()).select_from(Booking)
                                        .where(Booking.status == BookingStatus.requested)) or 0,
        "revenue_paid_paise": int(paid),
        "outbox_pending": db.scalar(select(func.count()).select_from(OutboxMessage)
                                    .where(OutboxMessage.status == "pending")) or 0,
    }


def recent_bookings(db: Session, limit: int = 20) -> list[dict]:
    rows = db.scalars(select(Booking).order_by(Booking.created_at.desc()).limit(limit)).all()
    out = []
    for b in rows:
        p = db.get(Professional, b.professional_id)
        out.append({
            "id": b.id, "reference": b.reference, "professional_name": p.name if p else "-",
            "professional_designation": p.designation if p else "-",
            "care_type": b.care_type, "shift": b.shift, "days": b.days,
            "start_date": b.start_date, "amount_paise": b.amount_paise, "status": b.status.value,
        })
    return out
