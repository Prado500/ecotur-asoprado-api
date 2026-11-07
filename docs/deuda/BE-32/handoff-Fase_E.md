# Handoff — BE-32 Fase_E: copias HTTP fuera y orden de las guardas de `assert_can_update` congelado

**Commit de la fase:** `11f2f17` (`test(access-policy): drop three HTTP copies and freeze the role guard order`). El
mensaje es el del plan letra a letra, con `Claude Opus 5.5` en el trailer. **Estado:** `completed`. **Siguiente:**
`/implementar BE-32 Fase_F`.

## Archivos tocados

`git show --stat 11f2f17`:

```text
 tests/test_auth.py               |  5 ++-
 tests/test_user_access_policy.py | 92 ++++++++++------------------------------
 2 files changed, 26 insertions(+), 71 deletions(-)
```

- `tests/test_auth.py`, en `test_admin_provisioning_admin_returns_403_without_row`: el conteo de `:388-389`
  (`select(func.count()).select_from(User)` + `scalar_one() == 1`) pasa a ser las tres líneas de la copia:
  `users = (await db_session.execute(select(User))).scalars().all()`, `assert len(users) == 1` y
  `assert users[0].cedula == admin.cedula`. `func` se queda (lo usa `:67`). Las líneas no estaban desplazadas.
- `tests/test_user_access_policy.py`:
  - Borrados `test_patch_hierarchy_violation_returns_403_detail`, `test_admin_cannot_provision_admin_account_403_and_no_db_mutation`
    y `test_admin_update_tourist_persists_mutation` (`:314`, `:384` y `:412` antes de la fase; coinciden con la base,
    porque la fase C solo cambió una línea de import por otra).
  - `from app.models.user import User, UserRole` → `from app.models.user import UserRole`. Lo hizo el hook (F401
    `--fix`) al quedar `User` sin uso tras borrar la copia de `:384`; el resultado es el que dicta el plan.
  - Nuevo, al final de `TestAssertCanUpdate` (l.201-221):
    `test_role_guard_for_non_superadmins_runs_before_the_self_role_guard`, con el cuerpo y el docstring del plan.
    `ruff format` partió la firma en tres líneas (`(\n        self, policy, make_user\n    ):`) porque pasa de 100
    columnas; el plan acepta el corte que deje `ruff format`.

## Ritual de arranque

- Árbol limpio en `item/be-32`, HEAD en `a861358`. `current_target` = `Fase_E`.
- `git fetch origin` correcto. `origin/develop` = `fd144ad`; `merge-base HEAD origin/develop` = `fd144ad`; `Base develop`
  de `verificacion.md` = `fd144ad`.
- Compuerta antes de tocar nada (exit 1): `547 passed, 5 warnings`, `TOTAL 943 23 138 19 96.11%`, ruff `Found 8 errors.`
  (los 8 I001 `app\...:1:1`), mypy `Found 9 errors in 5 files (checked 53 source files)` con A4 en
  `tests\test_user_service.py:105,203,280,298`, `Contracts: 4 kept, 0 broken.`, `57 files already formatted`. Coincide
  con la fila D.

## RED: mutante G1 en copia desechable

Copia fuera del árbol: `git archive HEAD | tar -x` en el scratchpad de la sesión (árbol versionado completo, sin
`.env`; la suite entera necesita `scripts/` y `docs/`), con variables de entorno ficticias (`JWT_SECRET_KEY`,
`DATABASE_URL=sqlite+aiosqlite:///:memory:`, `MAIL_*`, `AZURE_*`, `CORS_ORIGINS`) y el Python del `venv/`.
`app.services.user_access_policy.__file__` resolvía a la copia. Un script comprueba por contenido que `:66` es la guarda
de no-superadmin y `:71` la de auto-rol, intercambia los bloques `:66-69` y `:71-72`, corre pytest con `--no-cov`, y
restaura el archivo en un `finally`. "Antes" = tests de HEAD (`a861358`). "Después" = el `test_user_access_policy.py`
con el test nuevo copiado encima. `git diff --quiet -- app` en el repo: sin cambios.

Bloque mutado (impreso por el script; los acentos salen mal por la consola, no por el archivo):

```text
        if is_self_update and "role" in update_dict:
            raise AuthorizationError("Violaci�n de jerarqu�a: No puede modificar su propio rol.")

        if "role" in update_dict and actor.role != UserRole.superadmin:
            raise AuthorizationError(
                "Violaci�n de jerarqu�a: Solo un superadministrador puede modificar roles."
            )
```

| Mutante | Cambio | Antes (archivo / suite) | Después (archivo / suite) |
|---|---|---|---|
| G1 | `user_access_policy.py`: bloques `:66-69` y `:71-72` intercambiados | `77 passed` / `547 passed, 5 warnings` | `1 failed, 77 passed` / `1 failed, 547 passed, 5 warnings` |

Salida literal del script (líneas de resumen):

```text
# antes, archivo
unmutated:
    77 passed in 1.55s
G1:
    77 passed in 1.53s
# antes, suite
unmutated:
    547 passed, 5 warnings in 22.47s
G1:
    547 passed, 5 warnings in 23.56s
# después, archivo
unmutated:
    78 passed in 1.42s
G1:
    tests\test_user_access_policy.py:220: AssertionError
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_role_guard_for_non_superadmins_runs_before_the_self_role_guard
    1 failed, 77 passed in 1.51s
# después, suite (copia con el test nuevo y aún con las 3 copias HTTP)
unmutated:
    548 passed, 5 warnings in 19.94s
G1:
    tests\test_user_access_policy.py:220: AssertionError
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_role_guard_for_non_superadmins_runs_before_the_self_role_guard
    1 failed, 547 passed, 5 warnings in 22.59s
```

