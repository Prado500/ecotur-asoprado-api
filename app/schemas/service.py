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

    # === TITLE DATA HYGIENE ===
    @field_validator('name')
    @classmethod
    def format_service_name(cls, v: str) -> str:
        """
        Transforms inputs such as 'pAqUeTe tuRIsTiCo' into 'Paquete Turístico'
        It implements title case employing .title()
        """
        # Elimination of double whitespaces ("Tour   por el rio" -> "Tour por el rio")
        clean = " ".join(v.split())

        return clean.title()

class ServiceCreate(ServiceBase):
    # HttpUrl delegates the image url string domain and protocol verification to Rust.
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