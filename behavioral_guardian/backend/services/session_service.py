"""Session query service."""

from sqlalchemy.orm import Session

from behavioral_guardian.backend.schemas.models import SessionResponse
from behavioral_guardian.database import repositories as repo


class SessionService:
    """Read session state."""

    def get_session(self, db: Session, user_id: int) -> SessionResponse:
        """Return current session information."""
        session = repo.get_active_session(db, user_id)
        if session is None:
            return SessionResponse(
                user_id=user_id,
                session_id=None,
                is_active=False,
                started_at=None,
                last_seen_at=None,
                device_id=None,
            )
        return SessionResponse(
            user_id=user_id,
            session_id=session.id,
            is_active=session.is_active,
            started_at=session.started_at,
            last_seen_at=session.last_seen_at,
            device_id=session.device_id,
        )
