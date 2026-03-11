from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Ecotur-ASOPRADO API",
    description="API RESTful asíncrona para la gestión de servicios turísticos de ASOPRADO.",
    version="1.0.0",
)

# Configuración básica de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
async def read_root():
    return {"status": "ok", "message": "Ecotur-ASOPRADO API (Iteración 1) está en línea"}