"""Admin-only operations."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import require_admin
from ..models import Booking, BookingStatus, Professional, User
from ..schemas import BookingOut
from .bookings import _to_out

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/bookings", response_model=list[BookingOut])
def all_bookings(db: Session = Depends(get_db), admin: User = Depends(require_admin)) -> list[BookingOut]:
    from sqlalchemy import select
    rows = db.scalars(select(Booking).order_by(Booking.created_at.desc())).all()
    out = []
    for b in rows:
        p = db.get(Professional, b.professional_id)
        if p:
            out.append(_to_out(b, p))
    return out


@router.patch("/bookings/{booking_id}/status", response_model=BookingOut)
def set_status(
    booking_id: int,
    new_status: BookingStatus,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> BookingOut:
    b = db.get(Booking, booking_id)
    if b is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Booking not found")
    b.status = new_status
    db.commit()
    db.refresh(b)
    p = db.get(Professional, b.professional_id)
    if p is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Professional not found")
    return _to_out(b, p)
