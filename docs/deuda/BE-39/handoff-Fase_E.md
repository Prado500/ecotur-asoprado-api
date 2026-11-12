# Handoff — BE-39 · Fase E (cada ruta pública responde sin token y las tablas no repiten ni comparten filas, E2)

- **Commit de la fase:** `fee04bc` — `test(guards): pin public routes without a token and table hygiene`
- **Ejecutor:** fase-ejecutor (Claude Opus 5.5), 11 nov 2026. Última fase del ítem (`current_target` → `null`).

## Ritual de arranque

- `git status --short`: limpio. `HEAD` = `3b10acd` (`gaps.md` con la auditoría de D: PASS, 0 bloqueantes, 0 opcionales).
- `current_target` = `Fase_E`.
- Vigencia de la línea base: `git fetch origin` correcto. `git rev-parse --short origin/develop` = `3ca990a`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `3ca990a`. Ambos iguales a `Base develop` de
  `verificacion.md`.
- Compuerta antes de tocar nada: exit 0, todos los pasos en verde, `Total coverage: 96.29%`,
  `612 passed, 5 warnings in 15.34s`. Es la fila D del plan: la fase D no dejó nada roto.

## Archivos tocados

- `tests/test_route_guards.py`: las dos inserciones del plan, letra a letra. (1) Tras el cierre de `PUBLIC_ROUTES` y
  su línea en blanco, el comentario de dos líneas y `_ANONYMOUS_ON_PUBLIC_ROUTE` (422 ×3, 200 ×6), con una línea en
  blanco antes de `# Path parameters …`. (2) Al final, `test_route_tables_have_no_repeated_or_shared_entries` y
  `test_public_route_answers_without_token`. El test de inventario de la fase A y las tablas no cambian.
- Fin de línea: `git ls-files --eol tests/test_route_guards.py` → `i/lf w/lf`.

`git show --stat fee04bc`:

```text
 tests/test_route_guards.py | 38 ++++++++++++++++++++++++++++++++++++++
 1 file changed, 38 insertions(+)
```

Sin incidencias con el hook de ruff: la fase no añade imports (`pytest` ya estaba por la fase B).

Checklist `test-sanitizer` (Ecotur Enterprise Test Standards): sin mocks; sin usuarios ni tokens (los tests nuevos
no los necesitan); nombres e identificadores en inglés; ninguna aserción sobre texto, solo códigos y estructura de
las tablas. Nada que corregir.

## Mutantes (procedimiento común del plan)

Cada copia va en un directorio nuevo y vacío del scratchpad (`fex_nomut`, `fex_m15`, `fex_m16`, `fex_m17`, `fex_m18`;
comprobé antes que ningún `fex_*` existía). Se extrajo con `git -C C:/projects/ecotur-asoprado archive HEAD | tar -x -C <dir>`
(HEAD = `3b10acd`, así que `tests/test_audit.py` ya es el de la fase C; `diff -q` frente al árbol: idéntico) y encima
se copió `tests/test_route_guards.py` desde el árbol de trabajo. `find <dir> -name 'test_*probe*'` → 0 en las cinco.
Las ediciones se aplicaron con un script aparte (`fex_tools/apply_e.py`) que exige exactamente una coincidencia por
edición. `diff` frente al árbol (literal):

```text
== fex_m15
53d52
<     ProtectedRoute("GET", "/usuarios/mi-perfil", "user"),
80a80
>         ("GET", "/usuarios/mi-perfil"),
== fex_m16
39a40
>     ProtectedRoute("GET", "/usuarios/", "admin"),
== fex_m17
80a81
>         ("GET", "/usuarios/"),
== fex_m18
52a53
>     ProtectedRoute("GET", "/servicios/", "admin"),
75d75
<         ("GET", "/servicios/"),
```

`app/` de las copias: `diff -rq --exclude=__pycache__` solo señala `app/api/__init__.py`, por fin de línea (el árbol
lo tiene en CRLF, `i/lf w/crlf`; el contenido es el mismo). Comando, desde cada `<dir>`:
`C:/projects/ecotur-asoprado/venv/Scripts/python.exe -m pytest -q -p no:cacheprovider -rf --ignore=tests/test_check.py --ignore=tests/test_check_docs.py`.

| Estado | Resultado (literal) | Esperado por el plan |
|---|---|---|
| Sin mutante | `333 passed, 8 warnings in 10.11s` | 333 passed |
| M15 | `1 failed, 331 passed, 8 warnings in 10.24s` | 1 failed, 331 passed |
| M16 | `1 failed, 334 passed, 8 warnings in 10.38s` | 1 failed, 334 passed |
| M17 | `2 failed, 332 passed, 8 warnings in 10.44s` | 2 failed, 332 passed |
| M18 (recíproco) | `2 failed, 332 passed, 8 warnings in 11.03s` | 2 failed, 332 passed (lo matan B y C) |

