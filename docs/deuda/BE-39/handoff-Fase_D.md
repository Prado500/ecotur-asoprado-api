# Handoff — BE-39 · Fase D (la etiqueta `"user"` se comprueba: un turista pasa el guard de las 3 rutas de usuario)

- **Commit de la fase:** `284cfe7` — `test(guards): check the "user" label by letting a tourist through`
- **Ejecutor:** fase-ejecutor (Claude Opus 5.5), 11 nov 2026.

## Ritual de arranque

- `git status --short`: limpio. `HEAD` = `28d49be` (`gaps.md` con la auditoría de C: PASS, 0 bloqueantes, 1 opcional).
- `current_target` = `Fase_D`.
- Vigencia de la línea base: `git fetch origin` correcto. `git rev-parse --short origin/develop` = `3ca990a`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `3ca990a`. Ambos iguales a `Base develop` de
  `verificacion.md`.
- Compuerta antes de tocar nada: exit 0, todos los pasos en verde, `Total coverage: 96.29%`,
  `609 passed, 5 warnings in 17.21s`. Es la fila C del plan: la fase C no dejó nada roto.

## Archivos tocados

- `tests/test_route_guards.py`: las dos inserciones del plan, letra a letra. (1) Tras `ADMIN_ROUTES: …`, una línea en
  blanco, `USER_ROUTES`, el comentario de dos líneas y `_TOURIST_PAST_USER_GUARD` (200, 404, 404), con una línea en
  blanco antes de `PUBLIC_ROUTES`. (2) Al final, `test_user_route_lets_tourist_through`. Nada más cambia.
- Fin de línea: `git ls-files --eol tests/test_route_guards.py` → `i/lf w/lf`.

`git show --stat 284cfe7`:

```text
 tests/test_route_guards.py | 27 +++++++++++++++++++++++++++
 1 file changed, 27 insertions(+)
```

Sin incidencias con el hook de ruff: la fase no añade imports (`pytest` y `UserRole` ya estaban por las fases B y C).

## Mutantes (procedimiento común del plan)

Cada copia va en un directorio nuevo y vacío del scratchpad (`fdx_nomut`, `fdx_m12`, `fdx_m13`, `fdx_m14`; comprobé
antes que ninguno existía). Se extrajo con `git -C C:/projects/ecotur-asoprado archive HEAD | tar -x -C <dir>`
(HEAD = `28d49be`, así que `tests/test_audit.py` ya es el de la fase C) y encima se copió
`tests/test_route_guards.py` desde el árbol de trabajo. `find <dir> -name 'test_*probe*'` → 0 en las cuatro. Las
ediciones se aplicaron con un script aparte (`fdx_tools/mutate.py`) que exige exactamente una coincidencia. `diff`
frente al árbol: M12 solo cambia la línea 39 de la tabla, M13 solo la 53, M14 solo `app/api/routers/user.py:36`
(`diff -rq app <copia>/app` sin otros archivos, salvo `__pycache__`). Comando, desde cada `<dir>`:
`C:/projects/ecotur-asoprado/venv/Scripts/python.exe -m pytest -q -p no:cacheprovider -rf --ignore=tests/test_check.py --ignore=tests/test_check_docs.py`.

| Estado | Resultado (literal) | Esperado por el plan |
|---|---|---|
| Sin mutante | `323 passed, 5 warnings in 10.81s` | 323 passed |
| M12 | `1 failed, 322 passed, 5 warnings in 11.07s` | 1 failed, 322 passed |
| M13 (recíproco) | `1 failed, 322 passed, 5 warnings in 11.19s` | 1 failed, 322 passed (lo mata la fase C) |
| M14 | `18 failed, 305 passed, 4 warnings in 10.69s` | 18 failed, 305 passed |

`FAILED` (literal, sin el texto tras ` - `):

```text
# M12
FAILED tests/test_route_guards.py::test_user_route_lets_tourist_through[GET /usuarios/]
# M13
FAILED tests/test_route_guards.py::test_admin_route_rejects_tourist[GET /usuarios/mi-perfil]
# M14
FAILED tests/test_auth.py::test_self_soft_delete_keeps_row_and_blocks_login
FAILED tests/test_auth.py::test_tourist_self_update_persists_profile_change
FAILED tests/test_route_guards.py::test_user_route_lets_tourist_through[GET /usuarios/mi-perfil]
FAILED tests/test_route_guards.py::test_user_route_lets_tourist_through[DELETE /usuarios/{cedula}]
FAILED tests/test_route_guards.py::test_user_route_lets_tourist_through[PATCH /usuarios/{cedula}]
FAILED tests/test_token_failure_paths.py::test_valid_token_on_protected_route_returns_the_user
FAILED tests/test_user_access_policy.py::test_patch_nonexistent_cedula_returns_404_before_403
FAILED tests/test_user_access_policy.py::test_delete_nonexistent_cedula_returns_404_before_403
FAILED tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[hyphen]
FAILED tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[apostrophe]
FAILED tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[mixed_case_surname]
FAILED tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[66_chars]
FAILED tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[landline]
FAILED tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[11_digit_cedula]
FAILED tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[dotless_domain]
FAILED tests/test_user_response.py::test_my_profile_returns_stored_values_verbatim[mixed_case_domain]
FAILED tests/test_user_response.py::test_patch_on_off_rule_record_returns_200_with_persisted_change
FAILED tests/test_user_response.py::test_patch_still_rejects_hyphenated_name
```

M14: 3 casos nuevos + 15 que ya existían (`test_auth.py` 2, `test_token_failure_paths.py` 1,
`test_user_access_policy.py` 2, `test_user_response.py` 10), como dice el plan.

## Criterio de aceptación

- `./venv/Scripts/python.exe -m pytest tests/test_route_guards.py -q -p no:cacheprovider` → `35 passed in 0.69s`.
- `python -m ruff check tests/test_route_guards.py` → `All checks passed!`;
  `python -m mypy tests/test_route_guards.py` → `Success: no issues found in 1 source file`.
- Compuerta (`./venv/Scripts/python.exe scripts/check.py`), exit 0. Líneas clave y bloque RESUMEN, literales:

```text
61 files already formatted
All checks passed!
Success: no issues found in 56 source files
Contracts: 4 kept, 0 broken.
TOTAL                                        968     22    138     19  96.29%
Required test coverage of 92.0% reached. Total coverage: 96.29%
612 passed, 5 warnings in 16.76s
--- pytest + cobertura: OK en 19.3s

=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

Fila D del plan: 61 files · 56 · **612 passed** · 96,29 % · copia 323 passed. Coincide en todo. Ratchet: cobertura
96,29 % = línea base; 4 contratos KEPT = línea base; ruff y mypy en 0.

## Checklist `test-sanitizer` (solo checklist)

- Sin mocks. Usuario y token salen de las fábricas `persist_user` y `make_auth_headers`.
- Comportamiento por HTTP, no inspección de dependencias (E0, punto 3). No se lee ningún texto (AGENTS §5).
- Solo se afirma el código de estado: límite aceptado en E1 (los cuerpos los congelan `tests/test_auth.py` y
  `tests/test_user_response.py`). Sin mutación de estado que comprobar: la cédula no existe y `mi-perfil` es lectura.
- No se reescribió ningún test existente.

## Residuales y dudas

- Ninguno nuevo. R1–R4 del plan siguen como estaban.
- Sin desviaciones respecto del plan.
