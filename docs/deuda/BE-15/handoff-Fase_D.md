# Handoff — BE-15 Fase D: `test_auth.py`, sección RBAC y gestión de usuarios, sobre las fábricas

- **Fecha:** 2026-11-04 · **Rama:** `bloque/b-tests` · **Commit:** `ee9d54b`
  (`test(auth): build RBAC management tests with the central factories`; cuerpo idéntico al bloque del plan,
  comprobado con `diff` sobre `git log -1 --format=%B` sin el trailer → `MSG IDENTICAL`)
- **Base develop:** `7877829`. `git fetch origin` correcto; `git rev-parse --short origin/develop` = `7877829` y
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `7877829`. Coinciden con `verificacion.md`.
- Arranque: `git status --short` vacío; HEAD `c699ac6`; `current_target` = `Fase_D`.

## Archivos tocados

Solo el que el plan asigna a la fase D (`git show --stat ee9d54b`):

```
 tests/test_auth.py | 464 +++++++++++++----------------------------------------
 1 file changed, 111 insertions(+), 353 deletions(-)
```

- Sección RBAC (desde el banner, l.172 de `c699ac6`): los 11 tests reescritos. `User(...)`, `add`/`add_all`/`commit`,
  `get_password_hash("pass")`, `create_access_token` y `f"Bearer {..}"` pasan a `persist_user(role=...,
  is_active=..., deleted_at=...)` + `make_auth_headers(actor)`. Los tres tests que registraban por HTTP y activaban
  a mano usan `persist_user(role=UserRole.tourist)`. Toda relectura tras la petición va por `db_session.refresh`.
- Fuera de la sección RBAC, un único cambio: se quita `create_access_token,` del import de `app.core.security`
  (l.11), que el plan pide en D ("Se quitan los imports sin uso"). Comprobado: `head -n 171` del archivo previo, sin
  esa línea, es idéntico a `head -n 170` del nuevo; los hunks de `git diff -U0` son `@@ -11 +10,0 @@` y, después,
  desde `@@ -177,…` (primer `def` RBAC). El banner de l.172-176 no cambia.
- Sin fábricas nuevas; `conftest.py` intacto. Finales de línea: `git ls-files --eol` → `i/lf w/lf`.

## Renombrados (1:1 con la tabla del plan)

| Antes | Después |
|---|---|
| `test_actualizacion_perfil_self_service_exitoso` | `test_tourist_self_update_persists_profile_change` |
| `test_actualizacion_perfil_escalacion_rol_rechazada` | `test_tourist_self_role_escalation_returns_403_without_mutation` |
| `test_actualizacion_perfil_mutacion_estado_rechazada` | `test_tourist_self_is_active_change_returns_403_without_mutation` |
| `test_actualizacion_usuario_helpdesk_exitoso` | `test_admin_updates_tourist_email_and_persists_it` |
| `test_actualizacion_usuario_violacion_jerarquia` | `test_admin_patching_superadmin_returns_403_without_mutation` |
| `test_listar_usuarios_visibilidad_jerarquica` | `test_admin_directory_hides_superadmins` |
| `test_listar_usuarios_eliminados_visibilidad` | `test_admin_deleted_directory_hides_deleted_superadmins` |
| `test_recuperar_usuario_exitoso` | `test_admin_recovers_tourist_as_inactive` |
| `test_recuperar_usuario_violacion_jerarquia` | `test_admin_recovering_superadmin_returns_403_without_mutation` |
| `test_crear_administrador_violacion_jerarquia` | `test_admin_provisioning_admin_returns_403_without_row` |
| `test_crear_administrador_exitoso` | `test_superadmin_provisions_admin_account` |

## Red de seguridad (refactor sin RED)

`./venv/Scripts/python.exe -m pytest --collect-only -q -p no:cacheprovider tests/test_auth.py`: antes y después
`19 tests collected`. `diff` de las dos listas: las l.1-8 (fase C) idénticas; solo cambian las l.9-19, en el
mismo orden que la tabla:

