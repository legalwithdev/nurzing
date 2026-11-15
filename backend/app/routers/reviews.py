"""Reviews — published only with the family's written consent."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import current_user
from ..models import Professional, Review, User
from ..schemas import ReviewIn, ReviewOut

router = APIRouter(prefix="/api/professionals/{professional_id}/reviews", tags=["reviews"])


@router.get("", response_model=list[ReviewOut])
def list_reviews(professional_id: int, db: Session = Depends(get_db)) -> list[ReviewOut]:
    if db.get(Professional, professional_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Professional not found")
    rows = db.scalars(
        select(Review).where(Review.professional_id == professional_id, Review.published.is_(True))
        .order_by(Review.created_at.desc())
    ).all()
    return [ReviewOut(id=r.id, stars=r.stars, text=r.text, created_at=r.created_at) for r in rows]


@router.post("", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def add_review(
    professional_id: int,
    body: ReviewIn,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> ReviewOut:
    if db.get(Professional, professional_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Professional not found")
    if not body.consent:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Consent is required to publish a review")
    r = Review(professional_id=professional_id, user_id=user.id, stars=body.stars,
               text=body.text, consent=True, published=False)
    db.add(r)
    db.commit()
    db.refresh(r)
    return ReviewOut(id=r.id, stars=r.stars, text=r.text, created_at=r.created_at)
