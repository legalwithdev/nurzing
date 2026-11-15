"""Outbox worker.

Run it on a schedule (cron / a worker dyno / a Cloud Run job):
    python -m app.worker            # one pass
    python -m app.worker --loop 30  # every 30 seconds
"""
from __future__ import annotations

import argparse
import time

from . import jobs, scheduler
from .db import SessionLocal, init_db
from .notifications import drain
from . import tasks  # noqa: F401  (registers jobs)


def run_once(limit: int = 100) -> dict:
    init_db()
    with SessionLocal() as db:
        released = scheduler.release_due(db, limit=limit)
        drained = drain(db, limit=limit)
        ran = jobs.drain(db, limit=20)
        return {"released": released, "drained": drained, "jobs": ran}


def main() -> None:
    ap = argparse.ArgumentParser(description="NURZING outbox worker")
    ap.add_argument("--loop", type=int, default=0, help="seconds between passes (0 = run once)")
    ap.add_argument("--limit", type=int, default=100)
    args = ap.parse_args()

    if args.loop <= 0:
        print(run_once(args.limit))
        return
    while True:
        try:
            print(run_once(args.limit), flush=True)
        except Exception as exc:                      # keep the worker alive
            print("worker error:", exc, flush=True)
        time.sleep(args.loop)


if __name__ == "__main__":
    main()
