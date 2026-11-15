"""Audit trail for anything that changes money, people or access."""
from __future__ import annotations

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import AuditLog, User

SENSITIVE_ACTIONS = {
    "professional.update", "professional.verify", "application.verify", "application.reject",
    "booking.status", "booking.assign", "refund.approve", "refund.reject", "document.verify",
    "payment.verify", "user.role",
}


def record(db: Session, *, actor: str, action: str, entity: str, entity_id: str | int | None = None,
           detail: dict | None = None, ip: str | None = None) -> AuditLog:
    row = AuditLog(actor=actor, action=action, entity=entity,
                   entity_id=str(entity_id) if entity_id is not None else None,
                   detail=detail or {}, ip=ip)
    db.add(row)
    return row


def record_for_user(db: Session, user: User, *, action: str, entity: str,
                    entity_id: str | int | None = None, detail: dict | None = None,
                    request: Request | None = None) -> AuditLog:
    ip = None
    if request is not None:
        fwd = request.headers.get("x-forwarded-for")
        ip = (fwd.split(",")[0].strip() if fwd else
              (request.client.host if request.client else None))
    return record(db, actor=user.phone, action=action, entity=entity,
                  entity_id=entity_id, detail=detail, ip=ip)


def recent(db: Session, limit: int = 100, action: str | None = None) -> list[AuditLog]:
    stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    if action:
        stmt = (select(AuditLog).where(AuditLog.action == action)
                .order_by(AuditLog.created_at.desc()).limit(limit))
    return list(db.scalars(stmt))
