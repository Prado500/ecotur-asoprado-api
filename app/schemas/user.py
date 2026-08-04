from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    """
    Pydantic enumeration for user roles validation.

    Mirrors the SQLAlchemy UserRole enum to strictly validate incoming
    and outgoing payload data representing user privileges at the API boundary.
    """
    superadmin = "superadmin"
    admin = "admin"
    tourist = "tourist"

class UserBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    cedula: str = Field(
        ...,
        min_length=6,
        max_length=10,
        pattern=r"^\d{6,10}$",
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
    # === DATA HYGIENE ===
    @field_validator('first_name', 'last_name')
    @classmethod
    def format_title_case(cls, v: str) -> str:
        """
        Applies Postel's Law: silently transforms inputs like 'joSE MaNuEL'
        into 'Jose Manuel' before they are persisted to the database.
        """
        # .title() converts the first char of each word into CAPS; the rest of the chars are left in lowercase.
        return v.title()

class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        description="Contraseña segura (debe tener al menos 8 carácteres, al menos una mayúscula, al menos una minúscula y al menos un número. )"
    )
    data_consent: bool = Field(..., description="Aceptación de la Ley 1581 de protección de datos")

    # === EFFICIENT AND GRANULAR PASSWORD VALIDATION ===
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
       Password strength validation without regex lookaheads, avoiding Rust-side issues (Pydantic V2)
       and enabling specific, granular error messages for better UX.
        """
        if not any(c.isupper() for c in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula.')

        if not any(c.islower() for c in v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula.')

        if not any(c.isdigit() for c in v):
            raise ValueError('La contraseña debe contener al menos un número.')

        return v

    # ===  CONSENT LOGIC VALIDATION ===
    @field_validator('data_consent')
    @classmethod
    def check_consent(cls, v: bool) -> bool:
        """Logical validator: the system must not allow registration if the data protection law consent is not accepted."""
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

class UserUpdate(BaseModel):
    """
    Data Transfer Object (DTO) for updating existing user records.

    Enforces partial updates (PATCH/PUT behavior) by making all fields optional.
    Sensitive immutable fields such as 'cedula' and 'password' are fundamentally
    excluded to prevent unauthorized architectural mutations.
    """
    email: Optional[EmailStr] = Field(None, description="Correo electrónico válido")
    first_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=65,
        pattern=r"^[A-Za-zÁÉÍÓÚáéíóúÜüÑñ]+(?:\s[A-Za-zÁÉÍÓÚáéíóúÜüÑñ]+)*$"
    )
    last_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=65,
        pattern=r"^[A-Za-zÁÉÍÓÚáéíóúÜüÑñ]+(?:\s[A-Za-zÁÉÍÓÚáéíóúÜüÑñ]+)*$"
    )
    phone: Optional[str] = Field(None, pattern=r"^3\d{9}$")
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

    @field_validator('first_name', 'last_name')
    @classmethod
    def format_title_case(cls, v: Optional[str]) -> Optional[str]:
        """
        Silently applies title casing if the field is present in the payload.
        """
        if v is None:
            return v
        clean = " ".join(v.split())
        return clean.title()