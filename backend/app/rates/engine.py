"""The quote engine.

Every rupee a customer is charged is computed here, server-side, from a
published catalogue — never from anything the client sends.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .catalog import (GST_RATE, HOLIDAY_SURGE, PLATFORM_FEE_PAISE, SHIFT_MULTIPLIERS,
                      URGENT_SURGE, care_rate, duration_discount)
from .cities import city_profile


@dataclass(frozen=True)
class Quote:
    total_paise: int
    subtotal_paise: int
    gst_paise: int
    unit: str
    days: int
    care_type: str
    shift: str
    city: str
    breakdown: dict = field(default_factory=dict)

    @property
    def total_rupees(self) -> float:
        return round(self.total_paise / 100, 2)


def quote_detailed(
    *,
    care_type: str,
    shift: str,
    days: int = 1,
    city: str | None = None,
    day_rate_paise: int | None = None,
    urgent: bool = False,
    holiday: bool = False,
    include_platform_fee: bool = True,
) -> Quote:
    """Price a booking.

    `day_rate_paise` lets an individual professional override the catalogue rate
    (an experienced nurse can charge more). Everything else comes from the catalogue.
    """
    if shift not in SHIFT_MULTIPLIERS:
        raise ValueError(f"unknown shift: {shift}")
    rate = care_rate(care_type)
    days = max(1, int(days))
    if days < rate.min_days:
        raise ValueError(f"{care_type} needs at least {rate.min_days} day(s)")

    base = int(day_rate_paise if day_rate_paise is not None else rate.base_paise)
    if base <= 0:
        raise ValueError("day rate must be positive")

    profile = city_profile(city)
    shift_mult = SHIFT_MULTIPLIERS[shift]
    dur_mult = duration_discount(days) if rate.unit == "day" else 1.0

    per_unit = int(round(base * profile.multiplier * shift_mult * dur_mult))
    core = per_unit * (days if rate.unit == "day" else 1)

    surges = []
    if urgent:
        core = int(round(core * URGENT_SURGE))
        surges.append({"name": "same-day booking", "multiplier": URGENT_SURGE})
    if holiday:
        core = int(round(core * HOLIDAY_SURGE))
        surges.append({"name": "holiday", "multiplier": HOLIDAY_SURGE})

    travel = profile.travel_paise if rate.unit in ("visit", "session") else 0
    fee = PLATFORM_FEE_PAISE if include_platform_fee else 0
    subtotal = core + travel + fee
    gst = int(round(subtotal * GST_RATE))

    breakdown = {
        "catalogue_base_paise": rate.base_paise,
        "applied_day_rate_paise": base,
        "city": profile.name,
        "city_tier": profile.tier,
        "city_multiplier": profile.multiplier,
        "shift": shift,
        "shift_multiplier": shift_mult,
        "duration_multiplier": dur_mult,
        "days": days,
        "unit": rate.unit,
        "per_unit_paise": per_unit,
        "core_paise": core,
        "travel_paise": travel,
        "platform_fee_paise": fee,
        "surges": surges,
        "gst_rate": GST_RATE,
        "gst_paise": gst,
        "subtotal_paise": subtotal,
    }
    return Quote(total_paise=subtotal + gst, subtotal_paise=subtotal, gst_paise=gst,
                 unit=rate.unit, days=days, care_type=care_type, shift=shift,
                 city=profile.name, breakdown=breakdown)


def quote(*, day_rate_paise: int, shift: str, days: int, care_type: str = "Home Nursing",
          city: str | None = None) -> tuple[int, str, dict]:
    """Backwards-compatible helper used by the existing booking routers."""
    q = quote_detailed(care_type=care_type, shift=shift, days=days, city=city,
                       day_rate_paise=day_rate_paise)
    return q.total_paise, q.unit, q.breakdown
