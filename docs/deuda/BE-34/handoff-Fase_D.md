# Handoff — BE-34 · Fase D (`UserRepository.count_active_superadmins` y núcleo `bootstrap_superadmin`)

- Commit de la fase: `e9d010c` — `feat(users): create the first superadmin only when no active one exists` (mensaje
  exacto del plan, trailer `Co-Authored-By` incluido; `diff` contra las l. 831-850 de `plan.md` sin la sangría →
  `IDENTICAL`).
- Rama: `item/be-34`, sobre `a5cd7b5` (plan aprobado entero: E0, E1, E2, E3).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 14 nov 2026.
- Enmiendas que aplican: ninguna cambia la fase D (E0: "fases A → B → C → D como están escritas"; E2 punto 1 y E3: "las
  fases A → E quedan aprobadas tal como están escritas").

## Ritual de arranque

- `git status --short`: limpio. HEAD `a5cd7b5`. `current_target` = `Fase_D`. `gaps.md`: A, B y C PASS, 0 bloqueantes.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `4f10660`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `4f10660`; `Base develop` de `verificacion.md` = `4f10660`.
- Compuerta antes de tocar nada (exit 0), igual a la fila C del plan:
  `61 files already formatted` · `All checks passed!` · `Success: no issues found in 56 source files` ·
  `Contracts: 4 kept, 0 broken.` · `650 passed, 8 warnings` · `TOTAL 966 18 136 15 97.01%`.

## Archivos tocados (los cuatro de la fase)

`git show --stat --format= e9d010c` (última línea): `4 files changed, 296 insertions(+), 1 deletion(-)`.

`git show --numstat --format= e9d010c` (criterio de aceptación: `22 1`, `74 0`, `159 0`, `41 0`):

```
22	1	app/repositories/user_repository.py
74	0	app/services/superadmin_bootstrap.py
159	0	tests/test_superadmin_bootstrap.py
41	0	tests/test_user_repository.py
```

Cómo se escribió (aviso del auditor de A sobre el hook F401): `user_repository.py` se editó en una sola escritura con un
script de Python que sustituye anclas únicas (`assert s.count(old) == 1`), así `func` y `UserRole` entraron en la misma
escritura que su primer uso. Los dos archivos nuevos de `app/` y `tests/test_superadmin_bootstrap.py` se crearon con un
heredoc (el hook no corre; `ruff format --check` y `ruff check` se pasaron a mano). `tests/test_user_repository.py` se
creó con la herramienta Write (corrió el hook; `wc -l` = 41, sin cambios). Los cuatro blobs del commit y del árbol están
en UTF-8 con LF (0 bytes `\r`, contados con Python sobre `git show HEAD:<archivo>` y sobre el archivo).

## TDD

1. `tests/test_user_repository.py` primero →
   `./venv/Scripts/python.exe -m pytest tests/test_user_repository.py -q -p no:cacheprovider -rf --tb=no`:
   `5 failed in 0.11s`; causa: `AttributeError: 'UserRepository' object has no attribute 'count_active_superadmins'`
   (= plan).
2. Con el método: `5 passed in 0.13s`. Después `tests/test_superadmin_bootstrap.py`, antes del servicio:
   `E   ModuleNotFoundError: No module named 'app.services.superadmin_bootstrap'` ·
   `Interrupted: 1 error during collection` (= plan).
3. Con el servicio, los dos archivos: `17 passed in 1.32s` (= plan).

## Compuerta al cerrar (exit 0)

Archivos tocados: `ruff format --check` (los 4) → `4 files already formatted`; `ruff check` → `All checks passed!`;
`mypy` (los 4) → `Success: no issues found in 4 source files`.

`./venv/Scripts/python.exe scripts/check.py` → exit 0:

```
64 files already formatted
All checks passed!
Success: no issues found in 59 source files
Contracts: 4 kept, 0 broken.
TOTAL                                        988     18    140     15  97.07%
667 passed, 8 warnings in 24.92s
=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

Igual a la fila D del plan (667 passed · 97,07 % (988) · 64 files · 59 source files). Ratchet frente a C: +17 tests,
cobertura 97,01 % → 97,07 %, 4 kept, 0 errores de ruff y mypy.

## Mutantes (procedimiento común: copia nueva de `git archive HEAD` sobre `e9d010c`, un directorio por mutante)

Comando en cada copia: `C:/projects/ecotur-asoprado/venv/Scripts/python.exe -m pytest -q -p no:cacheprovider -rf --tb=no --ignore=tests/test_check.py --ignore=tests/test_check_docs.py`.
Cada edición se aplicó con un script que exige una sola aparición del texto original.

- Copia limpia: `378 passed, 8 warnings in 16.93s` (= columna "Suite de la copia" de la fila D).
- MD1 (borrar `User.is_active.is_(True),`):
  ```
  FAILED tests/test_superadmin_bootstrap.py::test_bootstrap_creates_when_no_superadmin_can_sign_in[inactive]
  FAILED tests/test_user_repository.py::test_count_active_superadmins_skips_those_who_cannot_sign_in[inactive]
  2 failed, 376 passed, 8 warnings in 16.03s
  ```
- MD2 (borrar `User.deleted_at.is_(None),`):
  ```
  FAILED tests/test_user_repository.py::test_count_active_superadmins_skips_those_who_cannot_sign_in[deleted-but-active-flag]
  1 failed, 377 passed, 8 warnings in 16.50s
  ```
- MD3 (borrar `User.role == UserRole.superadmin,`):
  ```
  FAILED tests/test_superadmin_bootstrap.py::test_bootstrap_never_takes_over_an_existing_account[active-tourist-cedula]
  FAILED tests/test_superadmin_bootstrap.py::test_bootstrap_never_takes_over_an_existing_account[active-tourist-email]
  FAILED tests/test_user_repository.py::test_count_active_superadmins_counts_each_active_one
  3 failed, 375 passed, 8 warnings in 16.30s
  ```
- MD4 (`> 0:` → `> 1:`):
  ```
  FAILED tests/test_superadmin_bootstrap.py::test_bootstrap_writes_nothing_when_an_active_superadmin_exists
  FAILED tests/test_superadmin_bootstrap.py::test_bootstrap_second_run_writes_nothing
  2 failed, 376 passed, 8 warnings in 16.62s
  ```
- MD5 (`    if existing_user:` → `    if False:`):
  ```
  FAILED tests/test_superadmin_bootstrap.py::test_bootstrap_never_takes_over_an_existing_account[active-tourist-cedula]
  FAILED tests/test_superadmin_bootstrap.py::test_bootstrap_never_takes_over_an_existing_account[active-tourist-email]
  FAILED tests/test_superadmin_bootstrap.py::test_bootstrap_never_takes_over_an_existing_account[inactive-admin-cedula]
  FAILED tests/test_superadmin_bootstrap.py::test_bootstrap_never_takes_over_an_existing_account[inactive-admin-email]
  FAILED tests/test_superadmin_bootstrap.py::test_bootstrap_never_takes_over_an_existing_account[deleted-superadmin-cedula]
  FAILED tests/test_superadmin_bootstrap.py::test_bootstrap_never_takes_over_an_existing_account[deleted-superadmin-email]
  6 failed, 372 passed, 8 warnings in 18.16s
  ```
- MD6 (`role=UserRole.superadmin,` → `role=credentials.role,`):
  ```
  FAILED tests/test_superadmin_bootstrap.py::test_bootstrap_always_creates_an_active_superadmin
  1 failed, 377 passed, 8 warnings in 17.02s
  ```
- MD7 (`is_active=True,` → `is_active=credentials.is_active,`):
  ```
  FAILED tests/test_superadmin_bootstrap.py::test_bootstrap_always_creates_an_active_superadmin
  1 failed, 377 passed, 8 warnings in 16.20s
  ```

Los siete = tabla del plan. Directorios: `scratchpad/mut_D_{MD1..MD7}` y `scratchpad/copy_D_clean` (no se borran).

## Fuera de alcance respetado

`git diff --stat a5cd7b5 e9d010c -- conftest.py tests/conftest.py alembic app/api app/main.py pyproject.toml app/core
app/models app/schemas app/services/user_service.py app/services/user_access_policy.py` → vacío. `create_user` y su
`commit()` (A3) sin cambios; el comando (fase E) no existe todavía.

## test-sanitizer (checklist)

Tests dictados por el plan, sin reescribir: sin mocks (repositorios reales sobre la base de prueba); usuarios con la
fábrica `persist_user`, nunca a mano; nombres en inglés; ninguna aserción sobre texto en español (tipos de excepción,
filas, roles, banderas y el `changes` de la auditoría); la escalada (promover, reactivar o recuperar una cuenta) cubierta
por la matriz de 6 casos que MD5 tumba entera.

## Residuales y dudas

- Ninguno nuevo. Observación sin acción: con el servicio aún sin crear, `ruff check` marca `I001` en
  `tests/test_superadmin_bootstrap.py` porque clasifica `app.services.superadmin_bootstrap` como de terceros; desaparece
  al existir el módulo (verificado: `All checks passed!` en el estado commiteado).
