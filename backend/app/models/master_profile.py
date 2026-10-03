import uuid
import datetime
from typing import Optional, List
from sqlalchemy import String, ForeignKey, DateTime, Integer, Boolean
from app.models.types import JSONType
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class MasterProfile(Base):
    """
    Canonical Master Career Profile header storing core user career records.
    """
    __tablename__ = "master_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    personal_info: Mapped[dict] = mapped_column(
        JSONType,
        default=dict,
        nullable=False
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

class Education(Base):
    """
    Relational User Education record linked to MasterProfile.
    """
    __tablename__ = "educations"

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
    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("master_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    school: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    degree: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    field_of_study: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    start_date: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    end_date: Mapped[Optional[str]] = mapped_column(
        String(50),
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

class Experience(Base):
    """
    Relational Work Experience record linked to MasterProfile.
    """
    __tablename__ = "experiences"

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
    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("master_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    company: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    start_date: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    end_date: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True
    )
    achievements: Mapped[list] = mapped_column(
        JSONType,
        default=list,
        nullable=False
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

class Project(Base):
    """
    Relational Projects portfolio record linked to MasterProfile.
    """
    __tablename__ = "projects"

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
    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("master_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True
    )
    url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True
    )
    technologies: Mapped[list] = mapped_column(
        JSONType,
        default=list,
        nullable=False
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

class Certification(Base):
    """
    Relational User Professional Certifications record linked to MasterProfile.
    """
    __tablename__ = "certifications"

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
    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("master_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    issuing_organization: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    issue_date: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    expiration_date: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    credential_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    credential_url: Mapped[Optional[str]] = mapped_column(
        String(512),
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

class UserSkill(Base):
    """
    Structured verified user skill registry.
    """
    __tablename__ = "user_skills"

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
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    normalized_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    category: Mapped[str] = mapped_column(
        String(50),
        default="general",
        nullable=False
    )
    proficiency: Mapped[str] = mapped_column(
        String(50),
        default="Intermediate",
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="USER_PROVIDED",
        nullable=False
    )

    @property
    def skill_name(self) -> str:
        return self.name or self.normalized_name
    first_verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    last_verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    evidence: Mapped[list] = mapped_column(
        JSONType,
        default=list,
        nullable=False
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

class Evidence(Base):
    """
    Canonical evidence registry record validating career profile claims.
    """
    __tablename__ = "evidence_registry"

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
    type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    source_url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True
    )
    description: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )
    properties: Mapped[dict] = mapped_column(
        JSONType,
        default=dict,
        nullable=False
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        nullable=False
    )

class CareerGoal(Base):
    """
    Structured target goals and job preferences registry.
    """
    __tablename__ = "career_goals"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    target_roles: Mapped[list] = mapped_column(
        JSONType,
        default=list,
        nullable=False
    )
    target_salary: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    target_locations: Mapped[list] = mapped_column(
        JSONType,
        default=list,
        nullable=False
    )
    preferred_companies: Mapped[list] = mapped_column(
        JSONType,
        default=list,
        nullable=False
    )
    preferred_industries: Mapped[list] = mapped_column(
        JSONType,
        default=list,
        nullable=False
    )
    work_mode: Mapped[str] = mapped_column(
        String(50),
        default="Remote",
        nullable=False
    )
    career_level: Mapped[str] = mapped_column(
        String(50),
        default="Mid",
        nullable=False
    )
    application_preferences: Mapped[dict] = mapped_column(
        JSONType,
        default=dict,
        nullable=False
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
