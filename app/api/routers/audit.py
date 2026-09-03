from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from app.schemas.audit import AuditLogResponse
from app.models.user import User
from app.api.dependencies import get_current_user, get_audit_service
from app.services.audit_service import AuditService

router = APIRouter()

@router.get("/", response_model=List[AuditLogResponse])
async def obtener_historial_auditoria(
        limit: int = Query(20, ge=1, le=100, description="Cantidad máxima de registros por página"),
        offset: int = Query(0, ge=0, description="Número de registros a omitir (Usado para Paginación)"),
        entity_name: Optional[str] = Query(None, description="Filtrar por nombre de la entidad (ej. User, TouristService)"),
        entity_id: Optional[str] = Query(None, description="Filtrar por identificador único de la entidad"),
        audit_service: AuditService = Depends(get_audit_service),
        usuario_actual: User = Depends(get_current_user)
):
    """
    Protected Endpoint: Retrieves the global audit history.

    Strictly gated to Administrators and Superadmins via the Service Layer.
    Utilizes limit/offset parameters to establish cursor-less pagination and prevent
    RAM exhaustion on large datasets. Exposes explicit Query Params to avoid frontend Over-fetching.
    """
    return await audit_service.retrieve_audit_history(
        current_user=usuario_actual,
        limit=limit,
        offset=offset,
        entity_name=entity_name,
        entity_id=entity_id
    )