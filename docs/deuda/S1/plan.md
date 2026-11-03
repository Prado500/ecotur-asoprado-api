# PLAN — S1: Declarar los modelos con `Mapped[]` y `mapped_column()` sin cambiar el esquema, y registrar `app.models` completo en Alembic

- **Fecha:** 2026-11-03 · **Fuente:** `verificacion.md` (confirmada) + fila "Alembic" del backlog como fase propia
  (bitácora 2026-11-03, apertura: David "ok") · **Bloque:** `B-S1` · **Rama:** `bloque/b-s1`
- **Base develop:** `b421268` (la de la verificación; el ejecutor la re-comprueba en su ritual de arranque)

## Resumen para aprobación

Los 33 `Column(` de `app/models/{user,service,audit}.py` y sus 2 `relationship()` pasan al estilo tipado de SQLAlchemy
2.0 (`Mapped[]` + `mapped_column()`) **sin cambiar el esquema ni tocar ningún consumidor**. Además, `alembic/env.py`
importa `app.models` entero y `app/models/__init__.py` declara su registro con `__all__` (fila "Alembic"). Tres fases y tres
commits: **A** congela el esquema en un test que pasa antes y después por diseño, **B** migra los modelos y **C** arregla
el registro de Alembic. Un sondeo sobre una copia de `HEAD` (el repo no se tocó) ya midió el final: esquema idéntico,
mypy de 44 a 10 (todo lo que queda es A4 más un error ajeno), 0 errores nuevos, 369 tests, cobertura 94.81 %, ruff de 82 a
60 y 4 KEPT. **Riesgo principal:** un cambio de esquema que nadie vea (nulabilidad o nombre de ENUM). Lo cubren el test
de A (11 mutaciones detectadas) y el `alembic check` de David antes de B y después de C. **No se tocan** servicios,
repositorios, routers, schemas, `database.py`, `alembic/versions/` ni `scripts/check.py`; no hay migración ni ADR nuevos.
**Aviso:** sin el venv activado, el paso import-linter de `check.py` es un falso verde (residual 1).

## Objetivo y decisiones bloqueadas

Que cada atributo de los modelos tenga para mypy su tipo Python real, sin una sola diferencia de esquema, y que Alembic
vea todos los modelos porque los importa de forma explícita y no por un efecto colateral.

1. **Esquema intacto.** No hay migración nueva. `alembic/versions/` y `app/db/database.py` no se tocan. La paridad la
   congela `tests/test_models_schema.py` (Fase A), que las Fases B y C no modifican, y la confirma David (M0/M1).
2. **La nulabilidad sale solo de la anotación.** `Mapped[T | None]` va exactamente en las 10 columnas que hoy admiten NULL
   (`users.phone`, `users.created_at`, `users.deleted_at`, `tourist_services.description`, `tourist_services.created_at`,
   `tourist_services.deleted_at`, `service_images.is_primary`, `service_images.created_at`, `audit_logs.changes`,
   `audit_logs.timestamp`) y `Mapped[T]` en las otras 23. Ningún `mapped_column` lleva `nullable=`. Si la anotación se
   equivoca, el test de A falla; si conviviera con un `nullable=` explícito, la anotación podría mentir sin que nada
   fallara (`orm/properties.py:767-770`).
3. **El tipo SQL se escribe solo cuando el tipo Python no lo determina:** `String(n)`, `Text`, `Numeric(10, 2)` con
   `Mapped[Decimal]`, `DateTime(timezone=True)`, `JSON().with_variant(JSONB, "postgresql")` con
   `Mapped[dict[str, Any] | None]` (la misma firma que `AuditService.log_transaction`) y `Enum`. Se omiten `Integer` y
   `Boolean`: los deducen `int` y `bool`, y en `service_id` el tipo lo pone la FK. Toda columna lleva
   `= mapped_column(...)`, incluso vacío (`max_capacity`), para que las 33 líneas se lean igual.
4. **Todo `Enum` lleva `name=` explícito:** `user_role`, `servicecategory` (hoy implícito) y `audit_action_enum`. Solo con
   `Mapped[UserRole]`, SQLAlchemy deduciría `userrole` (sondeado).
5. **Se conservan** `primary_key`, `index`, `unique`, `default`, `server_default=func.now()`,
   `ForeignKey("tourist_services.id", ondelete="CASCADE")` y `cascade="all, delete-orphan"`. Las `relationship()` ya no
   llevan el destino como texto: lo deducen de la anotación (`orm/relationships.py:1748-1830`). La referencia adelantada
   `Mapped[list[ServiceImage]]` va sin comillas, porque Python 3.14 difiere las anotaciones (ADR-0004), SQLAlchemy 2.0.48
   las lee con `annotationlib` y ruff UP037 marca las comillas.
6. **Los consumidores no se tocan.** El sondeo no destapa ningún error nuevo, así que no hay fase de consumidores. Si en la
   Fase B mypy reporta una línea fuera de la lista de los 10 esperados (abajo), el ejecutor se detiene y lo reporta sin
   corregirlo, y el plan se rehace.
7. **Quedan fuera** el plugin mypy legado de SQLAlchemy, `MappedAsDataclass`, `type_annotation_map` en `Base` y
   `StrEnum`. Los tres enums conservan `(str, enum.Enum)` con `# noqa: UP042 (backlog D2)` en la línea de la clase
   (precedente A9: `StrEnum` cambia `str()` de valores que llegan al ORM y a la API).
