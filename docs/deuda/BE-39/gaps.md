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

## Auditoría Fase C — 2026-11-11

**Veredicto Fase C: PASS (0 bloqueantes, 1 opcionales).**

Evidencia (auditor con contexto fresco, sobre `25bc30b`; commit de la fase `f980041`, padre `fb109e7`):

- Árbol: `git status --short` vacío antes y después de la compuerta.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`), exit 0: `61 files already formatted` ·
  `All checks passed!` · `Success: no issues found in 56 source files` · `Contracts: 4 kept, 0 broken.` · docs OK ·
  `Required test coverage of 92.0% reached. Total coverage: 96.29%` · `609 passed, 5 warnings in 17.25s` ·
  `Compuerta superada.` Frente a la línea base de `verificacion.md:180-190` (579 · 96,29 % · ruff 0 · mypy 0 / 55 · 4 kept):
  cobertura igual, ruff y mypy en 0, 4 kept. Coincide con la fila C del plan (`plan.md:156`) y con el handoff. Los 5
  warnings son los de siempre (`HTTP_422_UNPROCESSABLE_ENTITY` en `tests/test_services.py`, backlog S5).
- Archivos de la fase: `ruff check tests/test_route_guards.py tests/test_audit.py` → `All checks passed!`;
  `ruff format --check` → `2 files already formatted`; `mypy` sobre los dos → `Success: no issues found in 2 source files`;
  `pytest tests/test_route_guards.py -q -p no:cacheprovider` → `32 passed`.
- Contenido: el diff de `f980041` son exactamente las tres inserciones de `plan.md:351-373`: `from app.models.user import
  UserRole` tras `from app.main import app` (`tests/test_route_guards.py:15`); `ADMIN_ROUTES` entre el cierre de
  `PROTECTED_ROUTES` y `PUBLIC_ROUTES` con una línea en blanco a cada lado (`:58`); el test al final (`:120-137`). El bloque
  del test de `plan.md:355-372`, sin sangría, contra las últimas 18 líneas de `git show f980041:tests/test_route_guards.py`:
  `diff` vacío. 137 líneas, 0 bytes `\r`, termina en un solo `\n`; `i/lf w/lf` en los dos archivos.
  `tests/test_audit.py`: se borra exactamente `test_audit_trail_forbidden_for_tourist` (`git show 9ecc176:tests/test_audit.py`,
  `:50-59`) y las dos líneas en blanco que la seguían; el bloque `# ===…` de "UNIT TESTS" queda a dos líneas en blanco de
  `test_audit_trail_creation_and_retrieval` (`tests/test_audit.py:47-50`). `UserRole` sigue en uso (`:19`, `:69`, `:78`, `:111`).
- Criterio de aceptación: `grep -rn "test_audit_trail_forbidden_for_tourist" tests --include=*.py` → 0 líneas (y 0 para
  `test_audit_trail_requires_authentication`). `grep -rnE "status_code == 40[13]" tests --include=*.py | wc -l` → 30 y 0 en
  `tests/test_audit.py` (la cifra del paso 6 de la Verificación final); `grep -c "www-authenticate"` en el archivo nuevo → 2.
- Alcance: `git diff --name-only fb109e7 f980041` → solo `tests/test_audit.py` y `tests/test_route_guards.py`;
  `git diff --name-only 9ecc176 HEAD -- app alembic conftest.py tests/conftest.py` → 0 líneas. `25bc30b` toca solo
  `handoff-Fase_C.md` y `progress.json`. `app/` intacto: `get_current_admin_user` 15 y `assert_is_admin_plus(current_user)` 1.
- Mensaje de commit: `plan.md:390-408` sin la sangría y con `Claude Opus 5.5` en lugar de `<MODELO EJECUTOR>`, contra
  `git show -s --format=%B f980041`: la única diferencia es la línea vacía final que añade `%B`.
- `progress.json`: JSON válido; `Fase_C` `completed` con `f980041` (existe; `git show --stat` → 2 archivos, 21+, 12-);
  `current_target` = `Fase_D`; `last_handoff` presente; `Fase_A`, `Fase_B`, `Fase_D`, `Fase_E`, `edit_rules` y
  `allowed_statuses` sin cambios (diff `1e745e7..25bc30b`).
