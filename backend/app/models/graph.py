import uuid
import datetime
from sqlalchemy import String, ForeignKey, DateTime, JSON
from app.models.types import JSONType
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class GraphNode(Base):
    """
    Relational Graph Node representing a unified entity inside the Knowledge Graph.
    """
    __tablename__ = "graph_nodes"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        index=True
    )
    entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    properties: Mapped[dict] = mapped_column(
        JSONType,
        default=dict,
        nullable=False
    )
    embedding: Mapped[list] = mapped_column(
        JSONType,
        nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        nullable=False
    )

class GraphRelationship(Base):
    """
    Relational Graph Edge mapping connections between entity nodes.
    """
    __tablename__ = "graph_relationships"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    source_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )
    target_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )
    relation_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
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
