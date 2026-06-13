from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError

from app.api.routers import user, service

app = FastAPI(
    title="Ecotur-ASOPRADO API",
    description="API RESTful asíncrona para la gestión de paquetes turísticos",
    version="0.1.0",
)

# === MANEJADOR GLOBAL DE EXCEPCIONES DE BASE DE DATOS ===
@app.exception_handler(IntegrityError)
async def sqlalchemy_integrity_error_handler(request: Request, exc: IntegrityError):
    """
    Atrapa cualquier violación de integridad en la BD (ej. Unique constraints)
    y previene un Error 500, retornando un 409 Conflict limpio al cliente.
    """
    # Se podría hacer un parseo del exc.orig para saber exactamente qué campo falló,
    # pero por seguridad se decide devolver un mensaje genérico.
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": "Conflicto de datos: El registro que intenta crear ya existe o no es autorizado por la base de datos (problema de integridad)."
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
    return {"status": "ok", "message": "Ecotur-ASOPRADO API (Iteración 1) está en línea"}