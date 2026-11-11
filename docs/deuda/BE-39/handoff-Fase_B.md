# Handoff — BE-39 · Fase B (sin token: 401 con `WWW-Authenticate: Bearer` en las 17)

- **Commit de la fase:** `4612c42` — `test(guards): reject requests without a token on all 17 protected routes`
- **Ejecutor:** fase-ejecutor (Claude Opus 5.5), 11 nov 2026.

## Ritual de arranque

- `git status --short`: limpio. `HEAD` = `e8425ec` (plan aprobado con E0–E3).
- `current_target` = `Fase_B`. `gaps.md` de la fase A: PASS, 0 bloqueantes; sus 2 opcionales no son de esta fase.
- Vigencia de la línea base: `git fetch origin` correcto. `git rev-parse --short origin/develop` = `3ca990a`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `3ca990a`. Ambos iguales a `Base develop` de
  `verificacion.md`.
- Compuerta antes de tocar nada: exit 0, `61 files already formatted`, `All checks passed!`,
  `Success: no issues found in 56 source files`, `Contracts: 4 kept, 0 broken.`, `Total coverage: 96.29%`,
  `580 passed, 5 warnings in 16.37s`. Es la fila A del plan, así que la fase A no dejó nada roto.

## Archivos tocados

- `tests/test_route_guards.py`: las tres inserciones del plan (`import pytest`; `_PATH_PARAMS`, `_url` y `_route_id` entre
  `PUBLIC_ROUTES` y `_declared_routes`; `test_protected_route_rejects_request_without_token` al final). Comparé el archivo
  con el que dicta el plan (bloque de la fase A + las tres inserciones de la B, reconstruido desde `plan.md` sin la
  sangría): el `diff` solo muestra las dos líneas de cerca ``` que arrastró mi extractor, así que el contenido coincide.
- `tests/test_audit.py`: borrado `test_audit_trail_requires_authentication` (antes `:140-145`) y las dos líneas en blanco
  que lo precedían. El archivo termina en `    assert logs[0]["action"] == "CREATE"` + `\n`.
- Fin de línea: `git ls-files --eol` → `i/lf w/lf` en los dos.

`git show --stat 4612c42`:

```text
 tests/test_audit.py        |  8 --------
 tests/test_route_guards.py | 26 ++++++++++++++++++++++++++
 2 files changed, 26 insertions(+), 8 deletions(-)
