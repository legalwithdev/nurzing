"""NURZING priority rules — the standing rule, expressed once, in code.

Tier order (never change without the owner's sign-off):
  1 = B.Sc Nursing + RN&RM registration + experience + a specialisation  -> highest authority
  2 = RN&RM with GNM (a licensed nurse)
  3 = other licensed profession (e.g. physiotherapy)
  4 = non-medical support (attendant / ward boy / GDA)

The GOLD badge is tier 1 only. It is DERIVED, never stored by hand, so it can
never drift or be granted by mistake.
"""
from __future__ import annotations

from dataclasses import dataclass

TIER_BSC = 1
TIER_GNM = 2
TIER_LICENSED_OTHER = 3
TIER_SUPPORT = 4

REG_RNRM = "RN&RM"
REG_RANM = "RANM"
REG_NONE = "none"

SUPPORT_WORDS = (
    "attendant", "ward boy", "wardboy", "caregiver", "nursing assistant",
    "general duty assistant", "gda", "housekeeping", "ayah", "helper",
)
LICENSED_OTHER_WORDS = ("physiotherap", "occupational therap", "nutritionist", "dietitian")


@dataclass(frozen=True)
class Tier:
    tier: int
    gold: bool
    label: str


def has_specialisation(designation: str | None) -> bool:
    """A designation counts as specialised when it names one, e.g. 'RN&RM Nurse (ICU)'."""
    if not designation:
        return False
    d = designation.strip()
    return "(" in d and ")" in d and len(d.split("(")[-1].rstrip(")").strip()) > 0


def _is_support(designation: str | None) -> bool:
    d = (designation or "").lower()
    return any(w in d for w in SUPPORT_WORDS)


def _is_licensed_other(designation: str | None) -> bool:
    d = (designation or "").lower()
    return any(w in d for w in LICENSED_OTHER_WORDS)


def tier_for(
    *,
    qualification: str | None,
    reg_type: str | None,
    years: int | None,
    designation: str | None,
    gold_min_years: int = 7,
) -> Tier:
    """Compute the tier + gold flag from a professional's own record."""
    qual = (qualification or "").strip().lower()
    reg = (reg_type or REG_NONE).strip()
    yrs = int(years or 0)

    if _is_support(designation):
        return Tier(TIER_SUPPORT, False, "Non-medical support")
    if _is_licensed_other(designation):
        return Tier(TIER_LICENSED_OTHER, False, "Licensed professional")

    if reg == REG_RNRM:
        if qual in ("b.sc nursing", "bsc nursing", "b.sc. nursing") and yrs >= gold_min_years and has_specialisation(designation):
            return Tier(TIER_BSC, True, "B.Sc Nursing + RN&RM, experienced & specialised")
        return Tier(TIER_GNM, False, "Registered nurse (RN&RM)")

    if reg == REG_RANM:
        return Tier(TIER_GNM, False, "Registered auxiliary nurse midwife (RANM)")

    # unknown record: keep it visible but never claim a tier it hasn't earned
    return Tier(TIER_SUPPORT, False, "Unclassified")
