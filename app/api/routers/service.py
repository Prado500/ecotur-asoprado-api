from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload # <- IMPORTANTE PARA ASYNC
from typing import List

from app.db.database import get_db
from app.models.service import TouristService, ServiceImage
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
    Gestiona imágenes para la creación de paquetes turísticos mediante URLS enviadas desde el cliente.

    Primero, excluye la clave image_urls que llega con la petición del cliente para crear un objeto SQLAlchemy
    Con el cual preparar el statement de inserción inicial y cuyos atributos sean coherentes de acuerdo a la tabla tourist_services.

    Después pobla el atributo virtual de relacionamiento entre tourist_services (bd) y service_images (bd)
    propio del modelo TouristService, valiéndose de un ciclo for.

    Finalmente, se realiza flush en la base de datos usando el objeto SQLAlchemy nuevo_paquete
    De manera que solo después que se logre la inserción en la tabla tourist_services,
    El SGBD retorna el id asignado a dicha inserción para que el ORM pueda asignarlo a cada
    Objeto del atributo virtual images de TouristService. Inmediatamente después de ello,
    Se realiza la inserción de cada objeto SQLAlchemy representativo de las imágenes en la tabla service_images.

    Este endpoint retorna la relación entre un paquete turístico y toda su galería de imágenes.


    """

    if usuario_actual.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Privilegios insuficientes.")

    datos_paquete = paquete.model_dump(exclude={"image_urls"})
    nuevo_paquete = TouristService(**datos_paquete) # Primer objeto SQLAlchemy de inserción, es un renglon e la tabla.

    for idx, url in enumerate(paquete.image_urls):
        nueva_imagen = ServiceImage( # Segundo objeto SQLALchemy de inserción, es un renglon de la tabla.
            image_url=str(url), #Se parsea porque en ServiceCreate, cada imágen se retorna como objeto y no como String.
            # Si el índice es 0 (la primera foto de la lista), es_primary será True.
            # Para la 2da, 3ra, etc. será False.
            is_primary=(idx == 0)
        )
        # Agregar cada objeto de inserción de la tabla service_images (imagen) a la lista virtual del paquete (SQLAlchemy se encarga de las llaves foráneas)
        nuevo_paquete.images.append(nueva_imagen)

    db.add(nuevo_paquete)
    await db.commit()

    stmt = select(TouristService).options(selectinload(TouristService.images)).where(
        TouristService.id == nuevo_paquete.id
    )
    resultado = await db.execute(stmt)
    nuevo_paquete = resultado.scalar_one()



    return nuevo_paquete # En esta iteración, las imágenes vienen desde el frontend a manera de una lista de Strings donde cada String es una url de una imagen.


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