```

## Mutantes (procedimiento común del plan)

Cada copia va en un directorio nuevo y vacío del scratchpad (`fbx_nomut`, `fbx_m9`, `fbx_m9a`; comprobé antes que no
existían). Se extrajo con `git -C C:/projects/ecotur-asoprado archive HEAD | tar -x -C <dir>` (HEAD = `e8425ec`) y encima
se copiaron `tests/test_route_guards.py` y `tests/test_audit.py` desde el árbol de trabajo.
`find <dir> -name 'test_*probe*'` no encontró nada en ninguna de las tres. Las ediciones se aplicaron con un script que
vive aparte (`fbx_tools/mutate.py`) y exige una coincidencia única por cada sustitución. En las tres copias,
`diff -r -q --strip-trailing-cr <copia>/app app` solo muestra `app/api/dependencies.py` (M9 y M9a) o nada (sin mutante),
y los dos tests son idénticos a los del árbol. Desde la copia, `app` se importa de la propia copia
(`fbx_m9\app\__init__.py`). Comando, desde cada `<dir>`:
`C:/projects/ecotur-asoprado/venv/Scripts/python.exe -m pytest -q -p no:cacheprovider -rf --ignore=tests/test_check.py --ignore=tests/test_check_docs.py`.

| Estado | Edición en `app/api/dependencies.py` | Resultado (literal) | Esperado por el plan |
|---|---|---|---|
| Sin mutante | — | `307 passed, 5 warnings in 10.09s` | 307 passed |
| M9 | M9a + `from datetime import UTC, datetime` y línea en blanco antes de `import jwt` + el bloque `if token is None: return User(...)` del plan antes de `credentials_exception = HTTPException(` | `17 failed, 290 passed, 5 warnings in 10.38s` | 17 failed, 290 passed |
| M9a | `OAuth2PasswordBearer(tokenUrl="usuarios/login", auto_error=False)` | `307 passed, 5 warnings in 10.57s` | 307 passed (equivalente) |

Diff de M9 en la copia contra `HEAD:app/api/dependencies.py`:

```text
0a1,2
> from datetime import UTC, datetime
>
19c21
< oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login")
---
> oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login", auto_error=False)
111a114,127
>     if token is None:
>         return User(
>             id=0,
>             cedula="0000000001",
>             email="anonymous@test.com",
>             first_name="Anonymous",
>             last_name="Caller",
>             password_hash="x",
>             role=UserRole.tourist,
>             data_consent=True,
>             is_active=True,
>             created_at=datetime(2026, 1, 1, tzinfo=UTC),
>         )
>
```

`FAILED` literales de M9 (los 17 casos del test nuevo, ninguno más):

```text
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[GET /usuarios/]
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[GET /usuarios/admin/eliminados]
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[PATCH /usuarios/{cedula}/recuperar]
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[POST /usuarios/admin]
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[POST /servicios/upload-images/]
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[POST /servicios/]
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[GET /servicios/admin/inactivos]
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[GET /servicios/admin/eliminados]
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[PUT /servicios/{service_id}]
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[PATCH /servicios/{service_id}/activar]
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[PATCH /servicios/{service_id}/desactivar]
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[DELETE /servicios/{service_id}]
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[PATCH /servicios/{service_id}/recuperar]
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[GET /auditoria/]
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[GET /usuarios/mi-perfil]
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[DELETE /usuarios/{cedula}]
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[PATCH /usuarios/{cedula}]
17 failed, 290 passed, 5 warnings in 10.38s
```

M9a (`auto_error=False` sin más) no tumba ningún test: `jwt.decode(None, …)` lanza `DecodeError` y `get_current_user`
responde el mismo 401. Es el mutante equivalente que declara el plan.

## Criterio de aceptación

- `pytest tests/test_route_guards.py -q -p no:cacheprovider` → `18 passed in 0.24s`.
- `grep -rn "test_audit_trail_requires_authentication" tests --include=*.py | wc -l` → `0`.
- Archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `2 files already formatted`;
  `mypy tests/test_route_guards.py tests/test_audit.py` → `Success: no issues found in 2 source files`.
- Compuerta completa (`./venv/Scripts/python.exe scripts/check.py`), exit 0. Son las cifras de la fila B del plan:
  `61 files already formatted` · `All checks passed!` · `Success: no issues found in 56 source files` ·
  `Contracts: 4 kept, 0 broken.` · `Required test coverage of 92.0% reached. Total coverage: 96.29%` ·
  `596 passed, 5 warnings in 16.90s`.

Bloque RESUMEN literal:

```text
=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

| Métrica | Línea base | Fin de A | Fin de B | Plan (fila B) |
|---|---|---|---|---|
| pytest | 579 passed | 580 passed | 596 passed | 596 passed |
| Cobertura | 96,29 % | 96,29 % | 96,29 % | 96,29 % |
| ruff format | 60 files | 61 files | 61 files | 61 files |
| ruff check | 0 errores | 0 errores | 0 errores | 0 |
| mypy | 55 source files, 0 errores | 56, 0 errores | 56, 0 errores | 56 |
| import-linter | 4 kept | 4 kept | 4 kept | 4 kept |
| warnings | 5 | 5 | 5 | — |

## Checklist test-sanitizer (Ecotur Enterprise Test Standards)

El test no usa mocks ni fixtures de usuario: las peticiones son anónimas y solo usa `client`. Nombres, docstrings y
variables están en inglés. Contrato `{"detail"}` con `set(body) == {"detail"}` y `isinstance(..., str)`, sin leer
texto humano. ABAC no aplica a esta fase (la cubren C y D). No hay nada que corregir.

## Desviaciones respecto del plan

No hay ninguna en código, cifras ni mensaje de commit. El mensaje se usó letra a letra, cambiando `<MODELO EJECUTOR>` por
`Claude Opus 5.5`. Lo comprobé con `git show -s --format=%B 4612c42`, que solo difiere del texto del plan en el salto de
línea final que añade `%B`.

Incidencia de proceso, sin efecto en el resultado: tras la primera edición (`import pytest` todavía sin uso), el hook
`ruff check --fix` quitó el import. Volví a añadirlo después de insertar el test que lo usa, y el archivo final es el del
plan.

## Residuales y dudas

- Ninguno nuevo. R1–R4 del plan siguen como están.
- Patrón 6 de la verificación final, a mitad de camino: `grep -rnE "status_code == 40[13]" tests --include=*.py | wc -l`
  → `30` (se quitó la línea `test_audit.py:144` y entró la aserción 401 del test nuevo; la C quita `:58` y añade la de 403).
- Fuera de alcance, sin tocar: los tests de turista y `test_audit_trail_forbidden_for_tourist` (fase C); D y E; `app/`.
- Directorios del scratchpad de esta fase: `fbx_nomut`, `fbx_m9`, `fbx_m9a`, `fbx_tools`, y los ficheros `fbx_*.out`,
  `fbx_gate_post.txt`, `fbx_msg.txt`, `fb_gate_pre.txt` y `fb_expected.py`. No se pueden borrar (`rm -rf` está denegado),
  así que la fase C debe crear directorios nuevos.
