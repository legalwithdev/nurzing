"""Daily rollups.

Computing dashboards from raw tables gets slower every day. These rollups are
cheap to read and are safe to recompute at any time.
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .ledger import revenue_between
from .models import Booking, BookingStatus, DailyRollup, LedgerAccount, LedgerEntry, Payment, PaymentStatus, User


def _as_date(value) -> dt.date:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(str(value)[:10])


def compute_day(db: Session, day: dt.date) -> DailyRollup:
    d = str(day)

    created = db.scalar(select(func.count()).select_from(Booking)
                        .where(func.date(Booking.created_at) == d)) or 0
    completed = db.scalar(select(func.count()).select_from(Booking)
                          .where(Booking.status == BookingStatus.completed,
                                 func.date(Booking.created_at) == d)) or 0
    gmv = db.scalar(select(func.coalesce(func.sum(Payment.amount_paise), 0))
                    .where(Payment.status == PaymentStatus.paid,
                           func.date(Payment.created_at) == d)) or 0
    refunds = db.scalar(select(func.coalesce(func.sum(LedgerEntry.debit_paise), 0))
                        .where(LedgerEntry.account == LedgerAccount.refunds,
                               func.date(LedgerEntry.created_at) == d)) or 0
    new_users = db.scalar(select(func.count()).select_from(User)
                          .where(func.date(User.created_at) == d)) or 0

    row = db.scalars(select(DailyRollup).where(DailyRollup.day == day)).first()
    if row is None:
        row = DailyRollup(day=day)
        db.add(row)
    row.bookings_created = int(created)
    row.bookings_completed = int(completed)
    row.gmv_paise = int(gmv)
    row.revenue_paise = revenue_between(db, day, day)
    row.refunds_paise = int(refunds)
    row.new_users = int(new_users)
    row.computed_at = dt.datetime.now(dt.timezone.utc)
    db.commit()
    db.refresh(row)
    return row


def recompute(db: Session, days: int = 30, today: dt.date | None = None) -> list[DailyRollup]:
    today = today or dt.date.today()
    return [compute_day(db, today - dt.timedelta(days=i)) for i in range(days - 1, -1, -1)]


def series(db: Session, days: int = 30, today: dt.date | None = None) -> list[dict]:
    today = today or dt.date.today()
    start = today - dt.timedelta(days=days - 1)
    rows = {r.day: r for r in db.scalars(select(DailyRollup).where(DailyRollup.day >= start)).all()}
    out = []
    for i in range(days):
        day = start + dt.timedelta(days=i)
        r = rows.get(day)
        out.append({
            "day": day.isoformat(),
            "bookings_created": r.bookings_created if r else 0,
            "bookings_completed": r.bookings_completed if r else 0,
            "gmv_paise": r.gmv_paise if r else 0,
            "revenue_paise": r.revenue_paise if r else 0,
            "refunds_paise": r.refunds_paise if r else 0,
            "new_users": r.new_users if r else 0,
        })
    return out


def totals(db: Session, days: int = 30) -> dict:
    data = series(db, days)
    return {
        "days": days,
        "bookings_created": sum(d["bookings_created"] for d in data),
        "bookings_completed": sum(d["bookings_completed"] for d in data),
        "gmv_paise": sum(d["gmv_paise"] for d in data),
        "revenue_paise": sum(d["revenue_paise"] for d in data),
        "refunds_paise": sum(d["refunds_paise"] for d in data),
        "new_users": sum(d["new_users"] for d in data),
    }
