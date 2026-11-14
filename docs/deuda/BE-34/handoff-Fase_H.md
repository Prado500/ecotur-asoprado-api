# Handoff — BE-34 · Fase H (E4: el turista del test de correo tomado sale de la fábrica)

- Commit de la fase: `5ec73d2` — `test(cli): build the taken-email tourist with the user factory` (mensaje exacto del
  plan, l. 1997-2013, con su trailer `Co-Authored-By`).
- Rama: `item/be-34`, sobre `0dd6770` (fase H escrita por E4 y aprobada por E5).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 14 nov 2026.
- Enmiendas que aplican: E4 (qué debe cumplir H) y E5 (aprobación, opción (a) en las seis decisiones).

## Ritual de arranque

- `git status --short`: limpio. HEAD `0dd6770`. `current_target` = `Fase_H`. `gaps.md`: A–G PASS, 0 bloqueantes.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `4f10660`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `4f10660`; `Base develop` de `verificacion.md` = `4f10660`.
- Compuerta antes de tocar nada (exit 0), igual a la fila G del plan: `68 files already formatted` ·
  `All checks passed!` · `Success: no issues found in 63 source files` · `Contracts: 4 kept, 0 broken.` ·
  `TOTAL 1034 15 148 13 97.63%` · `691 passed, 8 warnings in 30.09s` · `Compuerta superada.`

## Archivo tocado (el único de la fase)

`git show --stat --format= 5ec73d2`:

```
 tests/test_bootstrap_superadmin_command.py | 36 +++++++++++++++---------------
 1 file changed, 18 insertions(+), 18 deletions(-)
```

`git show --numstat --format= 5ec73d2` (= criterio de aceptación):

```
18	18	tests/test_bootstrap_superadmin_command.py
```

Cómo se escribió (instrucción de David: el import de `Callable` en la misma edición que la firma que lo usa):
- Mi conjunto de herramientas no tiene MultiEdit. En su lugar, **una sola llamada a `Write`** sobre el archivo entero, con
  todas las sustituciones de la fase a la vez: `from collections.abc import Callable` tras `import sys`; `insert` fuera
  del import de `sqlalchemy`; `AsyncSession` en el de `sqlalchemy.ext.asyncio`; el ayudante `_add` entre `_execute` y
  `_count`; la firma con `make_user: Callable[..., User]`, y la llamada de una línea en lugar de las 15 del
  `insert(User)`. El hook corrió una vez, ya con el import en uso. Ni sed ni scripts.
- Error mío en esa escritura: dupliqué la línea `assert completed.returncode == 0, completed.stderr` del último test. Lo
  corregí con un `Edit` de esa sola línea, antes de cualquier prueba o commit. El commit no lo lleva (el `numstat` lo
  confirma).
- Comprobado antes del commit: `grep -n` → `13:from collections.abc import Callable`, `129:` (parámetro `make_user`),
  `132:` (llamada); `git diff --numstat` → `18	18`; 0 `\r` (LF), UTF-8.
- Sobre el archivo: `ruff format --check` → `1 file already formatted`; `ruff check` → `All checks passed!`;
  `mypy` → `Success: no issues found in 1 source file`;
  `./venv/Scripts/python.exe -m pytest tests/test_bootstrap_superadmin_command.py -q -p no:cacheprovider` → `8 passed in 1.91s`.

## Tests (RED → GREEN)

H no fija comportamiento nuevo; el RED es el paso 20 de la Verificación final, que en `HEAD` (`0dd6770`) daba:

```
tests/test_bootstrap_superadmin_command.py:17:from sqlalchemy import func, insert, select
tests/test_bootstrap_superadmin_command.py:121:            insert(User).values(
exit=0
```

Tras H: sin salida, `exit=1` (ver paso 20 abajo).

## Mutantes (procedimiento común: `git archive HEAD | tar -x` en un directorio nuevo del scratchpad por mutante)

Herramienta: un script de Python del scratchpad que exige una sola aparición de cada ancla. Comando, desde la copia:
`C:/projects/ecotur-asoprado/venv/Scripts/python.exe -m pytest -q -p no:cacheprovider -rf --tb=no --ignore=tests/test_check.py --ignore=tests/test_check_docs.py`.

