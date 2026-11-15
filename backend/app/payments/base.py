"""Payment provider contract — swap providers without touching the routers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class PaymentError(Exception):
    """Raised when a provider rejects a request or a signature fails."""


@dataclass(frozen=True)
class PaymentOrder:
    provider_order_id: str
    amount_paise: int
    currency: str
    public_key: str | None
    raw: dict


@dataclass(frozen=True)
class PaymentVerification:
    ok: bool
    provider_payment_id: str | None
    reason: str | None = None


class PaymentProvider(Protocol):
    name: str

    def create_order(self, *, amount_paise: int, receipt: str, notes: dict | None = None) -> PaymentOrder: ...

    def verify_payment(self, *, order_id: str, payment_id: str, signature: str) -> PaymentVerification: ...

    def verify_webhook(self, *, body: bytes, signature: str) -> bool: ...
