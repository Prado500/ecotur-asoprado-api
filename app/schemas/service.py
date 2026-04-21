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
    name: str = Field(..., max_length=150)
    description: Optional[str] = None
    category: ServiceCategory = Field(default=ServiceCategory.otro)
    base_price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    max_capacity: int = Field(..., gt=0)
    is_available: bool = Field(default=True)


class ServiceCreate(ServiceBase):
    pass


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