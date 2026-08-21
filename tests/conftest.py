from unittest.mock import MagicMock, AsyncMock

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_storage_client
from app.main import app
from app.db.database import Base, get_db


DATABASE_URL_TEST = "sqlite+aiosqlite:///:memory:"

# StaticPool allows for the in-memory database to exist until the test session is over.
engine_test = create_async_engine(
    DATABASE_URL_TEST,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = async_sessionmaker(
    bind=engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """
    This function is executed before each test (as it creates the database tables)
    and after each test (to perform database table deletion).

    It guarantees each test counts on a clean database.
    """
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session():
    """Returns test database session"""
    async with TestingSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def client(db_session):
    """
    Overwrites non-testable `get_db` API dependency over the SQLite session for testing.
    Runs an async HTTP client (httpx) aiming to this FastAPI app.
    """
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest_asyncio.fixture(autouse=True)
def override_azure_storage_client():
    """
    Overwrites the AzureStorageClient dependency globally for all tests.
    Ensures that no test attempts to instantiate the real cloud client,
    preventing missing environment variable errors and avoiding real HTTP egress.
    """
    mock_client = MagicMock()

    mock_client.upload_image = AsyncMock(return_value="https://ecoturasopradocdn2026.blob.core.windows.net/ecotur-images/fake_image.jpg")


    app.dependency_overrides[get_storage_client] = lambda: mock_client

    yield

    app.dependency_overrides.pop(get_storage_client, None)