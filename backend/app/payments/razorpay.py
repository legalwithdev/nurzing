"""Razorpay integration (orders + signature verification + webhooks).

Uses the REST API directly over httpx so it stays testable and dependency-light.
Docs: https://razorpay.com/docs/api/orders/
"""
from __future__ import annotations

import hashlib
import hmac

import httpx

from .base import PaymentError, PaymentOrder, PaymentVerification

API = "https://api.razorpay.com/v1"


class RazorpayProvider:
    name = "razorpay"

    def __init__(self, key_id: str, key_secret: str, webhook_secret: str = "") -> None:
        if not key_id or not key_secret:
            raise PaymentError("Razorpay keys are not configured")
        self.key_id = key_id
        self.key_secret = key_secret
        self.webhook_secret = webhook_secret

    def create_order(self, *, amount_paise: int, receipt: str, notes: dict | None = None) -> PaymentOrder:
        if amount_paise <= 0:
            raise PaymentError("amount must be positive")
        try:
            res = httpx.post(
                f"{API}/orders",
                auth=(self.key_id, self.key_secret),
                json={"amount": amount_paise, "currency": "INR", "receipt": receipt,
                      "notes": notes or {}, "payment_capture": 1},
                timeout=15.0,
            )
        except httpx.HTTPError as exc:
            raise PaymentError(f"razorpay unreachable: {exc}") from exc
        if res.status_code >= 400:
            raise PaymentError(f"razorpay rejected the order: {res.text[:200]}")
        data = res.json()
        return PaymentOrder(provider_order_id=data["id"], amount_paise=int(data["amount"]),
                            currency=data.get("currency", "INR"), public_key=self.key_id, raw=data)

    def verify_payment(self, *, order_id: str, payment_id: str, signature: str) -> PaymentVerification:
        expected = hmac.new(self.key_secret.encode(), f"{order_id}|{payment_id}".encode(),
                            hashlib.sha256).hexdigest()
        if hmac.compare_digest(expected, signature):
            return PaymentVerification(ok=True, provider_payment_id=payment_id)
        return PaymentVerification(ok=False, provider_payment_id=None, reason="signature mismatch")

    def verify_webhook(self, *, body: bytes, signature: str) -> bool:
        if not self.webhook_secret:
            return False
        expected = hmac.new(self.webhook_secret.encode(), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
