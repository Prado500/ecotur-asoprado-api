# ADR-0010 — Dominio unificado: los modelos SQLAlchemy son las entidades, declarados en estilo 2.0 (`Mapped[]`)

- **Estado:** aceptado. La primera parte (dominio unificado) es retroactiva: es la práctica del repositorio desde su
  inicio y AGENTS §3 la citaba como "ADR en `docs/adr/`" sin que existiera. La segunda parte (estilo de declaración)
  se decidió al cerrar S1.
- **Fecha de la decisión:** dominio unificado, desde el primer modelo (`20486ad`, 2026-03-20); estilo 2.0, 2026-11-03 (S1) ·
  **Fecha de registro:** 2026-11-03
- **Ubicación en el repo:** `docs/adr/0010-dominio-unificado-y-estilo-de-modelos.md`
- **Origen:** backlog S1 ("Modelos en estilo SQLAlchemy 1.x sobre base 2.0") y fila "Alembic" (`env.py` dependía de un
  efecto colateral de importación); `docs/deuda/S1/verificacion.md` y `plan.md` (decisiones 1 a 7); bitácora
  `2026-11-03` (M0 y M1). Commits: `a30795a` (test que congela el esquema), `0e833c0` (modelos), `8ba10c0` (registro en
  `env.py`); PR #74, merge `217e58f`. AGENTS §3 se corrige en el PR de AF-04 para citar este ADR.

## Decisión (resumen)

1. **Los modelos de SQLAlchemy (`app/models/`) son las entidades del dominio.** No hay una segunda capa de "entidades
   puras" ni mapeadores entre ambas. Los servicios trabajan con los modelos; los routers nunca los devuelven: devuelven
   schemas Pydantic.
2. **Todo modelo se declara en estilo 2.0:** cada columna es `nombre: Mapped[Tipo] = mapped_column(...)`. Está prohibido
   `Column(...)` en `app/models/`.
3. **La nulabilidad la decide solo la anotación:** `Mapped[T | None]` para una columna que admite NULL, `Mapped[T]` para
   una que no. Ningún `mapped_column` lleva `nullable=`.
4. **El tipo SQL se escribe cuando el tipo Python no lo determina** (`String(n)`, `Numeric(p, s)`,
   `DateTime(timezone=True)`, `JSON` con variante `JSONB`, `Enum`) y se omite cuando sí lo determina (`int`, `bool`, y la
   columna destino en una clave foránea). Todo `Enum` lleva `name=` explícito.
5. **Las relaciones van anotadas** (`Mapped[list[X]]` o `Mapped[X]`); `relationship()` ya no recibe el destino como
   texto.
6. **El registro de modelos es explícito:** `app/models/__init__.py` exporta cada modelo en `__all__`, `alembic/env.py`
   importa `app.models` una sola vez, y `tests/test_models_registry.py` falla si un modelo nuevo no está exportado o su
   tabla no está en `Base.metadata`.
7. **Cambiar la forma de declarar no cambia el esquema.** Cualquier refactor de modelos se prueba contra la base real
   con `alembic check` antes y después, y la salida tiene que ser la misma.

## Contexto

**Dominio unificado.** El repositorio nunca tuvo entidades separadas de los modelos: desde el primer día el servicio
recibe y devuelve instancias de `User`, `TouristService`, `ServiceImage` y `AuditLog` (el primer modelo entró en `20486ad`, 20 de
marzo de 2026). ADR-0002 solo tiene sentido con
esa decisión: si las invariantes de negocio viven también en la base de datos (índices únicos, claves foráneas,
restricciones), el modelo ORM es el lugar donde el dominio y la base se encuentran, y duplicarlo en una "entidad pura"
sería mantener dos verdades. AGENTS §3 lo decía desde el 24 de octubre ("decisión consciente, ADR en `docs/adr/`"), pero
el ADR no se había escrito. Este documento lo escribe.

**Estilo de declaración.** Los tres archivos de modelos estaban escritos con `Column(...)`, la forma de SQLAlchemy 1.x,
sobre una base `DeclarativeBase` de la 2.0. Funcionaba, pero con tres costes medidos en la verificación de S1
(`docs/deuda/S1/verificacion.md`):
- **mypy no podía tipar los modelos.** Veía cada atributo como `Column[...]` y no sabía qué tipo tenía cada columna de
  `Enum`. De los 44 errores de mypy del repositorio el 3 de noviembre, 34 nacían ahí y se propagaban a servicios,
  repositorio de usuarios, política de acceso y router de usuarios: código correcto marcado en rojo por culpa de la
  declaración.