8. **Python por ruta, nunca "activar el venv"** (instrucción de David). Evidencia: `python` a secas resolvió a
   `C:\Python314`, sin `jwt`, `mypy` ni `importlinter` (verificación, "Línea base"). En bash se escribe
   `./venv/Scripts/python.exe …` y en PowerShell `venv\Scripts\python.exe …`. Quedan prohibidos `python` a secas,
   `activate` y `Scripts\activate`. Vale para la compuerta (`./venv/Scripts/python.exe scripts/check.py`), mypy, pytest,
   ruff y Alembic (`-m alembic`). Import-linter se corre aparte con `./venv/Scripts/lint-imports.exe` (residual 1). Este
   punto **prevalece** sobre el `python …` literal de los rituales de `fase-ejecutor` y `handoff-auditor`.
9. **Trinquete (ADR-0005), en la práctica:** mypy sigue los imports y, al revisar cualquier modelo, imprime
   `app/db/database.py:11` (A4, no tocado). Por eso "0 errores de mypy en los archivos tocados" se mide filtrando la salida
   por la ruta de esos archivos (precedente A9). El juez de ruff es el del venv (0.17.2), no el del hook (residual 2).
10. Va un commit por fase, con el mensaje exacto de abajo. El trailer `Co-Authored-By` lo añade la sesión ejecutora con
    su modelo; el resto del mensaje es literal.

**Los 10 errores de mypy esperados tras B** (ninguno es S1): `app/db/database.py:11`, `app/core/security.py:71`, `:87`,
`app/services/user_service.py:124`, `:132`, `:133`, `app/api/dependencies.py:92`, `:93`, `:108` (A4) y
`app/repositories/service_repository.py:83` (residual 6).

## Análisis del redactor

**Contrastado hoy en `b421268`.** Hay 33 `Column(`, 2 `relationship(` sin anotar y 24 `nullable=` en `app/models`. mypy
con el venv da `Found 44 errors in 12 files`, en las mismas líneas que la tabla de la verificación. `alembic/env.py:17-18`
solo importa `User` y `TouristService`. Un matiz: `ServiceImage` no llega por efecto colateral, porque vive en
`service.py`, que `env.py` importa; el único que llega por la cadena de `app/models/__init__.py` es `AuditLog`, como dice
la bitácora. Ruff en los archivos que se tocarán: 3 I001 y 3 UP042 en los modelos; I001 y 4 F401 en `__init__.py`; 2 I001
y 9 E402 en `env.py`. Son 22 hallazgos, y de ahí sale el 82 → 60. Alembic está en `head` = `2cc4b57c136c`.

**Sondeo** (copia `git archive HEAD` en el scratchpad, con las variables del CI y una clave JWT de 32+ bytes; nada del
repo cambió). Con los modelos migrados según las decisiones 2 a 5, el volcado del esquema queda idéntico antes y después:
DDL de PostgreSQL y de SQLite de las 4 tablas e índices, más tipo, nulabilidad, PK, índice, único, `default`,
`server_default`, FK con `ondelete` de cada columna, y destino, `uselist`, `back_populates` y `cascade` de las dos
relaciones. Resultados: mypy 10 (exactamente la lista de arriba), 0 líneas `Column[`/`Need type annotation`;
`360 passed, 5 warnings` (igual que la línea base) y 94.80 %; 4 KEPT. Con la Fase C añadida: 369 passed, 94.81 %,
ruff 60. `alembic upgrade head --sql` con una URL ficticia sale con 0 y su SQL es idéntico al de antes. Con comillas en
`Mapped[list["ServiceImage"]]`, ruff marca UP037; sin ellas pasan la suite, mypy y ruff.

**Orden A → B → C.** A va primero y sola: el test de caracterización tiene que quedar commiteado sobre los modelos viejos,
para que su verde con el código 1.x sea un hecho del historial y B demuestre que no lo toca. B y C son independientes
(C no depende del estilo de las columnas). C va al final porque sigue la secuencia `m1`/`m2` del bloque (PLAN §2b) y
porque así B queda como un diff puro de modelos. No hay fase de consumidores (decisión 6): la verificación la recomendaba
para el caso de que el tipado destapara errores reales, y el sondeo demuestra que no destapa ninguno. Además, tocar
`user_service.py` obligaría a dejarlo con 0 en mypy, es decir, a corregir A4.

**Cómo se cumple "RED primero" en un refactor sin cambio de comportamiento.** No existe ningún test de pytest que deba
fallar antes de B: si existiera, el cambio alteraría el comportamiento. Hay tres piezas. (1) El test de A es un test de
caracterización: congela lo que los modelos declaran hoy y pasa antes y después por diseño. Que no es teatro lo
demuestran mutaciones: cada rincón de la verificación, roto a propósito, lo hace fallar (11 mutaciones validadas en el
sondeo). (2) En B, el rojo lo dan las herramientas (ADR-0001): antes de editar, `Column(` = 33 y las líneas S1 de mypy =
34; después, 0 y 0, con el test de A intacto y en verde. (3) En C sí hay rojo de pytest: `app.models.__all__` no existe
hoy, así que el test de registro falla con `AttributeError` (sondeado).

**Qué congela qué.** La suite actual (360) congela el comportamiento en tiempo de ejecución: constructores con kwargs,
`default` aplicados al insertar, cascada de imágenes, filtros por `deleted_at`. Lo hace sobre SQLite y no ve el esquema
de PostgreSQL. `tests/test_models_schema.py` congela el esquema declarado, compilado para PostgreSQL y sin BD; corre en el
CI. `alembic check` (M0/M1) compara los modelos con la BD real, pero no mira `server_default` (`compare_server_default` es
`False` por defecto y `env.py` no lo activa) ni las etiquetas de ENUM. Esos dos huecos los cubre el test de A. Lo que el
test no puede ver es la deriva que ya exista entre la BD y los modelos de hoy. Por eso M0 se corre **antes** de B: así una
diferencia en M1 se atribuye bien.

