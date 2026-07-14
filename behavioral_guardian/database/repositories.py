"""Database repositories."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session, joinedload

from behavioral_guardian.database.models import (
    Alert,
    Explanation,
    FeatureVector,
    ReauthEvent,
    ResponseEvent,
    RiskEvent,
    Session as UserSession,
    TriggeredRule,
    TrustEvent,
    User,
    UserSettings,
)


def get_or_create_user(db: Session, user_id: int, username: str | None = None) -> User:
    """Fetch user by id or create if missing."""
    user = db.get(User, user_id)
    if user is None:
        user = User(id=user_id, username=username or f"user_{user_id}")
        db.add(user)
        db.flush()
    return user


def save_feature_vector(db: Session, user_id: int, features: Dict[str, float], device_id: Optional[int] = None) -> FeatureVector:
    """Persist a feature vector row."""
    row = FeatureVector(user_id=user_id, device_id=device_id, **features)
    db.add(row)
    db.flush()
    return row


def save_trust_event(
    db: Session,
    user_id: int,
    identity_trust: float,
    status_level: str,
    anomaly_score: float,
    explanation: Optional[str] = None,
) -> TrustEvent:
    """Persist trust event and optional explanation."""
    event = TrustEvent(
        user_id=user_id,
        identity_trust=identity_trust,
        status_level=status_level,
        anomaly_score=anomaly_score,
    )
    db.add(event)
    db.flush()
    if explanation:
        db.add(Explanation(trust_event_id=event.id, summary=explanation))
    return event


def save_risk_event(
    db: Session,
    user_id: int,
    activity_risk: float,
    triggered_rules: List[Dict[str, Any]],
    explanations: List[str],
) -> RiskEvent:
    """Persist risk event, triggered rules, and explanations."""
    event = RiskEvent(user_id=user_id, activity_risk=activity_risk)
    db.add(event)
    db.flush()

    for rule in triggered_rules:
        db.add(
            TriggeredRule(
                risk_event_id=event.id,
                rule_name=rule["rule_name"],
                weight=rule["weight"],
                detail=rule.get("detail"),
            )
        )

    for summary in explanations:
        db.add(Explanation(risk_event_id=event.id, summary=summary))

    return event


def save_response_event(db: Session, user_id: int, action: str, level: int, detail: Optional[str] = None) -> ResponseEvent:
    """Persist response engine action."""
    event = ResponseEvent(user_id=user_id, action=action, level=level, detail=detail)
    db.add(event)
    db.flush()
    return event


def save_alert(db: Session, user_id: int, severity: str, title: str, message: str) -> Alert:
    """Persist alert."""
    alert = Alert(user_id=user_id, severity=severity, title=title, message=message)
    db.add(alert)
    db.flush()
    return alert


def save_reauth_event(db: Session, user_id: int, success: bool, message: str) -> ReauthEvent:
    """Persist reauthentication attempt."""
    event = ReauthEvent(user_id=user_id, success=success, message=message)
    db.add(event)
    db.flush()
    return event


def get_latest_trust(db: Session, user_id: int) -> Optional[TrustEvent]:
    """Return most recent trust event."""
    return (
        db.query(TrustEvent)
        .filter(TrustEvent.user_id == user_id)
        .order_by(TrustEvent.created_at.desc())
        .first()
    )


def get_latest_risk(db: Session, user_id: int) -> Optional[RiskEvent]:
    """Return most recent risk event."""
    return (
        db.query(RiskEvent)
        .filter(RiskEvent.user_id == user_id)
        .order_by(RiskEvent.created_at.desc())
        .first()
    )


def get_alerts(db: Session, user_id: int, limit: int = 50) -> List[Alert]:
    """Return recent alerts for a user."""
    return (
        db.query(Alert)
        .filter(Alert.user_id == user_id)
        .order_by(Alert.created_at.desc())
        .limit(limit)
        .all()
    )


def get_history(db: Session, user_id: int, limit: int = 100) -> Dict[str, List[Any]]:
    """Return trust and risk history."""
    trust_rows = (
        db.query(TrustEvent)
        .filter(TrustEvent.user_id == user_id)
        .order_by(TrustEvent.created_at.desc())
        .limit(limit)
        .all()
    )
    risk_rows = (
        db.query(RiskEvent)
        .filter(RiskEvent.user_id == user_id)
        .order_by(RiskEvent.created_at.desc())
        .limit(limit)
        .all()
    )
    return {"trust": trust_rows, "risk": risk_rows}


def get_active_session(db: Session, user_id: int) -> Optional[UserSession]:
    """Return active session for user."""
    return (
        db.query(UserSession)
        .filter(UserSession.user_id == user_id, UserSession.is_active.is_(True))
        .order_by(UserSession.started_at.desc())
        .first()
    )


def touch_session(db: Session, user_id: int, device_id: Optional[int] = None) -> UserSession:
    """Create or update active session."""
    session = get_active_session(db, user_id)
    now = datetime.now(timezone.utc)
    if session is None:
        session = UserSession(user_id=user_id, device_id=device_id, is_active=True, started_at=now, last_seen_at=now)
        db.add(session)
    else:
        session.last_seen_at = now
        if device_id is not None:
            session.device_id = device_id
    db.flush()
    return session


# ── auth / users / settings ──────────────────────────────────────

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Look up a user by primary key. Used by the auth dependency to resolve JWTs."""
    return db.get(User, user_id)


