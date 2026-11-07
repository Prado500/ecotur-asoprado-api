# Handoff — BE-32 Fase_A: que mypy no estreche el doble del correo

**Commit de la fase:** `e7c814d` (`test(fixtures): stop mypy narrowing the email double to the real function`). El mensaje
es el del plan letra a letra, con `Claude Opus 5.5` en el trailer. **Estado:** `completed`. **Siguiente:**
`/implementar BE-32 Fase_B`.

## Archivos tocados

`git show --stat e7c814d`:

```text
 tests/test_fixtures_contract.py | 7 ++++---
 1 file changed, 4 insertions(+), 3 deletions(-)
```

Diff (cuerpo de `test_email_dispatch_double_is_autouse_and_autospecced`; docstring y firma sin cambios):

```diff
-    assert user_router.send_verification_email is mock_send_email
+    double: Any = user_router.send_verification_email
+    assert double is mock_send_email

     with pytest.raises(TypeError):
-        await mock_send_email(recipient="x")
+        await double(recipient="x")

-    mock_send_email.assert_not_called()
+    double.assert_not_called()
```

## Ritual de arranque

- Árbol limpio en la rama `item/be-32`, con HEAD en `bcc7c8c`. `current_target` = `Fase_A`. No existe `gaps.md`.
- `git fetch origin` correcto. `origin/develop` = `fd144ad`; `merge-base HEAD origin/develop` = `fd144ad`; `Base develop`
  de `verificacion.md` = `fd144ad`.
- Compuerta antes de tocar nada (exit 1): `547 passed, 5 warnings`, 96.11 %, ruff `Found 9 errors.`, mypy `Found 5 errors
  in 4 files (checked 35 source files)`, `Contracts: 4 kept, 0 broken.`, `57 files already formatted`. Coincide con la
  línea base.

## RED (de herramienta)

`./venv/Scripts/python.exe -m mypy tests --cache-dir "$TMPDIR/mypycache"`, antes de editar. Líneas del archivo:

```text
tests\test_fixtures_contract.py:59: error: Unexpected keyword argument "recipient" for "send_verification_email"  [call-arg]
tests\test_fixtures_contract.py:59: note: "send_verification_email" defined in "app.core.email"
tests\test_fixtures_contract.py:61: error: "Callable[[str, str, str, str], Coroutine[Any, Any, Any]]" has no attribute "assert_not_called"  [attr-defined]
Found 16 errors in 9 files (checked 18 source files)
```

Después de editar, con el mismo comando:

```text
grep -cE "^tests.test_fixtures_contract"  -> 0
Found 14 errors in 8 files (checked 18 source files)
```

`pytest tests/test_fixtures_contract.py -q`: `9 passed` antes y después.

Los 9 errores que quedan en `tests/` con `mypy tests` son los 5 de BE-32 que corrige la fase B (`test_audit.py:72`,
`test_user_service.py:65`, `:71`, `test_services.py:157`, `conftest.py:239`) y los 4 de A4 (`test_user_service.py:103`,
`:197`, `:274`, `:292`).

## Compuerta (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

La corrí sobre el árbol editado justo antes del commit. El commit contiene exactamente ese contenido, porque solo ese
archivo estaba modificado.

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

```text
57 files already formatted
Found 9 errors.
Found 5 errors in 4 files (checked 35 source files)
Contracts: 4 kept, 0 broken.
TOTAL                                        943     23    138     19  96.11%
Required test coverage of 92.0% reached. Total coverage: 96.11%
547 passed, 5 warnings in 20.75s
```

Ruff (`ruff check . --output-format=concise`): los 8 I001 `:1:1` de `app/` y `tests\test_user_service.py:3:1`, igual que
en la base. mypy: `app\db\database.py:11`, `app\core\security.py:71`, `:87`, `app\services\user_service.py:124`,
`app\api\dependencies.py:95`, igual que en la base.

| Métrica | Línea base | Fase_A | Criterio (fila A) |
|---|---|---|---|
| pytest | 547 passed | 547 passed | 547 passed |
| Cobertura | 96.11 % | 96.11 % | ≥ 96.11 % |
| Contratos | 4 KEPT | 4 KEPT | 4 KEPT |
| ruff total | 9 | 9 | 9 (igual) |
| mypy (compuerta) | 5 en 4 archivos, 35 fuentes | 5 en 4 archivos, 35 fuentes | igual que la base |
| `mypy tests` | 16 en 9 archivos | 14 en 8 archivos | 14 en 8 archivos |

Archivo tocado: `ruff check tests/test_fixtures_contract.py` da `All checks passed!` y `ruff format --check` da
`1 file already formatted`. `mypy tests/test_fixtures_contract.py` no da ninguna línea del archivo. Sí lista 5 errores
(`Found 5 errors in 4 files (checked 1 source file)`), que son los de A4 en `app/`, adonde llega siguiendo imports.

## Checklist `test-sanitizer`

Se aplicó como checklist. El test sigue probando lo mismo: la identidad entre el nombre del router y el doble autouse,
`TypeError` con una firma ajena y ninguna llamada registrada. Sigue usando `mock_send_email` (autospec) y no lee texto
en español. No hay nada que corregir.

## Residuales

- La compuerta sigue en rojo por lo heredado: ruff 9 (8 de A4 y el I001 de `tests\test_user_service.py:3`, que corrige
  la fase B) y mypy 5 (A4). No lo toqué.

## Desviaciones y dudas

- No hay desviaciones de código ni de mensaje respecto al plan.
- **Medición del RED:** el plan dice que `grep -cE "^tests.test_fixtures_contract"` da `2` antes, pero da `3`. mypy añade
  una línea `note:` en `:59` que empieza por la misma ruta. Los errores son 2, como dice el plan
  (`grep -cE "^tests.test_fixtures_contract.*error:"` da `2`). El `0` de después coincide. El plan no se tocó.
