from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    tourist = "tourist"

class UserBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    cedula: str = Field(
        ...,
        min_length=6,
        max_length=10,
        pattern="^\d{6,10}$",
        description="Cédula de ciudadanía. Solo puede contener números del 0 al 9, y su longitud debe ser entre 6 y 10 dígitos"
    )


    email: EmailStr = Field(..., description="Correo electrónico debe ser válido")



    first_name: str = Field(
        ...,
        min_length=2,
        max_length=65,
        pattern=r"^[A-Za-zÁÉÍÓÚáéíóúÜüÑñ]+(?:\s[A-Za-zÁÉÍÓÚáéíóúÜüÑñ]+)*$",
        description="Nombres. Máximo 65 caracteres incluyendo un espacio en blanco entre nombres. (solo puede digitar letras, tíldes y un espacio entre palabras; todo nombre debe empezar con una letra)"
    )
    last_name: str = Field(
        ...,
        min_length=2,
        max_length=65,
        pattern=r"^[A-Za-zÁÉÍÓÚáéíóúÜüÑñ]+(?:\s[A-Za-zÁÉÍÓÚáéíóúÜüÑñ]+)*$",
        description="Apellidos. Máximo 65 caracteres incluyendo un espacio en blanco entre apellidos. (solo puede digitar letras, tíldes y un espacio entre palabras; todo apellido debe empezar con una letra)"
    )
    phone: Optional[str] = Field(
        None,
        pattern=r"^3\d{9}$",
        description="Número de celular (debe tener 10 dígitos y comenzar por el número tres (3) )"
    )
    # === HIGIENE DE DATOS ===
    @field_validator('first_name', 'last_name')
    @classmethod
    def format_title_case(cls, v: str) -> str:
        """
        Aplica la Ley de Postel: Transforma silenciosamente inputs como 'joSE MaNuEL'
        a 'Jose Manuel' antes de inyectarlos en la Base de Datos.
        """
        # El método .title() convierte la primera letra de cada palabra en mayúscula
        # y el resto en minúsculas.
        return v.title()

class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        description="Contraseña segura (debe tener al menos 8 carácteres, al menos una mayúscula, al menos una minúscula y al menos un número. )"
    )
    data_consent: bool = Field(..., description="Aceptación de la Ley 1581 de protección de datos")

    # === VALIDACIÓN EFICIENTE Y GRANULAR DE LA CONTRASEÑA ===
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validación de contraseña sin look-aheads de regex, evitando errores en Rust (Pydantic V2)
        y permitiendo mensajes de error específicos (UX granular).
        """
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula.')

        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula.')

        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número.')

        return v

    # === VALIDACIÓN LÓGICA DE CONSENTIMIENTO ===
    @field_validator('data_consent')
    @classmethod
    def check_consent(cls, v: bool) -> bool:
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