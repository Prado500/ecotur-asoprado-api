import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base


class ServiceCategory(str, enum.Enum):  # noqa: UP042 (backlog D2)
    """Enumeration of the categories a tourist service can belong to.

    Stored in PostgreSQL as the native ENUM type ``servicecategory``.
    """

    agroturismo = "agroturismo"
    recreacional = "recreacional"
    metalmecanico = "metalmecanico"
    otro = "otro"


class TouristService(Base):
    """SQLAlchemy domain model for a tourist service offered on the platform.

    Owns its images: deleting a service removes them both in the ORM
    (``delete-orphan`` cascade) and in the database (``ON DELETE CASCADE`` foreign key).
    """

    __tablename__ = "tourist_services"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[ServiceCategory] = mapped_column(
        Enum(ServiceCategory, name="servicecategory"), default=ServiceCategory.otro
    )
    base_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    max_capacity: Mapped[int] = mapped_column()
    is_available: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    images: Mapped[list[ServiceImage]] = relationship(
        back_populates="service", cascade="all, delete-orphan"
    )


class ServiceImage(Base):
    """SQLAlchemy domain model for an image attached to a tourist service."""

    __tablename__ = "service_images"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("tourist_services.id", ondelete="CASCADE"))
    image_url: Mapped[str] = mapped_column(Text)
    is_primary: Mapped[bool | None] = mapped_column(default=False)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    service: Mapped[TouristService] = relationship(back_populates="images")
