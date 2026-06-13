from pydantic import BaseModel, Field, ConfigDict
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
    name: str = Field(
        ...,
        min_length=20,
        max_length=65,
        description="Nombre del paquete (mínimo 20 caracteres, máximo 65)"
    )
    description: Optional[str] = Field(None, max_length=1000)
    category: ServiceCategory = Field(default=ServiceCategory.otro)

    # REGLA FINANCIERA ESTRICTA: ge=40000 (Greater than or Equal to 40000)
    # decimal_places=2 garantiza precisión de moneda, evitando floats con basura matemática (ej. 40000.000001)
    base_price: Decimal = Field(
        ...,
        ge=40000,
        max_digits=10,
        decimal_places=2,
        description="Precio base en COP. No puede ser inferior a $40,000"
    )

    # max_capacity: Imposible que un paquete sea para 0 personas o para más de 30 personas.
    max_capacity: int = Field(..., gt=0, le=30, description="Capacidad máxima de turistas")
    is_available: bool = Field(default=True)

class ServiceCreate(ServiceBase):
    image_urls: List[str] = Field(
        default=[],
        max_length=10, # Máximo 10 imágenes por paquete para no saturar la BD
        description="Lista de URLs de imágenes. La primera será la principal."
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