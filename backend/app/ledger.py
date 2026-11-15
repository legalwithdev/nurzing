"""Double-entry ledger.

Every payment posts balanced debits and credits, so revenue, what we owe
professionals, GST and refunds can all be read straight off the ledger instead
of being recomputed from bookings.
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import LedgerAccount, LedgerEntry

PLATFORM_SHARE = 0.20      # the bureau's margin on a booking
PROFESSIONAL_SHARE = 0.80


def _post(db: Session, *, account: LedgerAccount, debit: int = 0, credit: int = 0,
          booking_id: int | None = None, payment_id: int | None = None, memo: str = "") -> LedgerEntry:
    e = LedgerEntry(account=account, debit_paise=debit, credit_paise=credit,
                    booking_id=booking_id, payment_id=payment_id, memo=memo)
    db.add(e)
    return e


def post_payment(db: Session, *, booking_id: int, payment_id: int, amount_paise: int,
                 gst_paise: int = 0) -> list[LedgerEntry]:
    """Customer paid: cash in, revenue + payable + GST out. Debits must equal credits."""
    net = amount_paise - gst_paise
    platform = int(round(net * PLATFORM_SHARE))
    professional = net - platform
    rows = [
        _post(db, account=LedgerAccount.cash, debit=amount_paise, booking_id=booking_id,
              payment_id=payment_id, memo="payment captured"),
        _post(db, account=LedgerAccount.platform_revenue, credit=platform, booking_id=booking_id,
              payment_id=payment_id, memo="platform share"),
        _post(db, account=LedgerAccount.professional_payable, credit=professional,
              booking_id=booking_id, payment_id=payment_id, memo="professional share"),
    ]
    if gst_paise:
        rows.append(_post(db, account=LedgerAccount.gst_payable, credit=gst_paise,
                          booking_id=booking_id, payment_id=payment_id, memo="GST"))
    return rows


def post_refund(db: Session, *, booking_id: int, payment_id: int | None, amount_paise: int) -> list[LedgerEntry]:
    return [
        _post(db, account=LedgerAccount.refunds, debit=amount_paise, booking_id=booking_id,
              payment_id=payment_id, memo="refund"),
        _post(db, account=LedgerAccount.cash, credit=amount_paise, booking_id=booking_id,
              payment_id=payment_id, memo="refund paid out"),
    ]


def trial_balance(db: Session) -> dict:
    rows = db.execute(
        select(LedgerEntry.account, func.coalesce(func.sum(LedgerEntry.debit_paise), 0),
               func.coalesce(func.sum(LedgerEntry.credit_paise), 0)).group_by(LedgerEntry.account)
    ).all()
    out = {}
    total_d = total_c = 0
    for account, debit, credit in rows:
        account = account.value if hasattr(account, "value") else str(account)
        out[account] = {"debit_paise": int(debit), "credit_paise": int(credit),
                        "balance_paise": int(debit) - int(credit)}
        total_d += int(debit)
        total_c += int(credit)
    return {"accounts": out, "total_debit_paise": total_d, "total_credit_paise": total_c,
            "balanced": total_d == total_c}


def is_balanced(db: Session) -> bool:
    return trial_balance(db)["balanced"]


def revenue_between(db: Session, start: dt.date, end: dt.date) -> int:
    total = db.scalar(
        select(func.coalesce(func.sum(LedgerEntry.credit_paise), 0)).where(
            LedgerEntry.account == LedgerAccount.platform_revenue,
            func.date(LedgerEntry.created_at) >= str(start),
            func.date(LedgerEntry.created_at) <= str(end))
    )
    return int(total or 0)


def professional_payable(db: Session) -> int:
    d = db.scalar(select(func.coalesce(func.sum(LedgerEntry.debit_paise), 0))
                  .where(LedgerEntry.account == LedgerAccount.professional_payable)) or 0
    c = db.scalar(select(func.coalesce(func.sum(LedgerEntry.credit_paise), 0))
                  .where(LedgerEntry.account == LedgerAccount.professional_payable)) or 0
    return int(c) - int(d)
