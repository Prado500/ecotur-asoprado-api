README.md ENG sp 4 release


# Ecotur-ASOPRADO API - Backend Architecture (v0.2.0)

##  Project Context

This repository hosts the transactional backend for **Ecotur-ASOPRADO**, a web and mobile digital ecosystem developed as a degree project to diversify and manage the tourist offerings of the land adaptation district of Prado, Tolima. The architecture was designed under the **Clean Architecture** standard, prioritizing scalability, asynchronous performance, and information security.

###  Scope & Evolution: From v0.1.0 to v0.2.0

This major release consolidates the transition from the base MVP (Sprint 1) to a robust, enterprise-grade architecture (Sprint 4) encompassing Data Governance, Cloud Storage, and advanced Role-Based Access Control (RBAC).

* **HU-10 (Identity Verification):** Implementation of mandatory national ID (Cédula) validation for tourists. The system now enforces a Zero-Trust onboarding flow where accounts are created as `is_active=False`. Activation requires verification via a single-use ephemeral JWT dispatched asynchronously via email.
* **HU-11 (Data Governance & Soft Delete):** Eradicated physical `DELETE` statements from the database to maintain historical reservation integrity. Implemented a strict Soft Delete pattern (`is_active`, `deleted_at`) with dedicated REST operations for a Recycle Bin and hierarchical account recovery.
* **HU-12 (Multimedia Cloud CDN):** Transitioned from plaintext URL storage to an Asynchronous Media Staging architecture. The system now receives binary chunks (`multipart/form-data`) in an ephemeral Azure Blob container, returning staging URLs to the frontend. A concurrent I/O reconciliation algorithm executes "Copy & Delete" patterns to promote blobs to permanent storage via strict JSON contracts (`application/json`).


* **HU-13 (Transactional Robustness):** Enforced strict financial precision limits (`base_price` >= 40,000 COP) and integrated global exception handlers to translate database Integrity Errors (HTTP 409) and Pydantic validation errors (HTTP 422) into sanitized responses.
* **Audit Trail Ecosystem:** Engineered a JSONB-based audit log repository to silently intercept and persist structural or state mutations triggered by administrative personnel across all domain entities, preventing O(N) memory exhaustion via limit-offset pagination.
* **CI/CD Refactoring:** Decoupled pipelines to inject a Pytest Quality Gate requiring 100% success on PRs before enabling merges. Replaced Azure ARM deployments with webhook-based asynchronous triggers to bypass Entra ID tenant restrictions.

---

##  Architectural Decisions & Component Interrelation

The `v0.2.0` architecture strictly enforces the **Separation of Concerns (SoC)** through modern Python packaging (`pyproject.toml`) and Inversion of Control (IoC):

1. **Slim Controllers (`app/api/routers/`)**: Endpoints are decoupled from the database. They receive HTTP requests, parse tokens, and immediately delegate payloads to the Service layer.
2. **Business Logic Layer (`app/services/`)**: Validates complex domain rules. For instance, the `UserService` enforces a 3-tier Hybrid RBAC algorithm (Superadmin -> Admin -> Tourist) ensuring strict precedence policies for U+D operations.
3. **Data Access Layer (`app/repositories/`)**: The only layer containing SQLAlchemy 2.0 instructions. It shields the business logic from direct SQL dialects and handles ORM relationships.


4. **Asynchronous I/O Delegation (`app/core/`)**: External network egress (SMTP emails, Azure Blob Storage uploads) is dispatched concurrently via `asyncio.gather` and FastAPI `BackgroundTasks` to prevent blocking the main event loop.

---

##  Directory Structure (Clean Architecture)

```text
📦 ECOTUR-ASOPRADO
 ┣ 📂 .azure-pipelines/  # CI/CD flow definition (Pipeline as Code)
 ┣ 📂 alembic/           # Database version control and scripts
 ┣ 📂 app/               # Main application source code
 ┃ ┣ 📂 api/             # Routers (Slim Controllers) and Dependency Injection
 ┃ ┣ 📂 core/            # Global configs, security (JWT), storage clients, and emails
 ┃ ┣ 📂 db/              # Central metadata directory (SQLAlchemy 2.0 DeclarativeBase)
 ┃ ┣ 📂 models/          # Entities and relational mapping (ORM)
 ┃ ┣ 📂 repositories/    # Data Access Layer (Isolated SQL queries)
 ┃ ┣ 📂 schemas/         # Input/output validators and DTOs (Pydantic)
 ┃ ┣ 📂 services/        # Business Logic Layer and transactional rules
 ┃ ┗ 📜 main.py          # FastAPI application entry point with global exception handlers
 ┣ 📂 tests/             # Automated Pytest suite (Async Mocks, SQLite In-Memory)
 ┣ 📜 .python-version    # Strict project runtime declaration (3.11)
 ┣ 📜 alembic.ini        # Native migration engine config
 ┣ 📜 docker-compose.yml # Local services orchestration (API + DB)
 ┣ 📜 Dockerfile         # Container image build recipe
 ┣ 📜 pyproject.toml     # Modern dependency management and configuration (PEP 518)
 ┗ 📜 .env.example       # Secure environment variables template

```

