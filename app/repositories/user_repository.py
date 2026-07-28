from datetime import datetime, timezone
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


    async def get_non_deleted_user_by_email(self, email: str) -> Optional[User]:
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

    async def activate_user(self, email: str) -> bool:
        """
        Mutates the user's is_active state to True. Returns False if user is not found.
        """
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalars().first()

        if not user:
            return False

        user.is_active = True
        await self.db.commit()
        return True


    async def soft_delete_user(self, cedula: str) -> Optional[User]:
        """
        Applies logical deletion by stamping the current UTC time on deleted_at
        and defensively deactivating the user to instantly revoke access.
        """
        stmt = select(User).where(
            User.cedula == cedula,
            User.deleted_at.is_(None) # Ensure we don't re-delete
        )
        result = await self.db.execute(stmt)
        user = result.scalars().first()

        if not user:
            return None

        # State Mutation
        user.deleted_at = datetime.now(timezone.utc)
        user.is_active = False

        await self.db.commit()
        return user