**Riesgos.** (a) Deriva silenciosa del esquema: test de A, mutaciones, M0/M1. (b) Errores nuevos en consumidores: el
sondeo dice 0 y la decisión 6 obliga a parar si aparece alguno. (c) La referencia adelantada sin comillas: si falla, falla
con ruido al configurar los mappers (`create_all` del conftest). (d) Mover `load_dotenv()` en `env.py`: `find_dotenv()`
sube desde el directorio de quien llama y `override=False` es el valor por defecto (`dotenv/main.py:332-372,387`), así
que `env.py` y `app/db/database.py:6` encuentran el mismo `.env` de la raíz salvo que exista otro `.env` anidado en
`alembic/` o `app/` (supuesto; `.env` no se lee por regla). M1 ejercita el modo online con el `.env` real. (e) El hook
formatea con el ruff del sistema (0.16.6, porque se invoca con `python` a secas) y la compuerta juzga con el del venv
(0.17.2): antes de la compuerta, el ejecutor corre `./venv/Scripts/python.exe -m ruff format <archivos>` y
`… ruff check --fix <archivos>`. (f) Las mutaciones se aplican por Bash (`cp`/sustitución/`mv`), nunca con Edit/Write:
así no disparan el hook, que reordenaría imports de archivos ajenos a la fase.

**Por qué no hay ADR.** AGENTS §3 ya exige el estilo 2.0 en los modelos. Las decisiones 2 a 5 son el idioma documentado
de SQLAlchemy 2.0 más la paridad de esquema que pide ADR-0002. El `noqa: UP042` repite el precedente de A9 y la fila
Alembic es la corrección literal del backlog. Si David quiere que las reglas 2 a 4 obliguen al `Reservation` de
`B-RESERVAS`, el sitio es AGENTS §3, que se cambia por PR (residual 5).

## Regla de alcance

- **Sí:** `app/models/user.py`, `app/models/service.py`, `app/models/audit.py`, `app/models/__init__.py`,
  `alembic/env.py`, `tests/test_models_schema.py` (nuevo) y `tests/test_models_registry.py` (nuevo). Docstrings Google
  Style en las clases refactorizadas que hoy no tienen (`ServiceCategory`, `TouristService`, `ServiceImage`).
- **No:** `alembic/versions/` (sus `sa.Column` son la API correcta de Alembic), `app/db/database.py`, `app/services/`,
  `app/repositories/`, `app/api/`, `app/schemas/`, `tests/conftest.py` y los tests existentes, `scripts/`, `.claude/`,
  `AGENTS.md`. Tampoco: una migración, `StrEnum` (D2), pasar a NOT NULL las columnas NULL (residual 3), A4, ni el
  comentario en español de `audit.py:30` (residual 7). Los comentarios y docstrings existentes se conservan tal cual.

## Fases

**Protocolo de mutación** (lo usan A, B y C; no se commitea nada). Sustituye un texto exacto por Bash, corre un test y
restaura el archivo byte a byte. Antes del `git add`, `git status --short` no debe mostrar cambios en `app/`,
`alembic/` ni `tests/` fuera de los archivos de la fase.

```bash
mut() { cp "$1" "$1.bak" && ./venv/Scripts/python.exe -c "import pathlib,sys; p=pathlib.Path(sys.argv[1]); s=p.read_text(encoding='utf-8'); assert sys.argv[2] in s, 'pattern not found'; p.write_text(s.replace(sys.argv[2], sys.argv[3], 1), encoding='utf-8')" "$1" "$2" "$3"; ./venv/Scripts/python.exe -m pytest -q -p no:cacheprovider "$4" 2>&1 | tail -1; mv "$1.bak" "$1"; }
```

### Fase A — Congelar el esquema que declaran los modelos (la más pequeña)

- **Archivos:** `tests/test_models_schema.py` (nuevo).
- **Cambios exactos:**
  - `import app.models` (registra las 4 tablas) y `from app.db.database import Base`; `PG = postgresql.dialect()`.
  - `class FrozenColumn(NamedTuple)` con `sql_type: str`, `nullable: bool = False`, `primary_key: bool = False`,
    `indexed: bool = False`, `unique: bool = False`, `server_default: str | None = None`, `default: object = None` y
    `foreign_key: tuple[str, str | None] | None = None`. El campo se llama `indexed` y no `index` porque `index` choca
    con `tuple.index` y mypy lo rechaza (sondeado).
  - `_describe(column: Column[Any]) -> FrozenColumn` normaliza así: `column.type.compile(dialect=PG)`,
    `bool(column.nullable)`, `column.primary_key`, `bool(column.index)`, `bool(column.unique)`,
    `str(server_default.arg) if isinstance(server_default, DefaultClause) else None`,
    `default.arg if isinstance(default, ColumnDefault) else None`, y `(fk.target_fullname, fk.ondelete)` de su única FK
    o `None`. Los `isinstance` (con `ColumnDefault` y `DefaultClause`, públicas en `sqlalchemy`) son obligatorios: sin
    ellos mypy reporta que `FetchedValue` y `DefaultGenerator` no tienen `arg` (sondeado).
  - `EXPECTED: dict[str, dict[str, FrozenColumn]]` como **literal** con la tabla de abajo. Está prohibido calcular lo
    esperado desde `Base.metadata` o desde las migraciones en tiempo de ejecución: el test acabaría dándose la razón a sí
    mismo.

  | Tabla | Columnas (sin marca = NOT NULL, sin índice ni único ni default; `TZ` = `TIMESTAMP WITH TIME ZONE`) |
  |---|---|
  | `users` | `id` INTEGER pk index · `cedula` VARCHAR(13) index unique · `email` VARCHAR(150) index unique · `password_hash` VARCHAR(255) · `first_name` VARCHAR(100) · `last_name` VARCHAR(100) · `phone` VARCHAR(20) NULL · `role` user_role default `UserRole.tourist` · `data_consent` BOOLEAN default False · `is_active` BOOLEAN default False · `created_at` TZ NULL server `now()` · `deleted_at` TZ NULL |
  | `tourist_services` | `id` INTEGER pk index · `name` VARCHAR(150) · `description` TEXT NULL · `category` servicecategory default `ServiceCategory.otro` · `base_price` NUMERIC(10, 2) · `max_capacity` INTEGER · `is_available` BOOLEAN default False · `created_at` TZ NULL server `now()` · `deleted_at` TZ NULL |
  | `service_images` | `id` INTEGER pk index · `service_id` INTEGER fk (`tourist_services.id`, `CASCADE`) · `image_url` TEXT · `is_primary` BOOLEAN NULL default False · `created_at` TZ NULL server `now()` |
  | `audit_logs` | `id` INTEGER pk index · `entity_name` VARCHAR(50) index · `entity_id` VARCHAR(50) index · `action` audit_action_enum · `changes` JSONB NULL · `performed_by` VARCHAR(50) index · `timestamp` TZ NULL server `now()` index |

