from decimal import Decimal

from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from typing import List

from app.models.user import User
from app.schemas.service import ServiceCreate, ServiceListResponse, ServiceDetailResponse, ServiceUpdate
from app.api.dependencies import get_current_user, get_service_service
from app.services.tourist_services_service import TouristServicesService
from app.models.service import ServiceCategory
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError
router = APIRouter()

# -------------------------------------------------------------------
# DEPENDENCY INJECTION ADAPTER (Data Extractor & Validator when receiving multipart/form data)
# Employed to prevent error 422 unprocessable entity as tourist services creation data comes in multipart/form
# and not in application/json.
# -------------------------------------------------------------------
def multipart_package_adapter(
        name: str = Form(..., description="Name of the tourist package"),
        description: str = Form(None, description="Detailed package description"),
        category: ServiceCategory = Form(..., description="Package category classification"),
        base_price: Decimal = Form(..., description="Base price in COP"),
        max_capacity: int = Form(..., description="Maximum tourist capacity"),
        is_available: bool = Form(True, description="Initial availability status")
) -> ServiceCreate:
    """
    FastAPI dependency that intercepts individual form chunks from a
    multipart/form-data payload, assembles them, and triggers strict
    Pydantic validation by instantiating the ServiceCreate DTO.
    """

    try:
        return ServiceCreate(
            name=name,
            description=description,
            category=category,
            base_price=base_price,
            max_capacity=max_capacity,
            is_available=is_available,
            image_urls=[]
         )
    except ValidationError as exc:
        # Re-raise Pydantic's native error as FastAPI's RequestValidationError
        # This successfully triggers the custom global UX handler defined in main.py
        raise RequestValidationError(exc.errors())

@router.post("/", response_model=ServiceDetailResponse, status_code=status.HTTP_201_CREATED)
async def crear_paquete(
        paquete: ServiceCreate = Depends(multipart_package_adapter),
        service_service: TouristServicesService = Depends(get_service_service),
        usuario_actual: User = Depends(get_current_user),
        images: List[UploadFile] = File(...),
):
    """
    Protected endpoint: Delegates tourist services creation to TouristServicesService.
    Returns a JSON representation containing generic information of a tourist service just created.
    """
    return await service_service.create_tourist_package(package_data=paquete, image_files=images, current_user=usuario_actual)


@router.get("/", response_model=List[ServiceListResponse])
async def listar_paquetes(service_service: TouristServicesService = Depends(get_service_service)):
    """
    Public endpoint: Returns a list of all tourist services created which are in active state.
    """
    return await service_service.list_active_packages()

@router.get("/admin/inactivos", response_model=List[ServiceListResponse])
async def listar_inactivos(
        service_service: TouristServicesService = Depends(get_service_service),
        usuario_actual: User = Depends(get_current_user)
):
    """
    Protected Endpoint: Retrieves the collection of inactive packages.

    Serves the 'Por Activar' Kanban column for the administrative UI.
    Requires an active JWT session with an 'admin' role payload.
    """
    return await service_service.list_inactive_packages(usuario_actual)

@router.get("/admin/eliminados", response_model=List[ServiceDetailResponse])
async def listar_eliminados(
        service_service: TouristServicesService = Depends(get_service_service),
        usuario_actual: User = Depends(get_current_user)
):
    """
    Protected Endpoint: Retrieves the collection of soft-deleted packages.

    Serves the 'Eliminados' Kanban column. Returns a detailed DTO structure
    including the timestamp of deletion to comply with Data Governance audits.
    """
    return await service_service.list_deleted_packages(usuario_actual)

@router.put("/{service_id}", response_model=ServiceDetailResponse)
async def modificar_paquete(
        service_id: int,
        update_data: ServiceUpdate,
        service_service: TouristServicesService = Depends(get_service_service),
        usuario_actual: User = Depends(get_current_user)
):
    """
    Protected Endpoint: Modifies existing attributes of a target package.

    Expects a partial or full JSON payload. Image URL lists are handled through
    absolute replacement (destructive update).
    """
    return await service_service.update_package_details(service_id, update_data, usuario_actual)

@router.patch("/{service_id}/activar")
async def activar_paquete(
        service_id: int,
        service_service: TouristServicesService = Depends(get_service_service),
        usuario_actual: User = Depends(get_current_user)
):
    """
    Protected Endpoint: Triggers a state mutation transitioning a package to active.

    The package will immediately become visible in the public tourist catalog.
    """
    return await service_service.toggle_package_status(service_id, True, usuario_actual)

@router.patch("/{service_id}/desactivar")
async def desactivar_paquete(
        service_id: int,
        service_service: TouristServicesService = Depends(get_service_service),
        usuario_actual: User = Depends(get_current_user)
):
    """
    Protected Endpoint: Triggers a state mutation transitioning a package to inactive.

    The package is un-published from the public catalog but remains structurally intact.
    """
    return await service_service.toggle_package_status(service_id, False, usuario_actual)

@router.delete("/{service_id}")
async def borrar_paquete_logico(
        service_id: int,
        service_service: TouristServicesService = Depends(get_service_service),
        usuario_actual: User = Depends(get_current_user)
):
    """
    Protected Endpoint: Performs a logical deletion (Soft Delete) on the target package.

    This fulfills the referential integrity constraints avoiding hard deletions.
    The package is hidden and stamped with a UTC deletion timestamp.
    """
    return await service_service.soft_delete_package(service_id, usuario_actual)

@router.patch("/{service_id}/recuperar")
async def recuperar_paquete(
        service_id: int,
        service_service: TouristServicesService = Depends(get_service_service),
        usuario_actual: User = Depends(get_current_user)
):
    """
    Protected Endpoint: Recovers a soft-deleted package.

    Resets the deletion timestamp and forces the package state to inactive
    to require manual publishing validation.
    """
    return await service_service.recover_package(service_id, usuario_actual)