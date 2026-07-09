from fastapi import APIRouter, Depends, status
from typing import List

from app.models.user import User
from app.schemas.service import ServiceCreate, ServiceListResponse, ServiceDetailResponse
from app.api.dependencies import get_current_user, get_service_service
from app.services.tourist_services_service import TouristServicesService

router = APIRouter()

@router.post("/", response_model=ServiceDetailResponse, status_code=status.HTTP_201_CREATED)
async def crear_paquete(
        paquete: ServiceCreate,
        service_service: TouristServicesService = Depends(get_service_service),
        usuario_actual: User = Depends(get_current_user)
):
    """
    Protected endpoint: Delegates tourist services creation to TouristServicesService.
    Returns a JSON representation containing generic information of a tourist service just created.
    """
    return await service_service.create_tourist_package(paquete, usuario_actual)


@router.get("/", response_model=List[ServiceListResponse])
async def listar_paquetes(service_service: TouristServicesService = Depends(get_service_service)):
    """
    Public endpoint: Returns a list of all tourist services created which are in active state.
    """
    return await service_service.list_active_packages()