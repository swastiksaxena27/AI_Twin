"""FastAPI dependencies."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from behavioral_guardian.backend.services.analyze_service import AnalyzeService
from behavioral_guardian.backend.services.alert_service import AlertService
from behavioral_guardian.backend.services.analytics_service import AnalyticsService
from behavioral_guardian.backend.services.auth_service import AuthService
from behavioral_guardian.backend.services.history_service import HistoryService
from behavioral_guardian.backend.services.reauth_service import ReauthService
from behavioral_guardian.backend.services.risk_service import RiskService
from behavioral_guardian.backend.services.session_service import SessionService
from behavioral_guardian.backend.services.settings_service import SettingsService
from behavioral_guardian.backend.services.trust_service import TrustService
from behavioral_guardian.backend.services.user_service import UserService
from behavioral_guardian.database import repositories as repo
from behavioral_guardian.database.connection import get_db
from behavioral_guardian.database.models import User
from behavioral_guardian.utils.security import decode_access_token

__all__ = ["get_db", "get_current_user", "require_self_or_org_admin"]

_bearer_scheme = HTTPBearer()

_analyze_service = AnalyzeService()
_trust_service = TrustService()
_risk_service = RiskService()
_alert_service = AlertService()
_history_service = HistoryService()
_reauth_service = ReauthService()
_session_service = SessionService()
_auth_service = AuthService()
_user_service = UserService()
_settings_service = SettingsService()
_analytics_service = AnalyticsService()


def get_analyze_service() -> AnalyzeService:
    return _analyze_service


def get_trust_service() -> TrustService:
    return _trust_service


def get_risk_service() -> RiskService:
    return _risk_service


def get_alert_service() -> AlertService:
    return _alert_service


def get_history_service() -> HistoryService:
    return _history_service


def get_reauth_service() -> ReauthService:
    return _reauth_service


def get_session_service() -> SessionService:
    return _session_service


def get_auth_service() -> AuthService:
    return _auth_service


def get_user_service() -> UserService:
    return _user_service


def get_settings_service() -> SettingsService:
    return _settings_service


def get_analytics_service() -> AnalyticsService:
    return _analytics_service


# ── Auth ──────────────────────────────────────────────────────────────
# Ported over from the guardian-v2 backend: a bearer token is required on
# every route below, and resolved back to a real User row so handlers can
# check ownership instead of trusting whatever user_id shows up in the URL.

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the bearer token to a User row.

    Note: `_bearer_scheme` itself already rejects requests with no
    Authorization header at all, before this function ever runs (401 or 403
    depending on the installed FastAPI/Starlette version). This function only
    handles the case where a token IS present but is invalid, expired, or
    doesn't match a real (active) user — which it reports as 401.
    """
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = repo.get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_self_or_org_admin(user_id: int, current_user: User = Depends(get_current_user)) -> User:
    """Allow the request only if the caller IS `user_id`, or is an org admin
    in the same organization as `user_id`. Otherwise 403."""
    if current_user.id == user_id:
        return current_user
    if current_user.is_org_admin:
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized to access this user's data",
    )
