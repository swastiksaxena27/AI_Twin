"""Risk query service."""

from sqlalchemy.orm import Session

from behavioral_guardian.backend.schemas.models import RiskResponse
from behavioral_guardian.database import repositories as repo


class RiskService:
    """Read risk state for a user."""

    def get_risk(self, db: Session, user_id: int) -> RiskResponse:
        """Return latest activity risk or zero."""
        event = repo.get_latest_risk(db, user_id)
        activity_risk = event.activity_risk if event else 0.0
        return RiskResponse(user_id=user_id, activity_risk=activity_risk)
