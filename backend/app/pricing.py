"""Server-side price calculation.

Prices are computed HERE and never trusted from the client — otherwise anyone
can post any amount they like.
"""
from __future__ import annotations

SHIFT_MULTIPLIER = {
    "12-hour day shift": 1.0,
    "Night shift only": 1.0,
    "24-hour live-in": 1.15,
    "Hourly visit": 0.35,
}
VALID_SHIFTS = list(SHIFT_MULTIPLIER.keys())
CURRENCY = "INR"


def quote(*, day_rate_paise: int, shift: str, days: int) -> tuple[int, str, dict]:
    """Return (amount_paise, unit, breakdown)."""
    if shift not in SHIFT_MULTIPLIER:
        raise ValueError(f"unknown shift: {shift}")
    days = max(1, int(days))
    mult = SHIFT_MULTIPLIER[shift]
    base = int(round(day_rate_paise * mult))
    if shift == "Hourly visit":
        amount = base
        unit = "visit"
    else:
        amount = base * days
        unit = "day"
    breakdown = {
        "day_rate_paise": day_rate_paise,
        "shift": shift,
        "shift_multiplier": mult,
        "days": days,
        "base_paise": base,
    }
    return amount, unit, breakdown
