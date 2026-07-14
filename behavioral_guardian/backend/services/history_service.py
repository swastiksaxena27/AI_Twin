"""History query service."""

from sqlalchemy.orm import Session

from behavioral_guardian.backend.schemas.models import HistoryPoint, HistoryResponse
from behavioral_guardian.database import repositories as repo


class HistoryService:
    """Read trust and risk history."""

    def get_history(self, db: Session, user_id: int) -> HistoryResponse:
        """Return historical scores."""
        data = repo.get_history(db, user_id)
        trust_history = [
            HistoryPoint(created_at=row.created_at, score=row.identity_trust, label=row.status_level)
            for row in data["trust"]
        ]
        risk_history = [
            HistoryPoint(created_at=row.created_at, score=row.activity_risk, label="activity_risk")
            for row in data["risk"]
        ]
        return HistoryResponse(user_id=user_id, trust_history=trust_history, risk_history=risk_history)
