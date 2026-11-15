"""Request/response models (the public API contract)."""
from __future__ import annotations

import datetime as dt
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Health(BaseModel):
    status: str = "ok"
    version: str
    professionals: int


class TierInfo(BaseModel):
    tier: int
    gold: bool
    label: str


class ProfessionalOut(BaseModel):
    id: int
    slug: str
    name: str
    designation: str            # verbatim, exactly as listed
    qualification: str | None
    reg_type: str
    reg_verified: bool
    years: int
    city: str
    area: str
    rate_paise: int
    rating: float
    reviews_count: int
    available_today: bool
    distance_km: float
    care_types: list[str]
    languages: list[str] = []
    about: str | None = None
    tier: int
    gold: bool
    tier_label: str


class ProfessionalList(BaseModel):
    total: int
    items: list[ProfessionalOut]


class OtpRequest(BaseModel):
    phone: str = Field(min_length=8, max_length=20)

    @field_validator("phone")
    @classmethod
    def _digits(cls, v: str) -> str:
        v = v.strip().replace(" ", "").replace("-", "")
        if not v.startswith("+"):
            v = "+91" + v.lstrip("0")
        return v


class OtpRequested(BaseModel):
    ok: bool = True
    message: str = "OTP sent"
    debug_code: str | None = None      # only when NURZING_OTP_DEBUG=true


class OtpVerify(BaseModel):
    phone: str
    code: str = Field(min_length=4, max_length=8)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str


class UserOut(BaseModel):
    id: int
    phone: str
    name: str | None
    role: str


class QuoteIn(BaseModel):
    professional_id: int
    care_type: str
    shift: str
    days: int = Field(default=1, ge=1, le=365)


class QuoteOut(BaseModel):
    amount_paise: int
    currency: str = "INR"
    unit: str
    breakdown: dict


class BookingIn(BaseModel):
    professional_id: int
    care_type: str
    shift: str
    days: int = Field(default=1, ge=1, le=365)
    start_date: dt.date
    address: str = Field(min_length=6)
    patient_name: str | None = None
    phone: str
    notes: str | None = None


class BookingOut(BaseModel):
    id: int
    reference: str
    professional_id: int
    professional_name: str
    professional_designation: str
    care_type: str
    shift: str
    days: int
    start_date: dt.date
    address: str
    patient_name: str | None
    phone: str
    notes: str | None
    amount_paise: int
    status: str
    created_at: dt.datetime


class ApplicationIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str
    designation: str = Field(min_length=2, max_length=120)
    qualification: str | None = None
    reg_type: Literal["RN&RM", "RANM", "none"] = "none"
    reg_number: str | None = None
    years: int = Field(default=0, ge=0, le=60)
    city: str
    area: str
    care_types: list[str] = []
    notes: str | None = None


class ApplicationOut(BaseModel):
    id: int
    name: str
    phone: str
    designation: str
    qualification: str | None
    reg_type: str
    reg_number: str | None
    years: int
    city: str
    area: str
    care_types: list[str]
    status: str
    created_at: dt.datetime


class ReviewIn(BaseModel):
    stars: int = Field(ge=1, le=5)
    text: str = Field(min_length=4, max_length=1000)
    consent: bool


class ReviewOut(BaseModel):
    id: int
    stars: int
    text: str
    created_at: dt.datetime


class MetaOut(BaseModel):
    care_types: list[str]
    shifts: list[str]
    cities: list[str]
    gold_min_years: int


# ---------------------------------------------------------------- payments
class PaymentOrderIn(BaseModel):
    booking_id: int


class PaymentOrderOut(BaseModel):
    payment_id: int
    provider: str
    provider_order_id: str
    amount_paise: int
    currency: str
    public_key: str | None = None


class PaymentVerifyIn(BaseModel):
    payment_id: int
    provider_payment_id: str
    signature: str


class PaymentOut(BaseModel):
    id: int
    booking_id: int
    provider: str
    status: str
    amount_paise: int
    currency: str
    provider_order_id: str
    provider_payment_id: str | None
    signature_verified: bool
    created_at: dt.datetime


# ---------------------------------------------------------------- documents
class DocumentOut(BaseModel):
    id: int
    owner_type: str
    owner_id: int
    kind: str
    url: str
    content_type: str
    size: int
    verified: bool
    uploaded_at: dt.datetime


# ---------------------------------------------------------------- admin
class AdminStats(BaseModel):
    professionals: int
    active_professionals: int
    gold_professionals: int
    pending_applications: int
    bookings_total: int
    bookings_requested: int
    revenue_paid_paise: int
    outbox_pending: int


class ProfessionalUpdate(BaseModel):
    rate_paise: int | None = Field(default=None, ge=0)
    available_today: bool | None = None
    active: bool | None = None
    reg_verified: bool | None = None
    designation: str | None = Field(default=None, min_length=2, max_length=120)
    years: int | None = Field(default=None, ge=0, le=60)


class AssignIn(BaseModel):
    professional_id: int
