"""MSG91 (India) SMS provider."""
from __future__ import annotations

import httpx

from .base import SmsResult

OTP_URL = "https://control.msg91.com/api/v5/otp"
SMS_URL = "https://api.msg91.com/api/v2/sendsms"


class Msg91Provider:
    name = "msg91"

    def __init__(self, authkey: str, sender: str = "NURZNG", template_id: str = "") -> None:
        self.authkey = authkey
        self.sender = sender
        self.template_id = template_id

    def send_otp(self, phone: str, code: str) -> SmsResult:
        try:
            res = httpx.post(
                OTP_URL,
                params={"template_id": self.template_id, "mobile": phone.lstrip("+"),
                        "authkey": self.authkey, "otp": code},
                timeout=12.0,
            )
        except httpx.HTTPError as exc:
            return SmsResult(ok=False, error=str(exc))
        if res.status_code >= 400:
            return SmsResult(ok=False, error=res.text[:200])
        return SmsResult(ok=True, provider_id=res.text[:40])

    def send_text(self, phone: str, message: str) -> SmsResult:
        payload = {
            "sender": self.sender,
            "route": "4",
            "country": "91",
            "sms": [{"message": message, "to": [phone.lstrip("+")]}],
        }
        try:
            res = httpx.post(SMS_URL, json=payload,
                             headers={"authkey": self.authkey, "Content-Type": "application/json"},
                             timeout=12.0)
        except httpx.HTTPError as exc:
            return SmsResult(ok=False, error=str(exc))
        if res.status_code >= 400:
            return SmsResult(ok=False, error=res.text[:200])
        return SmsResult(ok=True, provider_id=res.text[:40])
