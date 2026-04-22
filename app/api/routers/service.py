from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload # <- IMPORTANTE PARA ASYNC
from typing import List

from app.db.database import get_db
from app.models.service import TouristService
from app.models.user import User, UserRole
from app.schemas.service import ServiceCreate, ServiceListResponse, ServiceDetailResponse
from app.api.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=ServiceDetailResponse, status_code=status.HTTP_201_CREATED)
async def crear_paquete(

        paquete: ServiceCreate,
        db: AsyncSession = Depends(get_db),
        usuario_actual: User = Depends(get_current_user)
):
    """
    Endpoint privado y exclusivo para administradores que les permite crear un nuevo paquete turístico.
    """

    if usuario_actual.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Privilegios insuficientes.")

    nuevo_paquete = TouristService(**paquete.model_dump())
    db.add(nuevo_paquete)
    await db.commit()

    stmt = select(TouristService).options(selectinload(TouristService.images)).where(
        TouristService.id == nuevo_paquete.id
    )
    resultado = await db.execute(stmt)
    nuevo_paquete = resultado.scalar_one()



    return nuevo_paquete #En esta iteración es importante no olvidar que las imagenes vendran de regrso a manera de lista vacía.


@router.get("/", response_model=List[ServiceListResponse])
async def listar_paquetes(db: AsyncSession = Depends(get_db)):
    """
    Endpoint público que permite listar todos los paquetes turísticos disponibles.
    Contribuye a la HU-03
    """

    # selectinload le dice a SQLAlchemy que se traiga todos los servicios Y también sus imágenes asociadas
    stmt = select(TouristService).options(selectinload(TouristService.images)).where(
        TouristService.is_available == True,
        TouristService.deleted_at.is_(None)
    )

    resultado = await db.execute(stmt)
    paquetes = resultado.scalars().all()

    return paquetes

