# Verificación — S1: Modelos en estilo SQLAlchemy 1.x (`Column`) sobre base 2.0

**Veredicto:** confirmada
**Fuente del ítem:** docs/backlog.md (§A2, fila `S1`, l.82) + informe `docs/archive/auditorias/Auditoría Ecotur-ASOPRADO.html` §07 "Sintaxis desactualizada", tarjeta `S1` (l.757–790) y fase 7 del plan de remediación (l.1117–1120)
**Fecha:** 2026-11-03

## Qué describe el ítem
Los modelos ORM declaran columnas con `Column(...)` (estilo 1.x) aunque `Base` ya hereda de `DeclarativeBase`
(2.0). La documentación oficial dice que `mapped_column()` sustituye a `Column()` y que `Mapped[]` da tipado real.
El informe lo califica de modernización y no de defecto, pero señala el beneficio concreto: con `Mapped[]`,
`user.role` tiene tipo conocido y mypy puede detectar errores como el de B3. El backlog midió el 24 oct
**33** `Column(` y **0** `mapped_column`; el bloque asignado es `B-S1` (PLAN: "mypy cae a casi cero").

## Evidencia en el código
Hoy hay **33** `Column(`, **0** `mapped_column`, **0** `Mapped[` en `app/`. Los números coinciden con los del backlog.

- `app/db/database.py:4,27`: la base ya es 2.0: `from sqlalchemy.orm import DeclarativeBase` · `class Base(DeclarativeBase):`
- `app/models/user.py:2`: `from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum`
- `app/models/user.py:33-44`: **12** `Column(` (`id`, `cedula`, `email`, `password_hash`, `first_name`, `last_name`,
  `phone`, `role`, `data_consent`, `is_active`, `created_at`, `deleted_at`).
  Ej. l.40: `role = Column(Enum(UserRole, name="user_role"), nullable=False, default=UserRole.tourist)`
- `app/models/service.py:2`: `from sqlalchemy import Column, String, Integer, Numeric, Text, Boolean, DateTime, Enum, ForeignKey`
- `app/models/service.py:18-26`: **9** `Column(` en `TouristService` (`id` … `deleted_at`).
  Ej. l.21: `category = Column(Enum(ServiceCategory), nullable=False, default=ServiceCategory.otro)`
- `app/models/service.py:28`: `images = relationship("ServiceImage", back_populates="service", cascade="all, delete-orphan")` (sin `Mapped[list[...]]`)
- `app/models/service.py:34-40`: **5** `Column(` en `ServiceImage` (`id`, `service_id` con FK `ondelete="CASCADE"`, `image_url`, `is_primary`, `created_at`)
- `app/models/service.py:42`: `service = relationship("TouristService", back_populates="images")` (sin `Mapped[...]`)
- `app/models/audit.py:2`: `from sqlalchemy import Column, Integer, String, DateTime, Enum, JSON`
- `app/models/audit.py:28-44`: **7** `Column(` en `AuditLog`. Ej. l.36: `action = Column(Enum(AuditAction, name="audit_action_enum"), nullable=False)`;
  l.39: `changes = Column(JSON().with_variant(JSONB, "postgresql"), nullable=True)`

Total: 12 + 9 + 5 + 7 = **33** `Column(` y **2** `relationship()` sin anotar.

### Consecuencia medible en mypy (línea base de hoy)
De los **44** errores de mypy, **34** vienen directamente del estilo `Column` (`Need type annotation` o `Column[...]`
usado donde se espera el tipo Python):

| Archivo | Errores | Ejemplo (salida literal de mypy) |
|---|---|---|
| `app/models/user.py:40` | 1 | `Need type annotation for "role"  [var-annotated]` |
| `app/models/service.py:21` | 1 | `Need type annotation for "category"  [var-annotated]` |
| `app/models/audit.py:36` | 1 | `Need type annotation for "action"  [var-annotated]` |
| `app/services/user_access_policy.py:32,55` | 2 | `Invalid index type "Column[Any]" for "dict[UserRole, int]"` |
| `app/repositories/user_repository.py:41,60,61` | 3 | `expression has type "bool", variable has type "Column[bool]"` |
| `app/services/user_service.py:99,101,105,163,212,238(x2),287,316(x2),348,349,356,418` | 14 | `incompatible type "Column[str]"; expected "str"` |
| `app/services/tourist_services_service.py:74,128,136,165,166,173,206,207,215,343` | 10 | `variable has type "Column[datetime]"` / `"Column[str]"; expected "str"` |
| `app/api/routers/user.py:72,73` | 2 | `Argument "email_to" to "add_task" ... "Column[str]"; expected "str"` |

