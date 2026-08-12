from fastapi import APIRouter, Depends
from typing import List

from app.schemas.audit import AuditLogResponse
from app.models.user import User
from app.api.dependencies import get_current_user, get_audit_service
from app.services.audit_service import AuditService

router = APIRouter()

@router.get("/", response_model=List[AuditLogResponse])
async def obtener_historial_auditoria(
        limite: int = 100,
        audit_service: AuditService = Depends(get_audit_service),
        usuario_actual: User = Depends(get_current_user)
):
    """
    Protected Endpoint: Retrieves the global audit history.

    Strictly gated to Administrators and Superadmins via the Service Layer.
    Utilizes a limit parameter to prevent RAM exhaustion on large datasets.
    """
    return await audit_service.retrieve_audit_history(current_user=usuario_actual, limit=limite)