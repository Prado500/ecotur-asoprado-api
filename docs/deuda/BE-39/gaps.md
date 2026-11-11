# Gaps — BE-39

## Auditoría Fase A — 2026-11-11

**Veredicto Fase A: PASS (0 bloqueantes, 2 opcionales).**

Evidencia (auditor con contexto fresco, sobre `f551351`; commit de la fase `d89e942`):

- Árbol: `git status --short` vacío antes y después de la compuerta.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`), exit 0: `61 files already formatted` ·
  `All checks passed!` · `Success: no issues found in 56 source files` · `Contracts: 4 kept, 0 broken.` · docs OK ·
  `Required test coverage of 92.0% reached. Total coverage: 96.29%` · `580 passed, 5 warnings in 17.78s` ·
  `Compuerta superada.` Frente a la línea base de `verificacion.md:180-190` (579 · 96,29 % · ruff 0 · mypy 0 / 55 · 4 kept):
  +1 test, cobertura igual, ruff y mypy en 0. Coincide con la fila A del plan y con el handoff.
- Archivo de la fase: `ruff check tests/test_route_guards.py` → `All checks passed!`; `ruff format --check` → `1 file
  already formatted`; `mypy tests/test_route_guards.py` → `Success: no issues found in 1 source file`;
  `pytest tests/test_route_guards.py -q` → `1 passed`.
- Contenido: `plan.md:163-252` sin la sangría de dos espacios contra `git show d89e942:tests/test_route_guards.py`: `diff`
  vacío (idéntico byte a byte; `i/lf w/lf`). Tabla: 17 filas, 14 `"admin"`, 3 `"user"`; sin duplicados y sin solapes
  entre `PROTECTED_ROUTES` y `PUBLIC_ROUTES` (medido importando el módulo).
- Alcance: `git diff --name-only 72492af d89e942` → solo `tests/test_route_guards.py`; `git diff --name-only 9ecc176 HEAD --
  app alembic conftest.py tests/conftest.py` → 0 líneas. `f551351` toca solo `handoff-Fase_A.md` y `progress.json`.
- Mensaje de commit: `plan.md:262-276` contra `git show -s --format=%B d89e942` con `Claude Opus 5.5` → `<MODELO EJECUTOR>`:
  `diff` vacío.
- `progress.json`: JSON válido; `Fase_A` `completed` con `d89e942` (existe, `git show --stat` → 1 archivo, 90 inserciones);
  `current_target` = `Fase_B`; `last_handoff` presente; `edit_rules` y `allowed_statuses` intactos.
- Mutantes re-medidos en directorios nuevos y vacíos del scratchpad (`audA_nomut`, `audA_m10`, `audA_m11`, extraídos con
  `git archive d89e942`; `find -name 'test_*probe*'` vacío en los tres), suite sin `test_check*.py`:
  sin mutante `291 passed`; M10 `1 failed, 290 passed` (`test_every_route_is_listed_as_protected_or_public`); M11
  `2 failed, 289 passed` (el inventario y `tests/test_services.py::test_inactive_column_returns_off_rule_package`).
  Las tres cifras son las del plan (`plan.md:254-256`) y las del handoff.
- AGENTS: sin mocks ni fixtures en la fase; identificadores, docstrings y mensaje de aserción en inglés; ninguna aserción
  sobre texto en español; `app/` intacto.

Hallazgos:

[OPCIONAL] — Fase A — El cuerpo del commit dice "The rejection tests that read the table come in the next two commits"; tras E0 vienen tres fases (B, C, D). El texto es el que dicta el plan y E0 congeló los commits de A, B y C, así que no es una desviación; el handoff ya lo declara. Sin acción; si se quiere, se aclara en la descripción del PR — evidencia: `git show -s d89e942` (línea 13 del cuerpo), `plan.md:273-274`, `plan.md:531-532`.
[OPCIONAL] — Fase A — El inventario prueba que cada ruta esté en alguna tabla, no que esté en la correcta: una ruta protegida nueva que se anote por error en `PUBLIC_ROUTES` sale de los tests de rechazo de B y C y nadie lo nota (la fase D cubre solo el error "admin" anotado como "user"). Tampoco detecta una entrada que esté a la vez en las dos tablas ni una fila duplicada, porque compara conjuntos (hoy hay 0 de cada, medido). Queda fuera del plan aprobado; destino posible: nota al cierre o fila de backlog (p. ej. un caso "pública sin token no responde 401") — evidencia: `tests/test_route_guards.py:86-90` (`protected | PUBLIC_ROUTES` como conjuntos).

## Auditoría Fase B — 2026-11-11

**Veredicto Fase B: PASS (0 bloqueantes, 0 opcionales).**

Evidencia (auditor con contexto fresco, sobre `1e745e7`; commit de la fase `4612c42`, padre `e8425ec`):

- Árbol: `git status --short` vacío antes y después de la compuerta.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`), exit 0: `61 files already formatted` ·
  `All checks passed!` · `Success: no issues found in 56 source files` · `Contracts: 4 kept, 0 broken.` · docs OK ·
  `Required test coverage of 92.0% reached. Total coverage: 96.29%` · `596 passed, 5 warnings in 15.72s` ·
  `Compuerta superada.` Frente a la línea base de `verificacion.md:180-190` (579 · 96,29 % · ruff 0 · mypy 0 / 55 · 4 kept):
  cobertura igual, ruff y mypy en 0, 4 kept. Coincide con la fila B del plan (`plan.md:155`) y con el handoff. Los 5 warnings
  son los de siempre (`HTTP_422_UNPROCESSABLE_ENTITY`, backlog S5), ninguno de los archivos de la fase.
