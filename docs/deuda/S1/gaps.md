# Gaps — S1

## Auditoría Fase A — 2026-11-03

Veredicto: PASS (0 bloqueantes, 3 opcionales). Auditado en HEAD `cbbd313` (contiene `a30795a` y `105275e`).

Verificado por el auditor (no tomado del relato del ejecutor):
- `progress.json`: Fase_A `completed`, commit `a30795a` real (`git show --stat`: solo `tests/test_models_schema.py`, 158 inserciones); `current_target` = `Fase_B`; `last_handoff` presente; `edit_rules` intacto. `105275e` solo añade handoff y progress.json.
- Mensaje del commit idéntico al del plan (más el trailer Co-Authored-By).
- Compuerta (`./venv/Scripts/python.exe scripts/check.py`): 367 passed, cobertura 94.77 % (= línea base), ruff check 82 (= base), mypy 44 en 12 archivos (= base), lint-imports 4 KEPT, docs OK. `ruff format --check`: verde (51 files already formatted).
- Archivo nuevo: `ruff check tests/test_models_schema.py` → All checks passed; `mypy tests/test_models_schema.py | grep ^tests` → vacío.
- 7 casos presentes y en verde; las 4 mutaciones MA1-MA4 re-ejecutadas por el auditor: `1 failed, 6 passed` · `2 failed, 5 passed` · `1 failed, 6 passed` · `1 failed, 6 passed`; archivos restaurados (`git status --short app tests` vacío, `git diff --stat` vacío).
- Valores esperados literales (no derivados de `Base.metadata`), sin aserciones en español, sin mocks.

[OPCIONAL] — Fase A — El handoff quedó desactualizado: su RESUMEN muestra `✘ ruff format --check` y el residual 1 lo atribuye a `plan.md`; el commit posterior `cbbd313` (excluye Markdown del formato, AF-03) lo dejó en verde — `ruff format --check .` → `51 files already formatted`; RESUMEN actual: solo ruff check y mypy en rojo (heredado, igual a la línea base).
[OPCIONAL] — Fase A — `docs/deuda/S1/plan.md` y `verificacion.md` siguen sin commitear (y `docs/bitacora/2026-11-03.md`); no afectan al código ni a la compuerta, pero conviene commitearlos antes de abrir el PR — `git status --short`.
[OPCIONAL] — Fase A — El commit `cbbd313` (pyproject.toml, AF-03) está fuera de las fases de S1; es un cambio ajeno colocado entre A y B, declarado en su propio mensaje, sin tocar los archivos de la fase. Solo se deja constancia para el historial del PR.

Recordatorio para Fase B: precondición humana M0 (`alembic current` y `alembic check`, salida a la bitácora) antes de `/implementar S1 Fase_B`.

## Auditoría Fase B — 2026-11-03

Veredicto: PASS (0 bloqueantes, 1 opcional). Auditado en HEAD `9457b8a` (contiene `0e833c0`, commit de la fase, y `9457b8a`, handoff y progress.json).

