"""Verification document uploads."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..deps import current_user
from ..models import Document, User
from ..schemas import DocumentOut
from ..storage import save_upload

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

KINDS = {"id_proof", "registration_certificate", "qualification_certificate", "police_check", "other"}


def _out(d: Document) -> DocumentOut:
    return DocumentOut(id=d.id, owner_type=d.owner_type, owner_id=d.owner_id, kind=d.kind, url=d.url,
                       content_type=d.content_type, size=d.size, verified=d.verified,
                       uploaded_at=d.uploaded_at)


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    kind: str = Form("other"),
    owner_type: str = Form("application"),
    owner_id: int = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> DocumentOut:
    if kind not in KINDS:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"kind must be one of {sorted(KINDS)}")
    if owner_type not in ("application", "professional"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "owner_type must be application or professional")

    stored = save_upload(file, owner=f"{owner_type}-{owner_id}")
    doc = Document(owner_type=owner_type, owner_id=owner_id, kind=kind, key=stored.key,
                   url=stored.url, content_type=stored.content_type, size=stored.size,
                   sha256=stored.sha256, verified=False)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return _out(doc)


@router.get("/{owner_type}/{owner_id}", response_model=list[DocumentOut])
def list_documents(owner_type: str, owner_id: int, db: Session = Depends(get_db),
                   user: User = Depends(current_user)) -> list[DocumentOut]:
    from sqlalchemy import select
    rows = db.scalars(select(Document).where(Document.owner_type == owner_type,
                                             Document.owner_id == owner_id)).all()
    return [_out(d) for d in rows]
