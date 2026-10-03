import uuid
import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime, Integer, Boolean, Float, Text
from app.models.types import JSONType
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class ResumeTailoringJob(Base):
    """
    Tracks lifecycle and audit trail of an async/sync resume tailoring operation.
    Statuses: QUEUED / PROCESSING / VALIDATING / READY_FOR_REVIEW / APPROVED / REJECTED / FAILED
    """
    __tablename__ = "resume_tailoring_jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    master_resume_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tailored_resume_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True, index=True
    )

    status: Mapped[str] = mapped_column(
        String(50), default="QUEUED", nullable=False, index=True
    )
    # QUEUED / PROCESSING / VALIDATING / READY_FOR_REVIEW / APPROVED / REJECTED / FAILED

    tailoring_plan: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    ats_score_before: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ats_score_after: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    score_delta: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    matched_skills: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    missing_required_skills: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    missing_preferred_skills: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)

    truth_guard_summary: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    diff_summary: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    started_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class ResumeChange(Base):
    """
    Granular section/bullet-level change audit record for a tailored resume.
    """
    __tablename__ = "resume_changes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("resume_tailoring_jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    section_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # Summary / Skills / Experience / Projects / Education / Certifications

    change_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # ADDED / REMOVED / MODIFIED / REORDERED / UNCHANGED

    original_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tailored_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    truth_guard_status: Mapped[str] = mapped_column(String(50), default="VERIFIED", nullable=False)
    # VERIFIED / REJECTED / PENDING

    evidence_ids: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
