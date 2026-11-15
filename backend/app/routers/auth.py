"""Phone + OTP login (passwordless)."""
from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..deps import current_user
from ..models import OtpCode, User, UserRole
from ..schemas import OtpRequest, OtpRequested, OtpVerify, TokenOut, UserOut
from ..security import create_token, hash_otp, new_otp, otp_expiry

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/request-otp", response_model=OtpRequested)
def request_otp(body: OtpRequest, db: Session = Depends(get_db)) -> OtpRequested:
    code = new_otp()
    db.add(OtpCode(phone=body.phone, code_hash=hash_otp(body.phone, code), expires_at=otp_expiry()))
    db.commit()
    # In production this is where the SMS provider is called. Nothing is logged
    # or returned unless NURZING_OTP_DEBUG is explicitly on (dev only).
    return OtpRequested(debug_code=code if settings.otp_debug else None)


@router.post("/verify-otp", response_model=TokenOut)
def verify_otp(body: OtpVerify, db: Session = Depends(get_db)) -> TokenOut:
    now = dt.datetime.now(dt.timezone.utc)
    row = db.scalars(
        select(OtpCode)
        .where(OtpCode.phone == body.phone, OtpCode.used.is_(False))
        .order_by(OtpCode.created_at.desc())
        .limit(1)
    ).first()
    if row is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No OTP requested for this number")
    expires = row.expires_at if row.expires_at.tzinfo else row.expires_at.replace(tzinfo=dt.timezone.utc)
    if expires < now:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "OTP expired — request a new one")
    if row.code_hash != hash_otp(body.phone, body.code):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Wrong OTP")

    row.used = True
    user = db.scalars(select(User).where(User.phone == body.phone)).first()
    if user is None:
        role = UserRole.admin if body.phone in settings.admin_list else UserRole.customer
        user = User(phone=body.phone, role=role)
        db.add(user)
    db.commit()
    db.refresh(user)
    return TokenOut(access_token=create_token(user.id, user.role.value), user_id=user.id, role=user.role.value)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)) -> UserOut:
    return UserOut(id=user.id, phone=user.phone, name=user.name, role=user.role.value)
