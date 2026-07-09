from fastapi import HTTPException, status
from typing import List

from app.repositories.service_repository import ServiceRepository
from app.models.user import User, UserRole
from app.models.service import TouristService, ServiceImage
from app.schemas.service import ServiceCreate

class TouristServicesService:
    """
        Encapsulates business logic and rules, validations, and the operational logic of TouristService entity.
    """
    def __init__(self, service_repo: ServiceRepository):
        self.service_repo = service_repo

    async def create_tourist_package(self, package_data: ServiceCreate, current_user: User) -> TouristService:
        if current_user.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privilegios insuficientes."
            )

        tourist_service_data = package_data.model_dump(exclude={"image_urls"})
        new_tourist_service = TouristService(**tourist_service_data)

        for idx, url in enumerate(package_data.image_urls):
            nueva_imagen = ServiceImage(
                image_url=str(url),
                is_primary=(idx == 0)
            )
            new_tourist_service.images.append(nueva_imagen)

        return await self.service_repo.create_service(new_tourist_service)

    async def list_active_packages(self) -> List[TouristService]:
        return await self.service_repo.get_all_active_services()