from datetime import UTC, datetime

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.operators import or_

from app.models.user import User, UserRole


class UserRepository:
    """Handles data access (SQL transactions) regarding User entity."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email_or_cedula(self, email: str, cedula: str) -> User | None:
        stmt = select(User).where(or_(User.cedula == cedula, User.email == email))
        result = await self.db.execute(stmt)

        return result.scalars().first()

    async def count_active_superadmins(self) -> int:
        """Counts the superadmins that can still sign in: active and not soft-deleted.

        The bootstrap command (BE-34) creates a superadmin only when this count is zero.

        Returns:
            int: Number of rows with role superadmin, is_active true and no deleted_at.
        """
        stmt = (
            select(func.count())
            .select_from(User)
            .where(
                User.role == UserRole.superadmin,
                User.is_active.is_(True),
                User.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_non_deleted_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email, User.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_user(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def soft_delete_user(self, cedula: str) -> User | None:
        """Applies logical deletion by stamping the current UTC time on deleted_at.

        It also deactivates the user defensively, which revokes access instantly.
        """
        stmt = select(User).where(
            User.cedula == cedula,
            User.deleted_at.is_(None),  # Ensure we don't re-delete
        )
        result = await self.db.execute(stmt)
        user = result.scalars().first()

        if not user:
            return None

        # State Mutation
        user.deleted_at = datetime.now(UTC)
        user.is_active = False

        await self.db.commit()
        return user

    async def get_all_users(self, include_deleted: bool = False) -> list[User]:
        """Retrieves the complete collection of users.

        Filters out logically deleted users by default unless specified,
        ordering the results by ID descending to surface newest records first.
        """
        stmt = select(User)
        if not include_deleted:
            stmt = stmt.where(User.deleted_at.is_(None))

        stmt = stmt.order_by(User.id.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_user_by_cedula(self, cedula: str, include_deleted: bool = False) -> User | None:
        """Retrieves a single user utilizing the primary business identifier (cedula)."""
        stmt = select(User).where(User.cedula == cedula)
        if not include_deleted:
            stmt = stmt.where(User.deleted_at.is_(None))

        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def save_user(self, user: User) -> User:
        """Commits any pending state mutations of an existing User entity to the database."""
        await self.db.commit()
        await self.db.refresh(user)
        return user
