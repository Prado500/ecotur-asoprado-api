# Handoff — BE-32 Fase_D: aserciones de dobles con argumentos

**Commit de la fase:** `8eb71d4` (`test(doubles): assert mock calls with their arguments`). El mensaje es el del plan
letra a letra, con `Claude Opus 5.5` en el trailer. **Estado:** `completed`. **Siguiente:** `/implementar BE-32 Fase_E`.

## Archivos tocados

`git show --stat 8eb71d4`:

```text
 tests/test_audit.py        |  1 -
 tests/test_services.py     | 12 ++++++------
 tests/test_storage.py      | 15 +++++++--------
 tests/test_user_service.py | 21 ++++++++++++++++-----
 4 files changed, 29 insertions(+), 20 deletions(-)
```

Líneas citadas en la posición previa a la fase (base + 1 en `test_user_service.py` y `test_services.py`, por el
`from typing import Any` de la fase B):

- `tests/test_user_service.py`: `from app.models.audit import AuditAction` (nueva l.19, entre `app.core.security` y
  `app.models.user`). `:111` → `user_repo.create_user.assert_awaited_once_with(result.user)`; `:112` →
  `log_transaction.assert_awaited_once_with(entity_name="User", entity_id="1005911792", action=AuditAction.CREATE,
  performed_by="1005911792")`. Borrado `assert_not_awaited()` (`:123`; `:122` en la base). `:329` →
  `create_user.assert_awaited_once_with(created_user)`; `:330` → la misma forma con `entity_id="5555555555"`,
  `performed_by=actor.cedula`, `changes={"role": "admin"}`, coma final en cada argumento.
- `tests/test_services.py`: `:220` → `upload_image.assert_awaited_once_with(StagedImage("test_image.jpg", "image/jpeg",
  b"fake_binary_payload"))`; se quedan `call_args.args[0]` + `isinstance` y se borran las 3 aserciones de campo.
  `:487` → lo mismo con `StagedImage("notes.bin", "application/octet-stream", b"binary")`; se borra la de
  `content_type`.
- `tests/test_storage.py`: `from azure.storage.blob import ContentSettings` (l.7, entre `azure.core.exceptions` y
  `azure.storage.blob.aio`). `:92-96` → `upload_blob.assert_awaited_once_with(b"bytes", overwrite=True,
  content_settings=ContentSettings(content_type="image/jpeg"))`. `:159`, `:189`, `:198` → `.assert_awaited_once_with()`.
- `tests/test_audit.py`: borrado `audit_repo.get_all_audit_logs.assert_not_awaited()` (`:88`; `:87` en la base).

Orden de edición según E1: las líneas con `AuditAction` y `ContentSettings` se escribieron antes que sus `import`. El
hook devolvió el F821 esperado entre las dos ediciones; tras añadir el `import`, ruff quedó limpio.

## Ritual de arranque

- Árbol limpio en `item/be-32`, HEAD en `eb68510`. `current_target` = `Fase_D`.
- `git fetch origin` correcto. `origin/develop` = `fd144ad`; `merge-base HEAD origin/develop` = `fd144ad`; `Base develop`
  de `verificacion.md` = `fd144ad`.
- Compuerta antes de tocar nada (exit 1): `547 passed, 5 warnings`, `TOTAL 943 23 138 19 96.11%`, ruff `Found 8 errors.`
  (los 8 I001 `app\...:1:1`), mypy `Found 9 errors in 5 files (checked 53 source files)` con A4 en
  `tests\test_user_service.py:104,198,275,293`, `Contracts: 4 kept, 0 broken.`, `57 files already formatted`. Coincide
  con la fila C.

## RED: mutantes en copia desechable

Copia fuera del árbol: `git archive HEAD app tests pyproject.toml` extraído en el scratchpad de la sesión, con variables
de entorno ficticias (`JWT_SECRET_KEY`, `DATABASE_URL=sqlite+aiosqlite:///:memory:`, `MAIL_*`, `AZURE_*`,
`CORS_ORIGINS`) y el Python del `venv/`. `app.__file__` resolvía a la copia, no al repo. Un script aplica cada mutante en
su línea (con un `assert` sobre el texto original), corre el archivo de tests y restaura. "Antes" = tests de HEAD
(`eb68510`). "Después" = los 4 archivos editados copiados encima. `git diff --quiet -- app` en el repo: sin cambios.
Tras restaurar, la copia sin mutar da `73 passed` en los tres archivos.

| Mutante | Cambio | Antes | Después |
|---|---|---|---|
| MU1 | `user_service.py:101` `performed_by=saved_user.email` | `19 passed` | `1 failed, 18 passed` (`test_register_tourist_returns_registration_result`) |
| MU2 | `user_service.py:425` sin `changes=...` | `19 passed` | `1 failed, 18 passed` (`test_create_administrative_account_provisions_admin`) |
| MS1 | `storage.py:202` `delete_blob(delete_snapshots="include")` | `18 passed` | `1 failed, 17 passed` (`test_promote_happy_path_copies_synchronously_then_deletes`) |
| MS2 | `storage.py:154` `delete_blob(delete_snapshots="include")` | `18 passed` | `2 failed, 16 passed` (`test_delete_image_deletes_blob_by_name`, `test_delete_image_swallows_sdk_failure`) |
| MR1 | `routers/service.py:76` `filename=""` | `1 failed, 35 passed` (`..._storage_outage_returns_503`) | `2 failed, 34 passed` (503 y `test_upload_images_non_image_returns_415`) |

