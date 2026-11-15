"""City tiers. A nurse in Mumbai costs more than the same nurse in Indore."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CityProfile:
    name: str
    tier: int
    multiplier: float
    travel_paise: int        # per-visit travel component
    active: bool = True


CITY_TIERS: dict[str, CityProfile] = {
    # tier 1 — metros, highest cost of living
    "Mumbai":     CityProfile("Mumbai", 1, 1.15, 20_000),
    "Delhi NCR":  CityProfile("Delhi NCR", 1, 1.12, 18_000),
    "Bengaluru":  CityProfile("Bengaluru", 1, 1.10, 18_000),
    # tier 2
    "Hyderabad":  CityProfile("Hyderabad", 2, 1.02, 14_000),
    "Pune":       CityProfile("Pune", 2, 1.00, 14_000),
    "Chennai":    CityProfile("Chennai", 2, 1.00, 14_000),
    # tier 3 — launching later
    "Ahmedabad":  CityProfile("Ahmedabad", 3, 0.92, 12_000, active=False),
    "Jaipur":     CityProfile("Jaipur", 3, 0.90, 12_000, active=False),
    "Indore":     CityProfile("Indore", 3, 0.88, 10_000, active=False),
    "Lucknow":    CityProfile("Lucknow", 3, 0.88, 10_000, active=False),
}

DEFAULT_PROFILE = CityProfile("Other", 3, 1.00, 12_000)


def city_profile(city: str | None) -> CityProfile:
    if not city:
        return DEFAULT_PROFILE
    return CITY_TIERS.get(city.strip(), DEFAULT_PROFILE)


def active_cities() -> list[str]:
    return [c.name for c in CITY_TIERS.values() if c.active]
