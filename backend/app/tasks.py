"""Registered background jobs. Import this module to populate the registry."""
from __future__ import annotations

from sqlalchemy.orm import Session

from . import analytics, jobs, notifications, scheduler


@jobs.job("analytics.recompute")
def recompute_analytics(db: Session, days: int = 30) -> dict:
    rows = analytics.recompute(db, days=int(days))
    return {"days": len(rows)}


@jobs.job("notifications.release")
def release_scheduled(db: Session) -> dict:
    return scheduler.release_due(db)


@jobs.job("outbox.drain")
def drain_outbox(db: Session, limit: int = 100) -> dict:
    return notifications.drain(db, limit=int(limit))
