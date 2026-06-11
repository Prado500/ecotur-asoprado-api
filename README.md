# 🍃 Ecotur-ASOPRADO API - Backend Architecture (v0.1.0)

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)
![Azure DevOps](https://img.shields.io/badge/Azure_DevOps-0078D7?style=for-the-badge&logo=azuredevops)

## 📋 Contexto del Proyecto

Este repositorio aloja el backend transaccional para **Ecotur-ASOPRADO**, un ecosistema digital web y móvil desarrollado como trabajo de grado para diversificar y gestionar la oferta turística del distrito de adecuación de tierras de Prado, Tolima. 

La arquitectura fue diseñada bajo el estándar de **Clean Architecture**, priorizando la escalabilidad, el rendimiento asíncrono y la seguridad de la información.

### 🎯 Alcance del Sprint 1 (MVP Base)
Esta versión contiene el Producto Mínimo Viable (MVP) consolidado en el primer sprint, satisfaciendo las siguientes Historias de Usuario:
* **HU-01:** Registro de turistas (con hashing de contraseñas).
* **HU-02:** Inicio de sesión (Autenticación JWT).
* **HU-03:** Visualización de paquetes turísticos.
* **HU-08:** Creación de paquetes turísticos.
* **Habilitador Técnico:** Endpoint de perfil para validación de Acceso Basado en Roles (RBAC).

---

## 📁 Estructura de Directorios (Clean Architecture)

El proyecto separa las responsabilidades en capas estrictas para garantizar un bajo acoplamiento y alta cohesión:

```text
📦 ECOTUR-ASOPRADO
 ┣ 📂 .azure-pipelines/  # Definición de flujos CI/CD (Pipeline as Code)
 ┣ 📂 alembic/           # Scripts y control de versiones de la base de datos
 ┣ 📂 app/               # Código fuente principal de la aplicación
 ┃ ┣ 📂 api/             # Enrutadores (Endpoints) y dependencias de inyección
 ┃ ┣ 📂 core/            # Configuraciones globales, seguridad (JWT) y variables de entorno
 ┃ ┣ 📂 crud/            # Lógica de persistencia y operaciones transaccionales
 ┃ ┣ 📂 db/              # Configuración de sesión y conexión con PostgreSQL
 ┃ ┣ 📂 models/          # Entidades y mapeo relacional (SQLAlchemy)
 ┃ ┣ 📂 schemas/         # Validadores de entrada/salida y DTOs (Pydantic)
 ┃ ┗ 📜 main.py          # Punto de entrada de la aplicación FastAPI
 ┣ 📂 tests/             # Batería de pruebas (QA y validaciones de API)
 ┣ 📜 alembic.ini        # Configuración del motor de migraciones
 ┣ 📜 docker-compose.yml # Orquestación de servicios locales (API + DB)
 ┣ 📜 Dockerfile         # Receta de construcción de la imagen del contenedor
 ┣ 📜 requirements.txt   # Dependencias de Python
 ┗ 📜 .env.example       # Plantilla de variables de entorno seguras
```

## 🚀 Resumen del Sistema
Sistema transaccional desarrollado con FastAPI (modo asíncrono), persistencia relacional en PostgreSQL, y seguridad mediante autenticación JWT. El despliegue está completamente automatizado mediante estrategias de Pipeline as Code en Azure DevOps.

### **Características Principales**

**Seguridad:** Autenticación JWT y control de acceso basado en roles (Turista / Admin).

**Catálogo Diverso y Biocultural:** Gestión de paquetes turísticos con soporte para múltiples imágenes.

**Base de Datos Relacional:** Migraciones automatizadas y mapeo objeto-relacional seguro.

**Auto-Documentación:** Especificación OpenAPI interactiva disponible en la ruta /docs.

**Integración Continua:** CI/CD robusto orquestado con Microsoft Azure.

## ☁️ Entornos Desplegados (CI/CD - Azure DevOps)
El pipeline promueve automáticamente el código a entornos específicos basándose en la rama de Git:

| Entorno | Rama | URL Base de la API |
| :--- | :--- | :--- |
| **Desarrollo (DEV)** | `develop` | `https://api-ecoturasoprado-dev-f2aaejf9cdc0e3er.canadacentral-01.azurewebsites.net` |
| **Pruebas (STG)** | `staging` | `https://api-ecoturasoprado-stg-gxb5bxcmcub3ftfx.canadacentral-01.azurewebsites.net` |
| **Producción (MAIN)** | `main` | `https://api-ecoturasoprado-main-bucve5dfdfbnffgh.canadacentral-01.azurewebsites.net` |

## 🛠️ Stack Tecnológico

**Lenguaje:** Python 3.11+

**Framework:** FastAPI (Asíncrono)

**ORM:** SQLAlchemy

**Validación de Datos:** Pydantic

**Migraciones:** Alembic

**Base de Datos:** PostgreSQL

**Contenedores:** Docker & Docker Compose

## ⚙️ Instalación y Ejecución Local

**1. Clonar el repositorio**
```Bash
git clone https://github.com/Prado500/ecotur-asoprado-api
cd ecotur-asoprado-backend
```
**2. Variables de Entorno**

Cree un archivo .env en la raíz del proyecto copiando la estructura de .env.example y asignando las credenciales proporcionadas por el administrador del sistema.


**3. Ejecutar con Docker (Recomendado)**

```Bash
docker-compose up -d --build
```


Una vez levantado, inicialice la base de datos ejecutando las migraciones:


```Bash
docker-compose exec web alembic upgrade head
```

API Base: http://localhost:8000


Documentación Interactiva (Swagger): http://localhost:8000/docs

## 📚 Endpoints Principales y Plantillas de Prueba (JSON)

A continuación se detallan las rutas principales del MVP y los payloads requeridos para realizar pruebas exitosas.

### 🔓 Públicos (No requieren token)

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| **POST** | `/usuarios/registro` | `Registro de nuevos turistas con contraseña hasheada desde el backend (HU-01)` |
| **POST** | `/usuarios/login` | `Inicio de sesión para obtención de Token JWT (HU-02)` |
| **GET** | `/servicios/` | `Ver catálogo general de paquetes turísticos (HU-03)` |

### **Ejemplo JSON para** `/usuarios/registro` :

```JSON
{
  "email": "mario.turista@rutadelarroz.com",
  "first_name": "Mario",
  "last_name": "Pacheco",
  "phone": "3111111111",
  "password": "ciscocisco",
  "data_consent": true
}
```
### **Ejemplo JSON para** `/usuarios/login`:

(Al ejecutar con éxito, retornará el Token Bearer necesario para rutas privadas).

```JSON
{
    "email": "mario.turista@rutadelarroz.com",
    "password": "ciscocisco"
}
```

## 🔒 Privados (Requieren Token Bearer en el Header)

| Método | Endpoint | Descripción | Nivel de Acceso| Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **GET** | `/usuarios/mi-perfil` | `Ver catálogo general de paquetes turísticos (HU-03)` |Usuario Autenticado| Ver detalles del perfil del usuario actual. |
| **POST** | `/servicios/` | `Ver catálogo general de paquetes turísticos (HU-03)` | Administrador | Crear nuevo paquete turístico (HU-08). |

**Nota sobre GETs Privados:** El endpoint `/usuarios/mi-perfil` no requiere cuerpo (body) en la petición JSON. Únicamente requiere inyectar el Token Bearer en las cabeceras de autorización (Authorization: Bearer `<token>`).


### Ejemplo JSON para `/servicios/` (Creación de Paquete - Solo Admin):

**⚠️ Nota importante sobre la Creación de Paquetes (`/servicios/`):** El campo category está estrictamente validado por un `Enum` de Pydantic. Los únicos valores permitidos en el cuerpo de la petición son: `"agroturismo"`, `"recreacional"`, `"metalmecanico"`, u `"otro"`.

```JSON
{
  "name": "TEST",
  "description": "ESTE ES UN PAQUETE DE PRUEBA",
  "category": "metalmecanico",
  "base_price": 85000.00,
  "max_capacity": 20,
  "is_available": true,
  "image_urls": [
    "[https://www.ndstudies.gov/energy/level2/files/level2/img/module04/iStock_000000730824Medium_hoover_dam_turbines-optimized.jpg](https://www.ndstudies.gov/energy/level2/files/level2/img/module04/iStock_000000730824Medium_hoover_dam_turbines-optimized.jpg)",
    "[https://s3.wasabisys.com/assets.elcronista.co/assets/media/monitoreo-permanente-a-represa-de-prado-realizan-autoridades.jpg](https://s3.wasabisys.com/assets.elcronista.co/assets/media/monitoreo-permanente-a-represa-de-prado-realizan-autoridades.jpg)"
  ]
}
```

## 🔐 Seguridad

**Autenticación:** JSON Web Tokens (JWT) inyectados vía cabecera de Autorización (Bearer <token>).

**Control de Acceso (RBAC):** Restricciones granulares a nivel de endpoint dependiendo del rol del usuario en la base de datos.

**Criptografía:** Contraseñas protegidas mediante algoritmos de hashing unidireccional (Bcrypt).