Salida literal del script:

```text
# antes
MU1: 19 passed in 1.75s
MU2: 19 passed in 1.85s
MS1: 18 passed in 1.63s
MS2: 18 passed in 1.60s
MR1: 1 failed, 35 passed, 3 warnings in 1.11s
    FAILED tests/test_services.py::test_upload_images_storage_outage_returns_503
# después
MU1: 1 failed, 18 passed in 2.42s
    FAILED tests/test_user_service.py::test_register_tourist_returns_registration_result
MU2: 1 failed, 18 passed in 2.26s
    FAILED tests/test_user_service.py::test_create_administrative_account_provisions_admin
MS1: 1 failed, 17 passed in 2.06s
    FAILED tests/test_storage.py::test_promote_happy_path_copies_synchronously_then_deletes
MS2: 2 failed, 16 passed in 1.95s
    FAILED tests/test_storage.py::test_delete_image_deletes_blob_by_name - Assert...
    FAILED tests/test_storage.py::test_delete_image_swallows_sdk_failure - Assert...
MR1: 2 failed, 34 passed, 3 warnings in 1.26s
    FAILED tests/test_services.py::test_upload_images_storage_outage_returns_503
    FAILED tests/test_services.py::test_upload_images_non_image_returns_415 - Ass...
```

## Patrones del criterio de aceptación

| Patrón | Antes | Después |
|---|---|---|
| `grep -rnE "\.assert_(called\|awaited)(_once)?\(\)" tests/ --include=*.py` | 11 | **1** (`tests/test_email.py:99`, fuera de alcance: fase H) |
| Patrón 1b (`assert_not_called` seguido de `assert_not_awaited`) | 2 (`test_audit.py:88`, `test_user_service.py:123`) | 0 |

## Compuerta tras la fase (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

La corrí sobre el árbol editado justo antes del commit; solo estaban modificados los 4 archivos de la fase.

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
app\api\dependencies.py:95: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
tests\test_user_service.py:105: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
tests\test_user_service.py:203: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
tests\test_user_service.py:280: error: Argument 2 has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
tests\test_user_service.py:298: error: Argument 2 has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
Found 9 errors in 5 files (checked 53 source files)
Contracts: 4 kept, 0 broken.
TOTAL                                        943     23    138     19  96.11%
547 passed, 5 warnings in 21.64s
```

`grep -c "error:"` sobre la salida = 9. Identidad de A4 por contenido:

```text
105:     claims = jwt.decode(result.verification_token, SECRET_KEY, algorithms=[ALGORITHM])
203:     claims = jwt.decode(result.access_token, SECRET_KEY, algorithms=[ALGORITHM])
280:         SECRET_KEY,
298:         SECRET_KEY,
```

Coincide con la fila D y con la columna "Tras D" de la decisión 5. En los archivos tocados:
`ruff format --check` → `4 files already formatted`; `ruff check` → `All checks passed!`; `mypy` sobre los 4 archivos →
solo los 4 de A4 en `test_user_service.py` (más `app\api\dependencies.py:95`, que entra por import). Es la excepción de la
decisión 5. Cobertura: 96.11 % antes y después.

## test-sanitizer (checklist)

Los dobles siguen con `create_autospec`. Todo está en inglés. Ninguna aserción lee texto en español: los valores
afirmados (`"1005911792"`, `"5555555555"`, nombres de fichero, MIME) son entradas del propio test. No se reescribió
ningún test que ya cumpliera.

## Desviaciones y dudas

1. **Patrón 1 del criterio de aceptación: da 1, no 0.** El plan pide que
   `grep -rnE "\.assert_(called|awaited)(_once)?\(\)" tests/` dé 0 en esta fase, pero `tests/test_email.py:99` (base 11 −
   10 de esta fase = 1) está fuera de alcance por el propio plan (fase H). El 0 solo es alcanzable al cerrar H, como dice
   la "Verificación final". Es un error de conteo del plan. No toqué `test_email.py`.
2. Las líneas que cita el plan son de la base. En `test_user_service.py`, `test_services.py` y `test_audit.py` estaban
   desplazadas +1 por la fase B (`:122` → `:123`, `:219` → `:220`, `:486` → `:487`, `:87` → `:88`). El contenido coincidía
   en todos los casos. `test_storage.py` no estaba desplazado.
3. MR1 "antes/después" en el plan dice solo `1 failed` / `2 failed`. La salida completa es `1 failed, 35 passed` /
   `2 failed, 34 passed` (archivo de 36 tests).
4. Los 3 `delete_blob.assert_awaited_once()` de `test_storage.py` se cambiaron con `sed` y no con Edit, así que el hook
   no corrió sobre esa edición. `ruff format --check` y `ruff check` sobre el archivo, ejecutados después a mano, salen
   limpios.

## Residuales

Sin residuales nuevos. Los del plan siguen igual (`call_args.args[0]` en `test_services.py:223,489`, solo para el
`isinstance`).
