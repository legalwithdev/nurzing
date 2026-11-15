"""Browsing professionals. Tier order is the standing rule: highest authority first."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..models import Professional
from ..schemas import ProfessionalList, ProfessionalOut
from ..tier import tier_for

router = APIRouter(prefix="/api/professionals", tags=["professionals"])


def to_out(p: Professional) -> ProfessionalOut:
    t = tier_for(
        qualification=p.qualification,
        reg_type=p.reg_type,
        years=p.years,
        designation=p.designation,
        gold_min_years=settings.gold_min_years,
    )
    return ProfessionalOut(
        id=p.id, slug=p.slug, name=p.name, designation=p.designation,
        qualification=p.qualification, reg_type=p.reg_type, reg_verified=p.reg_verified,
        years=p.years, city=p.city, area=p.area, rate_paise=p.rate_paise,
        rating=p.rating, reviews_count=p.reviews_count, available_today=p.available_today,
        distance_km=p.distance_km, care_types=p.care_types or [], languages=p.languages or [],
        about=p.about, tier=t.tier, gold=t.gold, tier_label=t.label,
    )


@router.get("", response_model=ProfessionalList)
def list_professionals(
    db: Session = Depends(get_db),
    city: str | None = None,
    care: str | None = None,
    q: str | None = None,
    sort: str = Query("recommended", pattern="^(recommended|rating|price|distance)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> ProfessionalList:
    rows = list(db.scalars(select(Professional).where(Professional.active.is_(True))))

    if city:
        rows = [p for p in rows if p.city.lower() == city.lower()]
    if care:
        rows = [p for p in rows if care.lower() in [c.lower() for c in (p.care_types or [])]]
    if q:
        needle = q.lower()
        rows = [p for p in rows if needle in (p.name + " " + p.area + " " + p.city + " " + p.designation).lower()]

    # tier is ALWAYS the primary key — a licensed nurse ranks above support staff
    # even when the user sorts by price or distance.
    def tier_of(p: Professional) -> int:
        return tier_for(qualification=p.qualification, reg_type=p.reg_type, years=p.years,
                        designation=p.designation, gold_min_years=settings.gold_min_years).tier

    if sort == "price":
        rows.sort(key=lambda p: (tier_of(p), p.rate_paise))
    elif sort == "distance":
        rows.sort(key=lambda p: (tier_of(p), p.distance_km))
    else:
        rows.sort(key=lambda p: (tier_of(p), -p.rating, -p.years))

    total = len(rows)
    page = rows[offset: offset + limit]
    return ProfessionalList(total=total, items=[to_out(p) for p in page])


@router.get("/{professional_id}", response_model=ProfessionalOut)
def get_professional(professional_id: int, db: Session = Depends(get_db)) -> ProfessionalOut:
    p = db.get(Professional, professional_id)
    if p is None or not p.active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Professional not found")
    return to_out(p)
