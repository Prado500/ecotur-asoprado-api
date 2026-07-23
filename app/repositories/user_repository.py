from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.operators import or_
from typing import Optional

from app.models.user import User

class UserRepository:
    """
    Handles data access (SQL transactions) regarding User entity.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email_or_cedula(self, email: str, cedula: str) -> Optional[User]:
        stmt = select(User).where(
            or_(
                User.cedula == cedula,
                User.email == email
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_active_user_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(
            User.email == email,
            User.deleted_at.is_(None)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_user(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user