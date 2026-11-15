"""Pricing, ledger, refunds, invoices, analytics, audit, jobs, scheduler, admin UI."""
from __future__ import annotations

import datetime as dt
import hashlib
import hmac

from app.rates import CITY_TIERS, quote_detailed


def _paid_booking(client, auth_headers):
    pid = client.get("/api/professionals").json()["items"][0]["id"]
    b = client.post("/api/bookings", json={
        "professional_id": pid, "care_type": "Home Nursing", "shift": "12-hour day shift",
        "days": 3, "start_date": str(dt.date.today()), "address": "12 MG Road, Bengaluru",
        "phone": "+919111111111"}, headers=auth_headers).json()
    order = client.post("/api/payments/order", json={"booking_id": b["id"]},
                        headers=auth_headers).json()
    sig = hmac.new(b"dummy-secret", f"{order['provider_order_id']}|pay_1".encode(),
                   hashlib.sha256).hexdigest()
    client.post("/api/payments/verify", json={"payment_id": order["payment_id"],
                                              "provider_payment_id": "pay_1", "signature": sig},
                headers=auth_headers)
    return b, order


# ---------------------------------------------------------------- pricing
def test_city_multiplier_changes_the_price():
    mum = quote_detailed(care_type="Home Nursing", shift="12-hour day shift", days=7, city="Mumbai")
    pune = quote_detailed(care_type="Home Nursing", shift="12-hour day shift", days=7, city="Pune")
    assert mum.total_paise > pune.total_paise
    assert mum.breakdown["city_multiplier"] == CITY_TIERS["Mumbai"].multiplier


def test_long_stays_get_cheaper_per_day():
    week = quote_detailed(care_type="Home Nursing", shift="12-hour day shift", days=7, city="Pune")
    month = quote_detailed(care_type="Home Nursing", shift="12-hour day shift", days=30, city="Pune")
    per_day_week = week.subtotal_paise / 7
    per_day_month = month.subtotal_paise / 30
    assert per_day_month < per_day_week


def test_unknown_care_type_is_rejected():
    import pytest
    with pytest.raises(ValueError):
        quote_detailed(care_type="Free surgery", shift="12-hour day shift", days=1)


def test_urgent_and_holiday_add_surge():
    base = quote_detailed(care_type="Home Nursing", shift="12-hour day shift", days=1, city="Pune")
    urgent = quote_detailed(care_type="Home Nursing", shift="12-hour day shift", days=1,
                            city="Pune", urgent=True)
    assert urgent.total_paise > base.total_paise
    assert any(s["name"] == "same-day booking" for s in urgent.breakdown["surges"])


# ---------------------------------------------------------------- ledger
def test_ledger_is_balanced_after_a_payment(client, auth_headers, admin_headers):
    _paid_booking(client, auth_headers)
    tb = client.get("/api/admin/ledger", headers=admin_headers).json()
    assert tb["balanced"] is True
    assert tb["total_debit_paise"] == tb["total_credit_paise"]
    assert tb["accounts"]["platform_revenue"]["credit_paise"] > 0
    assert tb["professional_payable_paise"] > 0


# ---------------------------------------------------------------- refunds
def test_refund_flow_posts_to_the_ledger(client, auth_headers, admin_headers):
    b, _ = _paid_booking(client, auth_headers)
    r = client.post(f"/api/bookings/{b['id']}/refund?reason=care%20no%20longer%20needed",
                    headers=auth_headers)
    assert r.status_code == 201, r.text
    refund_id = r.json()["id"]

    # a second request on the same booking is refused
    assert client.post(f"/api/bookings/{b['id']}/refund?reason=again",
                       headers=auth_headers).status_code == 409

    # a normal user cannot approve
    assert client.post(f"/api/admin/refunds/{refund_id}/decide").status_code in (401, 403)

    r = client.post(f"/api/admin/refunds/{refund_id}/decide?approve=true", headers=admin_headers)
    assert r.status_code == 200 and r.json()["status"] == "processed"

    tb = client.get("/api/admin/ledger", headers=admin_headers).json()
    assert tb["accounts"]["refunds"]["debit_paise"] > 0
    assert tb["balanced"] is True


