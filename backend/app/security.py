"""OTP hashing + JWT issuing/verification."""
from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import secrets

import jwt

from .config import settings


def new_otp() -> str:
    return f"{secrets.randbelow(900000) + 100000}"


def hash_otp(phone: str, code: str) -> str:
    msg = f"{phone}:{code}".encode()
    return hmac.new(settings.jwt_secret.encode(), msg, hashlib.sha256).hexdigest()


def otp_expiry() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=settings.otp_ttl_seconds)


def create_token(user_id: int, role: str) -> str:
    now = dt.datetime.now(dt.timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + dt.timedelta(minutes=settings.jwt_ttl_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
