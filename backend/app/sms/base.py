"""SMS provider contract."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SmsResult:
    ok: bool
    provider_id: str | None = None
    error: str | None = None


class SmsProvider(Protocol):
    name: str

    def send_otp(self, phone: str, code: str) -> SmsResult: ...
    def send_text(self, phone: str, message: str) -> SmsResult: ...
