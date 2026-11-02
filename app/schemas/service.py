from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

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
        description="Nombre del paquete (mínimo 20 caracteres, máximo 65)",
    )
    description: str | None = Field(None, max_length=1000)
    category: ServiceCategory = Field(default=ServiceCategory.otro)

    base_price: Decimal = Field(
        ...,
        ge=40000,
        max_digits=10,
        decimal_places=2,
        description="Precio base en COP. No puede ser inferior a $40,000",
    )

    max_capacity: int = Field(..., gt=0, le=30, description="Capacidad máxima de turistas")
    is_available: bool = Field(default=False)

    # === TITLE DATA HYGIENE ===
    @field_validator("name")
    @classmethod
    def format_service_name(cls, v: str) -> str:
        """Transforms inputs such as 'pAqUeTe tuRIsTiCo' into 'Paquete Turístico'.

        It implements title case employing .title()
        """
        # Elimination of double whitespaces ("Tour   por el rio" -> "Tour por el rio")
        clean = " ".join(v.split())

        return clean.title()


class ServiceCreate(ServiceBase):
    # HttpUrl delegates the image url string domain and protocol verification to Rust.
    image_urls: list[HttpUrl] = Field(
        default=[],
        max_length=10,
        description=(
            "Lista de URLs de imágenes. La primera será la principal. "
            "Asegúrese de haber pegado un link que empiece por http:// o https://"
        ),
    )


class ServiceListResponse(ServiceBase):
    id: int
    images: list[ServiceImageResponse] = []
    model_config = ConfigDict(from_attributes=True)


class ServiceDetailResponse(ServiceBase):
    id: int
    created_at: datetime
    deleted_at: datetime | None = None
    images: list[ServiceImageResponse] = []
    model_config = ConfigDict(from_attributes=True)


class ServiceImageOutput(BaseModel):
    image_urls: list[HttpUrl] = Field(default_factory=list, max_length=10)


class ServiceUpdate(BaseModel):
    name: str | None = Field(None, min_length=20, max_length=65)
    description: str | None = Field(None, max_length=1000)
    category: ServiceCategory | None = None
    base_price: Decimal | None = Field(None, ge=40000, max_digits=10, decimal_places=2)
    max_capacity: int | None = Field(None, gt=0, le=30)
    is_available: bool | None = None
    image_urls: list[HttpUrl] | None = Field(None, max_length=10)

    @field_validator("name")
    @classmethod
    def format_service_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        clean = " ".join(v.split())
        return clean.title()
