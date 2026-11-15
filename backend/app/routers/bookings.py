"""Bookings — price is always computed server-side."""
from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import current_user
from ..models import Booking, BookingStatus, Professional, User
from ..notifications import enqueue
from ..pricing import quote
from ..schemas import BookingIn, BookingOut, QuoteIn, QuoteOut

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


def _to_out(b: Booking, p: Professional) -> BookingOut:
    return BookingOut(
        id=b.id, reference=b.reference, professional_id=b.professional_id,
        professional_name=p.name, professional_designation=p.designation,
        care_type=b.care_type, shift=b.shift, days=b.days, start_date=b.start_date,
        address=b.address, patient_name=b.patient_name, phone=b.phone, notes=b.notes,
        amount_paise=b.amount_paise, status=b.status.value, created_at=b.created_at,
    )


@router.post("/quote", response_model=QuoteOut)
def get_quote(body: QuoteIn, db: Session = Depends(get_db)) -> QuoteOut:
    p = db.get(Professional, body.professional_id)
    if p is None or not p.active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Professional not found")
    try:
        amount, unit, breakdown = quote(day_rate_paise=p.rate_paise, shift=body.shift, days=body.days)
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from None
    return QuoteOut(amount_paise=amount, unit=unit, breakdown=breakdown)


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(body: BookingIn, db: Session = Depends(get_db), user: User = Depends(current_user)) -> BookingOut:
    p = db.get(Professional, body.professional_id)
    if p is None or not p.active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Professional not found")
    try:
        amount, _unit, _bd = quote(day_rate_paise=p.rate_paise, shift=body.shift, days=body.days)
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from None

    ref = "NZ" + secrets.token_hex(3).upper()
    b = Booking(
        reference=ref, user_id=user.id, professional_id=p.id, care_type=body.care_type,
        shift=body.shift, days=body.days, start_date=body.start_date, address=body.address,
        patient_name=body.patient_name, phone=body.phone, notes=body.notes, amount_paise=amount,
        status=BookingStatus.requested,
    )
    db.add(b)
    enqueue(db, phone=b.phone, template="booking_received",
            reference=ref, date=str(body.start_date))
    db.commit()
    db.refresh(b)
    return _to_out(b, p)


@router.get("", response_model=list[BookingOut])
def my_bookings(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[BookingOut]:
    rows = db.scalars(select(Booking).where(Booking.user_id == user.id).order_by(Booking.created_at.desc())).all()
    out = []
    for b in rows:
        p = db.get(Professional, b.professional_id)
        if p:
            out.append(_to_out(b, p))
    return out


@router.get("/{booking_id}", response_model=BookingOut)
def one_booking(booking_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> BookingOut:
    b = db.get(Booking, booking_id)
    if b is None or b.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Booking not found")
    p = db.get(Professional, b.professional_id)
    if p is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Professional not found")
    return _to_out(b, p)
