"""Reauthentication service."""

from sqlalchemy.orm import Session

from behavioral_guardian.backend.schemas.models import ReauthRequest, ReauthResponse
from behavioral_guardian.database import repositories as repo


class ReauthService:
    """Handle reauthentication requests."""

    def reauth(self, db: Session, payload: ReauthRequest) -> ReauthResponse:
        """Validate reauthentication attempt."""
        success = bool(payload.credential.strip())
        message = "Reauthentication successful" if success else "Invalid credentials"
        repo.save_reauth_event(db, payload.user_id, success, message)
        db.commit()
        return ReauthResponse(success=success, message=message)
