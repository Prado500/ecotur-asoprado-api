import enum
from sqlalchemy import Column, String, Integer, Numeric, Text, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class ServiceCategory(str, enum.Enum):
    agroturismo = "agroturismo"
    recreacional = "recreacional"
    metalmecanico = "metalmecanico"
    otro = "otro"

class TouristService(Base):
    __tablename__ = "tourist_services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(ServiceCategory), nullable=False, default=ServiceCategory.otro)
    base_price = Column(Numeric(10, 2), nullable=False)
    max_capacity = Column(Integer, nullable=False)
    is_available = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    images = relationship("ServiceImage", back_populates="service", cascade="all, delete-orphan")

class ServiceImage(Base):
    __tablename__ = "service_images"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("tourist_services.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(Text, nullable=False)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


    service = relationship("TouristService", back_populates="images")