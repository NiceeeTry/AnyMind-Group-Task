from datetime import datetime
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.infrastructure.persistence.database import Base


# Use SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


def _sqlite_date_trunc(precision: str, dt: str) -> str:
    if dt is None:
        return None
    try:
        parsed = datetime.fromisoformat(dt.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return dt
    
    if precision == "hour":
        return parsed.replace(minute=0, second=0, microsecond=0).isoformat()
    return dt


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )

    @event.listens_for(engine.sync_engine, "connect")
    def register_functions(dbapi_connection, connection_record):
        dbapi_connection.create_function("date_trunc", 2, _sqlite_date_trunc)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session_factory = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_factory() as session:
        yield session


