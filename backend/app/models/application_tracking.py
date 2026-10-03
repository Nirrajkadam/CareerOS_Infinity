"""
Application Tracking models — Part 7
Entities:
- ApplicationTrackingEvent: Immutable timeline event audit trail for state transitions.
- ApplicationResponse: Recruiter message logs, classified response type, confidence, evidence.
- FollowUp: Follow-up messages, schedule dates, approval state, outcomes.
"""
import uuid
import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, ForeignKey, DateTime, Integer, Boolean, Float, Text
from app.models.types import JSONType
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class ApplicationTrackingEvent(Base):
    """
    Immutable audit record for application status transitions and lifecycle events.
    """
    __tablename__ = "application_tracking_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # STATE_TRANSITION / RESPONSE_RECEIVED / INTERVIEW_SCHEDULED / FOLLOW_UP_SENT
    from_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    to_status: Mapped[str] = mapped_column(String(50), nullable=False)

    actor: Mapped[str] = mapped_column(String(100), default="SYSTEM", nullable=False)  # SYSTEM / USER / RECRUITER / BROWSER
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, default=dict)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=False, index=True
    )


class ApplicationResponse(Base):
    """
    Recruiter response message log with classification and evidence.
    """
    __tablename__ = "application_responses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    sender_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sender_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    raw_message_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Classification: POSITIVE / NEGATIVE / INTERVIEW_INVITATION / ASSESSMENT_REQUEST / INFORMATION_REQUEST / FOLLOW_UP / REJECTION / OFFER / NEUTRAL / UNKNOWN
    classification: Mapped[str] = mapped_column(String(50), default="UNKNOWN", nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    evidence_snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    requires_manual_review: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    received_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )


class FollowUp(Base):
    """
    Candidate follow-up message tracker.
    INVARIANT: Requires explicit user review & approval before sending.
    """
    __tablename__ = "followups"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, index=True)
    application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    followup_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    channel: Mapped[str] = mapped_column(String(50), default="EMAIL", nullable=False)  # EMAIL / LINKEDIN / PORTAL
    scheduled_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)

    draft_subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    draft_body: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(String(50), default="DRAFT", nullable=False, index=True)  # DRAFT / READY_FOR_REVIEW / USER_APPROVED / SENT / CANCELLED
    approval_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    sent_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )
