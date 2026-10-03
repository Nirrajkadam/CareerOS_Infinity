"""
JobDiscovery models — Part 6
Entities:
- JobDiscoveryRun: Tracks discovery iterations, source performance, duration, and counts.
- SkillGapAggregate: Tracks aggregate market missing skill counts, importance, and learning priority.
- JobPipelineControl: Per-user daily limits, pause/resume state, and emergency stop controls.
"""
import uuid
import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, ForeignKey, DateTime, Integer, Boolean, Float, Text
from app.models.types import JSONType
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class JobDiscoveryRun(Base):
    """
    Tracks a job discovery execution run across configured job sources.
    """
    __tablename__ = "job_discovery_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    query: Mapped[str] = mapped_column(String(255), nullable=False)
    sources: Mapped[Optional[List[str]]] = mapped_column(JSONType, nullable=True)

    status: Mapped[str] = mapped_column(String(50), default="RUNNING", nullable=False, index=True)  # RUNNING / COMPLETED / PAUSED / STOPPED / FAILED
    jobs_discovered_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    jobs_qualified_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    jobs_duplicate_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    jobs_risk_blocked_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    logs_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, default=dict)
    started_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )
    ended_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)


class SkillGapAggregate(Base):
    """
    Aggregates market missing skill gap metrics across discovered jobs for a user.
    INVARIANT: Missing skills NEVER populate canonical UserSkill or master profile data.
    """
    __tablename__ = "skill_gap_aggregates"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    job_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    required_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    preferred_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    importance_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    learning_priority: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    target_roles: Mapped[Optional[List[str]]] = mapped_column(JSONType, default=list)

    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False
    )


class JobPipelineControl(Base):
    """
    Stores per-user daily processing limits, pause state, and global emergency stop control.
    """
    __tablename__ = "job_pipeline_controls"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )

    daily_processing_limit: Mapped[int] = mapped_column(Integer, default=25, nullable=False)  # 10, 25, 50
    is_paused: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_emergency_stopped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    emergency_stopped_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    emergency_stop_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    today_processed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_reset_date: Mapped[str] = mapped_column(String(10), default=lambda: datetime.date.today().isoformat(), nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False
    )
