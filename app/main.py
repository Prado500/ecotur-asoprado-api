from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

from app.api.routers import user, service

app = FastAPI(
    title="Ecotur-ASOPRADO API",
    description="API RESTful asíncrona para la gestión de paquetes turísticos",
    version="0.1.0",
)

# === MANEJADOR GLOBAL DE EXCEPCIONES DE PYDANTIC (UX FRIENDLY/ UserCreate) ===
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Atrapa los errores de validación de Pydantic y los traduce a un formato amigable
    para el Frontend, aplicando nombres de campos en español.
    """
    errores_formateados = []

    # Diccionario para traducir variables técnicas a lenguaje humano
    DICCIONARIO_CAMPOS = {
        "first_name": "nombres",
        "last_name": "apellidos",
        "phone": "teléfono",
        "email": "correo electrónico",
        "password": "contraseña",
        "data_consent": "aceptación de términos",
        "name": "nombre del paquete",
        "base_price": "precio base",
        "max_capacity": "capacidad máxima"
    }

    for error in exc.errors():

        campo_tecnico = error.get("loc")[-1] if error.get("loc") else "desconocido"
        tipo_error = error.get("type")

        mensaje_original = error.get("msg", "")


        campo_humano = DICCIONARIO_CAMPOS.get(campo_tecnico, campo_tecnico)


        if "Value error, " in mensaje_original:
            mensaje_original = mensaje_original.replace("Value error, ", "")

        # === DICCIONARIO DE TRADUCCIÓN DE ERRORES ===
        if tipo_error == "string_pattern_mismatch":
            mensaje = f"El campo '{campo_humano}' contiene caracteres no permitidos o formato inválido."
        elif tipo_error == "string_too_short":
            mensaje = f"El campo '{campo_humano}' es demasiado corto."
        elif tipo_error == "string_too_long":
            mensaje = f"El campo '{campo_humano}' excede el número máximo de caracteres permitidos."
        elif tipo_error == "missing":
            mensaje = f"El campo '{campo_humano}' es obligatorio."
        elif campo_tecnico == "email" and tipo_error == "value_error":
            # Atrapa los errores en inglés de la librería email-validator
            mensaje = f"El {campo_humano} ingresado no tiene un formato válido."
        elif tipo_error == "value_error":
            # Atrapa validaciones (@field_validator) limpias
            mensaje = mensaje_original
        else:
            mensaje = f"Error en '{campo_humano}': Revisar el formato ingresado."

        errores_formateados.append({
            "campo": campo_tecnico, # Para que el Frontend sepa qué input pintar de rojo
            "mensaje": mensaje      # Para que el Humano lo lea
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detalle": errores_formateados},
    )

# === MANEJADOR GLOBAL DE EXCEPCIONES DE BASE DE DATOS ===
@app.exception_handler(IntegrityError)
async def sqlalchemy_integrity_error_handler(request: Request, exc: IntegrityError):
    """
    Atrapa cualquier violación de integridad en la BD (ej. Condición de carrera en UNIQUE)
    y previene un Error 500, retornando un 409 Conflict limpio al cliente.
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

@app.get("/", tags=["Health Check"])
async def root():
    return {"status": "ok", "message": "Ecotur-ASOPRADO API (v0.2.0) está en línea"}