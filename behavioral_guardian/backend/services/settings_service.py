"""Per-user settings (security policy + thresholds) service."""

from sqlalchemy.orm import Session

from behavioral_guardian.backend.schemas.models import SettingsResponse, SettingsUpdateRequest
from behavioral_guardian.database import repositories as repo


class SettingsService:
    """Read and update a user's security policy / threshold configuration."""

    def get_settings(self, db: Session, user_id: int) -> SettingsResponse:
        row = repo.get_user_settings(db, user_id)
        if row is None:
            row = repo.upsert_user_settings(db, user_id)  # creates with defaults
            db.commit()
        return SettingsResponse(
            user_id=user_id,
            continuous_monitoring=row.continuous_monitoring,
            auto_lock_critical=row.auto_lock_critical,
            reauth_medium_risk=row.reauth_medium_risk,
            block_usb_high_risk=row.block_usb_high_risk,
            high_risk_threshold=row.high_risk_threshold,
            medium_risk_threshold=row.medium_risk_threshold,
            low_risk_threshold=row.low_risk_threshold,
            trust_safe_threshold=row.trust_safe_threshold,
        )

    def update_settings(self, db: Session, user_id: int, payload: SettingsUpdateRequest) -> SettingsResponse:
        repo.upsert_user_settings(db, user_id, **payload.model_dump(exclude_unset=True))
        db.commit()
        return self.get_settings(db, user_id)