1. Antes de editar, sobre la copia de `HEAD` (`0dd6770`):

```
=== base_ME2
FAILED tests/test_bootstrap_superadmin_command.py::test_command_fails_when_the_email_belongs_to_another_account
1 failed, 401 passed, 8 warnings in 21.22s
=== base_MD5
FAILED tests/test_bootstrap_superadmin_command.py::test_command_fails_when_the_email_belongs_to_another_account
FAILED tests/test_email_case.py::test_bootstrap_rejects_an_email_taken_in_another_case
FAILED tests/test_superadmin_bootstrap.py::test_bootstrap_never_takes_over_an_existing_account[active-tourist-cedula]
FAILED tests/test_superadmin_bootstrap.py::test_bootstrap_never_takes_over_an_existing_account[active-tourist-email]
FAILED tests/test_superadmin_bootstrap.py::test_bootstrap_never_takes_over_an_existing_account[inactive-admin-cedula]
FAILED tests/test_superadmin_bootstrap.py::test_bootstrap_never_takes_over_an_existing_account[inactive-admin-email]
FAILED tests/test_superadmin_bootstrap.py::test_bootstrap_never_takes_over_an_existing_account[deleted-superadmin-cedula]
FAILED tests/test_superadmin_bootstrap.py::test_bootstrap_never_takes_over_an_existing_account[deleted-superadmin-email]
8 failed, 394 passed, 8 warnings in 23.00s
=== base_MH1
FAILED tests/test_bootstrap_superadmin_command.py::test_command_fails_when_the_email_belongs_to_another_account
1 failed, 401 passed, 8 warnings in 20.72s
=== base_MH2
FAILED tests/test_bootstrap_superadmin_command.py::test_command_fails_when_the_email_belongs_to_another_account
1 failed, 401 passed, 8 warnings in 19.85s
=== base_MH3
FAILED tests/test_bootstrap_superadmin_command.py::test_command_fails_when_the_email_belongs_to_another_account
FAILED tests/test_email_case.py::test_registration_rejects_an_email_taken_in_another_case
FAILED tests/test_email_case.py::test_provisioning_rejects_an_email_taken_in_another_case
FAILED tests/test_email_case.py::test_bootstrap_rejects_an_email_taken_in_another_case
FAILED tests/test_superadmin_bootstrap.py::test_bootstrap_never_takes_over_an_existing_account[active-tourist-email]
FAILED tests/test_superadmin_bootstrap.py::test_bootstrap_never_takes_over_an_existing_account[inactive-admin-email]
FAILED tests/test_superadmin_bootstrap.py::test_bootstrap_never_takes_over_an_existing_account[deleted-superadmin-email]
7 failed, 395 passed, 8 warnings in 22.35s
```

2. Tras el commit, sobre la copia de `5ec73d2` (A–H):

```
=== h_ME2
FAILED tests/test_bootstrap_superadmin_command.py::test_command_fails_when_the_email_belongs_to_another_account
1 failed, 401 passed, 8 warnings in 20.64s
=== h_MD5
(los mismos 8 FAILED que base_MD5)
8 failed, 394 passed, 8 warnings in 22.96s
=== h_MH1
FAILED tests/test_bootstrap_superadmin_command.py::test_command_fails_when_the_email_belongs_to_another_account
1 failed, 401 passed, 8 warnings in 21.06s
=== h_MH2
FAILED tests/test_bootstrap_superadmin_command.py::test_command_fails_when_the_email_belongs_to_another_account
1 failed, 401 passed, 8 warnings in 20.80s
=== h_MH3
(los mismos 7 FAILED que base_MH3)
7 failed, 395 passed, 8 warnings in 22.18s
```

   Comparación de base y H (líneas `FAILED` y última línea, sin los tiempos): `ME2 identical`, `MD5 identical`,
   `MH1 identical`, `MH2 identical`, `MH3 identical`.

3. MHT1 y MHT2, sobre copias de `5ec73d2`:

