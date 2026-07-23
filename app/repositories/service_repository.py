from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from app.models.service import TouristService

class ServiceRepository:
    """
    Handles data access (SQL transactions) regarding TouristService entity.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_service(self, service: TouristService) -> TouristService:
        self.db.add(service)
        await self.db.commit()
        # The freshest db registry, in which all the tourist service's images are properly linked to their corresponding service, is retrieved.
        stmt = select(TouristService).options(selectinload(TouristService.images)).where(
            TouristService.id == service.id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_all_active_services(self) -> List[TouristService]:
        stmt = select(TouristService).options(selectinload(TouristService.images)).where(
            TouristService.is_available == True,
            TouristService.deleted_at.is_(None)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())