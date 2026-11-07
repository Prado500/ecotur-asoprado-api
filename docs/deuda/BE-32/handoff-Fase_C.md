# Handoff — BE-32 Fase_C: higiene de la suite (`select`, comentario, `Yields:` e ids)

**Commit de la fase:** `5979b07` (`test(suite): import select from sqlalchemy, add Yields, rename stale ids`). El mensaje
es el del plan letra a letra, con `Claude Opus 5.5` en el trailer. **Estado:** `completed`. **Siguiente:**
`/implementar BE-32 Fase_D`.

## Archivos tocados

`git show --stat 5979b07`:

```text
 tests/conftest.py                | 12 ++++++++++++
 tests/test_audit.py              |  2 +-
 tests/test_check_docs.py         | 11 ++++++++---
 tests/test_services.py           |  2 +-
 tests/test_user_access_policy.py |  2 +-
 5 files changed, 23 insertions(+), 6 deletions(-)
```

- `tests/test_services.py:15` y `tests/test_user_access_policy.py:14`: `from sqlalchemy.future import select` →
  `from sqlalchemy import select`. El bloque de imports sigue ordenado (ruff sin I001).
- `tests/test_audit.py:22` (`:21` en la base; la fase B añadió `from typing import Any`): el comentario pasa a
  `# 1. Create a package with a plain JSON payload that satisfies ServiceCreate`.
- `tests/test_check_docs.py`: en `test_r7_flags_closed_row_without_mark`, `year-by-monotony` → `year-nearest-to-version` y
  `year-resets-per-table` → `year-nearest-in-each-table`. La lista `ids=[...]` pasa a una línea por elemento porque en una
  sola línea supera las 100 columnas (es el corte que deja `ruff format`, con coma final). En
  `test_r7_accepts_marked_future_or_undated_rows`, `year-jump-marked` → `new-year-rows-marked` y `year-jump-future-row` →
  `new-year-row-in-future`.
- `tests/conftest.py`: `Yields:` con línea en blanco delante, 3 líneas por fixture, con el texto del plan, en
  `setup_database`, `db_session`, `client` y `override_azure_storage_client`.

## Ritual de arranque

- Árbol limpio en `item/be-32`, HEAD en `133edb3`. `current_target` = `Fase_C`.
- `git fetch origin` correcto. `origin/develop` = `fd144ad`; `merge-base HEAD origin/develop` = `fd144ad`; `Base develop`
  de `verificacion.md` = `fd144ad`.
- Compuerta antes de tocar nada (exit 1): `547 passed, 5 warnings`, `TOTAL ... 96.11%`, ruff `Found 8 errors.` (los 8
  I001 `app\...:1:1`), mypy `Found 9 errors in 5 files (checked 53 source files)` con A4 en
  `tests\test_user_service.py:104,198,275,293`, `Contracts: 4 kept, 0 broken.`, `57 files already formatted`. Coincide
  con la fila B.

## RED (patrones de la verificación) antes → después

| Patrón | Antes | Después |
|---|---|---|
| `grep -rn "sqlalchemy.future" tests/ --include=*.py \| wc -l` | 2 (`test_services.py:15`, `test_user_access_policy.py:14`) | 0 |
| Patrón 5 de la verificación final (comentario en español) `\| wc -l` | 1 (`test_audit.py:22`) | 0 |
| `grep -cE "year-by-monotony\|year-resets-per-table\|year-jump" tests/test_check_docs.py` | **3** (`:1039`, `:1089`, `:1090`; 4 ids) | 0 |
| Comando AST del patrón 7 | `conftest.py:34 setup_database`, `:51 db_session`, `:62 client`, `:89 override_azure_storage_client`, `:76 override_get_db`, `test_email.py:43 send_message` | `tests\conftest.py:85 override_get_db`, `tests\test_email.py:43 send_message` |
| `pytest tests/test_check_docs.py -q` | `257 passed` | `257 passed` |

