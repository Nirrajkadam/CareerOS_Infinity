import logging
from typing import Any, AsyncGenerator, Type, TypeVar, Generic, Optional, List
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import select
from app.core.config import settings

logger = logging.getLogger("app.core.database")

# Setup async database engine with conditional kwargs for PostgreSQL or SQLite
engine_kwargs = {}
if "postgresql" in settings.DATABASE_URL:
    engine_kwargs = {
        "pool_size": 10,
        "max_overflow": 20,
        "connect_args": {
            "prepared_statement_cache_size": 0,
            "statement_cache_size": 0
        }
    }
elif "sqlite" in settings.DATABASE_URL:
    engine_kwargs = {
        "connect_args": {"check_same_thread": False}
    }

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    **engine_kwargs
)

# Async session maker binded to the engine
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# Core declarative base class
Base = declarative_base()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency yielding an asynchronous database session.
    Automatically commits or rolls back transactions on close.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            if session.is_active:
                await session.commit()
        except Exception as e:
            logger.error(f"Database session encountered error, rolling back: {e}")
            if session.is_active:
                await session.rollback()
            raise
        finally:
            await session.close()

T = TypeVar("T", bound=Base)

class BaseRepository(Generic[T]):
    """
    Clean Architecture Base Repository implementation wrapping basic database operations.
    """
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, entity_id: Any) -> Optional[T]:
        logger.info(f"Querying {self.model.__name__} by id: {entity_id}")
        import uuid
        target_id = entity_id
        if isinstance(entity_id, str):
            try:
                target_id = uuid.UUID(entity_id)
            except (ValueError, TypeError):
                pass
        query = select(self.model).filter(self.model.id == target_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        logger.info(f"Listing all {self.model.__name__} (skip={skip}, limit={limit})")
        query = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, entity: T) -> T:
        logger.info(f"Creating new {self.model.__name__} instance.")
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def delete(self, entity: T) -> None:
        logger.info(f"Deleting {self.model.__name__} entity.")
        await self.session.delete(entity)
        await self.session.flush()
