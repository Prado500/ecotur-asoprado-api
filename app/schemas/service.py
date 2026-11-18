from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from app.models.service import ServiceCategory
from app.schemas.partial_update import NoExplicitNull

# Scale of tourist_services.base_price, NUMERIC(10, 2): every price is written with two decimals.
_CENTS = Decimal("0.01")


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

    @field_validator("base_price")
    @classmethod
    def format_base_price(cls, v: Decimal) -> Decimal:
        """Writes the price with the two decimals of its column: 50000 becomes 50000.00."""
        return v.quantize(_CENTS)


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


class ServiceListResponse(BaseModel):
    """Serialized catalog view of a stored tourist package.

    Declared on BaseModel on purpose: it describes what is stored and never re-applies
    the input rules of ServiceBase (length, price floor, capacity cap, title-case), so
    one off-rule package cannot take the public catalog down (backlog A9).
    """

    name: str
    description: str | None = None
    category: ServiceCategory = ServiceCategory.otro
    base_price: Decimal
    max_capacity: int
    is_available: bool = False
    id: int
    images: list[ServiceImageResponse] = []
    model_config = ConfigDict(from_attributes=True)


class ServiceDetailResponse(BaseModel):
    """Serialized detail view of a stored tourist package, including its timestamps.

    Same rationale as ServiceListResponse: no input rules on output (backlog A9).
    """

    name: str
    description: str | None = None
    category: ServiceCategory = ServiceCategory.otro
    base_price: Decimal
    max_capacity: int
    is_available: bool = False
    id: int
    created_at: datetime
    deleted_at: datetime | None = None
    images: list[ServiceImageResponse] = []
    model_config = ConfigDict(from_attributes=True)


class ServiceImageOutput(BaseModel):
    image_urls: list[HttpUrl] = Field(default_factory=list, max_length=10)


class ServiceUpdate(BaseModel):
    """Partial update of a tourist package: only the fields present in the payload change.

    An explicit null is accepted only on description, whose column admits empty, and on
    image_urls, where it leaves the images as they are; on any other field it is a 422
    (ADR-0020).
    """

    name: Annotated[str | None, NoExplicitNull] = Field(None, min_length=20, max_length=65)
    description: str | None = Field(None, max_length=1000)
    category: Annotated[ServiceCategory | None, NoExplicitNull] = None
    base_price: Annotated[Decimal | None, NoExplicitNull] = Field(
        None, ge=40000, max_digits=10, decimal_places=2
    )
    max_capacity: Annotated[int | None, NoExplicitNull] = Field(None, gt=0, le=30)
    is_available: Annotated[bool | None, NoExplicitNull] = None
    image_urls: list[HttpUrl] | None = Field(None, max_length=10)

    @field_validator("name")
    @classmethod
    def format_service_name(cls, v: str) -> str:
        """Title-cases the package name and collapses repeated whitespace."""
        clean = " ".join(v.split())
        return clean.title()

    @field_validator("base_price")
    @classmethod
    def format_base_price(cls, v: Decimal) -> Decimal:
        """Writes the price with the two decimals of its column: 50000 becomes 50000.00."""
        return v.quantize(_CENTS)
