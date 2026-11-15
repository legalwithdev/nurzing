"""Payments, uploads, notifications, admin and rate limiting."""
from __future__ import annotations

import datetime as dt
import hashlib
import hmac

import pytest


def _booking(client, auth_headers):
    pid = client.get("/api/professionals").json()["items"][0]["id"]
    payload = {"professional_id": pid, "care_type": "Home Nursing", "shift": "12-hour day shift",
               "days": 2, "start_date": str(dt.date.today()), "address": "12 MG Road, Bengaluru",
               "phone": "+919111111111"}
    r = client.post("/api/bookings", json=payload, headers=auth_headers)
    assert r.status_code == 201, r.text
    return r.json()


def test_payment_order_and_verify(client, auth_headers):
    b = _booking(client, auth_headers)
    r = client.post("/api/payments/order", json={"booking_id": b["id"]}, headers=auth_headers)
    assert r.status_code == 201, r.text
    order = r.json()
    assert order["amount_paise"] == b["amount_paise"]
    assert order["provider"] == "dummy"

    # a wrong signature must be rejected
    r = client.post("/api/payments/verify",
                    json={"payment_id": order["payment_id"], "provider_payment_id": "pay_x",
                          "signature": "deadbeef"}, headers=auth_headers)
    assert r.status_code == 400

    # the correct one (dummy provider) is accepted and confirms the booking
    sig = hmac.new(b"dummy-secret", f"{order['provider_order_id']}|pay_x".encode(),
                   hashlib.sha256).hexdigest()
    r = client.post("/api/payments/verify",
                    json={"payment_id": order["payment_id"], "provider_payment_id": "pay_x",
                          "signature": sig}, headers=auth_headers)
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "paid" and r.json()["signature_verified"] is True

    mine = client.get("/api/bookings", headers=auth_headers).json()
    assert next(x for x in mine if x["id"] == b["id"])["status"] == "confirmed"


def test_payment_rejects_someone_elses_booking(client, auth_headers):
    b = _booking(client, auth_headers)
    r = client.post("/api/auth/request-otp", json={"phone": "+919333333333"})
    code = r.json()["debug_code"]
    other = client.post("/api/auth/verify-otp", json={"phone": "+919333333333", "code": code}).json()
    h = {"Authorization": f"Bearer {other['access_token']}"}
    r = client.post("/api/payments/order", json={"booking_id": b["id"]}, headers=h)
    assert r.status_code == 404


def test_upload_checks_content_not_just_the_claim(client, auth_headers):
    # a text file pretending to be a PNG must be refused
    files = {"file": ("evil.png", b"not really a png", "image/png")}
    data = {"kind": "id_proof", "owner_type": "application", "owner_id": "1"}
    r = client.post("/api/uploads", files=files, data=data, headers=auth_headers)
    assert r.status_code == 422

    png = b"\x89PNG\r\n\x1a\n" + b"0" * 64
    files = {"file": ("ok.png", png, "image/png")}
    r = client.post("/api/uploads", files=files, data=data, headers=auth_headers)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["content_type"] == "image/png" and body["verified"] is False


def test_outbox_queues_and_drains(client, auth_headers, admin_headers):
    _booking(client, auth_headers)
    stats = client.get("/api/admin/stats", headers=admin_headers).json()
    assert stats["outbox_pending"] >= 1
    r = client.post("/api/admin/outbox/drain", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["sent"] >= 1


def test_admin_stats_shape(client, admin_headers):
    s = client.get("/api/admin/stats", headers=admin_headers).json()
    for key in ("professionals", "gold_professionals", "pending_applications",
                "bookings_total", "revenue_paid_paise", "outbox_pending"):
        assert key in s
    assert s["gold_professionals"] >= 1


def test_admin_can_update_a_professional(client, admin_headers):
    p = client.get("/api/professionals").json()["items"][0]
    r = client.patch(f"/api/admin/professionals/{p['id']}", json={"available_today": False},
                     headers=admin_headers)
    assert r.status_code == 200 and r.json()["available_today"] is False
    # a normal user cannot
    r = client.patch(f"/api/admin/professionals/{p['id']}", json={"available_today": True})
    assert r.status_code in (401, 403)


def test_admin_endpoints_are_locked(client, auth_headers):
    for path in ("/api/admin/stats", "/api/admin/bookings", "/api/admin/professionals"):
        assert client.get(path, headers=auth_headers).status_code == 403


def test_rate_limit_blocks_a_flood(client):
    from app.config import settings
    from app.ratelimit import reset
    reset()
    settings.rate_limit_per_minute = 5
    try:
        codes = [client.get("/api/meta").status_code for _ in range(12)]
        assert 429 in codes, "expected the limiter to kick in"
    finally:
        settings.rate_limit_per_minute = 100000
        reset()