Los otros 10 errores no tienen que ver con S1: `str | None` de `os.getenv` (A4) en `database.py:11`, `security.py:71,87`,
`user_service.py:124,132,133` y `dependencies.py:92,93,108`, y un `return-value` en `service_repository.py:83`.

## Ficheros afectados (mapa completo)
- `app/models/user.py`: 12 `Column(`; import de `Column`.
- `app/models/service.py`: 14 `Column(` en dos clases y 2 `relationship()` sin `Mapped[]`; import de `Column`.
- `app/models/audit.py`: 7 `Column(`; import de `Column`.
- `app/db/database.py`: no tiene deuda (`Base(DeclarativeBase)` ya es 2.0). Es la base sobre la que se migra; no hay que tocarlo por S1.
- Consumidores donde hoy se ven los errores de tipo (no tienen `Column(`; los errores desaparecen o cambian al migrar):
  `app/services/user_service.py`, `app/services/tourist_services_service.py`, `app/services/user_access_policy.py`,
  `app/repositories/user_repository.py`, `app/api/routers/user.py`.

## Rincones no mencionados por la fuente
- **Nulabilidad implícita que la BD sí refleja.** Cinco columnas no declaran `nullable` y, según las migraciones, son
  `NULL` en el esquema: `app/models/audit.py:44` `timestamp` (`2cc4b57c136c...py:31` `nullable=True`),
  `app/models/service.py:25` `created_at` (`a0f621304d75...py:32`), `app/models/service.py:39` `is_primary`
  (`c48e057bd4cd...py:28`), `app/models/service.py:40` `created_at` (`c48e057bd4cd...py:29`),
  `app/models/user.py:43` `created_at` (`a0f621304d75...py:47`). Con `mapped_column`, la nulabilidad se deduce de
  `Mapped[T]` frente a `Mapped[T | None]`. Si se anota `Mapped[datetime]` sin `| None`, la columna pasa a
  `NOT NULL` y `alembic revision --autogenerate` detecta una diferencia de esquema.
- **Nombres de los tipos ENUM en PostgreSQL.** `user_role` (`user.py:40`) y `audit_action_enum` (`audit.py:36`) son
  explícitos. `ServiceCategory` (`service.py:21`) usa el nombre implícito `servicecategory`, que es el que figura en la
  migración `a0f621304d75...py:28`. Si la migración deja que el tipo se deduzca solo de `Mapped[UserRole]` (sin
  `Enum(..., name=...)`), el nombre cambia a `userrole` y el esquema deja de coincidir.
- **Alembic (fila "Alembic" del backlog l.95, mismo bloque `B-S1`):** `alembic/env.py:17-18` solo importa `User` y
  `TouristService`, con `# noqa: F401 ... B-S1 replaces it`. `AuditLog` y `ServiceImage` se registran en
  `Base.metadata` por un efecto colateral: importar `app.models.user` ejecuta antes `app/models/__init__.py:1-3`.
  Esto queda fuera de S1, pero el bloque es el mismo.
- `app/models/__init__.py:1-3`: ruff marca 4 `F401` (re-exportación sin `__all__`) y 1 `I001`. Relacionado con la fila Alembic, no con S1.
- **Tests:** `tests/` y `alembic/versions/` no tienen `Column(` del ORM. En las migraciones, los `sa.Column(` que hay
  dentro de `op.create_table`/`op.add_column` (33 en total) son la API correcta de Alembic, **no son deuda**.
  `tests/test_services.py:638` solo contiene la palabra "Column" en un docstring. Los tests crean modelos con kwargs
  (`User(...)`, `TouristService(**values)`, `ServiceImage(...)`, `AuditLog(...)`). El constructor declarativo 2.0
  conserva esa firma. La suite crea el esquema con `Base.metadata.create_all` sobre SQLite (`tests/conftest.py:16,41`).
- `setattr(model, key, value)` dinámico en `app/services/tourist_services_service.py:284` y `app/services/user_service.py:279`:
  el tipado no lo comprueba. No es deuda S1, pero ahí `Mapped[]` no aporta nada.