- **Tests (RED primero):** 7 casos, todos en verde sobre los modelos actuales (caracterización, ver Análisis):
  1. `test_metadata_holds_exactly_the_frozen_tables`: `set(Base.metadata.tables) == set(EXPECTED)`.
  2. a 5. `test_table_columns_match_the_frozen_schema[<tabla>]`, parametrizado sobre las 4 tablas:
     `{c.name: _describe(c) for c in table.columns} == EXPECTED[tabla]` (también detecta columnas añadidas o quitadas).
  6. `test_enum_types_keep_their_postgres_names_and_labels`: `{tipo.name: tipo.enums}` de las columnas `Enum` es igual a
     `user_role` → `["superadmin", "admin", "tourist"]`, `servicecategory` →
     `["agroturismo", "recreacional", "metalmecanico", "otro"]` y `audit_action_enum` →
     `["CREATE", "UPDATE", "SOFT_DELETE", "RECOVER", "ACTIVATE", "DEACTIVATE"]`.
  7. `test_service_relationships_keep_target_direction_and_cascade`: `TouristService.images` apunta a `ServiceImage` con
     `uselist=True`, `back_populates="service"` y `set(cascade) == {"save-update", "merge", "refresh-expire", "expunge",
     "delete", "delete-orphan"}`; `ServiceImage.service` apunta a `TouristService` con `uselist=False`,
     `back_populates="images"` y `set(cascade) == {"save-update", "merge"}`.

  Mutaciones sobre el código actual (pegar la última línea de cada una; cada una debe dar ≥ 1 failed):
  - MA1: `mut app/models/user.py 'Column(DateTime(timezone=True), server_default=func.now())' 'Column(DateTime(timezone=True), server_default=func.now(), nullable=False)' tests/test_models_schema.py`
  - MA2: `mut app/models/service.py 'Column(Enum(ServiceCategory)' 'Column(Enum(ServiceCategory, name="service_category")' tests/test_models_schema.py`
  - MA3: `mut app/models/service.py ', cascade="all, delete-orphan"' '' tests/test_models_schema.py`
  - MA4: `mut app/models/audit.py 'JSON().with_variant(JSONB, "postgresql")' 'JSON()' tests/test_models_schema.py`
- **Criterio de aceptación:** `7 passed` en el archivo nuevo; las cuatro mutaciones fallan y `git status --short` no muestra
  cambios en `app/`. `./venv/Scripts/python.exe scripts/check.py` da 367 passed y cobertura ≥ 94.77 %,
  ruff total 82, mypy total 44. `./venv/Scripts/lint-imports.exe` da `Contracts: 4 kept, 0 broken.`. Sobre el archivo
  nuevo, `./venv/Scripts/python.exe -m ruff check tests/test_models_schema.py` → 0 y
  `./venv/Scripts/python.exe -m mypy tests/test_models_schema.py 2>&1 | grep -E '^tests[/\\]'` → vacío.
- **Fuera de alcance de esta fase:** cualquier archivo de `app/` (las mutaciones se restauran) y el registro (Fase C).
- **Commit:**
  ```
  test(models): freeze the ORM schema before the Mapped migration

  S1 rewrites every column of app/models from Column() to Mapped[] and
  mapped_column(), and it must not change the database schema. Today only
  an Alembic autogenerate against a live database proves that, and only
  David can run it. This test pins the schema the models declare, offline
  and in CI, before the refactor starts.

  - Each column type is compiled for the PostgreSQL dialect, so the ENUM
    names (user_role, servicecategory, audit_action_enum), JSONB and
    NUMERIC(10, 2) are compared as PostgreSQL sees them, not as SQLite.
  - It freezes nullability, primary keys, index and unique flags, Python
    and server defaults, the service_images foreign key with ON DELETE
    CASCADE, the enum labels and both sides of the images relationship.
  - Expected values are literals taken from the current models; nothing
    is derived from Base.metadata at run time, so the test cannot agree
    with itself.

  It passes on the current models by design (characterization test); the
  handoff records the mutations that make it fail.
  ```

