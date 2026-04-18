import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_db
from app.main import app
from app.models import Base

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@postgres:5432/pcb_test"
)


API_PREFIX = ""


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Создаёт event loop для асинхронных тестов (нужно для pytest-asyncio)"""
    import asyncio

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Создаёт движок БД и таблицы один раз на все тесты"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, pool_pre_ping=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine):
    """
    Создаёт изолированную сессию для каждого теста.
    Использует транзакцию с откатом — данные не сохраняются между тестами.
    """
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )

    async with async_session() as session:

        await session.begin()
        yield session

        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """
    Асинхронный HTTP-клиент с подменой зависимости get_db.
    Все запросы в тестах будут использовать тестовую сессию БД.
    """

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow")
