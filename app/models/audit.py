import enum
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.database import Base


class AuditAction(str, enum.Enum):  # noqa: UP042 (backlog D2)
    """Standardized actions for the Audit Trail."""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    SOFT_DELETE = "SOFT_DELETE"
    RECOVER = "RECOVER"
    ACTIVATE = "ACTIVATE"
    DEACTIVATE = "DEACTIVATE"


class AuditLog(Base):
    """SQLAlchemy domain model for the Audit Trail ecosystem.

    changes holds, on UPDATE, {field: {"old": ..., "new": ...}} for the fields that
    changed; on CREATE, the values of the new row; on any other action, None (ADR-0021).
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # "User" or "TouristService"
    entity_name: Mapped[str] = mapped_column(String(50), index=True)

    # String to gracefully support both INT (Service ID) and VARCHAR (Cedula)
    entity_id: Mapped[str] = mapped_column(String(50), index=True)

    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction, name="audit_action_enum"))

    # UPDATE: {field: {"old", "new"}}; CREATE: the values of the new row (ADR-0021)
    changes: Mapped[dict[str, Any] | None] = mapped_column(JSON().with_variant(JSONB, "postgresql"))

    # The 'cedula' of the administrator who triggered the transaction
    performed_by: Mapped[str] = mapped_column(String(50), index=True)

    timestamp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