- Archivos de la fase: `ruff check tests/test_route_guards.py tests/test_audit.py` → `All checks passed!`;
  `ruff format --check` → `2 files already formatted`; `mypy` sobre los dos → `Success: no issues found in 2 source files`;
  `pytest tests/test_route_guards.py -q -p no:cacheprovider` → `18 passed`.
- Contenido: reconstruí el archivo que dicta el plan (bloque de A, `plan.md:166-255`, más las tres inserciones de B,
  `plan.md:285-316`, colocadas donde dice el texto) y lo comparé con `git show 4612c42:tests/test_route_guards.py`: idéntico
  (0 bytes `\r`, 116 líneas, termina en un solo `\n`). Inserciones en `tests/test_route_guards.py:11` (`import pytest`),
  `:71-83` (`_PATH_PARAMS`, `_url`, `_route_id`) y `:107-116` (el test). `tests/test_audit.py`: el diff borra exactamente
  `test_audit_trail_requires_authentication` (antes `:140-145`, `git show 9ecc176:tests/test_audit.py`) y las dos líneas en
  blanco previas; el archivo termina en `    assert logs[0]["action"] == "CREATE"\n`. `i/lf w/lf` en los dos.
- Criterio de aceptación: `grep -rn "test_audit_trail_requires_authentication" tests --include=*.py` → 0 líneas;
  `test_audit_trail_forbidden_for_tourist` sigue en `tests/test_audit.py:50` (es de la fase C, fuera de alcance aquí).
  `grep -rnE "status_code == 40[13]" tests --include=*.py | wc -l` → 30 (a mitad de camino del paso 6 de la Verificación final).
- Alcance: `git diff --name-only e8425ec 4612c42` → solo `tests/test_audit.py` y `tests/test_route_guards.py`;
  `git diff --name-only 9ecc176 HEAD -- app alembic conftest.py tests/conftest.py` → 0 líneas. `1e745e7` toca solo
  `handoff-Fase_B.md` y `progress.json`.
- Mensaje de commit: `plan.md:327-345` sin la sangría y con `Claude Opus 5.5` en lugar de `<MODELO EJECUTOR>`, contra
  `git show -s --format=%B 4612c42`: la única diferencia es la línea vacía final que añade `%B`.
- `progress.json`: JSON válido; `Fase_B` `completed` con `4612c42` (existe; `git show --stat` → 2 archivos, 26+, 8-);
  `current_target` = `Fase_C`; `last_handoff` presente; `Fase_A`, `edit_rules` y `allowed_statuses` sin cambios (diff de
  `1e745e7`).
- Mutantes re-medidos en directorios nuevos y vacíos del scratchpad (`audB_nomut`, `audB_m9`, `audB_m9a`, extraídos con
  `git archive 4612c42`; `find -name 'test_*probe*'` vacío en los tres). Ediciones aplicadas con un script aparte
  (`audB_tools/mut.py`) que exige una sola coincidencia por sustitución; `diff -r -q` contra `app/` solo muestra
  `app/api/dependencies.py` en M9 y M9a (y el CRLF de trabajo de `app/api/__init__.py`, que en el índice es LF). Suite sin
  `test_check*.py`: sin mutante `307 passed`; M9 `17 failed, 290 passed`, los 17 `FAILED` son los casos de
  `test_protected_route_rejects_request_without_token` y ninguno más; M9a `307 passed` (equivalente, como declara el plan).
  Las tres cifras son las de `plan.md:319-321` y las del handoff.
- AGENTS: sin mocks ni fábricas en la fase (peticiones anónimas, solo `client`); identificadores y docstrings en inglés;
  las aserciones miran código, cabecera, claves y tipo, nunca el texto de `detail`; `app/` intacto.

Hallazgos: ninguno.
