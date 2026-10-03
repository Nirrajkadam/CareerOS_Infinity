import uuid
import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime, Integer, Boolean, Float, Text, UniqueConstraint
from app.models.types import JSONType
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class JobSkillRequirement(Base):
    """
    Normalized skill requirements extracted from a job posting.
    Separate from user skills — never modifies the canonical user profile.
    """
    __tablename__ = "job_skill_requirements"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("job_postings.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    skill_name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_skill: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    skill_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # REQUIRED / PREFERRED / NICE_TO_HAVE
    proficiency_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )


class JobMatch(Base):
    """
    Computed match between a user's canonical career profile and a specific job posting.
    All scores are stored for explainability and traceability.
    Missing skills here NEVER propagate to user_skills.
    """
    __tablename__ = "job_matches"
    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_job_match"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Component scores (0.0 – 100.0)
    ats_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    semantic_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    skill_match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    experience_match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    role_match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    project_relevance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    location_match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    career_preference_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Composite
    overall_fit_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    recommendation_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    # APPLY_RECOMMENDED / STRONG_MATCH / POSSIBLE_MATCH / LOW_PRIORITY / NOT_RECOMMENDED

    # Evidence
    matched_skills: Mapped[Optional[list]] = mapped_column(JSONType, nullable=True)
    missing_required_skills: Mapped[Optional[list]] = mapped_column(JSONType, nullable=True)
    missing_preferred_skills: Mapped[Optional[list]] = mapped_column(JSONType, nullable=True)
    match_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Scoring metadata for traceability
    score_weights: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    embedding_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Freshness
    calculated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    is_stale: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class JobInteraction(Base):
    """
    User interaction state for a job posting.
    Unique per (user_id, job_id) — one row tracks the current interaction status.
    Part 2 statuses: DISCOVERED / VIEWED / SAVED / DISMISSED / SHORTLISTED
    Part 3+ statuses: APPLICATION_STARTED / APPLIED / REJECTED / WITHDRAWN
    """
    __tablename__ = "job_interactions"
    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_job_interaction"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # DISCOVERED / VIEWED / SAVED / DISMISSED / SHORTLISTED / APPLIED
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    interacted_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False
    )


class JobIngestionLog(Base):
    """
    Audit trail for each job ingestion event.
    """
    __tablename__ = "job_ingestion_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    ingested_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    ingested_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False, index=True
    )
    jobs_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    jobs_normalized: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    jobs_rejected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duplicates_detected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    errors: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
