import uuid
import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime, Integer, Boolean
from app.models.types import JSONType
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.core.database import Base

class Resume(Base):
    """
    CareerOS Infinity parsed Resume database model.
    Supports document versioning, pgvector search embeddings, and raw text storage.
    """
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    file_url: Mapped[str] = mapped_column(
        String(512),
        nullable=False
    )
    raw_text: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    resume_json: Mapped[dict] = mapped_column(
        JSONType,
        nullable=False
    )
    embedding: Mapped[list] = mapped_column(
        Vector(1536),
        nullable=True
    )
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("resumes.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    is_master: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    resume_type: Mapped[str] = mapped_column(
        String(100),
        default="TAILORED",
        nullable=False
    )
    lifecycle_status: Mapped[str] = mapped_column(
        String(50),
        default="ACTIVE",
        nullable=False
    )
    checksum: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True
    )
    validation_status: Mapped[Optional[str]] = mapped_column(
        String(50),
        default="PENDING",
        nullable=True
    )
    target_job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("job_postings.id", ondelete="SET NULL"),
        nullable=True
    )
    target_company: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    target_role: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    ats_score_before: Mapped[Optional[float]] = mapped_column(
        nullable=True
    )
    ats_score_after: Mapped[Optional[float]] = mapped_column(
        nullable=True
    )
    matched_skills: Mapped[Optional[dict]] = mapped_column(
        JSONType,
        nullable=True
    )
    missing_skills: Mapped[Optional[dict]] = mapped_column(
        JSONType,
        nullable=True
    )
    changed_sections: Mapped[Optional[dict]] = mapped_column(
        JSONType,
        nullable=True
    )
    truth_guard_result: Mapped[Optional[dict]] = mapped_column(
        JSONType,
        nullable=True
    )
    evaluation_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONType,
        nullable=True
    )
    approval_status: Mapped[Optional[str]] = mapped_column(
        String(50),
        default="PENDING",
        nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False
    )
