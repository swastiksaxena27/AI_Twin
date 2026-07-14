"""Database tests."""

import pytest
from sqlalchemy.orm import Session

from behavioral_guardian.database.connection import init_db, session_scope
from behavioral_guardian.database import repositories as repo


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()
    yield


def test_save_and_read_trust_event():
    with session_scope() as db:
        repo.get_or_create_user(db, 999, "test_user")
        event = repo.save_trust_event(db, 999, 88.0, "NORMAL", 0.12, "test")
        db.commit()
        assert event.id is not None
        latest = repo.get_latest_trust(db, 999)
        assert latest is not None
        assert latest.identity_trust == 88.0