- Mutantes re-medidos en directorios nuevos y vacíos del scratchpad (`audC_nomut`, `audC_m1`, `audC_m2`, `audC_m3`,
  `audC_m4`, `audC_m5`, `audC_m4m5`, `audC_m6`, `audC_m7`, extraídos con `git archive f980041`; `find -name 'test_*probe*'`
  → 0 en los nueve). Ediciones de `plan.md:117-125` aplicadas con un script aparte (`audC_tools/mut.py`) que exige el número
  exacto de coincidencias (7 en M2, 6 en M3, 2 en M6, 1 en el resto); `diff -r -q` de cada copia contra `audC_nomut/app`
  solo muestra el archivo mutado. Suite sin `test_check*.py`:

  | Estado | Resultado | Plan (`plan.md:379-383`) |
  |---|---|---|
  | Sin mutante | `320 passed` | 320 passed |
  | M1 | `6 failed, 314 passed` (3 de turista + 3 anónimos: `upload-images`, `admin/inactivos`, `admin/eliminados`) | igual |
  | M2 | `9 failed, 311 passed` (las 9 de `/servicios`, turista) | igual |
  | M3 | `12 failed, 308 passed` (9 de turista + los 3 anónimos de M1) | igual |
  | M4 | `320 passed` (R1, declarado) | igual |
  | M5 | `1 failed, 319 passed` (`TestAuditServiceAuthorization::test_tourist_raises_authorization_error_and_repo_never_called`) | igual |
  | M4+M5 | `2 failed, 318 passed` (el unitario + `[GET /auditoria/]`) | igual |
  | M6 | `4 failed, 316 passed` (las 4 de `/usuarios`) | igual |
  | M7 | `13 failed, 307 passed` (las 13 admin salvo `[GET /auditoria/]`) | igual |

  Los `FAILED` coinciden uno a uno con los que pega el handoff.
- AGENTS: sin mocks; usuario y token salen de `persist_user` y `make_auth_headers`; identificadores y docstrings en inglés;
  se afirma sobre código, ausencia de cabecera, claves y tipo de `detail`, nunca sobre su texto; `app/` intacto.

Hallazgos:

[OPCIONAL] — Fase C (fuera del commit de la fase) — El commit `fb109e7`, padre de la fase, que añade la auditoría de B a este archivo, lleva como mensaje `docs/deuda/BE-39/gaps.md`, que no es Conventional Commits (AGENTS §9). No afecta al código ni al plan; si el PR no se fusiona con squash, conviene reescribir ese mensaje al preparar `/pr` (p. ej. `docs(item-be39): phase B audit PASS (0 blocking, 0 optional)`, en línea con `5e24d3e`) — evidencia: `git show -s --format=%s fb109e7` → `docs/deuda/BE-39/gaps.md`.

## Auditoría Fase D — 2026-11-11

**Veredicto Fase D: PASS (0 bloqueantes, 0 opcionales).**

Evidencia (auditor con contexto fresco, sobre `e960867`; commit de la fase `284cfe7`, padre `28d49be`):

