"""
Async SQLAlchemy engine and session factory for Neon PostgreSQL.
Uses asyncpg driver with connection pooling optimised for serverless.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.config import settings


# NullPool is recommended for serverless / short-lived processes (Render free).
# For a persistent server, use QueuePool with small pool_size.
engine = create_async_engine(
    settings.async_database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    # Keep connections small on free tier (512MB RAM)
    pool_size=3,
    max_overflow=5,
    pool_recycle=300,  # recycle connections every 5 min
    connect_args={
        "server_settings": {
            "application_name": "nexusflow-api",
        }
    },
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for use outside FastAPI dependency injection (e.g. Inngest)."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
