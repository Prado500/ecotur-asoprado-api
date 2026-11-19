# Gaps — BE-50

## Auditoría Fase A — 2026-11-19
**Veredicto Fase A: PASS (0 bloqueantes, 1 opcionales).**
[OPCIONAL] — Fase A — Los contratos de import-linter siguen sin medirse para `e530980`: en esta máquina el paso no llega a evaluarlos (DLL `_rustgrimp` bloqueada). E1.5 manda que la sesión Mentor los mida sobre `git archive e530980` en Linux y lo anote en la bitácora antes de empezar B; en el repo todavía no hay evidencia de esa anotación. El riesgo es nulo porque la fase no toca código, pero es una condición previa de B, no algo que A deba corregir — evidencia: paso import-linter abajo (sin línea `Contracts:`); plan.md, E1.5; handoff-Fase_A.md:92-93.

### Evidencia

**Árbol y commits.** `git status --short` → vacío. `git log --oneline -3`: `787ee5c docs(progress): record BE-50 Fase_A completion`, `e530980 docs(adr): add ADR-0022, a verified-email mark decides the link`, `271abf5 docs(item-be50): E1, gate with --soft imports on a blocked machine`.

**Commit de la fase (`e530980`).** `git show --stat e530980` → 1 archivo, `docs/adr/0022-la-marca-de-correo-verificado-decide-el-enlace.md`, 88 inserciones. Comparé con `diff` el mensaje (`git log -1 --format=%B`) contra plan.md:118-131 (sin la sangría): idéntico salvo la línea vacía final que añade git. El alcance de `git diff --name-only 271abf5 e530980` es solo el ADR.

**Cambios exactos.** Comparé con `diff` plan.md:333-420 (Anexo A) contra el ADR. La única diferencia es la línea 3: `<FECHA DE APROBACIÓN>` pasa a ser `19 nov 2026`, como manda E0.1. `ls docs/adr/0022-*` → 1 archivo; `grep -c "<FECHA" docs/adr/0022-*.md` → `0`. No hay índice de ADR que actualizar: el precedente de ADR-0021 (`e3cdc4b`) tampoco tocó ninguno.

**Segundo commit (`787ee5c`).** Es conforme. El protocolo de `fase-ejecutor` (`.claude/agents/fase-ejecutor.md:62-63`) manda commitear aparte `progress.json` y `handoff-<fase>.md` con `docs(progress): record <ID> <fase> completion`, y así lo hicieron todas las fases anteriores (`04a5a71`, `9cdc9d1` de BE-38; `d368a5d` de BE-37). El mensaje único del plan es el del commit de la fase, que es `e530980`. `787ee5c` toca solo `docs/deuda/BE-50/` y ningún archivo de otra fase.

**progress.json.** JSON válido. `Fase_A`: `completed`, `commit: "e530980"` (un hash real; `git show --stat` lo confirma). `current_target` pasó de `Fase_A` a `Fase_B`. `last_handoff` está presente. `edit_rules` y `allowed_statuses` no cambiaron (`git show 787ee5c -- docs/deuda/BE-50/progress.json`).

**Compuerta re-ejecutada por el auditor** (`./venv/Scripts/python.exe scripts/check.py --soft imports`, E1.1). Código de salida `0`.

Paso import-linter (literal):
```
=== import-linter ===
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    from importlinter.cli import lint_imports_command; lint_imports_command()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\projects\ecotur-asoprado\venv\Lib\site-packages\importlinter\__init__.py", line 5, in <module>
    from .domain.contract import Contract, ContractCheck  # noqa
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\projects\ecotur-asoprado\venv\Lib\site-packages\importlinter\domain\contract.py", line 4, in <module>
    from grimp import ImportGraph
  File "C:\projects\ecotur-asoprado\venv\Lib\site-packages\grimp\__init__.py", line 3, in <module>
    from .application.graph import DetailedImport, Import, ImportGraph
  File "C:\projects\ecotur-asoprado\venv\Lib\site-packages\grimp\application\graph.py", line 6, in <module>
    from grimp import _rustgrimp as rust  # type: ignore[attr-defined]
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ImportError: DLL load failed while importing _rustgrimp: An Application Control policy has blocked this file.
--- import-linter: FALLA (exit 1) en 0.7s
```

RESUMEN (literal):
```
=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✘ import-linter (soft)
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada; tolerados en rojo: import-linter
```

Otras líneas: `71 files already formatted` · `All checks passed!` · `Success: no issues found in 66 source files` · `Documentación coherente (...)` · `TOTAL 1066 10 154 6 98.69%` · `Required test coverage of 92.0% reached. Total coverage: 98.69%` · `797 passed, 25 warnings in 23.71s`.

**E1.2:** (a) exit 0 ✔; (b) última línea `Compuerta superada; tolerados en rojo: import-linter` ✔; (c) el único `✘` es `import-linter (soft)` ✔; (d) contiene `DLL load failed while importing _rustgrimp` ✔. **E1.3:** no aplica, porque no hay línea `Contracts:`.

