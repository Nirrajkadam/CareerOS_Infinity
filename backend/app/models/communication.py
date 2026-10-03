import uuid
import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime, Integer, Boolean, Float, Text
from app.models.types import JSONType
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class ApplicationCommunication(Base):
    """
    Main entity for job-specific candidate communications (Cover Letter, Recruiter Email, etc.).
    Statuses: DRAFT / GENERATING / READY_FOR_REVIEW / EDITED / APPROVED / REJECTED / ARCHIVED / FAILED
    Types: COVER_LETTER / RECRUITER_EMAIL / APPLICATION_EMAIL / OUTREACH / FOLLOW_UP / APPLICATION_SUMMARY
    """
    __tablename__ = "application_communications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tailored_resume_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True, index=True
    )

    communication_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # COVER_LETTER / RECRUITER_EMAIL / APPLICATION_EMAIL / OUTREACH / FOLLOW_UP / APPLICATION_SUMMARY

    status: Mapped[str] = mapped_column(
        String(50), default="DRAFT", nullable=False, index=True
    )  # DRAFT / GENERATING / READY_FOR_REVIEW / EDITED / APPROVED / REJECTED / ARCHIVED / FAILED

    tone: Mapped[str] = mapped_column(
        String(50), default="Professional", nullable=False
    )  # Professional / Concise / Confident / Technical / Friendly / Formal

    current_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    word_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    character_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    truth_guard_result: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    evidence_ids: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    rejected_claims: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    generation_metadata: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False
    )
    approved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class CommunicationVersion(Base):
    """
    Version history for a communication draft.
    Editing or regenerating creates a new version.
    """
    __tablename__ = "communication_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    communication_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("application_communications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    change_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )


class CommunicationAudit(Base):
    """
    Audit log of actions performed on a communication item (GENERATED, EDITED, REGENERATED, APPROVED, REJECTED).
    """
    __tablename__ = "communication_audits"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    communication_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("application_communications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
