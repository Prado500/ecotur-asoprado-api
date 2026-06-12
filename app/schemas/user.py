from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
import re

class UserRole(str, Enum):
    admin = "admin"
    tourist = "tourist"

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico válido")

    first_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        pattern=r"^[A-Za-zÁÉÍÓÚáéíóúÜüÑñ\s]+$",
        description="Nombres (solo puede digitar letras, tíldes y espacios)"
    )
    last_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        pattern=r"^[A-Za-zÁÉÍÓÚáéíóúÜüÑñ\s]+$",
        description="Apellidos (solo puede digitar letras, tíldes y espacios)"
    )
    # Validación estricta para celular colombiano: Empieza con 3 y tiene 10 dígitos exactos.
    phone: Optional[str] = Field(
        None,
        pattern=r"^3\d{9}$",
        description="Número de celular (debe tener 10 dígitos y comenzar por el número tres (3) )"
    )

class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d\w\W]{8,}$",
        description="Contraseña segura (debe tener al menos 8 carácteres, al menos una mayúscula, al menos una minúscula y al menos un número. )"
    )
    data_consent: bool = Field(..., description="Aceptación de la Ley 1581 de protección de datos")

    @field_validator('data_consent')
    @classmethod
    def check_consent(cls, v):
        """Validador lógico: El sistema no debe permitir registros si no acepta la ley de datos."""
        if not v:
            raise ValueError('Debe aceptar la política de tratamiento de datos para registrarse.')
        return v

class UserCreateByAdmin(UserCreate):
    role: UserRole
    is_active: bool = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}