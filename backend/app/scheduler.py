"""Scheduled notifications.

Booking reminders, "how did it go?" follow-ups and payment nudges are written
here with a future timestamp and released by the worker when they come due.
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import OutboxMessage, ScheduledNotification
from .notifications import enqueue

REMINDER_OFFSETS_HOURS = {
    "booking_received": 0,
    "booking_reminder": -18,     # ~18h before the shift
    "booking_followup": 24,      # a day after it ends
}


def schedule(db: Session, *, phone: str, template: str, run_at: dt.datetime,
             **payload) -> ScheduledNotification:
    row = ScheduledNotification(phone=phone, template=template, payload=payload, run_at=run_at)
    db.add(row)
    return row


def schedule_booking_reminders(db: Session, *, phone: str, reference: str,
                               start: dt.date, days: int = 1) -> list[ScheduledNotification]:
    """A reminder the evening before, and a follow-up after the booking ends."""
    start_dt = dt.datetime.combine(start, dt.time(hour=18, tzinfo=dt.timezone.utc))
    rows = [
        schedule(db, phone=phone, template="booking_reminder",
                 run_at=start_dt - dt.timedelta(hours=18), reference=reference, date=str(start)),
        schedule(db, phone=phone, template="booking_followup",
                 run_at=start_dt + dt.timedelta(days=days), reference=reference),
    ]
    return rows


def due(db: Session, now: dt.datetime | None = None, limit: int = 100) -> list[ScheduledNotification]:
    now = now or dt.datetime.now(dt.timezone.utc)
    return list(db.scalars(
        select(ScheduledNotification)
        .where(ScheduledNotification.status == "pending", ScheduledNotification.run_at <= now)
        .order_by(ScheduledNotification.run_at)
        .limit(limit)
    ))


def release_due(db: Session, now: dt.datetime | None = None, limit: int = 100) -> dict:
    """Move due notifications into the outbox. Returns a small report."""
    rows = due(db, now, limit)
    released = 0
    for r in rows:
        try:
            enqueue(db, phone=r.phone, template=r.template, **r.payload)
            r.status = "released"
            released += 1
        except Exception:
            r.status = "invalid"
    db.commit()
    return {"due": len(rows), "released": released}
