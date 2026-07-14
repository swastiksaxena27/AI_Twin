"""Pydantic schemas — API contract models."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from behavioral_guardian.config.settings import FROZEN_FEATURE_NAMES


class FeatureVector(BaseModel):
    """Behavioral feature vector input."""

    user_id: int
    device_id: Optional[int] = None
    ks_dwell_mean: float = 0.0
    ks_dwell_std: float = 0.0
    ks_flight_mean: float = 0.0
    ks_flight_std: float = 0.0
    ks_wpm: float = 0.0
    ks_error_rate: float = 0.0
    ms_speed_mean: float = 0.0
    ms_speed_std: float = 0.0
    ms_click_rate: float = 0.0
    ms_idle_ratio: float = 0.0
    ap_unique_count: float = 0.0
    ap_unknown_flag: float = 0.0
    activity_signals: Dict[str, Any] = Field(default_factory=dict)

    def to_feature_dict(self) -> Dict[str, float]:
        """Return frozen feature names as dict."""
        return {name: getattr(self, name) for name in FROZEN_FEATURE_NAMES}


class AnalyzeResponse(BaseModel):
    """Response from POST /analyze."""

    user_id: int
    anomaly_score: float
    identity_trust: float
    status_level: str
    activity_risk: float
    triggered_rules: List[Dict[str, Any]]
    response_actions: List[str]
    explanations: List[str]


class TrustResponse(BaseModel):
    """Response from GET /trust/{user_id}."""

    user_id: int
    identity_trust: float
    status_level: str


class RiskResponse(BaseModel):
    """Response from GET /risk/{user_id}."""

    user_id: int
    activity_risk: float


class AlertResponse(BaseModel):
    """Single alert item."""

    id: int
    severity: str
    title: str
    message: str
    is_read: bool
    created_at: datetime


class HistoryPoint(BaseModel):
    """Historical score point."""

    created_at: datetime
    score: float
    label: str


class HistoryResponse(BaseModel):
    """Response from GET /history/{user_id}."""

    user_id: int
    trust_history: List[HistoryPoint]
    risk_history: List[HistoryPoint]


class ReauthRequest(BaseModel):
    """Reauthentication request payload."""

    user_id: int
    credential: str


class ReauthResponse(BaseModel):
    """Response from POST /reauth."""

    success: bool
    message: str


class SessionResponse(BaseModel):
    """Response from GET /session/{user_id}."""

    user_id: int
    session_id: Optional[int]
    is_active: bool
    started_at: Optional[datetime]
    last_seen_at: Optional[datetime]
    device_id: Optional[int]


# ── auth ──────────────────────────────────────────────

class RegisterRequest(BaseModel):
    """POST /auth/register payload."""

    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    organization: Optional[str] = None
    role: Optional[str] = None
    is_org_admin: bool = False


class LoginRequest(BaseModel):
    """POST /auth/login payload. `identifier` is a username or email."""

    identifier: str
    password: str


class AuthUser(BaseModel):
    """User info returned after successful auth."""

    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    organization: Optional[str] = None
    role: Optional[str] = None
    device_name: Optional[str] = None
    is_org_admin: bool = False


class AuthResponse(BaseModel):
    """Response from /auth/register and /auth/login."""

    success: bool
    message: str
    user: Optional[AuthUser] = None
    access_token: Optional[str] = None
    token_type: str = "bearer"


class DeviceTokenResponse(BaseModel):
    """Response from /auth/device-token — a long-lived token for the agent."""

    access_token: str
    token_type: str = "bearer"
    user_id: int


# ── users ─────────────────────────────────────────────

class UserProfile(BaseModel):
    """Roster entry — profile fields joined with the latest trust/risk snapshot."""

    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    organization: Optional[str] = None
    role: Optional[str] = None
    device_name: Optional[str] = None
    is_org_admin: bool = False
    is_active: bool = True
    created_at: datetime
    identity_trust: float
    status_level: str
    activity_risk: float


class UserUpdateRequest(BaseModel):
    """PATCH /users/{user_id} payload — every field optional."""

    full_name: Optional[str] = None
    organization: Optional[str] = None
    role: Optional[str] = None
    device_name: Optional[str] = None
    email: Optional[str] = None


# ── settings ──────────────────────────────────────────

class SettingsResponse(BaseModel):
    """GET /settings/{user_id} response."""

    user_id: int
    continuous_monitoring: bool
    auto_lock_critical: bool
    reauth_medium_risk: bool
    block_usb_high_risk: bool
    high_risk_threshold: int
    medium_risk_threshold: int
    low_risk_threshold: int
    trust_safe_threshold: int


class SettingsUpdateRequest(BaseModel):
    """PUT /settings/{user_id} payload — every field optional, only provided ones change."""

    continuous_monitoring: Optional[bool] = None
    auto_lock_critical: Optional[bool] = None
    reauth_medium_risk: Optional[bool] = None
    block_usb_high_risk: Optional[bool] = None
    high_risk_threshold: Optional[int] = None
    medium_risk_threshold: Optional[int] = None
    low_risk_threshold: Optional[int] = None
    trust_safe_threshold: Optional[int] = None


# ── analytics ─────────────────────────────────────────

class BehavioralBaseline(BaseModel):
    """One typing/mouse feature's similarity to the user's own historical baseline."""

    label: str
    pct: float


class RiskTrendPoint(BaseModel):
    """One day's average activity risk."""

    date: str
    avg_risk: float


class RiskTypeCount(BaseModel):
    """How many times a given risk rule fired in the period."""

    rule_name: str
    count: int


class AnalyticsInsights(BaseModel):
    """Peak/lowest/average trust over the analyzed period."""

    peak_trust: Optional[float] = None
    lowest_trust: Optional[float] = None
    average_trust: Optional[float] = None


class AnalyticsResponse(BaseModel):
    """GET /analytics/{user_id} response — real aggregates from risk/trust/alert/response events."""

    scope: str  # "user" or "organization"
    days: int
    total_alerts: int
    high_risk_events: int
    users_at_risk: int
    blocked_actions: int
    typing_baseline: List[BehavioralBaseline]
    mouse_baseline: List[BehavioralBaseline]
    risk_trend: List[RiskTrendPoint]
    top_risk_types: List[RiskTypeCount]
    insights: AnalyticsInsights
