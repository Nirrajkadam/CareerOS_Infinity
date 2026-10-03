import uuid
import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, ForeignKey, DateTime, Integer, Boolean, Float, Text
from app.models.types import JSONType
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Application(Base):
    """
    Core Job Application entity tracking candidate application lifecycle across portals.
    Statuses:
      DISCOVERED / QUALIFIED / PACKAGE_GENERATED / READY_FOR_REVIEW / USER_APPROVED /
      AUTOMATION_RUNNING / READY_TO_SUBMIT / SUBMITTED / SUBMISSION_VERIFIED / TRACKING /
      REJECTED / SKIPPED / FAILED / BLOCKED / EXPIRED / WITHDRAWN / DUPLICATE /
      LOGIN_REQUIRED / CAPTCHA_REQUIRED / MANUAL_ACTION_REQUIRED / SUBMISSION_UNCERTAIN
    """
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_posting_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tailored_resume_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True, index=True
    )
    communication_bundle_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    status: Mapped[str] = mapped_column(
        String(50), default="DISCOVERED", nullable=False, index=True
    )
    application_stage: Mapped[str] = mapped_column(
        String(50), default="UNSUBMITTED", nullable=False, index=True
    )  # UNSUBMITTED / SUBMITTED / UNDER_REVIEW / INTERVIEW / REJECTED / OFFER

    source: Mapped[str] = mapped_column(String(100), default="MANUAL", nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    application_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    company: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    job_fit_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    ats_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    priority_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    missing_skills: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    application_payload: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    submission_metadata: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    automation_metadata: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    approval_metadata: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)

    risk_status: Mapped[str] = mapped_column(String(50), default="LOW_RISK", nullable=False)
    risk_flags: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False
    )
    submitted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class ApplicationStatusHistory(Base):
    """
    Immutable event trail for application status transitions and automated worker actions.
    """
    __tablename__ = "application_status_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    from_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    to_status: Mapped[str] = mapped_column(String(50), nullable=False)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    automation_run_id: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )


class AutomationRun(Base):
    """
    Tracks browser automation executions for preparing and navigating application forms.
    """
    __tablename__ = "automation_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    adapter_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), default="INITIALIZED", nullable=False, index=True
    )  # INITIALIZED / RUNNING / PAUSED / WAITING_FOR_APPROVAL / COMPLETED / FAILED / LOGIN_REQUIRED / CAPTCHA_REQUIRED
    current_step: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    logs_json: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    started_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    ended_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class ApplicationField(Base):
    """
    Detected application form field mappings with truth verification flags.
    """
    __tablename__ = "application_fields"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    field_type: Mapped[str] = mapped_column(String(50), default="text", nullable=False)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    detected_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mapped_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    is_verified_truth: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    requires_manual_review: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class ApprovalRequest(Base):
    """
    Tracks explicit user approval events (Package Approval & Final Submission Approval).
    """
    __tablename__ = "approval_requests"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    approval_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # PACKAGE_APPROVAL / FINAL_SUBMISSION_APPROVAL
    status: Mapped[str] = mapped_column(
        String(50), default="PENDING", nullable=False, index=True
    )  # PENDING / APPROVED / REJECTED
    approval_token: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    approved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