- Árbol: `git status --short` vacío antes y después de la compuerta.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`), exit 0: `61 files already formatted` ·
  `All checks passed!` · `Success: no issues found in 56 source files` · `Contracts: 4 kept, 0 broken.` · docs OK ·
  `Required test coverage of 92.0% reached. Total coverage: 96.29%` · `612 passed, 5 warnings in 16.61s` ·
  `Compuerta superada.` Frente a la línea base de `verificacion.md:180-190` (579 · 96,29 % · ruff 0 · mypy 0 / 55 · 4 kept):
  cobertura igual, ruff y mypy en 0, 4 kept. Coincide con la fila D del plan (`plan.md:157`) y con el handoff. Los 5
  warnings son los de siempre (`HTTP_422_UNPROCESSABLE_ENTITY`, backlog S5).
- Archivo de la fase: `ruff check tests/test_route_guards.py` → `All checks passed!`; `ruff format --check` →
  `1 file already formatted`; `mypy tests/test_route_guards.py` → `Success: no issues found in 1 source file`;
  `pytest tests/test_route_guards.py -q -p no:cacheprovider` → `35 passed` (criterio de `plan.md:463`).
  `git ls-files --eol` → `i/lf w/lf`.
- Cambios exactos: reconstruí el archivo esperado (contenido de `28d49be` + el primer bloque de `plan.md:414-424` sin la
  sangría tras la línea `ADMIN_ROUTES: …` y una línea en blanco + el segundo bloque al final) y lo comparé con
  `git show 284cfe7:tests/test_route_guards.py`: idénticos byte a byte. `USER_ROUTES` en `tests/test_route_guards.py:60`,
  `_TOURIST_PAST_USER_GUARD` (200, 404, 404) en `:64-68`, `test_user_route_lets_tourist_through` en `:150-164`.
- Alcance: `git show --stat 284cfe7` → solo `tests/test_route_guards.py` (27+). `e960867` toca solo `handoff-Fase_D.md` y
  `progress.json`. `git diff --name-only 9ecc176 HEAD -- app alembic conftest.py tests/conftest.py` → 0 líneas; en `tests/`
  solo `tests/test_audit.py` y `tests/test_route_guards.py`. `app/` intacto: `get_current_admin_user` 15 y
  `assert_is_admin_plus(current_user)` 1. Tabla: 17 filas, 3 `"user"`.
- Mensaje de commit: `plan.md:468-482` sin la sangría y con `Claude Opus 5.5` en lugar de `<MODELO EJECUTOR>`, contra
  `git log -1 --format=%B 284cfe7` (con `strip`): idénticos.
- `progress.json`: JSON válido; `Fase_D` `completed` con `284cfe7` (existe; `git show --stat` → 1 archivo, 27+);
  `current_target` = `Fase_E`; `last_handoff` presente y describe la fase D; `Fase_A`, `Fase_B`, `Fase_C`, `Fase_E`,
  `allowed_statuses` y `edit_rules` sin cambios (diff `28d49be..e960867`; `edit_rules` igual que en `5b0537d`).
- Determinismo de los 404: `_PATH_PARAMS` usa la cédula `0000000000` (`tests/test_route_guards.py:85`) y `make_user` genera
  `1000000000 + n` (`tests/conftest.py:190`), así que el turista nunca coincide con la cédula de la ruta.
- Mutantes re-medidos en directorios nuevos y vacíos del scratchpad (`audD_nomut`, `audD_m12`, `audD_m13`, `audD_m14`,
  extraídos con `git archive 284cfe7`; `find -name 'test_*probe*'` → 0 en los cuatro). Ediciones de `plan.md:458-460`
  aplicadas con un script aparte (`audD_tools/mut.py`) que exige una sola coincidencia; `diff -r` contra `audD_nomut` solo
  muestra la línea mutada (M12 `tests/test_route_guards.py:39`, M13 `:53`, M14 `app/api/routers/user.py:36`). Suite sin
  `test_check*.py`:

  | Estado | Resultado | Plan (`plan.md:458-462`) |
  |---|---|---|
  | Sin mutante | `323 passed` | 323 passed |
  | M12 | `1 failed, 322 passed` (`test_user_route_lets_tourist_through[GET /usuarios/]`) | igual |
  | M13 (recíproco) | `1 failed, 322 passed` (`test_admin_route_rejects_tourist[GET /usuarios/mi-perfil]`) | igual |
  | M14 | `18 failed, 305 passed` (3 casos nuevos + `test_auth.py` 2, `test_token_failure_paths.py` 1, `test_user_access_policy.py` 2, `test_user_response.py` 10) | igual |

  Los `FAILED` coinciden uno a uno con los que pega el handoff.
- AGENTS: sin mocks; usuario y token salen de `persist_user` y `make_auth_headers`; identificadores, comentario y docstring
  en inglés; se afirma solo el código de estado (límite aceptado en E1), nunca texto; `app/` intacto.
- No es la última fase (queda `Fase_E`): la "Verificación final" de `plan.md:580-618` no se ejecuta en esta auditoría.

Hallazgos: ninguno.

## Auditoría Fase E — 2026-11-11

**Veredicto Fase E: PASS (0 bloqueantes, 0 opcionales).**

Evidencia (auditor con contexto fresco, sobre `6e4c66c`; commit de la fase `fee04bc`, padre `3b10acd`). Última fase del
ítem: incluye la Verificación final completa de `plan.md:580-620`, paso 12 incluido.

- Árbol: `git status --short` vacío antes y después de la compuerta y de los mutantes.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`), exit 0: `61 files already formatted` ·
  `All checks passed!` · `Success: no issues found in 56 source files` · `Contracts: 4 kept, 0 broken.` · docs OK ·
  `Required test coverage of 92.0% reached. Total coverage: 96.47%` · `622 passed, 8 warnings in 17.66s` ·
  `Compuerta superada.` Frente a la línea base de `verificacion.md:180-190` (579 · 96,29 % · ruff 0 · mypy 0 / 55 · 4 kept):
  +43 tests, cobertura +0,18, ruff y mypy en 0, 4 kept. Coincide con la fila E del plan (`plan.md:158`) y con el handoff.
  Los 8 warnings son todos `HTTP_422_UNPROCESSABLE_ENTITY` (backlog S5): los 5 de siempre más los 3 casos 422 nuevos
  (`[GET /usuarios/verificar-email]`, `[POST /usuarios/login]`, `[POST /usuarios/registro]`), efecto aceptado en E3.
