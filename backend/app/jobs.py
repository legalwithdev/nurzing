"""Durable background jobs.

The database is the queue, so this works with no extra infrastructure. If
`NURZING_REDIS_URL` is set, `publish` also pushes the job id onto Redis so
external workers (or Celery beat) can pick it up immediately.
"""
from __future__ import annotations

import datetime as dt
from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .models import Job, JobStatus

REGISTRY: dict[str, Callable[..., dict]] = {}


def job(name: str):
    """Register a handler."""
    def deco(fn: Callable[..., dict]):
        REGISTRY[name] = fn
        return fn
    return deco


def _redis():
    if not settings.redis_url:
        return None
    try:
        import redis  # optional dependency
    except ImportError:
        return None
    try:
        return redis.from_url(settings.redis_url, decode_responses=True)
    except Exception:
        return None


def publish(db: Session, name: str, payload: dict | None = None,
            run_at: dt.datetime | None = None) -> Job:
    if name not in REGISTRY:
        raise ValueError(f"unknown job: {name}")
    j = Job(name=name, payload=payload or {}, run_at=run_at or dt.datetime.now(dt.timezone.utc))
    db.add(j)
    db.commit()
    db.refresh(j)
    r = _redis()
    if r is not None:
        try:
            r.rpush("nurzing:jobs", str(j.id))
        except Exception:
            pass          # the DB copy is authoritative
    return j


def claim(db: Session, now: dt.datetime | None = None) -> Job | None:
    """Take one due job. The row lock keeps two workers from taking the same job."""
    now = now or dt.datetime.now(dt.timezone.utc)
    j = db.scalars(
        select(Job).where(Job.status == JobStatus.queued, Job.run_at <= now)
        .order_by(Job.run_at).with_for_update(skip_locked=True).limit(1)
    ).first()
    if j is None:
        return None
    j.status = JobStatus.running
    j.attempts += 1
    db.commit()
    db.refresh(j)
    return j


def run_one(db: Session, job_row: Job) -> dict:
    handler = REGISTRY.get(job_row.name)
    if handler is None:
        job_row.status = JobStatus.failed
        job_row.last_error = "no handler registered"
        db.commit()
        return {"ok": False, "error": "no handler"}
    try:
        result = handler(db, **(job_row.payload or {}))
        job_row.status = JobStatus.done
        job_row.finished_at = dt.datetime.now(dt.timezone.utc)
        job_row.last_error = None
        db.commit()
        return {"ok": True, "result": result}
    except Exception as exc:
        job_row.last_error = str(exc)[:500]
        job_row.status = (JobStatus.failed if job_row.attempts >= job_row.max_attempts
                          else JobStatus.queued)
        db.commit()
        return {"ok": False, "error": str(exc)[:200]}


def drain(db: Session, limit: int = 20) -> dict:
    done = failed = 0
    for _ in range(limit):
        j = claim(db)
        if j is None:
            break
        out = run_one(db, j)
        done += 1 if out["ok"] else 0
        failed += 0 if out["ok"] else 1
    return {"done": done, "failed": failed}
