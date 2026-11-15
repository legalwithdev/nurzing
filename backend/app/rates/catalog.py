"""What each kind of care costs before any city or shift adjustment."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CareRate:
    label: str
    base_paise: int          # per unit, before city/shift/duration
    unit: str                # day | visit | session
    min_days: int = 1
    requires_registration: bool = False   # only a licensed nurse may be booked for this


CARE_CATALOG: dict[str, CareRate] = {
    "Home Nursing":            CareRate("Home Nursing", 150_000, "day", requires_registration=True),
    "Live-in Nursing (24x7)":  CareRate("Live-in Nursing (24x7)", 280_000, "day", requires_registration=True),
    "Elderly Care & Attendants": CareRate("Elderly Care & Attendants", 95_000, "day"),
    "Post-Surgical Recovery":  CareRate("Post-Surgical Recovery", 170_000, "day", requires_registration=True),
    "Mother & Baby Care":      CareRate("Mother & Baby Care", 185_000, "day", requires_registration=True),
    "Physiotherapy at Home":   CareRate("Physiotherapy at Home", 85_000, "session"),
    "ICU-Trained Nurses":      CareRate("ICU-Trained Nurses", 240_000, "day", requires_registration=True),
}

SHIFT_MULTIPLIERS: dict[str, float] = {
    "12-hour day shift": 1.00,
    "Night shift only": 1.08,
    "24-hour live-in": 1.90,
    "Hourly visit": 0.22,
}
VALID_SHIFTS = list(SHIFT_MULTIPLIERS.keys())

# long stays get cheaper per day — this is what makes 30-day care sellable
DURATION_DISCOUNTS: list[tuple[int, float]] = [
    (30, 0.88),   # 30+ days -> 12% off
    (15, 0.92),
    (7, 0.96),
    (1, 1.00),
]

URGENT_SURGE = 1.15          # booking for today
HOLIDAY_SURGE = 1.10         # public holiday / festival day
GST_RATE = 0.0               # healthcare services are currently exempt; kept explicit
PLATFORM_FEE_PAISE = 4_900   # flat booking fee


def duration_discount(days: int) -> float:
    for threshold, mult in DURATION_DISCOUNTS:
        if days >= threshold:
            return mult
    return 1.0


def care_rate(care_type: str) -> CareRate:
    try:
        return CARE_CATALOG[care_type]
    except KeyError:
        raise ValueError(f"unknown care type: {care_type}") from None