`--collect-only` lista los ids nuevos: `[year-nearest-to-version]`, `[year-nearest-in-each-table]`,
`[new-year-rows-marked]`, `[new-year-row-in-future]`.

## Compuerta tras la fase (`./venv/Scripts/python.exe scripts/check.py`, exit 1)

La corrí sobre el árbol editado justo antes del commit; solo estaban modificados los 5 archivos de la fase.

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
  --> app\api\dependencies.py:1:1
 --> app\api\routers\audit.py:1:1
 --> app\core\email.py:1:1
 --> app\db\database.py:1:1
 --> app\repositories\user_repository.py:1:1
 --> app\schemas\audit.py:1:1
 --> app\services\audit_service.py:1:1
  --> app\services\user_service.py:1:1
Found 8 errors.
app\db\database.py:11: error: Argument 1 to "create_async_engine" has incompatible type "str | None"; expected "str | URL"  [arg-type]
app\core\security.py:71: error: Argument "key" has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
app\core\security.py:87: error: Argument "key" has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
app\services\user_service.py:124: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
tests\test_user_service.py:104: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
tests\test_user_service.py:198: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
tests\test_user_service.py:275: error: Argument 2 has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
tests\test_user_service.py:293: error: Argument 2 has incompatible type "str | None"; expected "RSAPrivateKey | EllipticCurvePrivateKey | Ed25519PrivateKey | Ed448PrivateKey | PyJWK | str | bytes"  [arg-type]
app\api\dependencies.py:95: error: Argument 2 has incompatible type "str | None"; expected "RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | PyJWK | str | bytes"  [arg-type]
Found 9 errors in 5 files (checked 53 source files)
Contracts: 4 kept, 0 broken.
TOTAL                                        943     23    138     19  96.11%
547 passed, 5 warnings in 21.09s
```

Líneas `error:` de mypy (contadas filtrando por `error:`): 9. Las cifras coinciden con la fila C: ruff 8 (solo `app/`),
mypy 9 con el conjunto exacto de A4 (5 de `app/` y `tests\test_user_service.py:104`, `:198`, `:275`, `:293`, sin
desplazar: la fase C no toca ese archivo), 4 kept, 547 passed, 96.11 % (= línea base).

Archivos tocados, por separado: `./venv/Scripts/python.exe -m ruff check <los 5>` → `All checks passed!`;
`ruff format --check tests/` → `18 files already formatted`; `mypy <los 5>` → 0 líneas `error:` en `tests\` (las 5 que
imprime son las de `app/` que siguen las importaciones, todas de A4).

## Checklist `test-sanitizer`

Sin aserciones, fixtures ni comportamiento nuevos: solo importaciones, un comentario, docstrings e ids de parametrize.
Nada que sanear; no reescribí ninguna prueba.

## Desviaciones y dudas

1. **RED de los ids: 3 líneas, no 2.** El plan dice `grep -cE ...` "2 → 0 (2 líneas, 4 ids)", pero los 4 ids están en 3
   líneas (`:1039` con dos, `:1089` y `:1090` con uno cada uno; el propio plan cita `:1089-1090`). Es un error de conteo
   del plan, no del código: el objetivo (0) y los 4 renombrados son los del plan.
2. **Corte de la lista `ids=` de `test_r7_flags_closed_row_without_mark`:** con los nombres nuevos la línea supera 100
   columnas, así que va en una línea por elemento (el corte de `ruff format`, como prevé el plan). Por eso
   `test_check_docs.py` suma `+8 −3` y no `+3 −3`.
3. **Comentario en `test_audit.py:22`, no `:21`:** la línea se movió una por el import de la fase B; el plan ya la cita
   como "`:21` en la base".
4. **Línea de `override_get_db`:** queda en `conftest.py:85` (76 + 9 de los tres `Yields:` de encima). La verificación
   final espera `:86`, que se alcanza cuando la fase G añada `from datetime import timedelta`.

## Residuales

Ninguno nuevo. `sqlalchemy.future` sigue en `app/repositories/*` (S2, fuera de alcance).
