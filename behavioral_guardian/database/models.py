"""SQLAlchemy ORM models for AI Behavioral Guardian."""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from behavioral_guardian.config.settings import DATABASE_URL


def utc_now() -> datetime:
    """Return current UTC timestamp."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Base declarative class."""


class User(Base):
    """Registered user."""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    organization: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    role: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    device_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    is_org_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    devices: Mapped[List["Device"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    feature_vectors: Mapped[List["FeatureVector"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    trust_events: Mapped[List["TrustEvent"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    risk_events: Mapped[List["RiskEvent"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    response_events: Mapped[List["ResponseEvent"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sessions: Mapped[List["Session"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    alerts: Mapped[List["Alert"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    reauth_events: Mapped[List["ReauthEvent"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    settings: Mapped[Optional["UserSettings"]] = relationship(back_populates="user", cascade="all, delete-orphan", uselist=False)


class Device(Base):
    """Device linked to a user."""

    __tablename__ = "device"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    device_name: Mapped[str] = mapped_column(String(256), nullable=False)
    os_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user: Mapped["User"] = relationship(back_populates="devices")


class FeatureVector(Base):
    """Behavioral feature snapshot."""

    __tablename__ = "feature_vector"
    __table_args__ = (Index("ix_feature_vector_user_created", "user_id", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    device_id: Mapped[Optional[int]] = mapped_column(ForeignKey("device.id"), nullable=True, index=True)
    ks_dwell_mean: Mapped[float] = mapped_column(Float, nullable=False)
    ks_dwell_std: Mapped[float] = mapped_column(Float, nullable=False)
    ks_flight_mean: Mapped[float] = mapped_column(Float, nullable=False)
    ks_flight_std: Mapped[float] = mapped_column(Float, nullable=False)
    ks_wpm: Mapped[float] = mapped_column(Float, nullable=False)
    ks_error_rate: Mapped[float] = mapped_column(Float, nullable=False)
    ms_speed_mean: Mapped[float] = mapped_column(Float, nullable=False)
    ms_speed_std: Mapped[float] = mapped_column(Float, nullable=False)
    ms_click_rate: Mapped[float] = mapped_column(Float, nullable=False)
    ms_idle_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    ap_unique_count: Mapped[float] = mapped_column(Float, nullable=False)
    ap_unknown_flag: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user: Mapped["User"] = relationship(back_populates="feature_vectors")


class TrustEvent(Base):
    """Identity trust score history."""

    __tablename__ = "trust_event"
    __table_args__ = (Index("ix_trust_event_user_created", "user_id", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    identity_trust: Mapped[float] = mapped_column(Float, nullable=False)
    status_level: Mapped[str] = mapped_column(String(32), nullable=False)
    anomaly_score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user: Mapped["User"] = relationship(back_populates="trust_events")
    explanations: Mapped[List["Explanation"]] = relationship(back_populates="trust_event", cascade="all, delete-orphan")


class RiskEvent(Base):
    """Activity risk score history."""

    __tablename__ = "risk_event"
    __table_args__ = (Index("ix_risk_event_user_created", "user_id", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    activity_risk: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user: Mapped["User"] = relationship(back_populates="risk_events")
    triggered_rules: Mapped[List["TriggeredRule"]] = relationship(back_populates="risk_event", cascade="all, delete-orphan")
    explanations: Mapped[List["Explanation"]] = relationship(back_populates="risk_event", cascade="all, delete-orphan")


class TriggeredRule(Base):
    """Rule fired during risk evaluation."""

    __tablename__ = "triggered_rule"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    risk_event_id: Mapped[int] = mapped_column(ForeignKey("risk_event.id"), nullable=False, index=True)
    rule_name: Mapped[str] = mapped_column(String(128), nullable=False)
    weight: Mapped[int] = mapped_column(Integer, nullable=False)
    detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    risk_event: Mapped["RiskEvent"] = relationship(back_populates="triggered_rules")


class ResponseEvent(Base):
    """Action taken by the response engine."""

    __tablename__ = "response_event"
    __table_args__ = (Index("ix_response_event_user_created", "user_id", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user: Mapped["User"] = relationship(back_populates="response_events")


class Alert(Base):
    """User or owner alert."""

    __tablename__ = "alert"
    __table_args__ = (Index("ix_alert_user_created", "user_id", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user: Mapped["User"] = relationship(back_populates="alerts")


class Session(Base):
    """Active or historical user session."""

    __tablename__ = "session"
    __table_args__ = (Index("ix_session_user_active", "user_id", "is_active"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    device_id: Mapped[Optional[int]] = mapped_column(ForeignKey("device.id"), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user: Mapped["User"] = relationship(back_populates="sessions")


class Explanation(Base):
    """Human-readable decision explanation."""

    __tablename__ = "explanation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trust_event_id: Mapped[Optional[int]] = mapped_column(ForeignKey("trust_event.id"), nullable=True, index=True)
    risk_event_id: Mapped[Optional[int]] = mapped_column(ForeignKey("risk_event.id"), nullable=True, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    trust_event: Mapped[Optional["TrustEvent"]] = relationship(back_populates="explanations")
    risk_event: Mapped[Optional["RiskEvent"]] = relationship(back_populates="explanations")


class ReauthEvent(Base):
    """Reauthentication attempt."""

    __tablename__ = "reauth_event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user: Mapped["User"] = relationship(back_populates="reauth_events")


class ModelMetadata(Base):
    """ML model training metadata."""

    __tablename__ = "model_metadata"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    training_samples: Mapped[int] = mapped_column(Integer, nullable=False)
    training_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    training_completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class UserSettings(Base):
    """Per-user security policy & threshold configuration."""

    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True, nullable=False, index=True)
    continuous_monitoring: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_lock_critical: Mapped[bool] = mapped_column(Boolean, default=True)
    reauth_medium_risk: Mapped[bool] = mapped_column(Boolean, default=True)
    block_usb_high_risk: Mapped[bool] = mapped_column(Boolean, default=False)
    high_risk_threshold: Mapped[int] = mapped_column(Integer, default=70)
    medium_risk_threshold: Mapped[int] = mapped_column(Integer, default=40)
    low_risk_threshold: Mapped[int] = mapped_column(Integer, default=20)
    trust_safe_threshold: Mapped[int] = mapped_column(Integer, default=80)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    user: Mapped["User"] = relationship(back_populates="settings")


engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
