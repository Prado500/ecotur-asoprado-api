import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")



engine = create_async_engine(DATABASE_URL, echo=True) # con echo = True para verificar desde la terminal exactamente cuál sentencia sql ejecuta Python.
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
    """
     Master metadata directory (SQLAlchemy 2.0).
    """
    pass



async def get_db():
    """
    Async session factory used for dependency injection.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()