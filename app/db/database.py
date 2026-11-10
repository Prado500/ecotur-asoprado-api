from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_database_settings

engine = create_async_engine(
    get_database_settings().database_url, echo=True
)  # con echo = True para verificar desde la terminal exactamente cuál sentencia sql ejecuta Python.
"""
 Handling of asynchronous requests according to concurrency levels
 defined during requirements gathering.

"""
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Master metadata directory (SQLAlchemy 2.0)."""

    pass


async def get_db():
    """Async session factory used for dependency injection."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