- Archivo de la fase: `ruff check tests/test_route_guards.py` → `All checks passed!`; `mypy tests/test_route_guards.py` →
  `Success: no issues found in 1 source file`; `pytest tests/test_route_guards.py -q -p no:cacheprovider` → `45 passed`
  (criterio de `plan.md:553`). `git ls-files --eol` → `i/lf w/lf`.
- Cambios exactos: reconstruí el archivo esperado (`git show 284cfe7:tests/test_route_guards.py` + el bloque de
  `plan.md:490-502` sin la sangría, tras el cierre de `PUBLIC_ROUTES` y su línea en blanco y con una línea en blanco antes
  de `# Path parameters`, + el bloque de `plan.md:506-529` al final) y lo comparé con
  `git show fee04bc:tests/test_route_guards.py`: idénticos byte a byte (202 líneas, 0 bytes `\r`, un solo `\n` final).
  `_ANONYMOUS_ON_PUBLIC_ROUTE` en `tests/test_route_guards.py:84-96`; `test_route_tables_have_no_repeated_or_shared_entries`
  en `:181-189`; `test_public_route_answers_without_token` en `:192-202`. El inventario y las tablas de A no cambian.
- Alcance: `git show --stat fee04bc` → solo `tests/test_route_guards.py` (38+). `6e4c66c` toca solo `handoff-Fase_E.md` y
  `progress.json`.
- Mensaje de commit: `plan.md:559-577` sin la sangría y con `Claude Opus 5.5` en lugar de `<MODELO EJECUTOR>`, contra
  `git log -1 --format=%B fee04bc` sin la línea vacía final: `diff` vacío.
- `progress.json`: JSON válido; `Fase_E` `completed` con `fee04bc` (existe; `git show --stat` → 1 archivo, 38+);
  `current_target` = `null` (cierre del ítem; 14 de los 16 `progress.json` de `docs/deuda/` lo tienen así); `last_handoff`
  presente y describe la fase E; `Fase_A`…`Fase_D`, `allowed_statuses` y `edit_rules` sin cambios (diff de `6e4c66c`;
  `edit_rules` igual que en `5b0537d`).
- AGENTS: sin mocks ni fábricas (peticiones anónimas, solo `client`; el test de higiene no hace E/S); identificadores,
  comentario y docstrings en inglés; se afirma solo el código de estado y la estructura de las tablas, nunca texto; `app/`
  intacto.

Verificación final (`plan.md:585-620`), desde la raíz tras `6e4c66c`:

| Paso | Esperado | Medido |
|---|---|---|
| 1. `app`, `alembic`, conftests desde `9ecc176` | 0 | 0 |
| 2. Archivos de `tests/` cambiados | `test_audit.py`, `test_route_guards.py` | esos dos |
| 3. Filas / admin / user | 17 / 14 / 3 | 17 / 14 / 3 |
| 4. `pytest tests/test_route_guards.py` | 45 passed | `45 passed, 3 warnings in 0.78s` |
| 5. `www-authenticate` | 2 | 2 |
| 6. `status_code == 40[13]` suite / `test_audit.py` | 30 / 0 | 30 / 0 |
| 7. Patrón 1 en `test_services.py` / archivo nuevo | 0 / 4 | 0 / 4 |
| 8. Patrón 3 | 3 (`test_auth.py:109`, `test_services.py:648`, `:668`) | esas 3 |
| 9. Tests sustituidos | 0 | 0 |
| 10. `get_current_admin_user` / `assert_is_admin_plus(current_user)` en `app` | 15 / 1 | 15 / 1 |
| 11. Compuerta | exit 0, 622, 96,47 %, 61 files, mypy 56, 4 kept | exit 0, 622, 96,47 %, 61 files, mypy 56, 4 kept |

