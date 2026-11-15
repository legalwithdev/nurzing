"""Simple sliding-window rate limiting.

In-memory by default (fine for one instance). Swap `_STORE` for Redis when you
run more than one process.
"""
from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

from .config import settings

_STORE: dict[str, deque[float]] = defaultdict(deque)
_LOCK = threading.Lock()


def _hit(key: str, limit: int, window: float = 60.0) -> tuple[bool, int]:
    now = time.monotonic()
    with _LOCK:
        q = _STORE[key]
        while q and now - q[0] > window:
            q.popleft()
        if len(q) >= limit:
            retry = int(window - (now - q[0])) + 1
            return False, retry
        q.append(now)
        return True, 0


def reset() -> None:
    """Test helper."""
    with _LOCK:
        _STORE.clear()


def _client(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def limiter(request: Request) -> None:
    ok, retry = _hit(f"all:{_client(request)}", settings.rate_limit_per_minute)
    if not ok:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many requests",
                            headers={"Retry-After": str(retry)})


async def auth_limiter(request: Request) -> None:
    ok, retry = _hit(f"auth:{_client(request)}", settings.rate_limit_auth_per_minute)
    if not ok:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many attempts",
                            headers={"Retry-After": str(retry)})
