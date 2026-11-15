"""Transactional notifications via an outbox.

Nothing is sent inline: the request writes a row and returns. `worker.drain()`
delivers pending messages, so a slow or failing SMS provider never blocks a
booking and nothing is silently lost.
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import OutboxMessage
from .sms import get_sms

TEMPLATES = {
    "otp": "Your NURZING verification code is {code}. It expires in {minutes} minutes.",
    "booking_received": "NURZING: booking {reference} received for {date}. A care advisor will call you shortly.",
    "booking_confirmed": "NURZING: booking {reference} is confirmed with {professional}.",
    "booking_cancelled": "NURZING: booking {reference} has been cancelled.",
    "application_received": "NURZING: we received your listing request. Our team will verify your details.",
    "application_verified": "NURZING: your profile is verified and live. You can now receive care requests.",
    "application_rejected": "NURZING: we could not verify your listing. Our team will contact you.",
    "booking_reminder": "NURZING: reminder — your care booking {reference} starts on {date}.",
    "booking_followup": "NURZING: how did the care go for booking {reference}? Reply and tell us.",
    "payment_received": "NURZING: payment received for booking {reference}. Thank you.",
    "refund_processed": "NURZING: refund of {amount} for booking {reference} has been processed.",
}


def render(template: str, **ctx) -> str:
    if template not in TEMPLATES:
        raise ValueError(f"unknown notification template: {template}")
    try:
        return TEMPLATES[template].format(**ctx)
    except KeyError as exc:
        raise ValueError(f"template {template!r} is missing {exc}") from None


def enqueue(db: Session, *, phone: str, template: str, **ctx) -> OutboxMessage:
    msg = OutboxMessage(phone=phone, template=template, payload=ctx,
                        body=render(template, **ctx))
    db.add(msg)
    return msg


def drain(db: Session, limit: int = 50) -> dict:
    """Deliver pending messages. Returns a small report."""
    provider = get_sms()
    rows = list(db.scalars(
        select(OutboxMessage)
        .where(OutboxMessage.status == "pending")
        .order_by(OutboxMessage.created_at)
        .limit(limit)
    ))
    sent = failed = 0
    for m in rows:
        result = provider.send_text(m.phone, m.body)
        m.attempts += 1
        if result.ok:
            m.status = "sent"
            m.sent_at = dt.datetime.now(dt.timezone.utc)
            m.last_error = None
            sent += 1
        else:
            m.status = "failed" if m.attempts >= 3 else "pending"
            m.last_error = (result.error or "unknown")[:500]
            failed += 1
    db.commit()
    return {"processed": len(rows), "sent": sent, "failed": failed, "provider": provider.name}