Verificado por el auditor (no tomado del relato del ejecutor):
- `git status --short`: solo `M docs/bitacora/2026-11-03.md` (cambios de David, fuera de `app/`, `alembic/` y `tests/`; no se tocó).
- `progress.json`: Fase_B `completed`, commit `0e833c0` real (`git show --stat`: solo `app/models/{audit,service,user}.py`, 81+/43-); `current_target` = `Fase_C`; `last_handoff` presente; `edit_rules` intacto; Fase_A sin cambios. `9457b8a` solo toca `handoff-Fase_B.md` y `progress.json`.
- Mensaje del commit idéntico al del plan, carácter a carácter, más el trailer Co-Authored-By.
- Diff contra "Cambios exactos": las 33 columnas y las 2 `relationship()` coinciden línea a línea con el bloque del plan (con los saltos de línea que impone `ruff format`); imports como pide el plan (fuera `Column`/`Integer`/`Boolean`; dentro `Mapped`, `mapped_column`, `datetime`, `Decimal` en service.py y `Any` en audit.py); 3 `# noqa: UP042 (backlog D2)` en la línea de clase; docstrings Google Style nuevos en `ServiceCategory`, `TouristService` (cascada ORM y FK `ON DELETE CASCADE`) y `ServiceImage`; los docstrings y los cuatro comentarios de `audit.py` se conservan literales (incluido el residual 7).
- Métricas de la Verificación final, aplicables a B: `Column(` 0 · `import … Column` 0 · `relationship(` sin anotar 0 · `nullable=` en app/models 0 · `= mapped_column(` 33 · `: Mapped[` 35 · `Enum(…, name=…)` 3 · `Mapped[T | None]` exactamente en las 10 columnas de la decisión 2.
- mypy: `./venv/Scripts/python.exe -m mypy 2>&1 | grep -cE "Column\[|Need type annotation"` → 0; total `Found 10 errors in 5 files (checked 35 source files)`, exactamente las 10 líneas de la lista del plan (database.py:11, security.py:71/87, service_repository.py:83, user_service.py:124/132/133, dependencies.py:92/93/108); `mypy app/models | grep ^app/models` → vacío (la decisión 6 no aplica).
- ruff: `ruff check` de los 3 modelos → `All checks passed!`; total `Found 76 errors.` (base 82, plan 76).
- Compuerta (`./venv/Scripts/python.exe scripts/check.py`, re-ejecutada): 367 passed, 5 warnings · `TOTAL 941 34 136 22 94.80%` (≥ 94.77 %) · ruff format OK (51 files already formatted) · import-linter con los 4 contratos impresos, `Contracts: 4 kept, 0 broken.` (también con `./venv/Scripts/lint-imports.exe`) · docs OK. Rojo solo en ruff check y mypy, ambos por debajo de la línea base y heredados en archivos no tocados.
- `tests/test_models_schema.py`: `git diff a30795a HEAD` vacío; `7 passed`.
- Mutaciones M1-M7 re-ejecutadas por el auditor con el `mut()` del plan: `1 failed, 6 passed` · `2 failed, 5 passed` · `1 failed, 6 passed` · `1 failed, 6 passed` · `1 failed, 6 passed` · `1 failed, 6 passed` · `2 failed, 5 passed`. Restauración comprobada con `sha256sum -c` (3 OK) y `git status --short` (solo la bitácora).
- Fuera de alcance intacto: `git diff b421268 --stat -- alembic/versions/ app/db/ app/services/ app/repositories/ app/api/ app/schemas/ tests/conftest.py scripts/` → vacío; `app/models/__init__.py` y `alembic/env.py` no aparecen en `0e833c0`.
- Precondición M0: la sección "M0 del plan de S1" está en `docs/bitacora/2026-11-03.md:121-144` (`2cc4b57c136c (head)`, `No new upgrade operations detected.`).
- Opcional 2 de la Fase A, resuelto: `plan.md` (`adafdd5`) y `verificacion.md` (`61cc853`) ya están commiteados.

[OPCIONAL] — Fase B — La evidencia de M0 (precondición humana de B y referencia para M1) solo existe en cambios sin commitear de `docs/bitacora/2026-11-03.md`; el handoff la cita, pero el historial no la contiene. Conviene que David la commitee antes de M1 y del PR — `git diff -U0 docs/bitacora/2026-11-03.md` → `@@ -119,0 +120,26 @@` añade `## M0 del plan de S1`.

Siguiente: `/implementar S1 Fase_C`; tras ella, M1 de David (`alembic check` debe repetir `No new upgrade operations detected.`) y la auditoría de C, que corre la "Verificación final" completa.

## Auditoría Fase C — 2026-11-03

Veredicto: PASS (0 bloqueantes, 2 opcionales). Auditado en HEAD `2581dbe` (contiene `8ba10c0`, commit de la fase; `a085bca`, handoff y progress.json; y `2581dbe`, bitácora de David con M1). Última fase del plan: se corrió la "Verificación final" completa.

