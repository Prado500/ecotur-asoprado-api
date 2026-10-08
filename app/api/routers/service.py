from typing import List

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.api.dependencies import get_current_admin_user, get_service_service
from app.models.user import User
from app.schemas.service import (
    ServiceCreate,
    ServiceDetailResponse,
    ServiceImageOutput,
    ServiceListResponse,
    ServiceUpdate,
)
from app.services.tourist_services_service import TouristServicesService

# -------------------------------------------------------------------
# ROUTER SEGMENTATION (RBAC at the transport boundary)
# Authorization is centralized in the router layer: admin routes inherit
# the get_current_admin_user dependency from admin_router, so handlers
# only inject the user when the service actually needs the identity
# (e.g. audit trail emission). Public routes carry no auth dependency.
# -------------------------------------------------------------------

public_router = APIRouter()
admin_router = APIRouter(dependencies=[Depends(get_current_admin_user)])


# -------------------------------------------------------------------
# PUBLIC ENDPOINTS
# -------------------------------------------------------------------

@public_router.get("/", response_model=List[ServiceListResponse])
async def listar_paquetes(service_service: TouristServicesService = Depends(get_service_service)):
    """
    Public endpoint: Returns a list of all tourist services created which are in active state.

    Args:
        service_service (TouristServicesService): Injected business-logic service.

    Returns:
        List[ServiceListResponse]: Public catalog of active tourist packages.
    """
    return await service_service.list_active_packages()


# -------------------------------------------------------------------
# ADMIN ENDPOINTS
# -------------------------------------------------------------------

@admin_router.post("/upload-images/", response_model=ServiceImageOutput, status_code=status.HTTP_200_OK)
async def upload_images(
        service_service: TouristServicesService = Depends(get_service_service),
        images: List[UploadFile] = File(...),
):
    """
    Protected endpoint: Allows image uploading via service-layer delegation per tourist service.

    Images arrive as multipart/form-data binaries, which FastAPI must accept as-is to
    prevent a 422 error before the payload reaches the service layer.

    Args:
        service_service (TouristServicesService): Injected business-logic service.
        images (List[UploadFile]): Image binaries to stage in Azure Blob Storage.

    Returns:
        ServiceImageOutput: JSON representation containing a list of urls redirecting
            to images stored inside Azure Blob Storage.
    """
    return await service_service.image_uploader(images_files=images)


@admin_router.post("/", response_model=ServiceDetailResponse, status_code=status.HTTP_201_CREATED)
async def crear_paquete(
        paquete: ServiceCreate,
        usuario_actual: User = Depends(get_current_admin_user),
        service_service: TouristServicesService = Depends(get_service_service)
):
    """
    Protected endpoint: Delegates tourist services creation to TouristServicesService.

    The admin identity is forwarded to the service because creation is a state
    mutation that MUST emit an audit trail entry.

    Args:
        paquete (ServiceCreate): Validated payload describing the new tourist package.
        usuario_actual (User): Authenticated administrator executing the mutation.
        service_service (TouristServicesService): Injected business-logic service.

    Returns:
        ServiceDetailResponse: JSON representation of the tourist service just created.
    """
    return await service_service.create_tourist_package(package_data=paquete, current_user=usuario_actual)


@admin_router.get("/admin/inactivos", response_model=List[ServiceListResponse])
async def listar_inactivos(
        service_service: TouristServicesService = Depends(get_service_service)
):
    """
    Protected Endpoint: Retrieves the collection of inactive packages.

    Serves the 'Por Activar' Kanban column for the administrative UI.
    Requires an active JWT session with an 'admin' role payload.

    Args:
        service_service (TouristServicesService): Injected business-logic service.

    Returns:
        List[ServiceListResponse]: A list of inactive package ORM entities.
    """
    return await service_service.list_inactive_packages()


@admin_router.get("/admin/eliminados", response_model=List[ServiceDetailResponse])
async def listar_eliminados(
        service_service: TouristServicesService = Depends(get_service_service)
):
    """
    Protected Endpoint: Retrieves the collection of soft-deleted packages.

    Serves the 'Eliminados' Kanban column. Returns a detailed DTO structure
    including the timestamp of deletion to comply with Data Governance audits.

    Args:
        service_service (TouristServicesService): Injected business-logic service.

    Returns:
        List[ServiceDetailResponse]: A list of logically deleted package ORM entities.
    """
    return await service_service.list_deleted_packages()