### Fase B — Columnas y relaciones con `Mapped[]` y `mapped_column()`

- **Precondición humana:** que David haya corrido M0 (abajo) y anotado su salida en la bitácora.
- **Archivos:** `app/models/user.py`, `app/models/service.py`, `app/models/audit.py`.
- **Cambios exactos** (decisiones 2 a 5; el hook y `ruff format` parten las líneas largas):
  ```python
  # user.py — User
  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  cedula: Mapped[str] = mapped_column(String(13), unique=True, index=True)
  email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
  password_hash: Mapped[str] = mapped_column(String(255))
  first_name: Mapped[str] = mapped_column(String(100))
  last_name: Mapped[str] = mapped_column(String(100))
  phone: Mapped[str | None] = mapped_column(String(20))
  role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), default=UserRole.tourist)
  data_consent: Mapped[bool] = mapped_column(default=False)
  is_active: Mapped[bool] = mapped_column(default=False)
  created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
  deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
  # service.py — TouristService
  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  name: Mapped[str] = mapped_column(String(150))
  description: Mapped[str | None] = mapped_column(Text)
  category: Mapped[ServiceCategory] = mapped_column(Enum(ServiceCategory, name="servicecategory"), default=ServiceCategory.otro)
  base_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
  max_capacity: Mapped[int] = mapped_column()
  is_available: Mapped[bool] = mapped_column(default=False)
  created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
  deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
  images: Mapped[list[ServiceImage]] = relationship(back_populates="service", cascade="all, delete-orphan")
  # service.py — ServiceImage
  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  service_id: Mapped[int] = mapped_column(ForeignKey("tourist_services.id", ondelete="CASCADE"))
  image_url: Mapped[str] = mapped_column(Text)
  is_primary: Mapped[bool | None] = mapped_column(default=False)
  created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
  service: Mapped[TouristService] = relationship(back_populates="images")
  # audit.py — AuditLog (se conservan los cuatro comentarios actuales encima de sus columnas)
  id: Mapped[int] = mapped_column(primary_key=True, index=True)
  entity_name: Mapped[str] = mapped_column(String(50), index=True)
  entity_id: Mapped[str] = mapped_column(String(50), index=True)
  action: Mapped[AuditAction] = mapped_column(Enum(AuditAction, name="audit_action_enum"))
  changes: Mapped[dict[str, Any] | None] = mapped_column(JSON().with_variant(JSONB, "postgresql"))
  performed_by: Mapped[str] = mapped_column(String(50), index=True)
  timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
  ```
  - Imports: desaparecen `Column`, `Integer` y `Boolean`. Entran `from sqlalchemy.orm import Mapped, mapped_column`
    (más `relationship` en `service.py`, cuyo import ya existe), `from datetime import datetime` (en los tres archivos),
    `from decimal import Decimal` (en `service.py`) y `from typing import Any` (en `audit.py`). El orden lo pone ruff (I001
    → 0).
  - `class UserRole(str, enum.Enum):  # noqa: UP042 (backlog D2)`, y lo mismo en `ServiceCategory` y `AuditAction`.
  - Docstring Google Style de una línea de resumen (más un cuerpo si aporta algo) para `ServiceCategory`, `TouristService`
    (dueño de sus imágenes: cascada ORM y FK `ON DELETE CASCADE`) y `ServiceImage`. Los docstrings existentes no cambian.
- **Tests (RED primero):** el rojo lo dan las herramientas. **Antes** de editar, pegar la salida de
  `grep -rnE "\bColumn\(" app --include=*.py | wc -l` (→ 33) y de
  `./venv/Scripts/python.exe -m mypy 2>&1 | grep -cE "Column\[|Need type annotation"` (→ 34). **Después** deben dar 0 y 0;
  `tests/test_models_schema.py` sigue en `7 passed` sin cambios (`git diff HEAD -- tests/test_models_schema.py` vacío).
  Mutaciones sobre el código nuevo (cada una debe dar ≥ 1 failed en `tests/test_models_schema.py`):
  - M1 `user.py`: `'created_at: Mapped[datetime | None]'` → `'created_at: Mapped[datetime]'` (nulabilidad)
  - M2 `user.py`: `'Enum(UserRole, name="user_role")'` → `'Enum(UserRole)'` (nombre de ENUM deducido: `userrole`)
  - M3 `service.py`: `'images: Mapped[list[ServiceImage]]'` → `'images: Mapped[ServiceImage]'` (`uselist`)
  - M4 `service.py`: `', ondelete="CASCADE"'` → `''` (FK)
  - M5 `audit.py`: `'JSON().with_variant(JSONB, "postgresql")'` → `'JSON()'` (JSONB)
  - M6 `service.py`: `'Numeric(10, 2)'` → `'Numeric()'` (precisión)
  - M7 `service.py`: `'name="servicecategory"'` → `'name="service_category"'` (nombre de ENUM)
- **Criterio de aceptación:** `Column(` 0, `from sqlalchemy import … Column` 0, `relationship(` sin anotar 0 y `nullable=`
  0 en `app/models`; `= mapped_column(` 33 y declaraciones `: Mapped[` 35. mypy total `Found 10 errors in 5 files`, con
  exactamente las 10 líneas de la lista; si aparece cualquier otra, se aplica la decisión 6.
  `./venv/Scripts/python.exe -m mypy app/models 2>&1 | grep -E '^app[/\\]models[/\\]'` → vacío. `ruff check` de los 3
  archivos → 0 y ruff total 76. 367 passed, cobertura ≥ 94.77 % y 4 KEPT con `lint-imports.exe`. Las 7 mutaciones fallan
  y `git status --short` no muestra cambios de código fuera de los 3 modelos.
