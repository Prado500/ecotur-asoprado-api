import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.database import Base


class UserRole(str, enum.Enum):  # noqa: UP042 (backlog D2)
    """Enumeration of system user roles.

    Defines the hierarchical Access Control levels within the platform,
    ensuring coherence across the persistence layer.

    Attributes:
        superadmin: Highest privilege level. Can create admins and tourists.
        admin: Mid privilege level. Can manage tourist accounts.
        tourist: Base privilege level. Standard consumer of the platform.
    """

    superadmin = "superadmin"
    admin = "admin"
    tourist = "tourist"


class User(Base):
    """SQLAlchemy domain model for the User entity.

    Represents the 'users' table in the database, handling authentication
    credentials, personal identification, and Role-Based Access Control (RBAC).
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cedula: Mapped[str] = mapped_column(String(13), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), default=UserRole.tourist
    )
    data_consent: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
