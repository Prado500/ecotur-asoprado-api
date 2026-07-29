from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.models.service import TouristService

class ServiceRepository:
    """
    Handles data access (SQL transactions) regarding TouristService entity.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_service(self, service: TouristService) -> TouristService:
        """Creates a new TouristService entity """
        self.db.add(service)
        await self.db.commit()
        # The freshest db registry, in which all the tourist service's images are properly linked to their corresponding service, is retrieved.
        stmt = select(TouristService).options(selectinload(TouristService.images)).where(
            TouristService.id == service.id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_all_active_services(self) -> List[TouristService]:
        """Returns a list of active TouristService entities (is_active = True)  """
        stmt = select(TouristService).options(selectinload(TouristService.images)).where(
            TouristService.is_available == True,
            TouristService.deleted_at.is_(None)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


    async def get_inactive_services(self) -> List[TouristService]:
        """ Returns a list of inactive TouristService entities (is_active = False) """
        stmt = select(TouristService).options(selectinload(TouristService.images)).where(
            TouristService.is_available == False,
            TouristService.deleted_at.is_(None)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_deleted_services(self) -> List[TouristService]:
        """Returns a list of deleted TouristService entities"""
        stmt = select(TouristService).options(selectinload(TouristService.images)).where(
            TouristService.deleted_at.is_not(None)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_service_by_id(self, service_id: int, include_deleted: bool = False) -> Optional[TouristService]:
        """Returns a TouristService based on its id. if no 2nd-positional argument is given, it will bring only non-deleted
           tourist services. Otherwise, it will retrieve a package even if it was soft-deleted.
        """
        stmt = select(TouristService).options(selectinload(TouristService.images)).where(
            TouristService.id == service_id
        )
        if not include_deleted:
            stmt = stmt.where(TouristService.deleted_at.is_(None))

        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def save_service(self, service: TouristService) -> TouristService:
        """Commits changes to an existing service and refreshes relationships"""
        await self.db.commit()
        await self.db.refresh(service)
        return service