- **Fuera de alcance de esta fase:** `app/models/__init__.py` y `alembic/env.py` (Fase C), cualquier consumidor (decisión
  6), `database.py`, `StrEnum` y cambiar comentarios existentes.
- **Commit:**
  ```
  refactor(models): declare columns with Mapped and mapped_column

  Base already extends DeclarativeBase (SQLAlchemy 2.0), but the 33
  columns of User, TouristService, ServiceImage and AuditLog were still
  declared in the 1.x Column() style. mypy could not type the three Enum
  columns and typed every other instance attribute as Column[...], which
  produced 34 errors across the models, the services, the user
  repository, the access policy and the user router. With Mapped[] the
  attributes carry their Python types and those errors disappear without
  touching any consumer (mypy 44 -> 10; none of the remaining ten comes
  from the models).

  The schema does not change; tests/test_models_schema.py is untouched
  and still green:
  - Nullability comes only from the annotation: Mapped[T | None] on the
    ten columns that are NULL today (five of them implicitly), and no
    nullable= argument anywhere.
  - The SQL type is written only where the Python type cannot imply it
    (string lengths, Text, Numeric(10, 2), DateTime(timezone=True), the
    JSONB variant). Every Enum keeps an explicit name=, including
    servicecategory, which used to be implicit, because the name derived
    from Mapped[UserRole] alone would be userrole.
  - relationship() takes its target and direction from Mapped[list[...]]
    and Mapped[...]; the forward reference is unquoted because Python
    3.14 defers annotations (ruff UP037).
  - The three enums keep their (str, Enum) base behind a line-level noqa
    for UP042: StrEnum changes str() of values that reach the ORM and the
    API, and enum cleanup is backlog D2.

  No legacy mypy plugin is added: Mapped[] is typed natively.
  ```

### Fase C — `env.py` importa `app.models` y el paquete declara su registro

- **Archivos:** `alembic/env.py`, `app/models/__init__.py`, `tests/test_models_registry.py` (nuevo).
- **Cambios exactos:**
  - `app/models/__init__.py` completo (imports y `__all__` en la **misma** edición):
    ```python
    """ORM models package: importing it registers every table on ``Base.metadata``.

    Alembic's ``env.py`` imports this package for autogenerate, so a new model module must be
    imported here and listed in ``__all__``; otherwise autogenerate does not see its table.
    """

    from app.models.audit import AuditLog
    from app.models.service import ServiceImage, TouristService
    from app.models.user import User

    __all__ = ["AuditLog", "ServiceImage", "TouristService", "User"]
    ```
  - `alembic/env.py`, solo el bloque de cabecera (de la l.1 a la l.18): las dos líneas `from app.models.<x> import …  #
    noqa … B-S1 replaces it` se sustituyen por
    `import app.models  # noqa: F401  # registers every model on Base.metadata for autogenerate`, escrita con su `noqa`
    en la misma edición. `load_dotenv()` pasa a ir justo **después** del bloque de imports (se conserva; ver riesgo d) y
    el orden de imports lo pone ruff. El resto del archivo no cambia.
- **Tests (RED primero):** `tests/test_models_registry.py`, 2 casos, **rojos hoy** (`AttributeError: module 'app.models'
  has no attribute '__all__'`; pegar esa salida antes de tocar `__init__.py`):
  1. `test_models_package_exports_every_model_defined_in_its_modules`: recorre
     `pkgutil.iter_modules(app.models.__path__)`, importa cada submódulo y reúne las clases que heredan de `Base`
     definidas en él (`obj.__module__ == module.__name__`). Ese conjunto debe ser igual a
     `{getattr(app.models, n) for n in app.models.__all__}`.
  2. `test_exported_models_cover_every_table_in_metadata`:
     `{getattr(app.models, n).__tablename__ for n in app.models.__all__} == set(Base.metadata.tables)`.

  Mutaciones (cada una debe dar 2 failed en `tests/test_models_registry.py`):
  - MC1: `mut app/models/__init__.py '"AuditLog", ' '' tests/test_models_registry.py`
  - MC2: crear `app/models/zz_probe.py` con un modelo mínimo `Probe(Base)` (`__tablename__ = "probe"`,
    `id: Mapped[int] = mapped_column(primary_key=True)`) **por Bash**, correr el test y borrar el archivo con `rm`.

  Smoke de `env.py` sin BD, antes y después de editar: `DATABASE_URL="postgresql+asyncpg://ci:ci@localhost:5432/ci"
  ./venv/Scripts/python.exe -m alembic upgrade head --sql > /tmp/s1_offline_<antes|despues>.sql; echo "exit $?"`. El
  primero sale con 0; el `diff` de los dos `.sql` debe salir vacío. `load_dotenv` no pisa la variable ya definida.
- **Criterio de aceptación:** `2 passed` y las dos mutaciones fallan; smoke con 0 y `diff` vacío.
  `grep -cE "^import app\.models\b" alembic/env.py` → 1, `grep -nE "from app\.models\.\w+ import" alembic/env.py` → vacío
  y `grep -rn "B-S1 replaces it" alembic app` → vacío. `ruff check` de los 3 archivos → 0 y ruff total 60.
  `./venv/Scripts/python.exe -m mypy app/models alembic/env.py tests/test_models_registry.py 2>&1 | grep -E
  '^(app[/\\]models|alembic|tests)[/\\]'` → vacío; mypy total sigue en 10. 369 passed, cobertura ≥ 94.77 % y 4 KEPT.
