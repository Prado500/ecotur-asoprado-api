import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_db


DATABASE_URL_TEST = "sqlite+aiosqlite:///:memory:"

# StaticPool permite que la base de datos en memoria persista durante la ejecución del test
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
    Se ejecuta ANTES de cada prueba: Crea las tablas.
    Se ejecuta DESPUÉS de cada prueba (yield): Borra las tablas.
    Garantiza que cada test arranque con una BD completamente en blanco.
    """
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session():
    """Retorna la sesión de base de datos de prueba."""
    async with TestingSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def client(db_session):
    """
    Sobrescribe la dependencia `get_db` de la API para que use la sesión SQLite.
    Levanta un cliente HTTP asíncrono (httpx) apuntando a nuestra app FastAPI.
    """
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()