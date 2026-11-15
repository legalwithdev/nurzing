"""Supply side: a professional listing themselves, and admin verification."""
from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import require_admin
from ..models import ApplicationStatus, Professional, ProfessionalApplication, User
from ..schemas import ApplicationIn, ApplicationOut

router = APIRouter(prefix="/api/applications", tags=["applications"])


def _out(a: ProfessionalApplication) -> ApplicationOut:
    return ApplicationOut(
        id=a.id, name=a.name, phone=a.phone, designation=a.designation,
        qualification=a.qualification, reg_type=a.reg_type, reg_number=a.reg_number,
        years=a.years, city=a.city, area=a.area, care_types=a.care_types or [],
        status=a.status.value, created_at=a.created_at,
    )


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def apply(body: ApplicationIn, db: Session = Depends(get_db)) -> ApplicationOut:
    """Public endpoint — any professional can list themselves."""
    a = ProfessionalApplication(**body.model_dump())
    db.add(a)
    db.commit()
    db.refresh(a)
    return _out(a)


@router.get("", response_model=list[ApplicationOut])
def list_applications(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
    status_filter: str | None = None,
) -> list[ApplicationOut]:
    stmt = select(ProfessionalApplication).order_by(ProfessionalApplication.created_at.desc())
    rows = list(db.scalars(stmt))
    if status_filter:
        rows = [r for r in rows if r.status.value == status_filter]
    return [_out(r) for r in rows]


@router.post("/{app_id}/verify", response_model=ApplicationOut)
def verify_application(
    app_id: int,
    approve: bool = True,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> ApplicationOut:
    """Approve an application -> it becomes a live professional record.

    Only an admin can do this, and only then may `reg_verified` become true.
    """
    a = db.get(ProfessionalApplication, app_id)
    if a is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found")
    if a.status != ApplicationStatus.pending:
        raise HTTPException(status.HTTP_409_CONFLICT, "Application already reviewed")

    a.status = ApplicationStatus.verified if approve else ApplicationStatus.rejected
    a.reviewed_by = admin.phone
    a.reviewed_at = dt.datetime.now(dt.timezone.utc)

    if approve:
        slug = f"{a.name.lower().replace(' ', '-')[:24]}-{a.id}"
        db.add(Professional(
            slug=slug, name=a.name, designation=a.designation, qualification=a.qualification,
            reg_type=a.reg_type, reg_number=a.reg_number,
            reg_verified=bool(a.reg_number),      # verified only when a number was supplied
            years=a.years, city=a.city, area=a.area, rate_paise=0,
            rating=0.0, reviews_count=0, available_today=False, distance_km=0.0,
            care_types=a.care_types or [], languages=[], about=a.notes,
        ))
    db.commit()
    db.refresh(a)
    return _out(a)
