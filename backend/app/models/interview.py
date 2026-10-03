"""
Interview models — Part 7
Entities:
- Interview: Interview stage, date, company, role, status.
- InterviewQuestion: Generated prep questions & STAR-grounded answers based strictly on canonical profile evidence.
- InterviewFeedback: Candidate feedback notes & post-interview rating.
"""
import uuid
import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, ForeignKey, DateTime, Integer, Boolean, Float, Text
from app.models.types import JSONType
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class Interview(Base):
    """
    Interview tracking entity for candidate job applications.
    """
    __tablename__ = "interviews"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    stage: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # HR / SCREENING / TECHNICAL / SYSTEM_DESIGN / BEHAVIORAL / OFFER
    status: Mapped[str] = mapped_column(String(50), default="SCHEDULED", nullable=False, index=True)  # SCHEDULED / PREPARED / COMPLETED / CANCELLED / RESCHEDULED

    company: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(255), nullable=False)
    scheduled_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)

    location_or_link: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    interviewer_names: Mapped[Optional[List[str]]] = mapped_column(JSONType, default=list)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )


class InterviewQuestion(Base):
    """
    Prepared interview question grounded in canonical candidate profile facts and evidence.
    """
    __tablename__ = "interview_questions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    interview_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True
    )

    category: Mapped[str] = mapped_column(String(50), nullable=False)  # HR / BEHAVIORAL / TECHNICAL / SYSTEM_DESIGN / RESUME / SKILL_GAP
    question_text: Mapped[str] = mapped_column(Text, nullable=False)

    # STAR technique answer format: Situation, Task, Action, Result
    prepared_answer_star: Mapped[Optional[Dict[str, str]]] = mapped_column(JSONType, nullable=True)
    grounded_evidence_ids: Mapped[Optional[List[str]]] = mapped_column(JSONType, default=list)

    is_truth_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    has_missing_skill_warning: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )


class InterviewFeedback(Base):
    """
    Post-interview candidate feedback and ratings.
    """
    __tablename__ = "interview_feedback"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    interview_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True
    )

    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 to 5 rating
    difficulty: Mapped[str] = mapped_column(String(50), default="MEDIUM", nullable=False)  # EASY / MEDIUM / HARD

    questions_asked: Mapped[Optional[List[str]]] = mapped_column(JSONType, default=list)
    feedback_notes: Mapped[str] = mapped_column(Text, nullable=False)
    perceived_outcome: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False)  # PENDING / ADVANCED / REJECTED / OFFER

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )
