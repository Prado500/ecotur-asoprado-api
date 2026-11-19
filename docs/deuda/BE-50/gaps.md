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

## Auditoría Fase C — 2026-11-19
**Veredicto Fase C: PASS (0 bloqueantes, 1 opcionales).**
[OPCIONAL] — Fase C — Quedan pasos humanos que el plan pone antes de mezclar y que no son defectos de C: la medición de contratos del Mentor sobre `git archive 86b30f2` en Linux (E1.5), la comprobación de R3 en el cliente Flutter y la viñeta R5 de AGENTS §3. El riesgo de E1.5 es nulo, porque en esta re-ejecución import-linter cargó y midió `Contracts: 4 kept, 0 broken.` sobre un árbol cuyo `app/` y `tests/` son los de `86b30f2` (`git diff --name-only 86b30f2 HEAD` solo lista `docs/deuda/BE-50/`). El CI del PR sigue siendo la medición que cuenta — evidencia: plan.md E1.5, R3 y R5 (líneas 306 y 308); docs/bitacora/2026-11-19.md:423-424 ("Siguiente"); handoff-Fase_C.md, "Pendientes para David".

### Evidencia

**Árbol y commits.** `git status --short` → vacío (antes y después de la compuerta). `git log --oneline -5`: `2ba6ed5 docs(progress): record BE-50 Fase_C completion`, `86b30f2 fix(auth): let the verification link change an account only once`, `ba493f3`, `a8be15a`, `cba3ddd`.

**Commit de la fase (`86b30f2`).** `git show --stat 86b30f2` → 5 archivos, 228 inserciones y 33 borrados: `app/api/routers/user.py`, `app/core/security.py`, `app/services/user_service.py`, `tests/test_auth.py`, `tests/test_user_service.py`. Son los cinco de plan.md:185-186. Mensaje: `diff` entre plan.md:216-239 (sin la sangría) y `git log -1 --format=%B 86b30f2` → solo la valla de apertura del bloque y la línea vacía final que añade git; el texto es idéntico.

**Condición previa de C** (plan.md:187-188, E0.5, E1.5). docs/bitacora/2026-11-19.md:385-420 contiene los pasos de David en PostgreSQL después de B (`upgrade head`, `check` → `No new upgrade operations detected.`, `downgrade -1`, `upgrade head`, `timestamp with time zone | YES` y `count` = 0) y los contratos del Mentor sobre `git archive cba3ddd` (`Contracts: 4 kept, 0 broken.`). Se commitearon en `ba493f3` (15:19:37), antes de `86b30f2` (15:25:25).

**Cambios exactos contra el Anexo C** (`git diff 86b30f2~1 86b30f2`):
- `user_service.py`: `from datetime import UTC, datetime` en la línea 1. Los cinco "single-use" se reescribieron con el texto del Anexo (`:33`, `:39`, `:71`, `:105` y el `Args` de `verify_email_account`). El docstring de `verify_email_account` es literal. En el cuerpo, la guarda `if user.email_verified_at is not None:` (`:159`) devuelve `"Su correo ya fue verificado."` antes de `changed_fields` (`:162`). Después se escriben la marca (`:163`) e `is_active`, `save_user` se llama siempre y `log_transaction` solo `if changes:`. Las dos líneas de excepción están en `recover_user_account`. El decode y la búsqueda no cambiaron.
- `security.py` y `routers/user.py`: solo los docstrings, con el texto del Anexo.
- `tests/test_user_service.py`: el import, `VERIFIED_AT`, C1 ampliado con `before` y el intervalo, C2 en lugar de `test_verify_email_on_active_account_writes_nothing`, y C3 y C4 nuevos. El texto es el del Anexo.
- `tests/test_auth.py`: C5 con la aserción de la marca, C6 y C7 en el sitio de los dos tests `test_be38_*`, y C8 a C12 tras C7 y antes de `test_verify_email_invalid_token_returns_400`. El texto es el del Anexo.

**Segundo commit (`2ba6ed5`).** Toca solo `docs/deuda/BE-50/handoff-Fase_C.md` (nuevo) y `progress.json`, con el mensaje `docs(progress): record BE-50 Fase_C completion`, que es la convención de `fase-ejecutor` y la de A y B.

**progress.json** (`git show 2ba6ed5 -- docs/deuda/BE-50/progress.json`). JSON válido (`json.load` correcto). `Fase_C`: `pending`/`null` → `completed`/`"86b30f2"`, un hash real. `current_target`: `Fase_C` → `null`. Es correcto para la última fase: de las 25 carpetas de `docs/deuda/`, 23 tienen `progress.json` y las 23 dicen `"current_target": null`, contando BE-50. Las otras 22 son ítems cerrados; A2 y BE-07 no tienen `progress.json`. `last_handoff` está presente. `edit_rules`, `allowed_statuses` y las descripciones no cambiaron.

**Compuerta re-ejecutada por el auditor** (`./venv/Scripts/python.exe scripts/check.py --soft imports`, E1.1). Exit `0`. import-linter cargó y evaluó los contratos, así que rige E1.3 y se cumple.

Paso import-linter (literal, líneas significativas):
```
Analyzed 56 files, 148 dependencies.
------------------------------------

Capas: api | cli -> services -> repositories -> models KEPT
Los servicios no conocen el transporte HTTP KEPT
Los repositorios solo conocen SQLAlchemy y los modelos KEPT
Los modelos y los schemas no dependen de capas superiores KEPT

Contracts: 4 kept, 0 broken.
--- import-linter: OK en 1.0s
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

Otras líneas: `Python 3.14.3` · `72 files already formatted` · `All checks passed!` · `Success: no issues found in 67 source files` · `Documentación coherente (...)` · `TOTAL 1071 10 156 6 98.70%` · `Required test coverage of 92.0% reached. Total coverage: 98.70%` · `806 passed, 25 warnings in 34.93s`.

**E1.2:** (a) exit 0 ✔; (b) la última línea es `Compuerta superada.` ✔; (c) no hay ningún `✘` ✔; (d) no aplica. **E1.3:** `Contracts: 4 kept, 0 broken.` ✔.

**Ratchet frente a la línea base** (verificacion.md: 797 · 98,69 % · ruff 0 · mypy 0 en 66 · 4 kept):

| Medida | Línea base | Auditoría C | Lectura |
|---|---|---|---|
| pytest | 797 (799 tras B) | 806 passed, 0 failed | +7, los del plan |
| Cobertura | 98,69 % | 98,70 % (1071 sentencias, 156 ramas) | sube |
| ruff | 0 | 0 | igual |
| mypy | 0 en 66 (67 tras B) | 0 en 67 | igual |
| Contratos | 4 kept | 4 kept, 0 broken | igual |

Coincide con lo que pegó el ejecutor (handoff-Fase_C.md, "Compuerta de salida") y con lo que E0.3 midió en Linux.

**Archivos tocados.** `ruff check` sobre los cinco → `All checks passed!`; `ruff format --check` → `5 files already formatted`; `mypy` → `Success: no issues found in 5 source files`.

**Tests exigidos.** Los doce del plan (C1 a C12) existen. Corridos por nombre: `12 passed, 41 deselected`. Las cifras RED (`11 failed, 795 passed`) y los mutantes MC1-MC6 (MC2 con 9 y MC4 con 5, como dice E0.2) constan en el handoff con su salida; el auditor no los repitió.

**Verificación final** (plan.md:246-291, con E0.2; Git Bash, HEAD `2ba6ed5`, cuyo código es el de `86b30f2`):

| # | Resultado del auditor | Esperado |
|---|---|---|
| 1 | `0` | 0 |
| 2 | `159:` guarda / `162:` `changed_fields` | 1 y 1; la guarda antes |
| 3 | `1` / `1` / `0` | 1 / 1 / 0 |
| 4 | `7` | 7 (E0.2) |
| 5 | `0` | 0 |
| 6 | `app/models/user.py:57`, `tests/test_migration_email_verified_at.py:1`, `alembic/versions/e50a7c3d9b12_users_email_verified_at.py:1` | esos 3 |
| 7 | `tests/test_auth.py`, `tests/test_email.py`, `tests/test_email_case.py` | esos 3 |
| 8 | `8` | 8 |
| 9 | `5` / `app/services/user_service.py:163: user.email_verified_at = datetime.now(UTC)` / `0` | 5 / 1 escritura / 0 |
| 10 | `1` (`alembic heads` → `e50a7c3d9b12 (head)`) | 1 |
| 11 | `docs/adr/0022-la-marca-de-correo-verificado-decide-el-enlace.md`; `<FECHA` = `0` | 1 archivo; 0 |
| 12 | los 10 archivos de plan.md:294-297, ni uno más | los 10 |
| 13 | exit 0; 806 passed; 98,70 %; ruff 0; mypy 0; 4 kept | igual |

La deuda no aparece en el repo: no queda ningún "single-use" en `app` ni en `tests`, la marca tiene una sola escritura y no hay ningún test con el nombre viejo. Fuera de `app`, `alembic`, `tests` y `docs/adr`, la rama solo cambió `docs/` del ítem, la bitácora, `docs/backlog.md` y `docs/CONTEXT.md`. Esos tres últimos los tocaron solo commits de la sesión Mentor (`79839fb`, `271abf5`, `3998cb3`, `ba493f3`), ninguno de una fase.

**AGENTS §3-§5 en el código nuevo.** No hay excepción de dominio nueva, ni ruta, ni DTO. La marca no aparece en `app/schemas/` (comando 9, `0`), y C12 prueba que un PATCH no la escribe ni la expone. El servicio solo importa `datetime` de la biblioteca estándar (contratos KEPT). Los unitarios usan `user_repo` y `audit_service` con `create_autospec(..., instance=True)` (`tests/test_user_service.py:71-79`). Los de integración no usan mocks, construyen los usuarios con `persist_user` y las cabeceras con `make_auth_headers`, y hacen `refresh` después de cada petición (ADR-0011). Los tests no afirman ningún texto en español (comando 3, `0`): el segundo mensaje se compara como distinto del primero. La auditoría de ADR-0021 se mantiene: hay fila solo cuando `is_active` cambia (C2, C6, C7 y C8 lo afirman).
