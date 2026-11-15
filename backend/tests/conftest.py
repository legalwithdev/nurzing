import os
import tempfile

import pytest

os.environ.setdefault("NURZING_DATABASE_URL", "sqlite:///" + tempfile.mktemp(suffix=".db"))
os.environ.setdefault("NURZING_JWT_SECRET", "test-secret")
os.environ.setdefault("NURZING_OTP_DEBUG", "true")
os.environ.setdefault("NURZING_ADMIN_PHONES", "+919000000000")

from fastapi.testclient import TestClient  # noqa: E402

from app.config import settings  # noqa: E402
from app.db import Base, engine  # noqa: E402

# keep the limiter out of the way except in the dedicated test
settings.rate_limit_per_minute = 100000
settings.rate_limit_auth_per_minute = 100000
from app.main import app  # noqa: E402
from app.seed import run as seed_run  # noqa: E402


@pytest.fixture(scope="session")
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_run()
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def auth_headers(client):
    r = client.post("/api/auth/request-otp", json={"phone": "+919111111111"})
    code = r.json()["debug_code"]
    r = client.post("/api/auth/verify-otp", json={"phone": "+919111111111", "code": code})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
def admin_headers(client):
    r = client.post("/api/auth/request-otp", json={"phone": "+919000000000"})
    code = r.json()["debug_code"]
    r = client.post("/api/auth/verify-otp", json={"phone": "+919000000000", "code": code})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
