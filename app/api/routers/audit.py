from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_audit_service, get_current_admin_user
from app.schemas.audit import AuditLogResponse
from app.services.audit_service import AuditService

router = APIRouter(dependencies=[Depends(get_current_admin_user)])


@router.get("/", response_model=list[AuditLogResponse])
async def obtener_historial_auditoria(
    limit: int = Query(20, ge=1, le=100, description="Cantidad máxima de registros por página"),
    offset: int = Query(
        0, ge=0, description="Número de registros a omitir (Usado para Paginación)"
    ),
    entity_name: str | None = Query(
        None, description="Filtrar por nombre de la entidad (ej. User, TouristService)"
    ),
    entity_id: str | None = Query(
        None, description="Filtrar por identificador único de la entidad"
    ),
    audit_service: AuditService = Depends(get_audit_service),
):
    """Protected Endpoint: Retrieves the global audit history.

    The router-level admin guard is the only role check on this route
    (ADR-0012, point 3); the handler needs no identity, so it injects none.
    Utilizes limit/offset parameters to establish cursor-less pagination and
    prevent RAM exhaustion on large datasets. Exposes explicit Query Params to
    avoid frontend Over-fetching.
    """
    return await audit_service.retrieve_audit_history(
        limit=limit,
        offset=offset,
        entity_name=entity_name,
        entity_id=entity_id,
    )
