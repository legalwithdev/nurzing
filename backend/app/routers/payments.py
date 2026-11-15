"""Payments — create an order, verify the signature, accept webhooks."""
from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import current_user
from ..models import Booking, BookingStatus, Payment, PaymentStatus, User
from ..notifications import enqueue
from .. import ledger
from ..payments import PaymentError, get_provider
from ..schemas import PaymentOrderIn, PaymentOrderOut, PaymentOut, PaymentVerifyIn

router = APIRouter(prefix="/api/payments", tags=["payments"])


def _out(p: Payment) -> PaymentOut:
    return PaymentOut(id=p.id, booking_id=p.booking_id, provider=p.provider, status=p.status.value,
                      amount_paise=p.amount_paise, currency=p.currency,
                      provider_order_id=p.provider_order_id, provider_payment_id=p.provider_payment_id,
                      signature_verified=p.signature_verified, created_at=p.created_at)


@router.post("/order", response_model=PaymentOrderOut, status_code=status.HTTP_201_CREATED)
def create_order(body: PaymentOrderIn, db: Session = Depends(get_db), user: User = Depends(current_user)) -> PaymentOrderOut:
    b = db.get(Booking, body.booking_id)
    if b is None or b.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Booking not found")
    if b.amount_paise <= 0:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Booking has no amount to pay")

    provider = get_provider()
    try:
        order = provider.create_order(amount_paise=b.amount_paise, receipt=b.reference,
                                      notes={"booking": b.reference})
    except PaymentError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from None

    pay = Payment(booking_id=b.id, provider=provider.name, provider_order_id=order.provider_order_id,
                  amount_paise=order.amount_paise, currency=order.currency, status=PaymentStatus.created)
    db.add(pay)
    db.commit()
    db.refresh(pay)
    return PaymentOrderOut(payment_id=pay.id, provider=pay.provider,
                           provider_order_id=pay.provider_order_id, amount_paise=pay.amount_paise,
                           currency=pay.currency, public_key=order.public_key)


@router.post("/verify", response_model=PaymentOut)
def verify(body: PaymentVerifyIn, db: Session = Depends(get_db), user: User = Depends(current_user)) -> PaymentOut:
    pay = db.get(Payment, body.payment_id)
    if pay is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Payment not found")
    booking = db.get(Booking, pay.booking_id)
    if booking is None or booking.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Payment not found")

    provider = get_provider()
    result = provider.verify_payment(order_id=pay.provider_order_id,
                                     payment_id=body.provider_payment_id, signature=body.signature)
    if not result.ok:
        pay.status = PaymentStatus.failed
        db.commit()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, result.reason or "Signature verification failed")

    pay.status = PaymentStatus.paid
    pay.provider_payment_id = body.provider_payment_id
    pay.signature_verified = True
    pay.paid_at = dt.datetime.now(dt.timezone.utc)
    booking.status = BookingStatus.confirmed
    ledger.post_payment(db, booking_id=booking.id, payment_id=pay.id,
                        amount_paise=pay.amount_paise, gst_paise=0)
    db.commit()
    db.refresh(pay)
    return _out(pay)


@router.post("/webhook", include_in_schema=False)
async def webhook(request: Request, db: Session = Depends(get_db)) -> dict:
    """Provider -> us. Signature is verified before anything is trusted."""
    raw = await request.body()
    signature = request.headers.get("x-razorpay-signature", "")
    provider = get_provider()
    if not provider.verify_webhook(body=raw, signature=signature):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Bad webhook signature")

    import json
    try:
        event = json.loads(raw.decode() or "{}")
    except ValueError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Bad JSON") from None

    entity = (event.get("payload", {}).get("payment", {}) or {}).get("entity", {}) or {}
    order_id = entity.get("order_id")
    payment_id = entity.get("id")
    if not order_id:
        return {"ok": True, "ignored": True}

    from sqlalchemy import select
    pay = db.scalars(select(Payment).where(Payment.provider_order_id == order_id)).first()
    if pay is None:
        return {"ok": True, "ignored": True}

    if event.get("event") == "payment.captured":
        pay.status = PaymentStatus.paid
        pay.provider_payment_id = payment_id
        pay.paid_at = dt.datetime.now(dt.timezone.utc)
        booking = db.get(Booking, pay.booking_id)
        if booking:
            booking.status = BookingStatus.confirmed
    elif event.get("event") == "payment.failed":
        pay.status = PaymentStatus.failed
    db.commit()
    return {"ok": True}


@router.get("/{payment_id}", response_model=PaymentOut)
def get_payment(payment_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)) -> PaymentOut:
    pay = db.get(Payment, payment_id)
    if pay is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Payment not found")
    booking = db.get(Booking, pay.booking_id)
    if booking is None or booking.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Payment not found")
    return _out(pay)