---

##  Deployed Environments (CI/CD - Azure DevOps)

| Environment | Branch | API Base URL |
| --- | --- | --- |
| **Development (DEV)** | `develop` | `[https://api-ecoturasoprado-dev-f2aaejf9cdc0e3er.canadacentral-01.azurewebsites.net](https://api-ecoturasoprado-dev-f2aaejf9cdc0e3er.canadacentral-01.azurewebsites.net)`<br> |
| **Staging (STG)** | `staging` | `[https://api-ecoturasoprado-stg-gxb5bxcmcub3ftfx.canadacentral-01.azurewebsites.net](https://api-ecoturasoprado-stg-gxb5bxcmcub3ftfx.canadacentral-01.azurewebsites.net)`<br> |
| **Production (MAIN)** | `main` | `[https://api-ecoturasoprado-main-bucve5dfdfbnffgh.canadacentral-01.azurewebsites.net](https://api-ecoturasoprado-main-bucve5dfdfbnffgh.canadacentral-01.azurewebsites.net)`<br> |

---

##  Tech Stack

* **Language:** Python 3.11+


* **Framework:** FastAPI (Asynchronous)


* **ORM:** SQLAlchemy 2.0


* **Data Validation:** Pydantic V2


* **Migrations:** Alembic


* **Database:** PostgreSQL


* **Cloud Storage:** Azure Blob Storage SDK (`azure-storage-blob`)
* **Testing:** Pytest, pytest-asyncio, httpx, aiosqlite
* **Containers:** Docker & Docker Compose



---

##  Local Setup & Execution

**1. Clone the repository**

```bash
git clone https://github.com/Prado500/ecotur-asoprado-api
cd ecotur-asoprado-backend

```

**2. Environment Variables**
Create a `.env` file in the project root by copying the `.env.example` structure and assigning the local credentials.

**3. Run with Docker (Recommended)**

```bash
docker-compose up -d --build

```

Once up and running, initialize the database by executing the migrations:

```bash
docker-compose exec web alembic upgrade head

```

---

##  Main Endpoints and Payloads

###  Public Routes

* **`POST /usuarios/registro`**: Registration enforcing national ID (`cedula`) and triggering the asynchronous verification email.


* **`POST /usuarios/login`**: Returns HTTP 403 if the user is inactive or HTTP 401 for invalid credentials.
* **`GET /servicios/`**: Public catalog (automatically omits soft-deleted services via ORM filters).

**Payload Example (`/usuarios/registro`):**

```json
{
  "email": "mario.turista@rutadelarroz.com",
  "first_name": "Mario",
  "last_name": "Pacheco",
  "phone": "3111111111",
  "cedula": "1002345678",
  "password": "Ciscocisco123",
  "data_consent": true
}

```

###  Private Routes (Require Bearer Token)

* **`GET /usuarios/mi-perfil`**: Returns specific profile data (Authenticated Users).


* **`POST /upload-images/`**: Accepts `List[UploadFile]` up to 10 files and returns an array of ephemeral CDN URLs (Admins Only).
* **`POST /servicios/`**: Creates a package consuming the staging URLs returned by the endpoint above (Admins Only).


* **`GET /auditoria/`**: Retrieves paginated JSONB administrative mutation logs (Admins/Superadmins Only).
* **`GET /usuarios/admin/eliminados`**: Retrieves the directory of soft-deleted accounts (Admins/Superadmins Only).

**Payload Example (`/servicios/`):**

```json
{
  "name": "Ruta de la Cascada Prado",
  "description": "Detalle exhaustivo de la experiencia de ecoturismo...",
  "category": "recreacional",
  "base_price": 85000.00,
  "max_capacity": 15,
  "is_available": true,
  "image_urls": [
    "https://ecoturasopradocdn.blob.core.windows.net/temp-ecotur-images/uuid-1.jpg",
    "https://ecoturasopradocdn.blob.core.windows.net/temp-ecotur-images/uuid-2.jpg"
  ]
}

```

---

##  Security & Critical Notes

* **Data Serialization Warning:** When interacting with the `AuditLog` JSONB implementation, ensure that complex Pydantic types (like `Decimal` or `HttpUrl`) are strictly sanitized to standard Python primitives via `.model_dump(mode='json')` before persistence to prevent `StatementError` crashes.
* **RBAC Hierarchy:** Superadmin identities are dynamically obscured from standard admin queries. Standard admins are hard-blocked (HTTP 403) from soft-deleting or recovering equal or higher-tier accounts.
* **CDN I/O Mutability:** The backend handles physical Azure file promotions via an internal `resolve_url` wrapper concurrently. The frontend must only submit valid HTTP URLs to avoid transaction validation failures (HTTP 422).