- **Fuera de alcance de esta fase:** los modelos (ya en B), el resto de `env.py` (docstrings y comentarios de la
  plantilla de Alembic), `compare_server_default`, `alembic.ini` y `alembic/versions/`.
- **Paso posterior (David):** M1.
- **Commit:**
  ```
  refactor(alembic): import the whole app.models registry in env.py

  alembic/env.py imported User and TouristService only; AuditLog reached
  Base.metadata because importing any submodule first runs
  app/models/__init__.py. Autogenerate worked by accident, and a model
  module added later outside that chain would be invisible to it.

  - app/models/__init__.py becomes the explicit registry: it imports
    every model and lists it in __all__, which also clears its four
    F401 and the I001.
  - alembic/env.py imports app.models as a whole (one noqa for F401: the
    import exists for its side effect) and calls load_dotenv() after the
    import block. app.db.database already loads the same .env on import,
    so the environment env.py reads is unchanged and the nine E402 go.
  - tests/test_models_registry.py fails if a model defined under
    app/models is not exported by the package, or if Base.metadata holds
    a table the package does not export.

  Offline rendering (alembic upgrade head --sql) is byte-identical.
  ```

## Verificación final

```bash
# Deuda S1 (esperado: 0 · 0 · 0 · 0)
grep -rnE "\bColumn\(" app --include=*.py
grep -rnE "^from sqlalchemy import .*\bColumn\b" app --include=*.py
grep -rnE "^\s+\w+\s*=\s*relationship\(" app --include=*.py
grep -rnE "nullable=" app/models --include=*.py
# Estilo 2.0 (esperado: 33 · 35 · 3 Enum con name=)
grep -rhoE "= mapped_column\(" app/models --include=*.py | wc -l
grep -rhE "^\s+\w+: Mapped\[" app/models --include=*.py | wc -l
grep -rnE 'Enum\(\w+, name="(user_role|servicecategory|audit_action_enum)"\)' app/models --include=*.py | wc -l
# mypy atribuible a S1 (esperado: 0) y total (esperado: "Found 10 errors in 5 files", las 10 líneas de la lista)
./venv/Scripts/python.exe -m mypy 2>&1 | grep -cE "Column\[|Need type annotation"
./venv/Scripts/python.exe -m mypy 2>&1 | tail -1
# Fila Alembic (esperado: 1 · vacío · vacío)
grep -cE "^import app\.models\b" alembic/env.py
grep -nE "from app\.models\.\w+ import" alembic/env.py
grep -rn "B-S1 replaces it" alembic app
# Nada fuera del alcance cambió desde la base (esperado: vacío)
git diff b421268 --stat -- alembic/versions/ app/db/ app/services/ app/repositories/ app/api/ app/schemas/ tests/conftest.py scripts/
# Trinquete sobre lo tocado y totales (ADR-0005)
./venv/Scripts/python.exe -m ruff check app/models alembic/env.py tests/test_models_schema.py tests/test_models_registry.py
./venv/Scripts/python.exe -m mypy app/models alembic/env.py 2>&1 | grep -E '^(app[/\\]models|alembic)[/\\]'   # vacío
./venv/Scripts/python.exe -m ruff check . | tail -1        # esperado: Found 60 errors (línea base 82)
./venv/Scripts/lint-imports.exe | tail -1                   # esperado: Contracts: 4 kept, 0 broken.
./venv/Scripts/python.exe -m pytest tests/test_models_schema.py tests/test_models_registry.py -q   # 9 passed
# Compuerta (línea base: 360 ✔ · 94.77 % · ruff ✘ 82 · mypy ✘ 44 · 4 KEPT). Esperado: 369 ✔ · ≥ 94.77 % · ruff ✘ 60 · mypy ✘ 10
./venv/Scripts/python.exe scripts/check.py
```

**Pasos manuales de David** (requieren la BD local; ningún agente los corre; PowerShell, desde la raíz):

- **M0, antes de `/implementar S1 Fase_B`:** `venv\Scripts\python.exe -m alembic current` (esperado:
  `2cc4b57c136c (head)`; si no, primero `venv\Scripts\python.exe -m alembic upgrade head`) y luego
  `venv\Scripts\python.exe -m alembic check`. La salida literal va a la bitácora. Si ya muestra diferencias, son deriva
  previa a S1 y van a Residuales.
- **M1, después de la Fase C:** los mismos dos comandos. La salida de `check` debe ser **idéntica** a la de M0; lo
  esperado es `No new upgrade operations detected.`. Cualquier operación nueva bloquea el PR del bloque.

## Residuales

1. **`scripts/check.py:48-53`: el paso import-linter es un no-op con el venv sin activar.** `shutil.which("lint-imports")`
   devuelve `None` porque `venv/Scripts` no está en el PATH, y el fallback `[PY, "-m", "importlinter.cli",
   "lint_imports"]` sale con 0 sin ejecutar nada: `importlinter/cli.py` (2.15) no tiene bloque `__main__`. Evidencia:
   la compuerta imprime `--- import-linter: OK en 0.2s` sin salida, mientras `./venv/Scripts/lint-imports.exe` imprime
   `Contracts: 4 kept, 0 broken.`. En el CI probablemente no pasa (`UsePythonVersion` pone `Scripts` en el PATH);
   conviene confirmarlo en el log. Corrección sugerida: buscar `lint-imports` junto a `sys.executable`. Fila sugerida:
   `| AF-05 | check.py: sin venv activado, el paso import-linter es un no-op (fallback -m importlinter.cli) | **1** fallback | Alta | XS | **Entra · \`B-TESTS\`** |`
   (la decisión es de David).