@admin_router.put("/{service_id}", response_model=ServiceDetailResponse)
async def modificar_paquete(
        service_id: int,
        update_payload: ServiceUpdate,
        usuario_actual: User = Depends(get_current_admin_user),
        service_service: TouristServicesService = Depends(get_service_service)
):
    """
    Protected Endpoint: Modifies existing attributes of a target package.

    Expects a partial or full JSON payload. Image URL lists are handled through
    absolute replacement (destructive update).

    Args:
        service_id (int): The unique identifier of the package to update.
        update_payload (ServiceUpdate): Partial DTO containing only modified fields.
        usuario_actual (User): Authenticated administrator executing the mutation.
        service_service (TouristServicesService): Injected business-logic service.

    Returns:
        ServiceDetailResponse: JSON representation of the refreshed package.
    """
    return await service_service.update_package_details(service_id, update_payload, usuario_actual)


@admin_router.patch("/{service_id}/activar")
async def activar_paquete(
        service_id: int,
        service_service: TouristServicesService = Depends(get_service_service),
        usuario_actual: User = Depends(get_current_admin_user)
):
    """
    Protected Endpoint: Triggers a state mutation transitioning a package to active.

    The package will immediately become visible in the public tourist catalog.

    Args:
        service_id (int): The unique identifier of the package to activate.
        service_service (TouristServicesService): Injected business-logic service.
        usuario_actual (User): Authenticated administrator executing the mutation.

    Returns:
        dict: Standardized JSON response confirming the state change.
    """
    return await service_service.toggle_package_status(service_id, True, usuario_actual)


@admin_router.patch("/{service_id}/desactivar")
async def desactivar_paquete(
        service_id: int,
        service_service: TouristServicesService = Depends(get_service_service),
        usuario_actual: User = Depends(get_current_admin_user)
):
    """
    Protected Endpoint: Triggers a state mutation transitioning a package to inactive.

    The package is un-published from the public catalog but remains structurally intact.

    Args:
        service_id (int): The unique identifier of the package to deactivate.
        service_service (TouristServicesService): Injected business-logic service.
        usuario_actual (User): Authenticated administrator executing the mutation.

    Returns:
        dict: Standardized JSON response confirming the state change.
    """
    return await service_service.toggle_package_status(service_id, False, usuario_actual)


@admin_router.delete("/{service_id}")
async def borrar_paquete_logico(
        service_id: int,
        service_service: TouristServicesService = Depends(get_service_service),
        usuario_actual: User = Depends(get_current_admin_user)
):
    """
    Protected Endpoint: Performs a logical deletion (Soft Delete) on the target package.

    This fulfills the referential integrity constraints avoiding hard deletions.
    The package is hidden and stamped with a UTC deletion timestamp.

    Args:
        service_id (int): The unique identifier of the package to delete.
        service_service (TouristServicesService): Injected business-logic service.
        usuario_actual (User): Authenticated administrator executing the mutation.

    Returns:
        dict: Standardized confirmation message.
    """
    return await service_service.soft_delete_package(service_id, usuario_actual)


@admin_router.patch("/{service_id}/recuperar")
async def recuperar_paquete(
        service_id: int,
        service_service: TouristServicesService = Depends(get_service_service),
        usuario_actual: User = Depends(get_current_admin_user)
):
    """
    Protected Endpoint: Recovers a soft-deleted package.

    Resets the deletion timestamp and forces the package state to inactive
    to require manual publishing validation.

    Args:
        service_id (int): The unique identifier of the package to recover.
        service_service (TouristServicesService): Injected business-logic service.
        usuario_actual (User): Authenticated administrator executing the mutation.

    Returns:
        dict: Standardized confirmation message.
    """
    return await service_service.recover_package(service_id, usuario_actual)


router = APIRouter()
router.include_router(public_router)
router.include_router(admin_router)
