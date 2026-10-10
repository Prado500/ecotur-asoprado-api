import itertools
from unittest.mock import MagicMock, AsyncMock

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_storage_client
from app.core.security import create_access_token
from app.main import app
from app.db.database import Base, get_db
from app.models.user import User, UserRole


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

    # Mocking environment variables bound to the client
    mock_client.temporal_container_name = "temp-ecotur-images"
    mock_client.container_name = "ecotur-images"

    # Mocking I/O Coroutines
    mock_client.upload_image = AsyncMock(return_value="https://ecoturasopradocdn2026.blob.core.windows.net/temp-ecotur-images/fake_image.jpg")
    mock_client.delete_image = AsyncMock(return_value=None)

    # Simulating Azure's Copy & Delete promotion behavior dynamically
    async def mock_promote(url: str) -> str:
        return url.replace("temp-ecotur-images", "ecotur-images")

    mock_client.promote_to_permanent = AsyncMock(side_effect=mock_promote)

    app.dependency_overrides[get_storage_client] = lambda: mock_client

    yield

    app.dependency_overrides.pop(get_storage_client, None)


# ==========================================
# CENTRALIZED USER/TEST-DATA FACTORIES
# (Authorization refactor suite)
# ==========================================

_USER_FACTORY_COUNTER = itertools.count()


@pytest.fixture
def make_user():
    """
    Centralized factory that builds non-persisted User ORM entities.

    Generates unique cedula/email identifiers per invocation so the same
    factory can be reused across pure unit tests (no DB) and integration
    tests (persisted through the session) without collisions.

    Returns:
        Callable[..., User]: Factory producing a User with English-safe
        defaults; keyword overrides customize role, is_active, deleted_at
        or any other scalar column.
    """
    def _make_user(
        *,
        role: UserRole = UserRole.tourist,
        is_active: bool = True,
        deleted_at=None,
        **overrides,
    ) -> User:
        sequence = next(_USER_FACTORY_COUNTER)
        return User(
            cedula=overrides.pop("cedula", f"{1000000000 + sequence}"),
            email=overrides.pop("email", f"user{sequence}@test.com"),
            first_name=overrides.pop("first_name", "John"),
            last_name=overrides.pop("last_name", "Doe"),
            phone=overrides.pop("phone", None),
            password_hash=overrides.pop("password_hash", "test-hash"),
            role=role,
            data_consent=overrides.pop("data_consent", True),
            is_active=is_active,
            deleted_at=deleted_at,
            **overrides,
        )

    return _make_user


@pytest.fixture
def make_token():
    """
    Centralized factory that signs a real JWT access token for a given User.

    Returns:
        Callable[[User], str]: Factory producing a signed bearer token with
        the user's email and role as claims.
    """
    def _make_token(user: User) -> str:
        return create_access_token(data={"sub": user.email, "role": user.role.value})

    return _make_token


@pytest.fixture
def make_auth_headers(make_token):
    """
    Centralized factory that builds Authorization headers for a given User.

    Returns:
        Callable[[User], dict]: Factory producing a ready-to-use header dict
        embedding a freshly signed bearer token.
    """
    def _make_auth_headers(user: User) -> dict:
        return {"Authorization": f"Bearer {make_token(user)}"}

    return _make_auth_headers


@pytest_asyncio.fixture
async def persist_user(db_session, make_user):
    """
    Centralized factory that builds and persists a User in the test database.

    Returns:
        Callable[..., User]: Async factory producing a refreshed, persisted
        User entity; keyword overrides are forwarded to make_user.
    """
    async def _persist(**overrides) -> User:
        user = make_user(**overrides)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    return _persist