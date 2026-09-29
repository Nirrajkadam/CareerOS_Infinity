import asyncio
from logging.config import fileConfig
import sys
import os

# Set sys.path so app modules load correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import settings and metadata
from app.core.config import settings
from app.core.database import Base

# Import all models to register them on metadata
from app.models.user import User
from app.models.resume import Resume
from app.models.graph import GraphNode, GraphRelationship
from app.models.audit import AuditLog
from app.models.auth import RefreshToken
from app.models.job import JobPosting
from app.models.master_profile import MasterProfile, Education, Experience, Project, Certification, UserSkill, Evidence, CareerGoal
from app.models import (
    application, application_tracking, communication, interview,
    job_discovery, job_intelligence, job_search_goal, tailoring,
)

target_metadata = Base.metadata

# Set database URL dynamically
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("%", "%%"))

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    from app.core.database import engine

    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
