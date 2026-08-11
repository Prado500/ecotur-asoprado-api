import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.database import Base

class AuditAction(str, enum.Enum):
    """
    Standardized actions for the Audit Trail.
    """
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    SOFT_DELETE = "SOFT_DELETE"
    RECOVER = "RECOVER"
    ACTIVATE = "ACTIVATE"
    DEACTIVATE = "DEACTIVATE"

class AuditLog(Base):
    """
    SQLAlchemy domain model for the Audit Trail ecosystem.

    Utilizes PostgreSQL's native JSONB data type to store structural
    snapshots of domain entities regardless of their rigid schema.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # "User" or "TouristService"
    entity_name = Column(String(50), nullable=False, index=True)

    # String to gracefully support both INT (Service ID) and VARCHAR (Cedula)
    entity_id = Column(String(50), nullable=False, index=True)

    action = Column(Enum(AuditAction, name="audit_action_enum"), nullable=False)

    # Dictionary snapshot containing 'old_values' and 'new_values'
    changes = Column(JSONB, nullable=True)

    # The 'cedula' of the administrator who triggered the transaction
    performed_by = Column(String(50), nullable=False, index=True)

    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)