"""Compatibility shim — the real engine lives in `app/rates/`."""
from .rates import VALID_SHIFTS, quote, quote_detailed, CARE_CATALOG  # noqa: F401

__all__ = ["VALID_SHIFTS", "quote", "quote_detailed", "CARE_CATALOG"]