`FAILED` (literal, sin el texto tras ` - `):

```text
# M15
FAILED tests/test_route_guards.py::test_public_route_answers_without_token[GET /usuarios/mi-perfil]
# M16
FAILED tests/test_route_guards.py::test_route_tables_have_no_repeated_or_shared_entries
# M17
FAILED tests/test_route_guards.py::test_route_tables_have_no_repeated_or_shared_entries
FAILED tests/test_route_guards.py::test_public_route_answers_without_token[GET /usuarios/]
# M18
FAILED tests/test_route_guards.py::test_protected_route_rejects_request_without_token[GET /servicios/]
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[GET /servicios/]
```

## Compuerta al cerrar

`./venv/Scripts/python.exe scripts/check.py` → exit 0. Líneas clave: `61 files already formatted`,
`All checks passed!`, `Success: no issues found in 56 source files`, `Contracts: 4 kept, 0 broken.`.
Sobre el archivo tocado: `python -m ruff check tests/test_route_guards.py` → `All checks passed!`;
`python -m mypy tests/test_route_guards.py` → `Success: no issues found in 1 source file`.

```text
============================== warnings summary ===============================
tests/test_route_guards.py::test_public_route_answers_without_token[GET /usuarios/verificar-email]
tests/test_route_guards.py::test_public_route_answers_without_token[POST /usuarios/login]
tests/test_route_guards.py::test_public_route_answers_without_token[POST /usuarios/registro]
tests/test_services.py::test_update_package_image_ceiling_limit_rejection
tests/test_services.py::test_create_still_rejects_short_name
tests/test_services.py::test_update_still_rejects_capacity_over_limit
tests/test_user_response.py::test_registration_still_rejects_hyphenated_name
tests/test_user_response.py::test_patch_still_rejects_hyphenated_name
  C:\projects\ecotur-asoprado\venv\Lib\site-packages\starlette\_exception_handler.py:59: StarletteDeprecationWarning: 'HTTP_422_UNPROCESSABLE_ENTITY' is deprecated. Use 'HTTP_422_UNPROCESSABLE_CONTENT' instead.
    response = await handler(conn, exc)  # type: ignore[arg-type]
...
TOTAL                                        968     21    138     18  96.47%

26 files skipped due to complete coverage.
Required test coverage of 92.0% reached. Total coverage: 96.47%
622 passed, 8 warnings in 16.68s
--- pytest + cobertura: OK en 19.1s

=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

Fila E del plan: 61 files, mypy 56, 622 passed, 96,47 %. Los warnings pasan de 5 a 8 por los 3 casos de 422
(constante deprecada de `app/main.py:94`, backlog S5), como prevé el plan (E3). La cobertura sube por
`app/main.py` (de 85,33 % a 88,00 %: la línea 76 deja de faltar).

## Verificación final del plan (pasos 1–10, desde la raíz, tras `fee04bc`)

| Paso | Esperado | Medido |
|---|---|---|
| 1. `app`, `alembic`, conftests sin cambios desde `9ecc176` | 0 | 0 |
| 2. Archivos de `tests/` cambiados | `test_audit.py`, `test_route_guards.py` | los dos |
| 3. Filas / admin / user | 17 / 14 / 3 | 17 / 14 / 3 |
| 4. `pytest tests/test_route_guards.py` | 45 passed | `45 passed, 3 warnings in 1.06s` |
| 5. `www-authenticate` | 2 | 2 |
| 6. `status_code == 40[13]` suite / `test_audit.py` | 30 / 0 | 30 / 0 |
| 7. Patrón 1 en `test_services.py` / archivo nuevo | 0 / 4 | 0 / 4 |
| 8. Patrón 3 | 3 líneas (`test_auth.py:109`, `test_services.py:648`, `:668`) | esas 3 |
| 9. Tests sustituidos | 0 | 0 |
| 10. `get_current_admin_user` / `assert_is_admin_plus(current_user)` en `app` | 15 / 1 | 15 / 1 |
| 11. Compuerta | exit 0, 622, 96,47 % | ver arriba |

El paso 12 (todos los mutantes M1–M18 sobre el estado final) no lo corrí: mi fase mide M15–M18. Queda para la
auditoría o la verificación de cierre.

## Residuales y dudas

- Sin desviaciones respecto del plan: código, cifras de mutantes, compuerta y mensaje de commit coinciden.
- R1–R4 del plan siguen como están (notas para BE-40, BE-42 y el PR humano de AGENTS §3); esta fase no los toca.
- Opcional 1 de la auditoría de A ("the next two commits" en el commit de A; fueron cuatro): sin acción en código,
  se declara en la descripción del PR (E2, punto 4).
- `progress.json`: `current_target` → `null`, la convención de los demás ítems cerrados (los otros 13 `progress.json` de `docs/deuda/` lo tienen así).
