from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, Index, UniqueConstraint, create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from datetime import datetime, timezone
import uuid

from backend.core.config import DATABASE_URL

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    external_id = Column(String(128), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_enrolled = Column(Boolean, default=False)
    enrollment_sample_count = Column(Integer, default=0)
    risk_tier = Column(String(16), default="standard")
    metadata_ = Column("metadata", JSON, default=dict)

    sessions = relationship("Session", back_populates="user", lazy="dynamic")
    baselines = relationship("Baseline", back_populates="user", lazy="dynamic")

    __table_args__ = (
        Index("ix_users_risk_tier", "risk_tier"),
    )


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    device_fingerprint = Column(String(256), nullable=True)
    ip_address = Column(String(45), nullable=True)
    final_trust_score = Column(Float, nullable=True)
    final_decision = Column(String(16), nullable=True)
    total_events = Column(Integer, default=0)
    total_alerts = Column(Integer, default=0)
    termination_reason = Column(String(64), nullable=True)

    user = relationship("User", back_populates="sessions")
    events = relationship("BehavioralEvent", back_populates="session", lazy="dynamic")
    trust_decisions = relationship("TrustDecision", back_populates="session", lazy="dynamic")

    __table_args__ = (
        Index("ix_sessions_user_active", "user_id", "is_active"),
        Index("ix_sessions_started_at", "started_at"),
    )


class BehavioralEvent(Base):
    __tablename__ = "behavioral_events"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    session_id = Column(String(64), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    sequence_number = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    features = Column(JSON, nullable=False)
    embedding_norm = Column(Float, nullable=True)
    similarity_score = Column(Float, nullable=True)
    cognitive_state = Column(String(24), nullable=True)
    processing_latency_ms = Column(Float, nullable=True)

    session = relationship("Session", back_populates="events")

    __table_args__ = (
        Index("ix_events_session_seq", "session_id", "sequence_number"),
        Index("ix_events_timestamp", "timestamp"),
    )


class TrustDecision(Base):
    __tablename__ = "trust_decisions"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    session_id = Column(String(64), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = Column(String(64), ForeignKey("behavioral_events.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    trust_score = Column(Float, nullable=False)
    effective_trust = Column(Float, nullable=False)
    decision = Column(String(16), nullable=False)
    trust_level = Column(String(24), nullable=False)
    similarity = Column(Float, nullable=False)
    drift_detected = Column(Boolean, default=False)
    drift_severity = Column(String(16), default="none")
    cognitive_state = Column(String(24), nullable=False)
    cognitive_stability = Column(Float, nullable=False)
    velocity = Column(Float, nullable=False)
    acceleration = Column(Float, nullable=False)
    anomaly_score = Column(Float, default=0.0)
    fraud_probability = Column(Float, default=0.0)
    fraud_trajectory = Column(String(24), nullable=True)
    transaction_amount = Column(Float, default=0.0)
    reasons = Column(JSON, default=list)
    explanation = Column(Text, nullable=True)
    latency_ms = Column(Float, nullable=False)

    session = relationship("Session", back_populates="trust_decisions")

    __table_args__ = (
        Index("ix_decisions_session_ts", "session_id", "timestamp"),
        Index("ix_decisions_decision", "decision"),
        Index("ix_decisions_trust_score", "trust_score"),
    )


class Baseline(Base):
    __tablename__ = "baselines"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    version = Column(Integer, default=1)
    sample_count = Column(Integer, default=0)
    embedding_dimension = Column(Integer, default=384)
    embedding_blob = Column(Text, nullable=False)
    stability_score = Column(Float, default=1.0)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="baselines")

    __table_args__ = (
        Index("ix_baselines_user_active", "user_id", "is_active"),
        UniqueConstraint("user_id", "version", name="uq_baselines_user_version"),
    )


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    session_id = Column(String(64), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    severity = Column(String(16), nullable=False)
    message = Column(Text, nullable=False)
    cognitive_state = Column(String(24), nullable=True)
    trust_score = Column(Float, nullable=True)
    decision = Column(String(16), nullable=True)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(128), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_alerts_severity", "severity"),
        Index("ix_alerts_session_ts", "session_id", "timestamp"),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    user_id = Column(String(64), nullable=False, index=True)
    session_id = Column(String(64), nullable=False)
    action = Column(String(32), nullable=False)
    details = Column(JSON, default=dict)
    ip_address = Column(String(45), nullable=True)

    __table_args__ = (
        Index("ix_audit_user_ts", "user_id", "timestamp"),
        Index("ix_audit_action", "action"),
    )


engine = None
SessionLocal = None

_engine_initialized = False


def _get_engine():
    global engine, SessionLocal, _engine_initialized
    if _engine_initialized:
        return engine
    _engine_initialized = True
    try:
        engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=10, pool_pre_ping=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception:
        engine = None
        SessionLocal = None
    return engine


def init_db():
    eng = _get_engine()
    if eng is None:
        raise RuntimeError("Cannot connect to database. Check DATABASE_URL configuration.")
    Base.metadata.create_all(bind=eng)


def get_db():
    _get_engine()
    if SessionLocal is None:
        raise RuntimeError("Database not available.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
