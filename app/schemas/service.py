from pydantic import BaseModel, Field, ConfigDict, HttpUrl, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from app.models.service import ServiceCategory

class ServiceImageResponse(BaseModel):
    id: int
    image_url: str
    is_primary: bool
    model_config = ConfigDict(from_attributes=True)

class ServiceBase(BaseModel):
    # Eliminar espacios en blanco al inicio y al final de cualquier string.
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(
        ...,
        min_length=20,
        max_length=65,
        description="Nombre del paquete (mínimo 20 caracteres, máximo 65)"
    )
    description: Optional[str] = Field(None, max_length=1000)
    category: ServiceCategory = Field(default=ServiceCategory.otro)

    base_price: Decimal = Field(
        ...,
        ge=40000,
        max_digits=10,
        decimal_places=2,
        description="Precio base en COP. No puede ser inferior a $40,000"
    )

    max_capacity: int = Field(..., gt=0, le=30, description="Capacidad máxima de turistas")
    is_available: bool = Field(default=True)

    # === MUTADOR SILENCIOSO DE HIGIENE DE DATOS ===
    @field_validator('name')
    @classmethod
    def format_service_name(cls, v: str) -> str:
        """
        Transforma silenciosamente inputs como ' pAqUeTe tuRIsTiCo '
        a 'Paquete Turístico'. Se emplea .title() para que funcione como "Title Case" (primeras Letras En Mayúscula)
        """
        # Elimina espacios dobles accidentales en el medio ("Tour   por el rio" -> "Tour por el rio")
        limpio = " ".join(v.split())

        return limpio.title()

class ServiceCreate(ServiceBase):
    # HttpUrl delega a Rust la validación estricta de que el string
    # empiece con http:// o https:// y tenga un dominio válido.
    image_urls: List[HttpUrl] = Field(
        default=[],
        max_length=10,
        description="Lista de URLs de imágenes. La primera será la principal. Asegúrese de haber pegado un link que empiece por http:// o https://"
    )

class ServiceListResponse(ServiceBase):
    id: int
    images: List[ServiceImageResponse] = []
    model_config = ConfigDict(from_attributes=True)

class ServiceDetailResponse(ServiceBase):
    id: int
    created_at: datetime
    deleted_at: Optional[datetime] = None
    images: List[ServiceImageResponse] = []
    model_config = ConfigDict(from_attributes=True)