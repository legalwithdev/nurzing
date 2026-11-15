"""NURZING API — FastAPI application entrypoint."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import func, select

from . import __version__
from .config import settings
from .db import SessionLocal, init_db
from .models import Professional
from .ratelimit import limiter
from .routers import (admin, applications, auth, bookings, meta, payments,
                      professionals, reviews, uploads)
from .schemas import Health


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="NURZING API",
    version=__version__,
    description="Professionals, bookings, verification and reviews for NURZING.",
    lifespan=lifespan,
    dependencies=[Depends(limiter)],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (auth.router, professionals.router, bookings.router, applications.router,
          reviews.router, meta.router, admin.router, payments.router, uploads.router):
    app.include_router(r)


@app.get("/api/health", response_model=Health, tags=["meta"])
def health() -> Health:
    with SessionLocal() as db:
        count = db.scalar(select(func.count()).select_from(Professional)) or 0
    return Health(status="ok", version=__version__, professionals=int(count))


@app.exception_handler(ValueError)
async def value_error_handler(_request, exc: ValueError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})