- **La nulabilidad era implícita.** Con `Column`, no escribir `nullable` significa "admite NULL". Cinco columnas estaban
  en esa situación sin que nadie lo hubiera decidido (`created_at` en tres tablas, `audit_logs.timestamp`,
  `service_images.is_primary`); la base las tiene como NULL y los schemas de salida las declaran obligatorias. No es
  un error de S1 (hoy coinciden modelo y base), pero es una decisión que nadie tomó. Queda como BE-30.
- **`B-RESERVAS` añade modelos nuevos en dos semanas** y AGENTS §3 ya pedía "modelos nuevos en estilo 2.0" sin que
  ningún modelo existente sirviera de ejemplo. Un repositorio con dos estilos invita a copiar el equivocado.

**Registro en Alembic.** `alembic/env.py` importaba solo `app.models.user` y `app.models.service`. `AuditLog` llegaba a
`Base.metadata` porque importar un submódulo ejecuta antes `app/models/__init__.py`, que importaba los tres. Funcionaba
por un efecto colateral de segundo orden: un modelo nuevo añadido fuera de esa cadena habría sido invisible para
`alembic revision --autogenerate`, justo la herramienta con la que `B-RESERVAS m2` va a crear sus tablas.

## Decisión (detalle)

### Por qué la nulabilidad sale solo de la anotación
SQLAlchemy 2.0 permite las dos cosas a la vez: `Mapped[str | None]` y `nullable=False` en la misma línea. Si conviven,
gana `nullable=` y la anotación miente sin que nada lo detecte (`orm/properties.py:767-770`, SQLAlchemy 2.0.48). Con una
sola fuente de verdad, la anotación es a la vez lo que lee mypy, lo que lee quien abre el archivo y lo que crea la
tabla. Si la anotación se equivoca, el test del esquema (`tests/test_models_schema.py`) falla.

### Por qué el tipo SQL va explícito donde hace falta
El mapa de tipos por defecto de SQLAlchemy es pobre para una base de producción: `Decimal` → `Numeric` sin precisión,
`datetime` → `DateTime` sin zona horaria, `str` → `String` sin longitud. Escribirlos evita que un modelo nuevo cree una
columna distinta de la que el autor cree estar creando. `int` y `bool` sí se deducen bien, y en una clave foránea el
tipo lo fija la columna destino, así que ahí no se repite. Cada `Enum` lleva `name=` porque, sin él, SQLAlchemy nombra
el tipo de PostgreSQL con el nombre de la clase en minúsculas (`userrole`) y la base ya tiene `user_role`: el nombre
explícito es lo que mantiene el esquema igual.

### Por qué las relaciones van anotadas
`relationship("ServiceImage")` con el destino entre comillas era necesario en 1.x. En 2.0 el destino, si es una lista y
si es uno a uno se deducen de la anotación (`orm/relationships.py:1748-1830`). Con Python 3.14 (ADR-0004) las
anotaciones se evalúan de forma diferida, así que una referencia adelantada (`Mapped[list[ServiceImage]]` antes de que
exista la clase) va sin comillas; ruff (UP037) marca las comillas como innecesarias.

### Por qué el registro es explícito y tiene test
`import app.models` en `env.py` hace que el registro dependa de una línea que cualquiera puede leer, no de un orden de
imports. `__all__` en `app/models/__init__.py` es la lista de modelos del sistema; `tests/test_models_registry.py`
compara esa lista con `Base.metadata.tables` y falla si alguien añade un modelo y olvida exportarlo. Es la misma idea
que `_DOMAIN_ERROR_STATUS` en ADR-0003: una tabla explícita con un test que detecta el olvido.

### Lo que no cambia con este ADR
- Los tres enums de la aplicación siguen heredando de `(str, enum.Enum)` con `# noqa: UP042`. Pasar a `StrEnum` cambia
  el `str()` de los valores que llegan al ORM y a la API (precedente A9); es la fila D2 del backlog, que retira los
  cuatro `noqa` al unificar las definiciones.
- No se usa el plugin de mypy de SQLAlchemy (deprecado; `Mapped` lo hace innecesario), ni `MappedAsDataclass`, ni un
  `type_annotation_map` en `Base`. Son generalidades que el MVP no necesita (AGENTS §3: nada de generalidad
  especulativa).
