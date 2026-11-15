# NURZING API (Python / FastAPI)

The real backend for NURZING: professionals, verification, bookings, OTP login and reviews.
The website stays static on Cloudflare Pages; this service is the live data layer.

**Status:** code complete and **tested** — `10/10` pytest tests pass locally.
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
auth, booking creation, the admin-only verification flow, and consent-gated reviews.

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

---

## Deploy

The backend cannot run on Cloudflare Pages (that host is static-only). Pick a Python host:

1. **Render / Railway / Fly.io** — push this repo, set the start command
   `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, and set the env vars from `.env.example`.
2. **Database** — the default is SQLite, which is fine for a single instance. For production use
   Postgres: set `NURZING_DATABASE_URL=postgresql+psycopg://...` and add `psycopg[binary]` to
   `requirements.txt`.
3. **CORS** — add your site origin to `NURZING_CORS_ORIGINS`.
4. **Point the app at it** — in `public/app/index.html`, uncomment:
   ```html
   <script>window.NZ_API_BASE = "https://your-api.example.com";</script>
   ```
   Until that is set, the app keeps working on local demo data.
5. **Migrations** — `Base.metadata.create_all` is used for now. Before real data exists, switch to
   Alembic so schema changes are versioned.

Docker is also included:

```bash
docker build -t nurzing-api backend
docker run -p 8000:8000 --env-file backend/.env nurzing-api
```

---

## Before this goes live (honest list)

- **Every seeded record is a placeholder** — names, ratings, review counts and registration
  numbers are invented. Do not serve them as real.
- **OTP delivery is not wired** — `request-otp` generates and stores a code but no SMS is sent.
  Plug in an Indian SMS provider (MSG91 / Kaleyra / Twilio) before launch.
- **No payment gateway** — bookings are recorded with a server-computed amount, but no money moves.
- **Legal review needed** — worker classification, licensing, liability and the exact permitted
  wording for registration claims.
- **Rate limiting / abuse protection** is not implemented on the public endpoints.