Verificado por el auditor (no tomado del relato del ejecutor):
- `git status --short`: vacío (árbol limpio).
- `progress.json`: Fase_C `completed`, commit `8ba10c0` real (`git show --stat`: solo `alembic/env.py` 14 (+5/-9), `app/models/__init__.py` 12, `tests/test_models_registry.py` 48 nuevo; 63+/11-); Fase_A y Fase_B sin cambios; `last_handoff` presente; `edit_rules` intacto. `current_target` = `"cierre"`, coherente con los precedentes de ítems cerrados: `docs/deuda/A9/progress.json` y `docs/deuda/SEC1/progress.json` dicen `"current_target": "cierre"`. `a085bca` solo toca `handoff-Fase_C.md` y `progress.json`; `2581dbe` solo `docs/bitacora/2026-11-03.md`.
- Mensaje del commit idéntico al del plan (`plan.md:375-393`): `diff` del texto del plan contra `git log -1 --format=%B 8ba10c0` sin el trailer → vacío.
- Diff contra "Cambios exactos": `app/models/__init__.py` es literalmente el bloque del plan (docstring, 3 imports, `__all__` de 4). `alembic/env.py`: un solo hunk en la cabecera; los dos `from app.models.<x> import … B-S1 replaces it` sustituidos por `import app.models  # noqa: F401  # registers every model on Base.metadata for autogenerate` (l.10); `load_dotenv()` justo tras el bloque de imports (l.14); el resto del archivo no cambia.
- RED → GREEN re-ejecutado: con el `__init__.py` de `0e833c0` → `AttributeError: module 'app.models' has no attribute '__all__'` ×2, `2 failed in 0.20s`; con el de `8ba10c0` → `2 passed in 0.03s`.
- Mutaciones re-ejecutadas: MC1 (`mut` del plan, sin `"AuditLog", `) → `2 failed in 0.16s`; MC2 (`app/models/zz_probe.py` con `Probe(Base)` creado por Bash y borrado con `rm`) → `2 failed in 0.16s`. Restauración: `sha256sum -c` OK en `__init__.py` y `env.py`, `git status --short` vacío.
- Smoke offline: `DATABASE_URL="postgresql+asyncpg://ci:ci@localhost:5432/ci" ./venv/Scripts/python.exe -m alembic upgrade head --sql` con el `env.py` de `07804ff` y con el de `8ba10c0`: `exit 0` las dos veces, 116 líneas cada uno, `diff` vacío (salidas en el scratchpad del auditor, no en `/tmp`).
- Compuerta (`./venv/Scripts/python.exe scripts/check.py`, re-ejecutada): `369 passed, 5 warnings` · `TOTAL 942 34 136 22 94.81%` (≥ 94.77 %) · `52 files already formatted` · ruff check `Found 60 errors.` (base 82, plan 60) · mypy `Found 10 errors in 5 files (checked 35 source files)`, exactamente las 10 líneas de la lista del plan · import-linter con los 4 contratos impresos, `Contracts: 4 kept, 0 broken.` (también con `./venv/Scripts/lint-imports.exe`) · docs OK. Rojo solo en ruff check y mypy, heredado en archivos no tocados y por debajo de la línea base.
- Archivos tocados: `ruff check alembic/env.py app/models tests/test_models_schema.py tests/test_models_registry.py` → `All checks passed!`; `mypy app/models alembic/env.py tests/test_models_registry.py | grep -E '^(app[/\]models|alembic|tests)[/\]'` → vacío.
- Verificación final del plan (`plan.md:398-425`), completa: `Column(` 0 · `import … Column` 0 · `relationship(` sin anotar 0 · `nullable=` en app/models 0 · `= mapped_column(` 33 (12 user, 14 service, 7 audit) · `: Mapped[` 35 · `Enum(…, name=…)` 3 · mypy `Column[|Need type annotation` 0 y total `Found 10 errors in 5 files` · `^import app.models` en env.py 1 · `from app.models.\w+ import` en env.py vacío · `B-S1 replaces it` en alembic/app vacío · `git diff b421268 --stat -- alembic/versions/ app/db/ app/services/ app/repositories/ app/api/ app/schemas/ tests/conftest.py scripts/` vacío · `pytest tests/test_models_schema.py tests/test_models_registry.py` → `9 passed`.
- Test nuevo conforme a AGENTS §5: sin mocks, sin usuarios/tokens a mano, nombres y aserciones en inglés, aserciones sobre conjuntos (no texto humano); descubre los modelos desde los submódulos, no desde una lista fija.
- M1 (`docs/bitacora/2026-11-03.md:163-185`) contra M0 (`:121-145`), solo contraste de texto: mismo head `2cc4b57c136c (head)`; `alembic check` con la misma frase `No new upgrade operations detected.` y las mismas cuatro líneas `Detected sequence named '<tabla>_id_seq'` (tourist_services, users, service_images, audit_logs; solo cambia el orden); ninguna operación nueva. Cumple el criterio del plan (`plan.md:433-434`): salida de `check` idéntica en contenido a M0. M1 se registró tras `8ba10c0` (bitácora 14:34; commit 12:56) y está commiteado (`2581dbe`).
- Opcional de la Fase B (M0 sin commitear): resuelto en `ba4e5c2` (`docs(bitacora): 3 nov, M0 reference for S1`).

[OPCIONAL] — Fase C — M1 se invocó como `python.exe -m alembic …` con el venv activado, no con `venv\Scripts\python.exe -m alembic …` como fija la decisión 8 y "los mismos dos comandos" de M0; la salida es equivalente (mismo head, misma frase, mismas secuencias) y la bitácora declara que era el `python.exe` del venv, así que no invalida la paridad. Además, el `alembic current` de M1 conserva la línea `Context impl PostgresqlImpl.` que M0 omitió (diferencia de recorte, no de resultado) — `docs/bitacora/2026-11-03.md:127,163-170`.
[OPCIONAL] — Fase C — Los residuales 1-7 del plan (`plan.md:436-465`: AF-05 del no-op de import-linter, intérprete del hook, 5 columnas NULL, nota en D2 sobre los 3 nuevos `noqa: UP042`, AGENTS §3, `service_repository.py:83`, comentario en español de `audit.py:30`) aún no están en `docs/backlog.md`, y las filas S1 (`backlog.md:82`) y Alembic (`backlog.md:95`) siguen describiendo la deuda como abierta (`33 Column(`, `0 mapped_column`). Es la tarea de cierre del ítem que decide David; conviene hacerla antes o junto con el PR — `grep -nE "AF-05|AF-06" docs/backlog.md` → vacío; `backlog.md:77` (D2) solo menciona el `noqa` de A9.

Siguiente: S1 queda listo para PR (las tres fases auditadas en PASS, M1 = M0, compuerta sin regresión y por debajo de la línea base). El rojo restante de ruff (60) y mypy (10) es heredado y le toca a `B-TESTS`.
