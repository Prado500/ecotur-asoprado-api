from pydantic import BaseModel, ConfigDict
from typing import Any
from datetime import datetime
from app.models.audit import AuditAction


class AuditLogBase(BaseModel):
    """Base Data Transfer Object for Audit Logs."""

    entity_name: str
    entity_id: str
    action: AuditAction
    changes: dict[str, Any] | None = None
    performed_by: str


class AuditLogCreate(AuditLogBase):
    """DTO utilized internally by the Service Layer to dispatch
    records to the Audit Repository.
    """

    pass


class AuditLogResponse(AuditLogBase):
    """DTO utilized to serialize backend audit data outward to the
    frontend administrative dashboards.
    """

    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