## Patrones de detección (copiables)
```bash
# Deuda: debe llegar a 0 en app/
grep -rnE "\bColumn\(" app --include=*.py
grep -rnE "^from sqlalchemy import .*\bColumn\b" app --include=*.py
# relationship sin anotar (debe llegar a 0)
grep -rnE "^\s+\w+\s*=\s*relationship\(" app --include=*.py
# Estilo 2.0 (deben subir: 33 mapped_column, 35 Mapped[ con las 2 relationship)
grep -rnc "mapped_column(" app/models
grep -rnc "Mapped\[" app/models
# Errores mypy atribuibles a S1 (hoy 34; objetivo 0)
python -m mypy 2>&1 | grep -cE "Column\[|Need type annotation"
# Paridad de esquema tras migrar (no debe generar operaciones): requiere BD; lo corre David
# alembic revision --autogenerate -m "check" --sql  -> la revisión debe salir vacía
```

## Línea base (python scripts/check.py)
- Base develop: `b421268`
- `git fetch origin` correcto. `git merge-base HEAD origin/develop` es igual a `git rev-parse origin/develop`
  (`b42126809045b87cfb83fbaac544d4e09c4f94aa`), así que la precondición se cumple. Rama `bloque/b-s1`, HEAD = origin/develop.
- Comando: `./venv/Scripts/python.exe scripts/check.py` (desde la raíz del repo). Nota: con `python` a secas se
  ejecutó el intérprete del sistema (`C:\Python314`), que no tiene `jwt`, `mypy` ni `importlinter`, y la compuerta
  falló por el entorno. La medición válida es la del venv del proyecto.

```
=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff check, mypy
```
- pytest: `360 passed, 5 warnings in 14.02s` (0 failed)
- Cobertura total: `94.77%` (umbral `Required test coverage of 92.0% reached`)
- ruff format: `147 files already formatted`
- ruff check: `Found 82 errors.` (23 E501, 17 I001, 13 D205, 9 E402, 6 D415, 4 B904, 4 F401, 3 W293, 3 UP042). En
  `app/models` + `app/db` + `alembic/env.py` hay 24, ninguno por `Column`.
- mypy: `Found 44 errors in 12 files (checked 35 source files)`; 34 atribuibles a S1 (tabla de arriba)
- import-linter: OK · `Contracts: 4 kept, 0 broken.` (capas api→services→repositories→models; servicios sin HTTP; repositorios solo SQLAlchemy+modelos; modelos/schemas sin capas superiores: todos KEPT)
- La compuerta **ya falla antes de tocar nada** (ruff check y mypy). Es deuda heredada y conocida: el CI corre
  `--soft format,ruff,mypy` (`.azure-pipelines/ci-pipeline.yml:30`) y rige el trinquete de ADR-0005, que exige no
  empeorar estos totales.
- Entorno: Python 3.14.3, SQLAlchemy 2.0.48.

## Conclusión para el planificador
El plan tiene que migrar los 33 `Column(` y las 2 `relationship()` de `app/models/{user,service,audit}.py` a
`Mapped[]` + `mapped_column()` **sin cambiar el esquema**. Para eso: `T | None` en las 5 columnas de nulabilidad
implícita y en las que ya son `nullable=True`; `Enum(..., name=...)` explícito para conservar `user_role`,
`audit_action_enum` y `servicecategory`; `Numeric(10, 2)` → `Mapped[Decimal]`; mantener la variante JSON/JSONB, la FK
con `ondelete="CASCADE"`, `index`/`unique` y los `default`/`server_default`. Criterio verificable: 0 `Column(` en `app/`,
mypy baja de 44 a ≤ 10 (los 34 errores atribuibles a S1 desaparecen y no aparecen otros), 360 tests en verde,
cobertura ≥ 94.77% y una autogeneración de Alembic vacía, que corre David contra la BD.
No debe tocar: `alembic/versions/` (los `sa.Column` de ahí son correctos), `Base`/`database.py`, la lógica de los
servicios ni los errores `str | None` de `os.getenv` (A4). Tampoco debe añadir el plugin mypy legado de SQLAlchemy:
`Mapped[]` funciona sin él. La fila "Alembic" (`env.py` → `import app.models`) es del mismo bloque, pero es un ítem distinto.
Riesgos: que la BD cambie sin que nadie lo note por nulabilidad o nombre de ENUM, y que el tipado nuevo destape
errores reales en los consumidores (por ejemplo, comparaciones de rol). Conviene corregirlos en una fase propia y
no mezclarlos con la migración de los modelos.
