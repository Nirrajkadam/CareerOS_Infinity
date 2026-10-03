import uuid
import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime, Integer, Boolean, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.models.types import JSONType


class JobPosting(Base):
    """
    Extended JobPosting model — Part 2 Job Intelligence Engine.
    Extends the minimal Part 1 stub with full ingestion, normalization,
    deduplication, quality, and intelligence fields.
    """
    __tablename__ = "job_postings"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    # Core identity
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Source provenance
    source: Mapped[str] = mapped_column(String(100), default="manual", nullable=False, index=True)
    source_job_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    # Location & work mode
    location: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, index=True)
    work_mode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)  # REMOTE/HYBRID/ONSITE

    # Employment details
    employment_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # FULL_TIME/PART_TIME/CONTRACT/INTERNSHIP
    seniority_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Experience requirements
    experience_min_years: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    experience_max_years: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Salary
    salary_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_currency: Mapped[Optional[str]] = mapped_column(String(10), default="INR", nullable=True)

    # Lifecycle timestamps
    posted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    discovered_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    last_seen_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False, index=True)
    # ACTIVE / EXPIRED / REMOVED / DUPLICATE

    # Quality
    quality_status: Mapped[str] = mapped_column(String(50), default="MEDIUM", nullable=False, index=True)
    # HIGH / MEDIUM / LOW / EXPIRED / SUSPICIOUS
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Deduplication
    raw_content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    canonical_job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("job_postings.id", ondelete="SET NULL"), nullable=True
    )
    duplicate_group_id: Mapped[Optional[uuid.UUID]] = mapped_column(nullable=True, index=True)
    is_canonical: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Normalized fields for search/matching
    normalized_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    normalized_company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    # AI-extracted intelligence (structured JD analysis)
    jd_intelligence: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)

    # Vector embedding for semantic search
    embedding: Mapped[Optional[list]] = mapped_column(JSONType, nullable=True)

    # Audit
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False
    )
