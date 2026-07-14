"""Alert query service."""

from typing import List

from sqlalchemy.orm import Session

from behavioral_guardian.backend.schemas.models import AlertResponse
from behavioral_guardian.database import repositories as repo


class AlertService:
    """Read alerts for a user."""

    def get_alerts(self, db: Session, user_id: int) -> List[AlertResponse]:
        """Return recent alerts."""
        rows = repo.get_alerts(db, user_id)
        return [
            AlertResponse(
                id=row.id,
                severity=row.severity,
                title=row.title,
                message=row.message,
                is_read=row.is_read,
                created_at=row.created_at,
            )
            for row in rows
        ]