```
9,19c9,19
< tests/test_auth.py::test_actualizacion_perfil_self_service_exitoso
< tests/test_auth.py::test_actualizacion_perfil_escalacion_rol_rechazada
< tests/test_auth.py::test_actualizacion_perfil_mutacion_estado_rechazada
< tests/test_auth.py::test_actualizacion_usuario_helpdesk_exitoso
< tests/test_auth.py::test_actualizacion_usuario_violacion_jerarquia
< tests/test_auth.py::test_listar_usuarios_visibilidad_jerarquica
< tests/test_auth.py::test_listar_usuarios_eliminados_visibilidad
< tests/test_auth.py::test_recuperar_usuario_exitoso
< tests/test_auth.py::test_recuperar_usuario_violacion_jerarquia
< tests/test_auth.py::test_crear_administrador_violacion_jerarquia
< tests/test_auth.py::test_crear_administrador_exitoso
---
> tests/test_auth.py::test_tourist_self_update_persists_profile_change
> tests/test_auth.py::test_tourist_self_role_escalation_returns_403_without_mutation
> tests/test_auth.py::test_tourist_self_is_active_change_returns_403_without_mutation
> tests/test_auth.py::test_admin_updates_tourist_email_and_persists_it
> tests/test_auth.py::test_admin_patching_superadmin_returns_403_without_mutation
> tests/test_auth.py::test_admin_directory_hides_superadmins
> tests/test_auth.py::test_admin_deleted_directory_hides_deleted_superadmins
> tests/test_auth.py::test_admin_recovers_tourist_as_inactive
> tests/test_auth.py::test_admin_recovering_superadmin_returns_403_without_mutation
> tests/test_auth.py::test_admin_provisioning_admin_returns_403_without_row
> tests/test_auth.py::test_superadmin_provisions_admin_account
```

`tests/test_auth.py` → `19 passed in 2.36s`.

## Aserción a aserción (AGENTS §5: ninguna se debilita)

| # | Antes | Después |
|---|---|---|
| 1 | 200; `first_name == "Nombre Modificado"`, `role == "tourist"`, `is_active is True` (JSON); `refresh` → los mismos tres en BD | idénticas (7) |
| 2 | 403; `"detail" in json`; `refresh` → `role == tourist` | idénticas (3) |
| 3 | 403; `"detail" in json`; `refresh` → `is_active is True` | idénticas (3) |
| 4 | 200; `json["email"] == "correo_corregido@…"` | las mismas **+** `refresh(tourist)` → `email == "correo_corregido@…"` |
| 5 | 403; `"Violación de jerarquía" in detail` | 403; `set(body) == {"detail"}`; `isinstance(detail, str)`; `refresh(superadmin)` → `first_name == original_first_name` |
| 6 | 200; `"tourist" in roles`, `"admin" in roles`, `"superadmin" not in roles` | 200; `{u["cedula"]} == {tourist.cedula, admin.cedula}` (igualdad exacta: implica las tres anteriores, porque cada cédula tiene rol fijo, y además excluye filas de más) |
| 7 | 200; `"888888" in cedulas`, `"777777" not in cedulas` | 200; `[u["cedula"]] == [deleted_tourist.cedula]` (implica las dos y además excluye al admin activo y a cualquier otra fila) |
| 8 | 200; `success is True`; `refresh` → `deleted_at is None`, `is_active is False` | idénticas (4) |
| 9 | 403; `"jerarquía" in detail.lower()` | 403; `set(body) == {"detail"}`; `isinstance(detail, str)`; `refresh(superadmin)` → `deleted_at is not None` |
| 10 | 403; `"superusuario" in detail.lower()` | 403; `set(body) == {"detail"}`; `isinstance(detail, str)`; `count(User) == 1` |
| 11 | 201; `role == "admin"`, `cedula == "555555"`, `is_active is True` | idénticas (4) |

Lo único que sale son las 3 aserciones sobre texto en español (5, 9, 10). Su poder de distinguir *qué* 403 se
produce lo cubren por tipo `tests/test_user_access_policy.py:115-216` (Análisis del redactor); aquí se sustituye por
la forma `{"detail": str}` y por la **ausencia de mutación** en BD, que antes no se comprobaba en ninguno de los tres.

