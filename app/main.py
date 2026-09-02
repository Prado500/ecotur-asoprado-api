from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

from app.api.routers import user, service, audit

app = FastAPI(
    title="Ecotur-ASOPRADO API",
    description="API RESTful asíncrona para la gestión de paquetes turísticos",
    version="0.2.0",
)

# ===  GLOBAL PYDANTIC EXCEPTION HANDLER (UX FRIENDLY/ UserCreate) ===
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Catches Pydantic validation exceptions and translates them
    to a user-friendly format containing field names in spanish.
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
        "max_capacity": "capacidad máxima"
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
            message = f"El campo '{translated_field}' contiene caracteres no permitidos o formato inválido."
        elif error_type == "string_too_short":
            message = f"El campo '{translated_field}' es demasiado corto."
        elif error_type == "string_too_long":
            message = f"El campo '{translated_field}' excede el número máximo de caracteres permitidos."
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

        formated_errors.append({
            "raw_field": raw_filed, # For the client to understand what to paint red
            "message": message      # For the human eye to read.
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detalle": formated_errors},
    )

# === GLOBAL DATABASE EXCEPTION HANDLER ===
@app.exception_handler(IntegrityError)
async def sqlalchemy_integrity_error_handler(request: Request, exc: IntegrityError):
    """
    Catches any integrity transgression at the persistence layer (e.g. race condition set UNIQUE)
    and prevents 500 error obtention by returning a 409 Conflict response instead.
    """
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": "Conflicto de datos: El registro que intenta procesar ya existe o la acción no está permitida."
        },
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