Paso 12, mutantes sobre el estado final: 19 copias en directorios nuevos y vacíos del scratchpad (`audE_NOMUT`, `audE_M1`…
`audE_M18`, `audE_M4M5`, `audE_M9a`; ningún `audE_*` existía), extraídas con `git archive HEAD` (`6e4c66c`; su
`tests/test_route_guards.py` es idéntico al del árbol, `cmp`); `find -name 'test_*probe*'` → 0 en las 19. Ediciones de
`plan.md:117-147`, `:456-460` y `:545-550` aplicadas con un script aparte (`audE_tools/apply.py`) que exige el número
exacto de coincidencias (7 en M2, 6 en M3, líneas 21 y 37 en M6, 1 en el resto); `diff -rq` de cada copia contra
`audE_NOMUT` solo muestra el archivo mutado. Suite sin `test_check*.py`:

| Mutante | Medido | Plan (`plan.md:616-620`) |
|---|---|---|
| Sin mutante | 333 passed | 333 |
| M1 | 6 failed, 327 passed (3 sin token + 3 turista: `upload-images`, `admin/inactivos`, `admin/eliminados`) | 6/327 |
| M2 | 9 failed, 324 passed (las 9 de `/servicios`, turista) | 9/324 |
| M3 | 12 failed, 321 passed (9 turista + los 3 sin token de M1) | 12/321 |
| M4 | 333 passed (R1) | 333 (sin rojo, R1) |
| M4+M5 | 2 failed, 331 passed (`TestAuditServiceAuthorization::test_tourist_raises_…` + `[GET /auditoria/]`) | 2/331 |
| M6 | 4 failed, 329 passed (las 4 admin de `/usuarios`) | 4/329 |
| M7 | 13 failed, 320 passed (las 13 admin salvo `[GET /auditoria/]`) | 13/320 |
| M9 | 17 failed, 316 passed (los 17 casos sin token) | 17/316 |
| M9a | 333 passed (equivalente) | 333 (sin rojo, equivalente) |
| M10 | 1 failed, 332 passed (inventario) | 1/332 |
| M11 | 4 failed, 329 passed (inventario, `[GET /servicios/admin/inactivos]` sin token y turista, `test_inactive_column_returns_off_rule_package`) | 4/329 |
| M12 | 1 failed, 332 passed (`test_user_route_lets_tourist_through[GET /usuarios/]`) | 1/332 |
| M13 | 1 failed, 332 passed (`test_admin_route_rejects_tourist[GET /usuarios/mi-perfil]`) | 1/332 |
| M14 | 18 failed, 315 passed (3 de usuario + `test_auth.py` 2, `test_token_failure_paths.py` 1, `test_user_access_policy.py` 2, `test_user_response.py` 10) | 18/315 |
| M15 | 1 failed, 331 passed (`test_public_route_answers_without_token[GET /usuarios/mi-perfil]`) | 1/331 |
| M16 | 1 failed, 334 passed (`test_route_tables_have_no_repeated_or_shared_entries`) | 1/334 |
| M17 | 2 failed, 332 passed (higiene + `test_public_route_answers_without_token[GET /usuarios/]`) | 2/332 |
| M18 | 2 failed, 332 passed (`test_protected_route_rejects_request_without_token[GET /servicios/]`, `test_admin_route_rejects_tourist[GET /servicios/]`) | 2/332 |

Las 19 cifras coinciden con el plan; M15–M18 coinciden además, `FAILED` a `FAILED`, con las que pega el handoff.

Hallazgos: ninguno.

Pendientes de cierre ya decididos (no son hallazgos de esta fase): la línea de AGENTS §3 (E0 punto 2, P1/R4) la escribe
David antes de `/pr`; el opcional 1 de la auditoría de A va a la descripción del PR (E2 punto 4); el opcional de la
auditoría de C (mensaje de `fb109e7`) se resuelve al preparar `/pr`; R1–R3 son notas para BE-40 y BE-42.
