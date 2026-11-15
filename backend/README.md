# NURZING API (Python / FastAPI)

The real backend for NURZING: professionals, verification, bookings, OTP login and reviews.
The website stays static on Cloudflare Pages; this service is the live data layer.

**Status:** code complete and **tested** — `18/18` pytest tests pass locally.
**Not deployed** — it needs a host (see *Deploy* below). I cannot host it from here.

---

## Run it locally

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then edit NURZING_JWT_SECRET
python -m app.seed            # loads the 12 demo professionals
uvicorn app.main:app --reload --port 8000
```

- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/api/health

## Tests

```bash
cd backend
pytest -q
```

Covers: tier ordering, the gold badge, verbatim designations, filters, server-side pricing,
auth, booking creation, the admin-only verification flow, consent-gated reviews, payment
order + signature verification, upload content sniffing, the notification outbox, admin stats
and rate limiting.

---

## What is enforced in code

These are the standing rules, implemented once so they cannot drift:

| Rule | Where |
|---|---|
| **Tier order is always the primary sort** — B.Sc + RN&RM + experience + specialisation first, then RN&RM/GNM, then other licensed professions, then non-medical support. Applies to every sort mode. | `app/tier.py`, `routers/professionals.py` |
| **The GOLD badge is derived, never stored** — it appears only when the record actually meets all four conditions. | `app/tier.py` |
| **Designation is returned verbatim** — no mapping, no added "RN". | `models.py`, `schemas.py` |
| **Registration is separate from designation** — `reg_type` / `reg_verified`; a badge is only claimed when verified. | `models.py` |
| **Prices are computed server-side** — the client can never post its own amount. | `app/pricing.py`, `routers/bookings.py` |
| **Reviews need consent and admin approval** before they are published. | `routers/reviews.py` |
| **Only an admin can verify an application** and create a live professional record. | `routers/applications.py` |
| **OTP is never returned in production** — only when `NURZING_OTP_DEBUG=true`. | `routers/auth.py` |
| **Payment signatures are verified before anything is trusted** — client-verified and webhook-verified. | `payments/`, `routers/payments.py` |
| **Uploads are validated by content, not by the client's claimed type.** | `storage.py` |
| **Nothing is sent inline** — SMS goes through an outbox so a failing provider never blocks a booking. | `notifications.py`, `worker.py` |

---

## Endpoints

| Method | Path | Notes |
|---|---|---|
| GET | `/api/health` | liveness + professional count |
| GET | `/api/meta` | care types, shifts, cities |
| GET | `/api/professionals` | `?city=&care=&q=&sort=&limit=&offset=` — tier-sorted |
| GET | `/api/professionals/{id}` | one professional |
| GET | `/api/professionals/{id}/reviews` | published reviews only |
| POST | `/api/professionals/{id}/reviews` | auth + consent required |
| POST | `/api/bookings/quote` | server-side price |
| POST | `/api/bookings` | auth required |
| GET | `/api/bookings` | my bookings (auth) |
| POST | `/api/auth/request-otp` | phone + OTP |
| POST | `/api/auth/verify-otp` | returns a JWT |
| GET | `/api/auth/me` | current user |
| POST | `/api/applications` | **public** — a professional lists themselves |
| GET | `/api/applications` | admin only |
| POST | `/api/applications/{id}/verify` | admin only — approve/reject |
| GET | `/api/admin/bookings` | admin only |
| PATCH | `/api/admin/bookings/{id}/status` | admin only |
| POST | `/api/admin/bookings/{id}/assign` | admin only |
| GET | `/api/admin/stats` | dashboard counters |
| GET/PATCH | `/api/admin/professionals` `/{id}` | admin only |
| POST | `/api/admin/outbox/drain` | deliver queued SMS now |
| POST | `/api/payments/order` | create a provider order |
| POST | `/api/payments/verify` | verify the signature, confirm the booking |
| POST | `/api/payments/webhook` | provider callback (signature-checked) |
| POST | `/api/uploads` | verification document (content-sniffed) |
| GET | `/api/uploads/{owner_type}/{owner_id}` | documents for a record |

---

---

---

## Deploy

The API needs a Python host — Cloudflare Pages is static-only and cannot run it. Set the
NURZING_* variables on that host, apply the Alembic migration, run the outbox worker on a
schedule, and set the window.NZ_API_BASE global in the app shell so the site talks to it.
