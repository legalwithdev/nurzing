"""Static metadata the frontend needs (care types, shifts, cities)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..models import Professional
from ..pricing import VALID_SHIFTS
from ..schemas import MetaOut

router = APIRouter(prefix="/api/meta", tags=["meta"])

CARE_TYPES = [
    "Home Nursing", "Live-in Nursing (24x7)", "Elderly Care & Attendants",
    "Post-Surgical Recovery", "Mother & Baby Care", "Physiotherapy at Home", "ICU-Trained Nurses",
]


@router.get("", response_model=MetaOut)
def meta(db: Session = Depends(get_db)) -> MetaOut:
    cities = sorted({p.city for p in db.scalars(select(Professional)).all()})
    return MetaOut(care_types=CARE_TYPES, shifts=VALID_SHIFTS, cities=cities,
                   gold_min_years=settings.gold_min_years)
