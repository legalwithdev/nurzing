"""End-to-end API tests."""
from __future__ import annotations

import datetime as dt


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["professionals"] == 12


def test_tier_order_is_primary(client):
    """A B.Sc + RN&RM + experienced + specialised nurse must rank first,
    even when the caller sorts by price."""
    for sort in ("recommended", "price", "distance", "rating"):
        items = client.get(f"/api/professionals?sort={sort}").json()["items"]
        tiers = [i["tier"] for i in items]
        assert tiers == sorted(tiers), f"tier not primary for sort={sort}"
        assert items[0]["tier"] == 1


def test_gold_badge_is_derived(client):
    items = client.get("/api/professionals").json()["items"]
    gold = [i for i in items if i["gold"]]
    assert gold, "expected some gold professionals"
    for i in gold:
        assert i["tier"] == 1
        assert i["qualification"].lower().startswith("b.sc")
        assert i["reg_type"] == "RN&RM"
        assert i["years"] >= 7
        assert "(" in i["designation"]


def test_designation_verbatim(client):
    items = client.get("/api/professionals").json()["items"]
    designations = {i["designation"] for i in items}
    assert "Attendant / Ward Boy" in designations
    assert "Physiotherapist" in designations
    # never invent an RN suffix for someone who is not a registered nurse
    for i in items:
        if i["reg_type"] == "none":
            assert "RN&RM" not in i["designation"]


def test_filter_by_city_and_care(client):
    items = client.get("/api/professionals?city=Chennai").json()["items"]
    assert items and all(i["city"] == "Chennai" for i in items)
    items = client.get("/api/professionals?care=ICU-trained").json()["items"]
    assert items and all("ICU-trained" in i["care_types"] for i in items)


def test_quote_is_server_side(client):
    pid = client.get("/api/professionals").json()["items"][0]["id"]
    r = client.post("/api/bookings/quote", json={"professional_id": pid, "care_type": "Home Nursing",
                                                 "shift": "12-hour day shift", "days": 3})
    assert r.status_code == 200
    body = r.json()
    assert body["amount_paise"] > 0 and body["unit"] == "day"
    # an unknown shift is rejected, not silently priced
    r = client.post("/api/bookings/quote", json={"professional_id": pid, "care_type": "Home Nursing",
                                                 "shift": "free please", "days": 3})
    assert r.status_code == 422


def test_booking_requires_auth(client, auth_headers):
    pid = client.get("/api/professionals").json()["items"][0]["id"]
    payload = {"professional_id": pid, "care_type": "Home Nursing", "shift": "12-hour day shift",
               "days": 2, "start_date": str(dt.date.today()), "address": "12 MG Road, Bengaluru",
               "phone": "+919111111111"}
    assert client.post("/api/bookings", json=payload).status_code in (401, 403)
    r = client.post("/api/bookings", json=payload, headers=auth_headers)
    assert r.status_code == 201, r.text
    b = r.json()
    assert b["reference"].startswith("NZ") and b["amount_paise"] > 0
    mine = client.get("/api/bookings", headers=auth_headers).json()
    assert any(x["id"] == b["id"] for x in mine)


def test_application_flow_needs_admin(client, admin_headers):
    payload = {"name": "Test Nurse", "phone": "+919222222222", "designation": "RN&RM Nurse (ICU)",
               "qualification": "B.Sc Nursing", "reg_type": "RN&RM", "reg_number": "KA/12345",
               "years": 8, "city": "Bengaluru", "area": "HSR", "care_types": ["Home Nursing"]}
    r = client.post("/api/applications", json=payload)
    assert r.status_code == 201
    app_id = r.json()["id"]
    # not visible in the public list until approved
    assert all(i["name"] != "Test Nurse" for i in client.get("/api/professionals").json()["items"])
    # a normal user cannot approve
    assert client.post(f"/api/applications/{app_id}/verify").status_code in (401, 403)
    r = client.post(f"/api/applications/{app_id}/verify?approve=true", headers=admin_headers)
    assert r.status_code == 200 and r.json()["status"] == "verified"
    assert any(i["name"] == "Test Nurse" for i in client.get("/api/professionals").json()["items"])


def test_review_requires_consent(client, auth_headers):
    pid = client.get("/api/professionals").json()["items"][0]["id"]
    r = client.post(f"/api/professionals/{pid}/reviews",
                    json={"stars": 5, "text": "Very kind and careful.", "consent": False},
                    headers=auth_headers)
    assert r.status_code == 422
    r = client.post(f"/api/professionals/{pid}/reviews",
                    json={"stars": 5, "text": "Very kind and careful.", "consent": True},
                    headers=auth_headers)
    assert r.status_code == 201
    # not published until an admin approves it
    assert client.get(f"/api/professionals/{pid}/reviews").json() == []


def test_meta(client):
    m = client.get("/api/meta").json()
    assert "Home Nursing" in m["care_types"] and m["gold_min_years"] == 7