Criterios de la fase sobre `tests/test_auth.py`: `User(` → 0; `create_access_token` → 0; `f"Bearer {` → 0;
`get_password_hash("pass")` → 0; `def test_` con nombre en español (regex del punto 6 de la Verificación final) →
0; aserciones de texto (regex del punto 5) → 0; `jerarqu|superusuario|Violaci` → 0; `sqlalchemy.future` → 0;
`^async def test_` → 19.

## Compuerta (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

Bloque RESUMEN literal:

```
=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff check, mypy
```

| Medida | Línea base (antes de tocar, HEAD `c699ac6`) | Tras la fase D | Fila "Fase D" del plan |
|---|---|---|---|
| pytest | `381 passed, 5 warnings in 12.58s` | `381 passed, 5 warnings in 14.89s` | 381 |
| Cobertura | `TOTAL 942 34 136 22 94.81%` | `TOTAL 942 34 136 22 94.81%` | ≥ 94.81 % |
| import-linter | `Contracts: 4 kept, 0 broken.` | `Contracts: 4 kept, 0 broken.` | 4 KEPT |
| ruff total | `Found 56 errors.` | `Found 56 errors.` | 56 |
| ruff en `tests/` | `Found 3 errors.` | `Found 3 errors.` | 3 |
| mypy | `Found 10 errors in 5 files (checked 35 source files)` | igual | 10 |
| ruff format | `53 files already formatted` | `53 files already formatted` | OK |

- `ruff check tests/test_auth.py` → `All checks passed!`; `ruff format` → `1 file left unchanged`.
- Los 3 de `tests/`: `test_user_access_policy.py:347` y `:395` (E501, fase E) y `test_user_service.py:3` (I001,
  residual del plan).
- `mypy tests/test_auth.py` → `Found 3 errors in 2 files (checked 1 source file)`, los tres en `app/` (imports
  seguidos: `app/db/database.py:11`, `app/core/security.py:71` y `:87`); 0 en `test_auth.py`, igual que antes de la
  fase.
- `git diff --stat` sobre `app/ pyproject.toml scripts/ .azure-pipelines/ .claude/ AGENTS.md CLAUDE.md
  tests/conftest.py` → vacío.

## Desviaciones y dudas

Ninguna necesaria para mypy (los tests no llevan anotaciones y mypy no los comprueba; el archivo sigue en 0). Tres
detalles menores que no cambian lo que pide la tabla:

1. En los tests 9 y 10 se añade `isinstance(body["detail"], str)` además de `set(body) == {"detail"}`, que es lo
   único que lista la tabla. Es la forma de la decisión 4 y la del test 5; el commit habla de "the detail shape".
   Solo endurece.
2. Test 5: "`first_name` sin cambios" se afirma contra `original_first_name`, capturado del objeto que devuelve
   `persist_user` antes de la petición, y no contra un literal.
3. Docstrings multilínea → una línea en inglés (como en la fase C); se quitan los comentarios AAA. Se conservan
   como datos (no prosa afirmada sobre la respuesta de error) `"Nombre Modificado"`, `"correo_corregido@asoprado.com"`
   y los payloads de alta de admin, tal como dice "se conservan" en la tabla.

- `test-sanitizer` aplicado como checklist: sin dobles nuevos; preparación con `persist_user` y `make_auth_headers`;
  nombres y variables en inglés; aserciones sobre `{"detail"}`, tipos y estado en BD, nunca texto; casos ABAC
  (escalada de rol, jerarquía en PATCH, recuperación y alta) conservados.

## Residuales

- Los del plan, sin cambios: duplicados HTTP con `test_user_access_policy.py:274-291` y `:344-369`; las claves en
  español de la respuesta de recuperación (`cc`, `correo`, `nombre`, `apellido`), que no se afirman.
- `mypy` de `tests/conftest.py:223` (`persist_user` devuelve `Any`), el mismo residual de las fases A y C; no tocado.