**Ratchet frente a la línea base** (verificacion.md:162-163, 182: 797 passed · 98,69 % · ruff 0 · mypy 0 en 66 · 4 kept): pytest 797/0 failed, igual; cobertura 98,69 %, igual; ruff 0, igual; mypy 0 en 66, igual; contratos no medibles aquí (tolerado por E1, ver el opcional). Ruff y mypy sobre los archivos tocados no aplican: la fase solo toca un `.md`. Coincide con lo que pegó el ejecutor (handoff-Fase_A.md:31-86).

**Criterio de aceptación de A:** el archivo existe ✔; `<FECHA` = 0 ✔; la compuerta pasa según E1 con 797 passed y sin cambios en código ✔. La fase no lleva tests (lo dice el plan). No es la última fase, así que la Verificación final no se ejecuta. No hay código nuevo, así que las comprobaciones de AGENTS §3-§5 no aplican.

## Auditoría Fase B — 2026-11-19
**Veredicto Fase B: PASS (0 bloqueantes, 2 opcionales).**
[OPCIONAL] — Fase B — Los pasos de PostgreSQL de después de B todavía no están en la bitácora y son condición previa de C, no un defecto de B. Faltan `upgrade head`, `check`, `downgrade -1`, `upgrade head` y las dos consultas SQL. La sección más reciente de la bitácora es la de antes de B, con `alembic current`/`check` (12:54), y su "Siguiente" los deja pendientes. Respecto a E1.5: en esta re-ejecución import-linter sí cargó y midió `Contracts: 4 kept, 0 broken.` sobre un árbol cuyo `app/`, `alembic/` y `tests/` son los de `cba3ddd` (`git diff --name-only cba3ddd HEAD` solo lista `docs/deuda/BE-50/`). Si esa medición sustituye a la de Linux lo decide la sesión Mentor — evidencia: plan.md:154-160 y :187-188; docs/bitacora/2026-11-19.md:353-383 (no hay sección posterior a B); paso import-linter abajo.
[OPCIONAL] — Fase B — R-B1 se confirma. El hook `.claude/hooks/ruff_on_edit.py:27-28` pasa la ruta explícita a `ruff format` y `ruff check --fix`, y así ruff no aplica `extend-exclude` (`pyproject.toml:61`). Medido sin escribir nada: `ruff format --check alembic/versions/e50a7c3d9b12_users_email_verified_at.py` da `1 file would be reformatted` (comillas dobles y una línea en blanco tras el docstring), y la misma orden con `--force-exclude` da `No Python files found under the given path(s)` con rc 0. Afecta a toda migración escrita a mano con Write/Edit; C no toca `alembic/`. Destino: fila AF en el backlog; `.claude/` queda fuera del alcance del ítem — evidencia: salidas citadas; handoff-Fase_B.md, "Desviaciones" y R-B1.

### Evidencia

**Árbol y commits.** `git status --short` → vacío. `git log --oneline -5`: `a8be15a docs(progress): record BE-50 Fase_B completion`, `cba3ddd feat(users): add the email_verified_at column, empty in every row`, `3998cb3 docs(item-be50): phase A audit PASS (0 blocking, 1 optional)`, `787ee5c`, `e530980`.

**Commit de la fase (`cba3ddd`).** `git show --stat cba3ddd` → 4 archivos, 132 inserciones: `alembic/versions/e50a7c3d9b12_users_email_verified_at.py` (37), `app/models/user.py` (3), `tests/test_migration_email_verified_at.py` (91), `tests/test_models_schema.py` (1). Son los cuatro de plan.md:135-136. `git diff --name-only 3998cb3 cba3ddd` lista los mismos cuatro. Mensaje: `diff` entre plan.md:164-181 (sin la sangría) y `git log -1 --format=%B cba3ddd` → solo la línea vacía final que añade git.

**Cambios exactos contra el Anexo B** (`diff` del bloque del plan contra `git show cba3ddd:<archivo>`):
- Migración: plan.md:436-472 frente al archivo commiteado → sin diferencias (rc 0). Mantiene las comillas simples y `Union[...]` del estilo `script.py.mako`, así que la restauración que declara el ejecutor tras el paso del hook está en el commit. `grep -rln "down_revision.*'b51f3c9e2a64'" alembic/versions` → solo `e50a7c3d9b12_users_email_verified_at.py` (comando 10 de la Verificación final: 1).
- Test nuevo: plan.md:484-574 frente al archivo commiteado → sin diferencias (rc 0).
- Modelo: el diff añade exactamente plan.md:428-430 tras `deleted_at` (`app/models/user.py:56-58`). Usa `Mapped[datetime | None]` sin `nullable=` ni `default` y con `DateTime(timezone=True)`, como piden ADR-0010 y AGENTS §3. `grep -rn email_verified_at app` → solo `app/models/user.py:58`: nadie lee ni escribe la columna todavía, como manda el "Fuera de alcance" de B.
- Esquema congelado: una sola línea, `"email_verified_at": FrozenColumn(TZ, nullable=True),` tras `deleted_at` (`tests/test_models_schema.py:80`).

