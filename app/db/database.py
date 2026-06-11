import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")



engine = create_async_engine(DATABASE_URL, echo=True) # con Echo para verificar desde la terminal exactamente cual sql ejecuta Python.

# Uso de gestión asíncrona de peticiones de acuerdo a niveles de concurrencia delimitados en el levantamiento de requerimientos.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


Base = declarative_base()

# Esta función otorgará una sesión de base de datos a cada endpoint y la cerrará automáticamente al terminar su ejecución.
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()