def get_user_by_username_or_email(db: Session, identifier: str) -> Optional[User]:
    """Look up a user by exact username OR email match."""
    return (
        db.query(User)
        .filter((User.username == identifier) | (User.email == identifier))
        .first()
    )


def create_user(
    db: Session,
    username: str,
    password_hash: str,
    email: Optional[str] = None,
    full_name: Optional[str] = None,
    organization: Optional[str] = None,
    role: Optional[str] = None,
    is_org_admin: bool = False,
) -> User:
    """Create and persist a new registered user."""
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        full_name=full_name,
        organization=organization,
        role=role,
        is_org_admin=is_org_admin,
    )
    db.add(user)
    db.flush()
    return user


def list_users(db: Session, organization: Optional[str] = None) -> List[User]:
    """List all users, optionally filtered to one organization."""
    query = db.query(User).order_by(User.id.asc())
    if organization:
        query = query.filter(User.organization == organization)
    return query.all()


def update_user_profile(
    db: Session,
    user_id: int,
    full_name: Optional[str] = None,
    organization: Optional[str] = None,
    role: Optional[str] = None,
    device_name: Optional[str] = None,
    email: Optional[str] = None,
) -> Optional[User]:
    """Patch profile fields on an existing user. Only provided fields are changed."""
    user = db.get(User, user_id)
    if user is None:
        return None
    if full_name is not None:
        user.full_name = full_name
    if organization is not None:
        user.organization = organization
    if role is not None:
        user.role = role
    if device_name is not None:
        user.device_name = device_name
    if email is not None:
        user.email = email
    db.flush()
    return user


def get_user_settings(db: Session, user_id: int) -> Optional[UserSettings]:
    """Fetch stored settings row for a user, if any."""
    return db.query(UserSettings).filter(UserSettings.user_id == user_id).first()


def upsert_user_settings(db: Session, user_id: int, **fields) -> UserSettings:
    """Create or update the settings row for a user with the given fields."""
    row = get_user_settings(db, user_id)
    if row is None:
        row = UserSettings(user_id=user_id)
        db.add(row)
    for key, value in fields.items():
        if value is not None and hasattr(row, key):
            setattr(row, key, value)
    db.flush()
    return row


# ── analytics ─────────────────────────────────────────

def get_risk_events_since(db: Session, user_ids: List[int], since: datetime) -> List[RiskEvent]:
    """Risk events (with triggered rules eager-loaded) for a set of users since a timestamp."""
    return (
        db.query(RiskEvent)
        .options(joinedload(RiskEvent.triggered_rules))
        .filter(RiskEvent.user_id.in_(user_ids), RiskEvent.created_at >= since)
        .order_by(RiskEvent.created_at.asc())
        .all()
    )


def get_trust_events_since(db: Session, user_ids: List[int], since: datetime) -> List[TrustEvent]:
    """Trust events for a set of users since a timestamp."""
    return (
        db.query(TrustEvent)
        .filter(TrustEvent.user_id.in_(user_ids), TrustEvent.created_at >= since)
        .order_by(TrustEvent.created_at.asc())
        .all()
    )


def get_alerts_since(db: Session, user_ids: List[int], since: datetime) -> List[Alert]:
    """Alerts for a set of users since a timestamp."""
    return (
        db.query(Alert)
        .filter(Alert.user_id.in_(user_ids), Alert.created_at >= since)
        .all()
    )


def get_response_events_since(db: Session, user_ids: List[int], since: datetime) -> List[ResponseEvent]:
    """Response engine actions for a set of users since a timestamp."""
    return (
        db.query(ResponseEvent)
        .filter(ResponseEvent.user_id.in_(user_ids), ResponseEvent.created_at >= since)
        .all()
    )


def get_feature_vectors(db: Session, user_id: int, limit: int = 200) -> List[FeatureVector]:
    """Most recent feature vectors for one user, newest first."""
    return (
        db.query(FeatureVector)
        .filter(FeatureVector.user_id == user_id)
        .order_by(FeatureVector.created_at.desc())
        .limit(limit)
        .all()
    )
