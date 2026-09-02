README.md ESP sp 4 release

#  Ecotur-ASOPRADO API - Arquitectura Backend (v0.2.0)

##  Contexto del Proyecto

Este repositorio aloja el backend transaccional para **Ecotur-ASOPRADO**, un ecosistema digital web y móvil desarrollado como trabajo de grado para diversificar y gestionar la oferta turística del distrito de adecuación de tierras de Prado, Tolima. La arquitectura fue diseñada bajo el estándar de **Clean Architecture** (Arquitectura Limpia), priorizando la escalabilidad, el rendimiento asíncrono y la seguridad de la información.

###  Alcance y Evolución: De v0.1.0 a v0.2.0

Este *release* mayor consolida la transición desde el MVP base (Sprint 1) hacia una arquitectura robusta y de grado empresarial (Sprint 4) que abarca la Gobernanza de Datos, Almacenamiento en la Nube (Cloud Storage) y un Control de Acceso Basado en Roles (RBAC) avanzado.

* **HU-10 (Verificación de Identidad):** Implementación de validación obligatoria de Cédula de Ciudadanía para turistas. El sistema ahora impone un flujo de *onboarding* Zero-Trust (Cero Confianza) donde las cuentas nacen por defecto con `is_active=False`. La activación requiere verificación a través de un JWT efímero de un solo uso despachado asíncronamente vía correo electrónico.
* **HU-11 (Gobernanza de Datos y Borrado Lógico):** Erradicación de sentencias físicas `DELETE` de la base de datos para mantener la integridad histórica de las reservas. Se implementó un patrón estricto de Borrado Lógico (Soft Delete) mediante los campos `is_active` y `deleted_at`, junto con operaciones REST dedicadas para una Papelera de Reciclaje y recuperación jerárquica de cuentas.
* **HU-12 (CDN Cloud Multimedia):** Transición del almacenamiento de URLs en texto plano a una arquitectura de *Asynchronous Media Staging* (Almacenamiento Temporal de Medios Asíncrono). El sistema ahora recibe fragmentos binarios (`multipart/form-data`) en un contenedor efímero de Azure Blob Storage, devolviendo URLs temporales al frontend. Un algoritmo de reconciliación de I/O concurrente ejecuta patrones de "Copiar y Borrar" (Copy & Delete) para promover los *blobs* al almacenamiento permanente mediante contratos JSON estrictos (`application/json`).


* **HU-13 (Robustez Transaccional):** Imposición de límites estrictos de precisión financiera (`base_price` >= 40.000 COP) e integración de manejadores de excepciones globales para traducir errores de integridad de base de datos (HTTP 409) y de validación de Pydantic (HTTP 422) en respuestas sanitizadas y orientadas a la UX.
* **Ecosistema de Auditoría (Audit Trail):** Ingeniería de un repositorio de logs de auditoría basado en JSONB para interceptar y persistir silenciosamente mutaciones estructurales o de estado desencadenadas por el personal administrativo sobre todas las entidades del dominio, previniendo el agotamiento de memoria O(N) mediante paginación limit-offset.
* **Refactorización CI/CD:** Desacoplamiento de los pipelines para inyectar una Compuerta de Calidad (Quality Gate) con Pytest que exige 100% de éxito en los Pull Requests antes de habilitar las fusiones. Reemplazo de los despliegues de Azure ARM por disparadores asíncronos basados en webhooks nativos para evadir las restricciones de *tenant* de Entra ID.

---

## Decisiones Arquitectónicas e Interrelación de Componentes

La arquitectura `v0.2.0` impone estrictamente la **Separación de Responsabilidades (SoC)** a través del empaquetado moderno de Python (`pyproject.toml`) y la Inversión de Control (IoC):

1. **Slim Controllers (`app/api/routers/`)**: Los enrutadores están totalmente desacoplados de la base de datos. Reciben las peticiones HTTP, parsean los tokens y delegan inmediatamente los *payloads* a la capa de Servicios.
2. **Capa de Lógica de Negocio (`app/services/`)**: Centraliza y valida las reglas de dominio complejas. Por ejemplo, el `UserService` aplica un algoritmo RBAC Híbrido de 3 niveles (Superadmin -> Admin -> Turista) garantizando políticas de precedencia estrictas para operaciones de actualización y borrado (U+D).
3. **Capa de Acceso a Datos (`app/repositories/`)**: La única capa que contiene instrucciones de SQLAlchemy 2.0. Aísla la lógica de negocio de los dialectos SQL directos y maneja las relaciones del ORM.


4. **Delegación de I/O Asíncrono (`app/core/`)**: La salida de red externa (correos SMTP, subidas a Azure Blob Storage) se despacha concurrentemente mediante `asyncio.gather` y `BackgroundTasks` de FastAPI para evitar bloquear el *event loop* principal.

---

## Estructura de Directorios (Clean Architecture)

