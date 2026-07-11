
---
# Ecotur-ASOPRADO API - Backend Architecture (v0.1.1)

---
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)
![Azure DevOps](https://img.shields.io/badge/Azure_DevOps-0078D7?style=for-the-badge&logo=azuredevops)

##  Project Context

This repository hosts the transactional backend for **Ecotur-ASOPRADO**, a web and mobile digital ecosystem developed as a degree project to diversify and manage the tourist offerings of the land adaptation district of Prado, Tolima.

The architecture was designed under the **Clean Architecture** standard, prioritizing scalability, asynchronous performance, and information security.

### Sprint 4 Scope: U+D Operations with Soft Delete, Governance, Cloud Storage for images, and Wompi API POC (In progress)
This sprint aims to implement the update and soft delete (U+D) operations for User and TouristService, strengthen data governance, prepare the infrastructure for cloud storage, and investigate financial integrations.
* **Technical Enabler (v0.1.1):** Deep architectural refactoring towards *Clean Architecture* (Separation into Services and Repositories layers) to mitigate technical debt.
* **HU-10 & HU-11:** Operations implementation (U+D) with state mutation via **Soft Delete** and Data Governance. Implementation of national ID (Cédula) verification.
* **HU-12:** Multimedia Cloud Infrastructure. Transitioning from plaintext URL storage to binary file uploads (`multipart/form-data`) and integration with CDN/Object Storage.
* **Spike (Research):** Proof of Concept (POC) for transactional integration and Webhooks with Bancolombia's Wompi API.

### Sprint 1 Scope: Core MVP (v0.1.0)
This release contains the Minimum Viable Product (MVP) consolidated in the first sprint:
* **Technical Enabler  (v0.1.0):** Containerization, creation, and configuration of cloud infrastructure (Azure), and deployment under automated CI/CD pipelines across 3 cloud environments (Develop, Staging, and Main).
* **HU-01:** Tourist registration (with password hashing).
* **HU-02:** Login (JWT Authentication).
* **HU-03:** Visualization of tourist packages.
* **HU-08:** Creation of tourist packages.

---

##  Directory Structure (Clean Architecture)

The project separates responsibilities into strict layers to ensure low coupling and high cohesion:

```text
📦 ECOTUR-ASOPRADO
 ┣ 📂 .azure-pipelines/  # CI/CD flow definition (Pipeline as Code)
 ┣ 📂 alembic/           # Database version control and scripts
 ┣ 📂 app/               # Main application source code
 ┃ ┣ 📂 api/             # Routers (Slim Controllers) and Dependency Injection
 ┃ ┣ 📂 core/            # Global configs, security (JWT), and environment variables
 ┃ ┣ 📂 db/              # Central metadata directory (SQLAlchemy 2.0)
 ┃ ┣ 📂 models/          # Entities and relational mapping (ORM)
 ┃ ┣ 📂 repositories/    # Data Access Layer (Isolated SQL queries)
 ┃ ┣ 📂 schemas/         # Input/output validators and DTOs (Pydantic)
 ┃ ┣ 📂 services/        # Business Logic Layer and transactional rules
 ┃ ┗ 📜 main.py          # FastAPI application entry point
 ┣ 📂 tests/             # Automated testing suite (Pytest)
 ┣ 📜 .python-version    # Strict project runtime declaration (3.11)
 ┣ 📜 alembic.ini        # Native migration engine config
 ┣ 📜 docker-compose.yml # Local services orchestration (API + DB)
 ┣ 📜 Dockerfile         # Container image build recipe
 ┣ 📜 pyproject.toml     # Modern dependency management and configuration (PEP 518)
 ┗ 📜 .env.example       # Secure environment variables template
```
---
##  System Overview

Transactional system developed with FastAPI (asynchronous mode), relational persistence in PostgreSQL, and security via JWT authentication. Deployment is fully automated using Pipeline as Code strategies in Azure DevOps.

### **Main Features**

**Security:** JWT Authentication and Role-Based Access Control (Tourist / Admin).

**Diverse and Biocultural Catalog:** Management of tourist packages with support for multiple images.

**Relational Database:** Automated migrations and secure object-relational mapping.

**Auto-Documentation:** Interactive OpenAPI specification available at the /docs route.

**Continuous Integration:** Robust CI/CD orchestrated with Microsoft Azure.


---
## Deployed Environments (CI/CD - Azure DevOps)

The pipeline automatically promotes code to specific environments based on the Git branch:

| Environment | Branch | API Base URL |
| :--- | :--- | :--- |
| **Development (DEV)** | `develop` | `https://api-ecoturasoprado-dev-f2aaejf9cdc0e3er.canadacentral-01.azurewebsites.net` |
| **Staging (STG)** | `staging` | `https://api-ecoturasoprado-stg-gxb5bxcmcub3ftfx.canadacentral-01.azurewebsites.net` |
| **Production (MAIN)** | `main` | `https://api-ecoturasoprado-main-bucve5dfdfbnffgh.canadacentral-01.azurewebsites.net` |

---


## Tech Stack

**Language:** Python 3.11+

**Framework:** FastAPI (Asynchronous)

**ORM:** SQLAlchemy

**Data Validation:** Pydantic

**Migrations:** Alembic

**Database:** PostgreSQL

**Containers:** Docker & Docker Compose

---
## Local Setup & Execution

**1. Clone the repository**

```Code snippet
git clone https://github.com/Prado500/ecotur-asoprado-api

cd ecotur-asoprado-backend
```

**2. Environment Variables**

Create a .env file in the project root by copying the .env.example structure and assigning the credentials provided by the system administrator.

**3. Run with Docker (Recommended)**

```Code snippe
tdocker-compose up -d --build
```
Once up and running, initialize the database by executing the migrations:

```Code snippet
docker-compose exec web alembic upgrade head
```
API Base URL: http://localhost:8000

Interactive Documentation (Swagger): http://localhost:8000/docs

---

##  Main Endpoints and Test Templates (JSON)
Below are the main MVP routes and the required payloads for successful testing.

### Public (No token required)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/usuarios/registro` | `Registration of new users with password hashing at the backend layer  (HU-01)` |
| **POST** | `/usuarios/login` | `Login and obtain a JWT token (HU-02)` |
| **GET** | `/servicios/` | `Public catalog of all tourist services available (HU-03)` |

### JSON Example for /usuarios/registro :


```Code snippet
{
  "email": "mario.turista@rutadelarroz.com",
  "first_name": "Mario",
  "last_name": "Pacheco",
  "phone": "3111111111",
  "password": "ciscocisco",
  "data_consent": true
}
```
### JSON Example for /usuarios/login: (Upon successful execution, it will return the Bearer Token required for private routes).

```Code snippet
{
    "email": "mario.turista@rutadelarroz.com",
    "password": "ciscocisco"
}
```
## Private (Require Bearer Token in the Header)

| Method | Endpoint | Description | Access Level| 
| :--- | :--- | :--- | :--- |
| **GET** | `/usuarios/mi-perfil` | Allows a user to view his/her own specific profile containing generic user data |Authenticated Users Only |
| **POST** | `/servicios/` | Allows an admin to create a tourist service | Admins Only | 



**Note on Private GETs:** The /usuarios/mi-perfil endpoint does not require a body in the JSON request. It only requires injecting the Bearer Token into the authorization headers (Authorization: Bearer ).

### JSON Example for /servicios/ (Package Creation - Admin Only):

**⚠️ Important note on Package Creation (/servicios/):** The category field is strictly validated by a Pydantic Enum. The only allowed values in the request body are: "agroturismo", "recreacional", "metalmecanico", or "otro".

```Code snippet
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
---


## Security
* **Authentication:** JSON Web Tokens (JWT) injected via Authorization header (Bearer ).

* **Access Control (RBAC):** Granular endpoint-level restrictions depending on the user's role in the database.

* **Cryptography:** Passwords protected by one-way hashing algorithms (Bcrypt).

---
