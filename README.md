# 🍃 Ecotur-ASOPRADO API

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)

Repositorio oficial del *Backend* para el ecosistema digital del distrito de adecuación de tierras (ASOPRADO).

## Arquitectura
Este proyecto implementa **Clean Architecture** y principios SOLID, separando las responsabilidades en capas:
* `api/`: Enrutadores y dependencias.
* `core/`: Configuraciones de seguridad (JWT) y variables de entorno.
* `models/`: Entidades de base de datos (SQLAlchemy).
* `schemas/`: DTOs y validación de datos (Pydantic).
* `crud/`: Lógica de persistencia de datos.