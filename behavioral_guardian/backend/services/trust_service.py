"""Trust query service."""

from sqlalchemy.orm import Session

from behavioral_guardian.backend.schemas.models import TrustResponse
from behavioral_guardian.database import repositories as repo
from behavioral_guardian.engines.trust_engine.status import resolve_status_level


class TrustService:
    """Read trust state for a user."""

    def get_trust(self, db: Session, user_id: int) -> TrustResponse:
        """Return latest trust score or default."""
        event = repo.get_latest_trust(db, user_id)
        if event is None:
            return TrustResponse(user_id=user_id, identity_trust=100.0, status_level=resolve_status_level(100.0))
        return TrustResponse(user_id=user_id, identity_trust=event.identity_trust, status_level=event.status_level)