# ---------------------------------------------------------------- invoices
def test_invoice_pdf_is_a_real_pdf(client, auth_headers):
    b, _ = _paid_booking(client, auth_headers)
    r = client.get(f"/api/bookings/{b['id']}/invoice.pdf", headers=auth_headers)
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content.startswith(b"%PDF-1.4")
    assert r.content.rstrip().endswith(b"%%EOF")


# ---------------------------------------------------------------- analytics
def test_analytics_rollups(client, admin_headers):
    data = client.get("/api/admin/analytics?days=7", headers=admin_headers).json()
    assert len(data["series"]) == 7
    assert data["totals"]["bookings_created"] >= 1
    assert data["series"][-1]["day"] == dt.date.today().isoformat()


# ---------------------------------------------------------------- audit
def test_admin_actions_are_audited(client, admin_headers):
    p = client.get("/api/professionals").json()["items"][0]
    client.patch(f"/api/admin/professionals/{p['id']}", json={"available_today": True},
                 headers=admin_headers)
    rows = client.get("/api/admin/audit?limit=50", headers=admin_headers).json()
    assert rows, "expected audit entries"


# ---------------------------------------------------------------- jobs
def test_jobs_queue_round_trip():
    from app import jobs, tasks  # noqa: F401
    from app.db import SessionLocal, init_db
    from app.models import Job, JobStatus

    init_db()
    with SessionLocal() as db:
        j = jobs.publish(db, "analytics.recompute", {"days": 2})
        assert j.status == JobStatus.queued
        out = jobs.drain(db, limit=5)
        assert out["done"] >= 1
        db.refresh(j)
        assert j.status == JobStatus.done


def test_unknown_job_is_rejected():
    import pytest
    from app import jobs
    from app.db import SessionLocal
    with SessionLocal() as db:
        with pytest.raises(ValueError):
            jobs.publish(db, "does.not.exist")


# ---------------------------------------------------------------- scheduler
def test_scheduled_notification_releases_into_the_outbox():
    from app import scheduler
    from app.db import SessionLocal, init_db
    from app.models import OutboxMessage, ScheduledNotification

    init_db()
    with SessionLocal() as db:
        row = scheduler.schedule(db, phone="+919444444444", template="booking_reminder",
                                 run_at=dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=1),
                                 reference="NZTEST", date=str(dt.date.today()))
        db.commit()
        out = scheduler.release_due(db)
        assert out["released"] >= 1
        db.refresh(row)
        assert row.status == "released"
        assert db.query(OutboxMessage).filter(OutboxMessage.phone == "+919444444444").count() >= 1


# ---------------------------------------------------------------- admin UI
def test_admin_ui_redirects_when_signed_out(client):
    r = client.get("/admin", follow_redirects=False)
    assert r.status_code in (303, 307, 302)
    assert "/admin/login" in r.headers.get("location", "")


def test_admin_ui_renders_after_login(client):
    from app.db import SessionLocal, init_db
    from app.models import User, UserRole
    from app.security import create_token

    init_db()
    with SessionLocal() as db:
        u = db.query(User).filter(User.phone == "+919000000000").first()
        if u is None:
            u = User(phone="+919000000000", role=UserRole.admin)
            db.add(u); db.commit(); db.refresh(u)
        u.role = UserRole.admin
        db.commit()
        uid = u.id

    client.cookies.set("nz_admin", create_token(uid, "admin"))
    r = client.get("/admin")
    assert r.status_code == 200, r.text
    body = r.text
    assert "Dashboard" in body and "Professionals" in body and "Gold tier" in body

    # each page renders
    for path, needle in [("/admin/bookings", "Bookings"), ("/admin/professionals", "Designation"),
                         ("/admin/applications", "Applications"), ("/admin/ledger", "Double-entry"),
                         ("/admin/audit", "Audit log")]:
        rr = client.get(path)
        assert rr.status_code == 200, (path, rr.status_code)
        assert needle in rr.text, path
    client.cookies.clear()