2. **El intérprete del venv en el resto del flujo.** `.claude/settings.json` invoca el hook con `python` a secas, así que
   el ruff del hook es el 0.16.6 de `C:\Python314` y el de la compuerta es el 0.17.2 del venv. Los rituales de
   `fase-ejecutor.md` y `handoff-auditor.md` dicen `python scripts/check.py`. ADR-0001 (veredicto sobre
   `deuda-verificador`, punto c) eligió a propósito el comando portable en lugar de `venv\Scripts\python.exe`; la
   evidencia de hoy muestra que en esta máquina la forma portable solo funciona con el venv activado. Si cambiar eso
   cambia la decisión de ADR-0001, toca un ADR nuevo o un addendum (ADR-0009). Destino: la misma fila AF-05 o una
   AF-06; `.claude/` lo edita David.
3. **Cinco columnas NULL que en la práctica siempre tienen valor** (`created_at` ×3 y `timestamp` con `server_default`;
   `is_primary` con `default`), mientras los schemas de salida las declaran no opcionales (`app/schemas/user.py:148`,
   `app/schemas/service.py:97`, `app/schemas/audit.py:31`): una fila con NULL daría 500 al leerse. Endurecerlas a NOT NULL
   es una migración que exige revisar los datos. Fila sugerida con `Sale → B-FUTURO`.
4. **D2:** al cierre, la fila D2 debería decir que, al unificar los enums, se retiran 4 `noqa: UP042` (el de
   `app/schemas/user.py` y los 3 nuevos de `app/models`).
5. **AGENTS §3:** si David quiere que las decisiones 2 a 4 obliguen a los modelos de `B-RESERVAS`, añadir una línea a
   AGENTS §3 por PR (precedente A9).
6. **`app/repositories/service_repository.py:83`** (`return-value`: devuelve `TouristService | None` donde la firma
   promete `TouristService`). No es S1 ni A4; es uno de los 10 errores que quedan. Destino: `B-TESTS`, que deja la
   compuerta en verde, o una fila propia.
7. **`app/models/audit.py:30`:** el comentario `# "User" o "TouristService"` está en español (AGENTS §4). Se conserva
   literal en B para no meter ruido en el diff; es trivial y opcional.

## Referencias

- **Context7 no estuvo disponible en esta sesión** (el subagente no tenía la herramienta MCP). Cada API se contrastó
  contra el código fuente **instalado** en el `venv` (la fuente exacta para la versión en uso) y con el sondeo del
  scratchpad. Si se quiere la confirmación por Context7, la biblioteca es `/sqlalchemy/sqlalchemy`.
- SQLAlchemy · 2.0.48 · `Mapped`/`mapped_column`: la nulabilidad sale de la anotación salvo que haya `nullable=`
  explícito (`orm/properties.py:767-770`); el tipo explícito prevalece y, en una FK, el tipo lo pone la columna destino
  (`:877`) · https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#mapped-column-derives-the-datatype-and-nullability-from-the-mapped-annotation
- SQLAlchemy · 2.0.48 · `Enum` deducido de `Mapped[EnumClass]`: nombre en minúsculas de la clase (`userrole`, sondeado);
  `name=` explícito lo fija · https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#using-python-enum-or-pep-586-literal-types-in-the-type-map
- SQLAlchemy · 2.0.48 · mapa de tipos por defecto (`Decimal` → `Numeric` sin precisión, `datetime` → `DateTime` sin
  zona, `str` → `String` sin longitud): por eso se escriben explícitos · https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#customizing-the-type-map
- SQLAlchemy · 2.0.48 · `TypeEngine.with_variant` (JSON → JSONB en PostgreSQL) · https://docs.sqlalchemy.org/en/20/core/type_api.html#sqlalchemy.types.TypeEngine.with_variant
- SQLAlchemy · 2.0.48 · `relationship()` con `Mapped[list[...]]`/`Mapped[...]`: destino, colección y `uselist` desde la
  anotación (`orm/relationships.py:1748-1830`) · https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html
- SQLAlchemy · 2.0.48 · anotaciones diferidas de Python 3.14 leídas con `annotationlib` en formato `FORWARDREF`
  (`util/compat.py:65-66,131-137`) · https://docs.sqlalchemy.org/en/20/changelog/changelog_20.html
- SQLAlchemy · 2.0.48 · el plugin mypy legado está deprecado y no hace falta con `Mapped` · https://docs.sqlalchemy.org/en/20/orm/extensions/mypy.html
- Alembic · 1.18.4 · `alembic check` (`command.py:323-370`); `--sql` con `--autogenerate` lanza `CommandError`
  (`command.py:279-282`); `compare_server_default=False` por defecto (`runtime/migration.py:184-185`); exige la BD en
  `head` (`autogenerate/api.py:608`) · https://alembic.sqlalchemy.org/en/latest/autogenerate.html
- python-dotenv · 1.2.2 · `find_dotenv` sube desde el directorio de quien llama y `override=False` por defecto
  (`dotenv/main.py:332-372,387`) · https://saurabh-kumar.com/python-dotenv/
- import-linter · 2.15 · el punto de entrada es la consola `lint-imports`; `cli.py` no tiene `__main__` · https://import-linter.readthedocs.io/en/stable/usage.html
- ruff · 0.17.2 (venv) · UP037 y UP042 · https://docs.astral.sh/ruff/rules/quoted-annotation/ · https://docs.astral.sh/ruff/rules/replace-str-enum/
- mypy · 2.4.0 · sigue los imports y reporta errores de los módulos importados (por eso el filtro por ruta) · https://mypy.readthedocs.io/en/stable/running_mypy.html#following-imports
