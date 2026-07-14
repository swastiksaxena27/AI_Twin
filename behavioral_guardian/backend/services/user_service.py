"""User roster + profile service."""

from typing import List, Optional

from sqlalchemy.orm import Session

from behavioral_guardian.backend.schemas.models import UserProfile, UserUpdateRequest
from behavioral_guardian.database import repositories as repo
from behavioral_guardian.engines.trust_engine.status import resolve_status_level


class UserService:
    """List and update users, enriched with their latest trust/risk snapshot."""

    def _to_profile(self, db: Session, user) -> UserProfile:
        trust_event = repo.get_latest_trust(db, user.id)
        risk_event = repo.get_latest_risk(db, user.id)
        identity_trust = trust_event.identity_trust if trust_event else 100.0
        status_level = trust_event.status_level if trust_event else resolve_status_level(identity_trust)
        activity_risk = risk_event.activity_risk if risk_event else 0.0
        return UserProfile(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            organization=user.organization,
            role=user.role,
            device_name=user.device_name,
            is_org_admin=user.is_org_admin,
            is_active=user.is_active,
            created_at=user.created_at,
            identity_trust=identity_trust,
            status_level=status_level,
            activity_risk=activity_risk,
        )

    def list_users(self, db: Session, organization: Optional[str] = None) -> List[UserProfile]:
        users = repo.list_users(db, organization=organization)
        return [self._to_profile(db, u) for u in users]

    def get_user(self, db: Session, user_id: int) -> Optional[UserProfile]:
        user = db.get(repo.User, user_id)
        if user is None:
            return None
        return self._to_profile(db, user)

    def update_user(self, db: Session, user_id: int, payload: UserUpdateRequest) -> Optional[UserProfile]:
        user = repo.update_user_profile(
            db,
            user_id,
            full_name=payload.full_name,
            organization=payload.organization,
            role=payload.role,
            device_name=payload.device_name,
            email=payload.email,
        )
        if user is None:
            return None
        db.commit()
        return self._to_profile(db, user)
