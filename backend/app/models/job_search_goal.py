"""
JobSearchGoal model — Part 7
User-defined career goals and daily submission limits.
"""
import uuid
import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, ForeignKey, DateTime, Integer, Boolean, Float, Text
from app.models.types import JSONType
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class JobSearchGoal(Base):
    """
    Candidate user-defined career goals and submission ceilings.
    INVARIANT: daily_submission_target is a LIMIT ceiling, NOT authorization for auto-submission.
    """
    __tablename__ = "job_search_goals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )

    target_role: Mapped[str] = mapped_column(String(255), default="Backend Engineer", nullable=False)
    target_salary_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    target_salary_target: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    target_location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    preferred_work_mode: Mapped[str] = mapped_column(String(50), default="REMOTE", nullable=False)  # REMOTE / HYBRID / ONSITE / ANY

    preferred_industries: Mapped[Optional[List[str]]] = mapped_column(JSONType, default=list)
    preferred_companies: Mapped[Optional[List[str]]] = mapped_column(JSONType, default=list)
    blocked_companies: Mapped[Optional[List[str]]] = mapped_column(JSONType, default=list)
    blocked_roles: Mapped[Optional[List[str]]] = mapped_column(JSONType, default=list)

    minimum_match_score: Mapped[float] = mapped_column(Float, default=60.0, nullable=False)
    daily_preparation_target: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    daily_submission_target: Mapped[int] = mapped_column(Integer, default=5, nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False
    )
