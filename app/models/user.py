import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from app.db.database import Base

class UserRole(str, enum.Enum):
    """
    Enumeration of system user roles.

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
    """
    SQLAlchemy domain model for the User entity.

    Represents the 'users' table in the database, handling authentication
    credentials, personal identification, and Role-Based Access Control (RBAC).
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    cedula = Column(String(13), unique=True, index=True, nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(Enum(UserRole, name="user_role"), nullable=False, default=UserRole.tourist)
    data_consent = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)