Falla la aserción `==` (l.220): con el mutante, el admin que envía su propio rol recibe la respuesta de auto-rol, y no
la de no-superadmin que recibe para el rol de otro. La aserción que se copió a `test_auth.py` no es RED (replica una que
ya pasaba), como dice el plan.

## Cobertura antes y después de borrar las copias

| Momento | pytest | Cobertura |
|---|---|---|
| Arranque (sin cambios) | `547 passed, 5 warnings` | `TOTAL 943 23 138 19 96.11%` |
| Con G1 y la aserción en `test_auth.py`, **antes** de borrar las copias (`pytest --cov=app --cov-branch`) | `548 passed, 5 warnings` | `TOTAL 943 23 138 19 96.11%` |
| **Después** de borrar las copias (compuerta) | `545 passed, 5 warnings` | `TOTAL 943 23 138 19 96.11%` |

## Patrones del criterio de aceptación

| Patrón | Resultado |
|---|---|
| `grep -cE "def test_(patch_hierarchy_violation\|admin_cannot_provision_admin_account\|admin_update_tourist_persists)" tests/test_user_access_policy.py` | `0` |
| `grep -cE "def test_(admin_patching_superadmin\|admin_provisioning_admin\|admin_updates_tourist_email)" tests/test_auth.py` | `3` |
| `grep -c "assert users\[0\].cedula == admin.cedula" tests/test_auth.py tests/test_user_access_policy.py` | `tests/test_auth.py:1`, `tests/test_user_access_policy.py:0` |
| `grep -c "def test_role_guard_for_non_superadmins_runs_before_the_self_role_guard" tests/test_user_access_policy.py` | `1` |

## Compuerta tras la fase (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

La corrí sobre el árbol editado justo antes del commit; solo estaban modificados los 2 archivos de la fase.

```text
=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff check, mypy
```

Cifras por paso:

```text
57 files already formatted
Found 8 errors.            (los 8 I001 :1:1 de app\: api\dependencies.py, api\routers\audit.py, core\email.py,
                            db\database.py, repositories\user_repository.py, schemas\audit.py,
                            services\audit_service.py, services\user_service.py)
app\db\database.py:11: error: Argument 1 to "create_async_engine" has incompatible type "str | None"; expected "str | URL"  [arg-type]
app\core\security.py:71: error: Argument "key" has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
app\core\security.py:87: error: Argument "key" has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
app\services\user_service.py:124: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
tests\test_user_service.py:105: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
tests\test_user_service.py:203: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
tests\test_user_service.py:280: error: Argument 2 has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
tests\test_user_service.py:298: error: Argument 2 has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
app\api\dependencies.py:95: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
Found 9 errors in 5 files (checked 53 source files)
Contracts: 4 kept, 0 broken.
TOTAL                                        943     23    138     19  96.11%
545 passed, 5 warnings in 20.49s
```

`grep -c "error:"` sobre la salida = 9. Identidad de A4 por contenido (`grep -n SECRET_KEY tests/test_user_service.py`):

```text
105:    claims = jwt.decode(result.verification_token, SECRET_KEY, algorithms=[ALGORITHM])
203:    claims = jwt.decode(result.access_token, SECRET_KEY, algorithms=[ALGORITHM])
280:        SECRET_KEY,
298:        SECRET_KEY,
```

Coincide con la fila E (igual que D) y con la columna "Tras D (y al cerrar)" de la decisión 5. En los archivos tocados:
`ruff format --check` → `2 files already formatted`; `ruff check` → `All checks passed!`; `ruff check tests/` →
`All checks passed!`; `mypy tests/test_auth.py tests/test_user_access_policy.py` → `Found 5 errors in 4 files (checked
2 source files)`, los 5 de `app/` (A4) que entran por import; ninguno en los archivos tocados.

## test-sanitizer (checklist)

El test nuevo usa la fábrica `make_user` y el fixture `policy`, no construye usuarios a mano. No hay mocks. Compara
`.detail` entre excepciones con `==`/`!=`, nunca contra texto en español. Todo en inglés, con docstring. No se reescribió
ningún test que ya cumpliera: en `test_auth.py` solo se sustituyó el conteo por la aserción más fuerte que dicta el plan.

## Desviaciones y dudas

1. **El import lo quitó el hook, no una edición mía.** Al borrar la copia de `:384`, `User` quedó sin uso y el
   `ruff check --fix` del hook (F401) lo quitó. El resultado es la línea que dicta el plan
   (`from app.models.user import UserRole`).
2. **Firma partida por `ruff format`.** La línea `def test_role_guard_...(self, policy, make_user):` sale de 100
   columnas; el formato la deja en tres líneas. El plan lo permite ("el corte de línea es el que deje `ruff format`").
3. **Rango de la aserción copiada.** El plan dice `:407-409` y el encargo `:406-409`; `:406` es la línea en blanco
   previa. Se copiaron las tres líneas de aserción (`:407-409`) y se mantuvo la línea en blanco que ya había en
   `test_auth.py`.
4. Las líneas que cita el plan (`test_user_access_policy.py:314,384,412,407-409`, `test_auth.py:361,388-389`,
   `user_access_policy.py:66-69,71-72`) coincidían con la base; ninguna fase anterior las desplazó. Las localicé además
   por contenido.
5. El conteo del plan cuadra: 547 − 3 + 1 = 545, y la cobertura no se mueve (96.11 % antes y después).

## Residuales

Sin residuales nuevos. Los del plan siguen igual.
