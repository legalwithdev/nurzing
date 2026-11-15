"""Deterministic provider for local dev and tests. Never moves money."""
from __future__ import annotations

import hashlib
import hmac

from .base import PaymentError, PaymentOrder, PaymentVerification

SECRET = b"dummy-secret"


class DummyProvider:
    name = "dummy"

    def create_order(self, *, amount_paise: int, receipt: str, notes: dict | None = None) -> PaymentOrder:
        if amount_paise <= 0:
            raise PaymentError("amount must be positive")
        oid = "order_dummy_" + hashlib.sha1(f"{receipt}:{amount_paise}".encode()).hexdigest()[:12]
        return PaymentOrder(provider_order_id=oid, amount_paise=amount_paise, currency="INR",
                            public_key=None, raw={"id": oid, "receipt": receipt})

    def verify_payment(self, *, order_id: str, payment_id: str, signature: str) -> PaymentVerification:
        expected = hmac.new(SECRET, f"{order_id}|{payment_id}".encode(), hashlib.sha256).hexdigest()
        if hmac.compare_digest(expected, signature):
            return PaymentVerification(ok=True, provider_payment_id=payment_id)
        return PaymentVerification(ok=False, provider_payment_id=None, reason="bad signature")

    def verify_webhook(self, *, body: bytes, signature: str) -> bool:
        expected = hmac.new(SECRET, body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
