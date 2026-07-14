"""Database connection and session management."""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.orm import Session

from behavioral_guardian.config.settings import DATA_DIR
from behavioral_guardian.database.models import Base, SessionLocal, engine
from behavioral_guardian.utils.logging_config import ensure_directory, setup_logging

logger = setup_logging(__name__)


def init_db() -> None:
    """Create database directory and all tables."""
    ensure_directory(DATA_DIR)
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized at %s", DATA_DIR)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Context manager for database sessions with commit/rollback."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    init_db()
