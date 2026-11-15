"""Dev provider: prints instead of sending. Never use in production."""
from __future__ import annotations

from .base import SmsResult


class ConsoleProvider:
    name = "console"

    def send_otp(self, phone: str, code: str) -> SmsResult:
        print(f"[sms:console] OTP for {phone}: {code}")
        return SmsResult(ok=True, provider_id="console-otp")

    def send_text(self, phone: str, message: str) -> SmsResult:
        print(f"[sms:console] to {phone}: {message}")
        return SmsResult(ok=True, provider_id="console-text")