```
=== h_MHT1
FAILED tests/test_bootstrap_superadmin_command.py::test_command_fails_when_the_email_belongs_to_another_account
1 failed, 401 passed, 8 warnings in 20.96s
=== h2_MHT2
402 passed, 8 warnings in 20.14s
```

   MHT2 con `-X dev` sobre el archivo de la copia: `grep -c ResourceWarning` → `1`. `diff` de cada copia frente al repo:
   MHT1 `75d74 <         await session.commit()`; MHT2 `76d75 <     await engine.dispose()`.
   La primera ejecución de MHT2 (directorio `mut_h_MHT2`) no llegó a correr: el ancla de mi script tenía 12 espacios
   de sangría en vez de 8 y salió con `anchor found 0 times`. Corregí el ancla y repetí en un directorio nuevo
   (`mut_h2_MHT2`); el plan no cambia.

Todos los resultados = tabla del plan (ME2, MD5 con las cifras de "Aplicación de E4"; MH1–MH3, MHT1, MHT2).

## Compuerta tras H (`./venv/Scripts/python.exe scripts/check.py`, exit 0)

```
68 files already formatted
All checks passed!
Success: no issues found in 63 source files
Contracts: 4 kept, 0 broken.
--- docs (coherencia): OK en 0.1s
TOTAL                                       1034     15    148     13  97.63%
691 passed, 8 warnings in 28.49s
=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

= fila H del plan. Ratchet: 691 passed (= línea base de la fase), cobertura 97,63 % (=), 4 kept (=), ruff y mypy 0 (=).

## Verificación final (pasos de tras H; el 19 es de David y no se ejecutó)

- **20** → sin salida, `exit=1`.
- **21** → `tests/test_bootstrap_superadmin_command.py:129` (parámetro) y `:132` (llamada).
- **22** → `tests/test_bootstrap_superadmin_command.py | 36 +++++++++++++++---------------` ·
  `1 file changed, 18 insertions(+), 18 deletions(-)`.
- **23** → `0` (con MHT2, `1`).
- **16** (recalculado) → 7 archivos: la migración `b51f3c9e2a64`, `app/models/user.py`, `app/schemas/user.py`,
  `docs/adr/0016-correo-en-minusculas.md`, `tests/test_bootstrap_superadmin_command.py`, `tests/test_email_case.py`,
  `tests/test_user_response.py`.
- **18** → la compuerta de arriba.
- Los que H no cambia, repetidos: 1 → `exit=1`; 2/17 → 9 líneas (`.env.example:6`, `app/cli/bootstrap_superadmin.py:19`,
  `app/core/config.py:12`, `app/repositories/user_repository.py:1`, `app/services/superadmin_bootstrap.py:3`,
  `tests/test_bootstrap_superadmin_command.py:16`, `tests/test_config.py:41`, `tests/test_email_case.py:5`,
  `tests/test_superadmin_bootstrap.py:11`), suma 114; 3 → 4 líneas (`bootstrap_superadmin.py:90`,
  `superadmin_bootstrap.py:60`, `user_service.py:88`, `:412`); 4 → `dependencies.py:199`, `routers/user.py:35`,
  `user_access_policy.py:67`, `:72`; 5 → `tests/test_config.py:243`; 6 → los 3 archivos de G,
  `3 files changed, 49 insertions(+), 5 deletions(-)`; 7 → 17 archivos; 8 → `15 6`; 10 → `exit=1`; 11 → `:18`, `:44`,
  `:56`; 12 → `app/schemas/user.py:22`, `:39`, `:134`, `:166`; 13 → migración `:2`, `app/models/user.py:1`,
  `app/schemas/user.py:1`, `tests/test_email_case.py:2`; 14 → `b51f3c9e2a64 (head)`; 15 → contiene
  `ALTER TABLE users ADD CONSTRAINT ck_users_email_lowercase CHECK (email = lower(email));`.

## Checklist `test-sanitizer` (Ecotur Enterprise Test Standards)

1. Mocks con `spec`: no hay mocks. 2. Fábricas: el turista sale de `make_user` (el objetivo de H). 3. Inglés: sí.
4. Contrato JSON: no aplica (comando; códigos de salida). 5. ABAC: no aplica. Ninguna aserción cambió.

## Residuales y dudas

- Ningún hallazgo nuevo. No se tocó `app/`, ningún `conftest.py` ni otro test.
- Desviación de forma: la instrucción pedía MultiEdit; no está en mis herramientas, y usé un único `Write` con todas las
  sustituciones (mismo efecto: import y uso en la misma edición).
