"""Shared pytest fixtures.

Critical: this sets BEHAVIORAL_GUARDIAN_DATABASE_URL to a throwaway temp file
*before* any `behavioral_guardian.*` module is imported, so the whole test
suite runs against a fresh, isolated SQLite database — never your real
demo database at behavioral_guardian/data/behavioral_guardian.db.
"""

import os
import tempfile

_tmp_dir = tempfile.mkdtemp(prefix="abg_test_db_")
os.environ["BEHAVIORAL_GUARDIAN_DATABASE_URL"] = f"sqlite:///{_tmp_dir}/test.db"

import pytest  # noqa: E402  (must come after the env var is set above)
from fastapi.testclient import TestClient  # noqa: E402

from behavioral_guardian.backend.main import app  # noqa: E402
from behavioral_guardian.database.connection import init_db  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _setup_test_database():
    """Create all tables once in the temp test database before any test runs."""
    init_db()
    yield


@pytest.fixture(scope="session")
def client():
    """A FastAPI TestClient shared across the whole test session."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def register_user(client):
    """Factory fixture: register_user(username=..., **extra) -> AuthUser dict.

    The returned dict also carries `access_token` (added on top of the plain
    AuthUser fields) so tests can build `{"Authorization": f"Bearer {token}"}`
    headers for the now-protected routes.
    """

    def _register(username: str, password: str = "Secret123!", **extra):
        payload = {"username": username, "password": password, **extra}
        res = client.post("/api/v1/auth/register", json=payload)
        assert res.status_code == 200, res.text
        body = res.json()
        assert body["success"], body
        user = body["user"]
        user["access_token"] = body["access_token"]
        return user

    return _register


def auth_headers(user: dict) -> dict:
    """Build an Authorization header dict from a register_user() result."""
    return {"Authorization": f"Bearer {user['access_token']}"}