```text
📦 ECOTUR-ASOPRADO
 ┣ 📂 .azure-pipelines/  # Definición de flujos CI/CD (Pipeline as Code)
 ┣ 📂 alembic/           # Scripts y control de versiones de la base de datos
 ┣ 📂 app/               # Código fuente principal de la aplicación
 ┃ ┣ 📂 api/             # Enrutadores (Slim Controllers) e Inyección de Dependencias
 ┃ ┣ 📂 core/            # Configuraciones globales, seguridad (JWT), clientes de almacenamiento y correos
 ┃ ┣ 📂 db/              # Directorio central de metadatos (SQLAlchemy 2.0 DeclarativeBase)
 ┃ ┣ 📂 models/          # Entidades y mapeo relacional (ORM)
 ┃ ┣ 📂 repositories/    # Capa de Acceso a Datos (Consultas SQL aisladas)
 ┃ ┣ 📂 schemas/         # Validadores de entrada/salida y DTOs (Pydantic)
 ┃ ┣ 📂 services/        # Capa de Lógica de Negocio y reglas transaccionales
 ┃ ┗ 📜 main.py          # Punto de entrada de FastAPI con manejadores de excepciones globales
 ┣ 📂 tests/             # Batería de pruebas Pytest (Mocks Asíncronos, SQLite en memoria)
 ┣ 📜 .python-version    # Declaración estricta del runtime del proyecto (3.11)
 ┣ 📜 alembic.ini        # Configuración nativa del motor de migraciones
 ┣ 📜 docker-compose.yml # Orquestación de servicios locales (API + DB)
 ┣ 📜 Dockerfile         # Receta de construcción de la imagen del contenedor
 ┣ 📜 pyproject.toml     # Gestión moderna de dependencias y configuración (PEP 518)
 ┗ 📜 .env.example       # Plantilla de variables de entorno seguras

```

---

## Entornos Desplegados (CI/CD - Azure DevOps)

| Entorno | Rama | URL Base de la API |
| --- | --- | --- |
| **Desarrollo (DEV)** | `develop` | `[https://api-ecoturasoprado-dev-f2aaejf9cdc0e3er.canadacentral-01.azurewebsites.net](https://api-ecoturasoprado-dev-f2aaejf9cdc0e3er.canadacentral-01.azurewebsites.net)`<br> |
| **Pruebas (STG)** | `staging` | `[https://api-ecoturasoprado-stg-gxb5bxcmcub3ftfx.canadacentral-01.azurewebsites.net](https://api-ecoturasoprado-stg-gxb5bxcmcub3ftfx.canadacentral-01.azurewebsites.net)`<br> |
| **Producción (MAIN)** | `main` | `[https://api-ecoturasoprado-main-bucve5dfdfbnffgh.canadacentral-01.azurewebsites.net](https://api-ecoturasoprado-main-bucve5dfdfbnffgh.canadacentral-01.azurewebsites.net)`<br> |

---

## Stack Tecnológico

* **Lenguaje:** Python 3.11+


* **Framework:** FastAPI (Asíncrono)


* **ORM:** SQLAlchemy 2.0


* **Validación de Datos:** Pydantic V2


* **Migraciones:** Alembic


* **Base de Datos:** PostgreSQL


* **Almacenamiento Cloud:** Azure Blob Storage SDK (`azure-storage-blob`)
* **Testing/QA:** Pytest, pytest-asyncio, httpx, aiosqlite
* **Contenedores:** Docker & Docker Compose



---

## Instalación y Ejecución Local

**1. Clonar el repositorio**

```bash
git clone https://github.com/Prado500/ecotur-asoprado-api
cd ecotur-asoprado-backend

```

**2. Variables de Entorno**
Cree un archivo `.env` en la raíz del proyecto copiando la estructura de `.env.example` y asigne las credenciales locales.

**3. Ejecutar con Docker (Recomendado)**

```bash
docker-compose up -d --build

```

Una vez levantado, inicialice la base de datos ejecutando las migraciones:

```bash
docker-compose exec web alembic upgrade head

```

---

## Endpoints Principales y Plantillas de Prueba (JSON)

### Rutas Públicas (No requieren token)

* **`POST /usuarios/registro`**: Registro de usuarios exigiendo documento de identidad (`cedula`) y desencadenando el correo electrónico asíncrono de verificación.


* **`POST /usuarios/login`**: Retorna HTTP 403 si el usuario está inactivo, o HTTP 401 si las credenciales son inválidas.
* **`GET /servicios/`**: Catálogo público (omite automáticamente los servicios borrados lógicamente mediante filtros del ORM).

**Ejemplo de Payload (`/usuarios/registro`):**

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

### Rutas Privadas (Requieren Token Bearer en el Header)

* **`GET /usuarios/mi-perfil`**: Retorna los datos específicos del perfil (Solo Usuarios Autenticados).


* **`POST /upload-images/`**: Acepta `List[UploadFile]` hasta un límite de 10 archivos y devuelve un arreglo de URLs efímeras del CDN (Solo Administradores).
* **`POST /servicios/`**: Crea un paquete turístico consumiendo las URLs temporales retornadas por el endpoint anterior (Solo Administradores).


* **`GET /auditoria/`**: Recupera el historial JSONB paginado de mutaciones administrativas (Solo Admins/Superadmins).
* **`GET /usuarios/admin/eliminados`**: Recupera el directorio de la Papelera de Reciclaje de cuentas borradas (Solo Admins/Superadmins).

**Ejemplo de Payload (`/servicios/`):**

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

## Seguridad y Notas Críticas

* **Advertencia de Serialización de Datos:** Al interactuar con la implementación JSONB del `AuditLog`, asegúrese de que los tipos complejos de Pydantic (como `Decimal` o `HttpUrl`) sean estrictamente sanitizados a primitivas estándar de Python mediante `.model_dump(mode='json')` antes de la persistencia para prevenir caídas fatales por `StatementError`.
* **Jerarquía RBAC:** Las identidades de la capa Superadmin están dinámicamente ofuscadas de las consultas de los administradores estándar. Los administradores estándar están bloqueados a nivel de backend (HTTP 403) para aplicar borrado lógico o recuperar cuentas de un nivel igual o superior.
* **Mutabilidad I/O del CDN:** El backend maneja las promociones físicas de archivos en Azure de forma concurrente mediante el *wrapper* interno `resolve_url`. El frontend debe enviar únicamente URLs HTTP válidas para evitar fallos de validación transaccional (HTTP 422).