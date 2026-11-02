from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.api.routers import audit, service, user
from app.core.exceptions import (
    AccountNotActiveError,
    AlreadyExistsError,
    AuthorizationError,
    BusinessRuleViolationError,
    DomainError,
    InvalidCredentialsError,
    InvalidImageUrlError,
    InvalidVerificationTokenError,
    NotFoundError,
    StorageUnavailableError,
    UnsupportedMediaTypeError,
)

app = FastAPI(
    title="Ecotur-ASOPRADO API",
    description="API RESTful asíncrona para la gestión de paquetes turísticos",
    version="0.2.0",
)


# ===  GLOBAL PYDANTIC EXCEPTION HANDLER (UX FRIENDLY/ UserCreate) ===
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Translates Pydantic validation errors to a user-friendly Spanish format.

    Field names are rendered in Spanish for the client.
    """
    formated_errors = []

    field_dict = {
        "first_name": "nombres",
        "last_name": "apellidos",
        "cedula": "documento",
        "phone": "teléfono",
        "email": "correo electrónico",
        "password": "contraseña",
        "data_consent": "aceptación de términos",
        "name": "nombre del paquete",
        "base_price": "precio base",
        "max_capacity": "capacidad máxima",
    }

    for error in exc.errors():
        raw_filed = error.get("loc")[-1] if error.get("loc") else "desconocido"
        error_type = error.get("type")

        raw_err_msg = error.get("msg", "")

        translated_field = field_dict.get(raw_filed, raw_filed)

        if "Value error, " in raw_err_msg:
            raw_err_msg = raw_err_msg.replace("Value error, ", "")

        # === ERROR TRANSLATION DICTIONARY ===
        if error_type == "string_pattern_mismatch":
            message = (
                f"El campo '{translated_field}' contiene caracteres no permitidos "
                "o formato inválido."
            )
        elif error_type == "string_too_short":
            message = f"El campo '{translated_field}' es demasiado corto."
        elif error_type == "string_too_long":
            message = (
                f"El campo '{translated_field}' excede el número máximo de caracteres permitidos."
            )
        elif error_type == "missing":
            message = f"El campo '{translated_field}' es obligatorio."
        elif raw_filed == "email" and error_type == "value_error":
            # catches errors in english languages thrown by email-validator library.
            message = f"El {translated_field} ingresado no tiene un formato válido."
        elif error_type == "value_error":
            # Catches clean (@Field_validator) exceptions.
            message = raw_err_msg
        else:
            message = f"Error en '{translated_field}': Revisar el formato ingresado."

        formated_errors.append(
            {
                "raw_field": raw_filed,  # For the client to understand what to paint red
                "message": message,  # For the human eye to read.
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detalle": formated_errors},
    )


# === GLOBAL DATABASE EXCEPTION HANDLER ===
@app.exception_handler(IntegrityError)
async def sqlalchemy_integrity_error_handler(request: Request, exc: IntegrityError):
    """Translates persistence integrity violations into a 409 Conflict response.

    Catches e.g. a race condition on a UNIQUE constraint and prevents a 500.
    """
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": (
                "Conflicto de datos: El registro que intenta procesar ya existe "
                "o la acción no está permitida."
            )
        },
    )


# === GLOBAL DOMAIN EXCEPTION HANDLER ===
# Single DRY handler translating every service-layer DomainError into its
# documented HTTP response. The HTTP status codes live exclusively here,
# keeping app/services/ free of transport semantics.
_DOMAIN_ERROR_STATUS: dict[type[DomainError], int] = {
    AuthorizationError: status.HTTP_403_FORBIDDEN,
    NotFoundError: status.HTTP_404_NOT_FOUND,
    AlreadyExistsError: status.HTTP_400_BAD_REQUEST,
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
    AccountNotActiveError: status.HTTP_403_FORBIDDEN,
    InvalidVerificationTokenError: status.HTTP_400_BAD_REQUEST,
    BusinessRuleViolationError: status.HTTP_400_BAD_REQUEST,
    StorageUnavailableError: status.HTTP_503_SERVICE_UNAVAILABLE,
    UnsupportedMediaTypeError: status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    InvalidImageUrlError: status.HTTP_400_BAD_REQUEST,
}


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    """Maps every domain-level failure to its documented HTTP response.

    Keeps transport semantics out of the service layer.

    Two documented special behaviors:
    - 401 responses advertise the Bearer scheme via WWW-Authenticate.
    - DomainError subtypes absent from the mapping table degrade to 500
      instead of leaking unhandled stack traces.

    Args:
        request (Request): The incoming HTTP request that raised the failure.
        exc (DomainError): The domain exception carrying the detail.

    Returns:
        JSONResponse: Serialized {"detail": ...} payload with the mapped status.
    """
    status_code = _DOMAIN_ERROR_STATUS.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    headers = (
        {"WWW-Authenticate": "Bearer"} if status_code == status.HTTP_401_UNAUTHORIZED else None
    )
    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.detail},
        headers=headers,
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(service.router, prefix="/servicios", tags=["Servicios Turísticos"])
app.include_router(audit.router, prefix="/auditoria", tags=["Auditoría"])


@app.get("/", tags=["Health Check"])
async def root():
    return {"status": "ok", "message": "Ecotur-ASOPRADO API (v0.2.0) está en línea"}