**Segundo commit (`a8be15a`).** Toca solo `docs/deuda/BE-50/progress.json` y `handoff-Fase_B.md`, con el mensaje `docs(progress): record BE-50 Fase_B completion`, como manda el paso 6 de `.claude/agents/fase-ejecutor.md`. Ningún archivo de otra fase.

**progress.json** (`git show a8be15a -- docs/deuda/BE-50/progress.json`). JSON válido. `Fase_B`: `pending`/`null` → `completed`/`"cba3ddd"`, un hash real. `current_target`: `Fase_B` → `Fase_C`. `last_handoff` presente. `edit_rules`, `allowed_statuses` y las descripciones no cambiaron.

**Compuerta re-ejecutada por el auditor** (`./venv/Scripts/python.exe scripts/check.py --soft imports`, E1.1). Exit `0`. Esta vez la extensión `_rustgrimp` cargó y el paso import-linter evaluó los contratos, así que rige E1.3 y se cumple.

Paso import-linter (literal):
```
=== import-linter ===
=============
Import Linter
=============


---------
Contracts
---------

Analyzed 56 files, 147 dependencies.
------------------------------------

Capas: api | cli -> services -> repositories -> models KEPT
Los servicios no conocen el transporte HTTP KEPT
Los repositorios solo conocen SQLAlchemy y los modelos KEPT
Los modelos y los schemas no dependen de capas superiores KEPT

Contracts: 4 kept, 0 broken.
--- import-linter: OK en 2.7s
```

RESUMEN (literal):
```
=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

Otras líneas: `Python 3.14.3` · `72 files already formatted` · `All checks passed!` · `Success: no issues found in 67 source files` · `Documentación coherente (...)` · `TOTAL 1067 10 154 6 98.69%` · `Required test coverage of 92.0% reached. Total coverage: 98.69%` · `799 passed, 25 warnings in 35.61s`.

**E1.2:** (a) exit 0 ✔; (b) la última línea es `Compuerta superada.`, la forma que E1.2(b) admite cuando el paso sale en verde ✔; (c) no hay ningún `✘` ✔; (d) no aplica, porque el paso no falló. **E1.3:** `Contracts: 4 kept, 0 broken.` ✔. El ejecutor vio el paso en rojo por la DLL y el auditor lo ve en verde. Es una diferencia de entorno, no de código, y deja en evidencia más de lo que E1 exigía.

**Ratchet frente a la línea base** (verificacion.md: 797 passed · 98,69 % · ruff 0 · mypy 0 en 66 · 4 kept):

| Medida | Línea base | Auditoría B | Lectura |
|---|---|---|---|
| pytest | 797 passed | 799 passed, 0 failed | +2, los del plan |
| Cobertura | 98,69 % | 98,69 % (1067 sentencias) | igual |
| ruff | 0 | 0 | igual |
| mypy | 0 en 66 | 0 en 67 | igual; +1 archivo, el test nuevo |
| Contratos | 4 kept | 4 kept, 0 broken | igual |

Coincide con lo que pegó el ejecutor (handoff-Fase_B.md, "Compuerta de salida"), salvo import-linter, que aquí sí se midió.

**Archivos tocados:** `ruff check` y `ruff format --check` sobre `app/models/user.py`, `tests/test_models_schema.py` y `tests/test_migration_email_verified_at.py` dan `All checks passed!` y `3 files already formatted`, y `mypy` sobre los tres da `Success: no issues found in 3 source files`. La migración está fuera de ruff y mypy por `extend-exclude`, como prevé el plan.

**Tests exigidos.** Los tres del plan existen y pasan dentro de los 799: `test_table_columns_match_the_frozen_schema[users]`, `test_migration_adds_the_column_empty_in_every_row` y `test_migration_downgrade_drops_the_column_and_keeps_the_rows`. Las cifras RED (`1 failed, 796 passed, 2 errors`), el SQL fuera de línea (`ALTER TABLE users ADD COLUMN email_verified_at TIMESTAMP WITH TIME ZONE;` y ningún `UPDATE users`) y los mutantes MB1-MB4 constan en el handoff con su salida; el auditor no los repitió. Coinciden con lo que E0.3 midió en Linux.

**AGENTS §3-§5 en el código nuevo:** no hay excepción de dominio nueva, ni ruta, ni DTO. El modelo no es nuevo, así que `__all__` no cambia. El test nuevo no usa mocks y construye los usuarios con `make_user`. `grep` de `Mock|patch` y de caracteres en español sobre el test nuevo → 0 coincidencias. La invariante "nace vacía" está en la base (la columna sin `server_default`) y la prueba el test de migración.

**Condición previa de C** (plan.md:187-188, E0.5, E1.5): los cuatro comandos de `alembic` y las dos consultas de David en PostgreSQL, con su salida literal en la bitácora. Ver el primer opcional.