- Los consumidores de los modelos (servicios, repositorios, routers) no se tocaron: la migración de estilo no cambió
  ninguna firma.

## Consecuencias

- **Positivas:** 0 `Column(` en `app/models/` (33 `mapped_column`); mypy pasa de 44 errores en 12 archivos a 10 en 5,
  ninguno en los modelos; ruff de 82 a 60 (las anotaciones entre comillas y similares desaparecen al reescribir); 369
  tests, cobertura 94,81 %. Un modelo nuevo tiene tres ejemplos del estilo que debe seguir y un test que lo obliga a
  registrarse.
- **El esquema no cambió, y está medido:** `tests/test_models_schema.py` se escribió antes del refactor (literales,
  nunca derivados de `Base.metadata`), quedó en verde con los modelos viejos y siguió en verde con los nuevos;
  `alembic upgrade head --sql` es idéntico byte a byte antes y después; y contra la base local, `alembic check` dio
  `No new upgrade operations detected.` antes de tocar los modelos (M0) y después (M1), con el mismo `head`
  (`2cc4b57c136c`). Esa paridad es la que ADR-0002 necesita para que `B-RESERVAS m2` pueda usar `autogenerate` con
  confianza.
- **Obligaciones para los modelos de `B-RESERVAS`** (recogidas en AGENTS §3 por el PR de AF-04): estilo 2.0,
  nulabilidad por anotación, tipos explícitos, `Enum` con `name=`, relación anotada, modelo exportado en `__all__`, y
  `alembic check` limpio antes del PR.
- **Residuos declarados:** BE-30 (las cinco columnas NULL con `server_default`/`default` frente a schemas de salida
  obligatorios: endurecerlas a NOT NULL es una migración que exige revisar datos y no entra en un cambio neutro de
  esquema); D2 (los enums); `app/repositories/service_repository.py:83`, un error de mypy que S1 destapó y no es suyo
  (va a `B-TESTS`); un comentario en español en `app/models/audit.py:30` (AGENTS §4), que se corrige con el próximo PR
  que toque el archivo.

## Alternativas consideradas

- **Entidades de dominio puras con mapeadores hacia los modelos ORM** (Clean Architecture estricta): descartada. Para
  cuatro tablas y un equipo de dos, duplicar cada entidad y mantener el mapeo en ambos sentidos es coste sin beneficio
  medible, y ADR-0002 ya pone las invariantes en la base: el modelo ORM *es* el punto de verdad. Se reconsidera solo
  si el dominio deja de caber en los modelos (reglas que necesiten objetos sin tabla).
- **Mantener `Column` y silenciar mypy** (`# type: ignore`, o el plugin legado): descartada. Esconde 34 errores en vez
  de resolverlos y deja el ejemplo equivocado para los modelos nuevos.
- **`Mapped[]` con `nullable=` explícito además de la anotación "por claridad":** descartada. Dos fuentes de verdad
  para la misma propiedad; cuando discrepan, nada avisa.
- **`StrEnum`, `MappedAsDataclass`, `type_annotation_map`:** fuera de alcance, explicado arriba.

## Evidencia

- `docs/deuda/S1/verificacion.md` (línea base: 33 `Column(`, 0 `mapped_column`, 44 errores de mypy, cinco columnas con
  nulabilidad implícita) y `plan.md` (decisiones 1 a 7; verificación final).
- `tests/test_models_schema.py` (congela tipos compilados para PostgreSQL, nulabilidad, claves, índices, valores por
  defecto, la clave foránea con `ON DELETE CASCADE`, nombres y etiquetas de los enums, la relación `images`) y
  `tests/test_models_registry.py`.
- Mutaciones MA1–MA4 (fase A), M1–M7 (fase B) y MC1–MC2 (fase C): cada una pone los tests nuevos en rojo; ejecutadas por
  el ejecutor y repetidas por el auditor, archivos restaurados byte a byte (`docs/deuda/S1/gaps.md`).
- M0 y M1 en `docs/bitacora/2026-11-03.md`, salida literal de `alembic current` y `alembic check`.
- SQLAlchemy 2.0.48: `mapped_column` deriva tipo y nulabilidad de la anotación
  (https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#mapped-column-derives-the-datatype-and-nullability-from-the-mapped-annotation);
  relaciones desde la anotación (https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html); mapa de tipos por
  defecto (https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#customizing-the-type-map).
