# Handoff — BE-38 · Fase E (el precio con la escala de su columna, opción (b))

- Fecha: 18 nov 2026. Rama `item/be-38`. Commit de la fase: `1d9752e`.
- Plan: `docs/deuda/BE-38/plan.md`, fase E y **solo el Anexo E(b)** (E0.2: opción (b)). El Anexo E(a) no se ejecutó:
  `app/repositories/service_repository.py` sin cambios (`git diff --stat 6cae238 HEAD -- app/repositories/service_repository.py`
  vacío). Mutantes según E1: en copias `git archive 1d9752e` del scratchpad, después del commit, nunca en el árbol del repo.

## Ritual de arranque

- `git status --short`: limpio. HEAD `584b40f`. `current_target` = `Fase_E`.
- Vigencia de la línea base: `git fetch origin` correcto. `git rev-parse --short origin/develop` = `290a942`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `290a942`; `Base develop` de `verificacion.md` = `290a942`.
  Coinciden los dos.
- Compuerta antes de tocar nada (exit 0, todos los pasos con ✔): `71 files already formatted` · `All checks passed!` ·
  `Success: no issues found in 66 source files` · `Contracts: 4 kept, 0 broken.` ·
  `TOTAL 1055 10 154 6 98.68%` · `789 passed, 25 warnings`. Igual al GREEN de la fase D; no peor.

## Archivos tocados (2, los del plan para la opción (b))

- `app/schemas/service.py`: `_CENTS = Decimal("0.01")` con su comentario; `format_base_price` (`v.quantize(_CENTS)`,
  validador `after`) en `ServiceBase` y en `ServiceUpdate`. Ningún DTO de salida cambia (A9).
- `tests/test_services.py`: imports de `ValidationError` y `ServiceUpdate`; en `test_be38_price_change_audits_old_and_new_values`
  la línea `"new": "60000"` pasa a `"new": "60000.00"`; sección nueva al final con
  `test_be38_create_answers_the_price_with_two_decimals` ×3, `test_be38_update_answers_the_price_with_two_decimals` ×3 y
  `test_be38_schema_keeps_rejecting_a_third_decimal`.

Texto copiado del diff literal del Anexo E(b); `git diff` antes del commit con los mismos hunks (`@@ -7,6 +7,9`,
`@@ -51,6 +54,12`, `@@ -130,3 +139,9`; `@@ -12,6 +12,7`, `@@ -25,6 +26,7`, `@@ -1028,7 +1030,7`, `@@ -1100,3 +1102,66`).
`git diff --numstat`: `15 0` (`app/schemas/service.py`) y `66 1` (`tests/test_services.py`); el plan dicta `15 0` y
`66 1`: idénticos. Nota de proceso: el hook de ruff marcó F821 mientras los tests nuevos existían sin sus imports
(se añadieron después, en ese orden, para que `--fix` no borrara imports aún sin uso); el diff final es el del Anexo.

`git show --stat --format= 1d9752e`:

```
 app/schemas/service.py | 15 +++++++++++
 tests/test_services.py | 67 +++++++++++++++++++++++++++++++++++++++++++++++++-
 2 files changed, 81 insertions(+), 1 deletion(-)
```

(+81 −1, el `numstat` (b) de la tabla de fases del plan.)

## RED (solo los tests, suite completa, `pytest -q -rf -p no:cacheprovider`)

```
FAILED tests/test_services.py::test_be38_price_change_audits_old_and_new_values
FAILED tests/test_services.py::test_be38_create_answers_the_price_with_two_decimals[integer]
FAILED tests/test_services.py::test_be38_create_answers_the_price_with_two_decimals[one-decimal]
FAILED tests/test_services.py::test_be38_update_answers_the_price_with_two_decimals[integer]
FAILED tests/test_services.py::test_be38_update_answers_the_price_with_two_decimals[one-decimal]
5 failed, 791 passed, 25 warnings in 31.29s
```

Plan: `5 failed, 791 passed`, misma lista ("Mediciones", 1, `RED fase E (b)`). Coincide caso por caso; `two-decimals`
(×2) y `test_be38_schema_keeps_rejecting_a_third_decimal` pasan desde el inicio, como dice el plan.

## GREEN — compuerta completa (`./venv/Scripts/python.exe scripts/check.py`, exit 0)

```
71 files already formatted
All checks passed!
Success: no issues found in 66 source files
Contracts: 4 kept, 0 broken.
app\db\database.py                            13      4      0      0  69.23%   31-35
app\main.py                                   57      1     18      1  97.33%   72
app\repositories\user_repository.py           53      1      6      1  96.61%   67
app\schemas\user.py                           58      2      8      2  93.94%   112, 126
app\services\tourist_services_service.py     108      2     38      2  97.26%   49, 297
TOTAL                                       1064     10    154      6  98.69%
796 passed, 25 warnings in 33.95s

=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

- pytest: `796 passed` (plan: 796). Cobertura: 98,69 % (plan: 98,69 %, `TOTAL 1064 10 154 6`, idéntico; ≥ 98,49 % de la
  línea base de la verificación y ≥ 98,68 % de la fase D). Avisos: 25, como la base.
- Sobre los archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `2 files already formatted`;
  `mypy` → `Success: no issues found in 2 source files`.
- Contratos: 4 kept, 0 broken (= línea base).
- Comprobaciones de la Verificación final que ya aplican tras E (`git grep`):
  - Comando 11 (`populate_existing|_CENTS` en `app`): `app/schemas/service.py:11`, `:61`, `:147` (plan, (b): `:11 :61 :147`).
  - Comando 14 (`def test_be(38|61)_` en `tests`): `test_auth.py:3`, `test_services.py:11`, `test_user_update_audit.py:5`.
    El plan da `test_services.py:12` tras G; la diferencia es `test_be61_create_audits_every_promoted_url_in_order`, que
    nace en F. Esperado, no desviación.

## Mutantes de la fase: M8b, M8c, M13 y M2 (E1)

Dónde: una copia `git archive 1d9752e | tar -x` por mutante en
`C:\Users\dalde\AppData\Local\Temp\claude\3d697dd508bd54e7\ba4274f2-c4af-46c6-a6c8-a3926f89de7b\scratchpad\copies\<id>`,
el mutante aplicado allí con un script del scratchpad (reemplazo exacto con recuento comprobado), `diff -ru` contra una
copia prístina del mismo commit, y la suite completa con el intérprete del venv del repo por ruta
(`pytest -q -rf -p no:cacheprovider`, cwd = la copia). Los tracebacks de la sonda de import de cada copia citan
`...\scratchpad\copies\<id>\app\...`: el código importado es el de la copia, no el del repo. `git status --short` del
repo vacío antes y después. Salida literal:

```
== M8b (1d9752e):
    FAILED tests/test_services.py::test_be38_create_answers_the_price_with_two_decimals[integer]
    FAILED tests/test_services.py::test_be38_create_answers_the_price_with_two_decimals[one-decimal]
    2 failed, 794 passed, 25 warnings in 31.79s
== M8c (1d9752e):
    FAILED tests/test_services.py::test_be38_price_change_audits_old_and_new_values
    FAILED tests/test_services.py::test_be38_update_answers_the_price_with_two_decimals[integer]
    FAILED tests/test_services.py::test_be38_update_answers_the_price_with_two_decimals[one-decimal]
    3 failed, 793 passed, 25 warnings in 31.70s
== M13 (1d9752e):
    FAILED tests/test_services.py::test_be38_schema_keeps_rejecting_a_third_decimal
    1 failed, 795 passed, 25 warnings in 31.70s
== M2 (1d9752e):
    796 passed, 25 warnings in 31.99s
```

Mutaciones (diff contra la copia prístina):
- M8b: sin el `format_base_price` de `ServiceBase`.
- M8c: sin el `format_base_price` de `ServiceUpdate`.
- M13: el de `ServiceUpdate` con `@field_validator("base_price", mode="before")` y cuerpo
  `return v if v is None else Decimal(str(v)).quantize(_CENTS)`: redondea antes de la comprobación `decimal_places`.
  El plan no dicta el cuerpo literal ("el validador en modo `before` (redondea antes de comprobar decimales)"); se
  eligió el cuerpo que redondea de verdad, para que el test muera por la regla y no por un `AttributeError` sobre un `str`.
- M2: `if getattr(entity, field) != value` → `if audit_value(getattr(entity, field)) != audit_value(value)`
  (`app/services/audit_service.py:47`).

Contraste con el plan ("Mediciones", 4, copias finales de (b) tras G):
- M8c `3 failed` y M13 `1 failed`: los mismos casos; solo cambia `passed` (793/795 aquí frente a 794/796 allí, la suite
  final tiene un test más).
- M8b: muere con `2 failed`; el plan mide `3 failed` sobre la copia final, y el tercero es
  `test_create_package_promotes_temporal_url`, que solo afirma la fila `CREATE` completa (`"base_price": "50000.00"`)
  desde la fase F (Anexo F; el criterio de F dice "M8b con (b), por la fila"). Esperado por el orden de las fases, no
  desviación.
- M2: vive (`796 passed`), lo que E0.2, riesgo 4 y R7 dan por esperado con la opción (b).

## Checklist `test-sanitizer` (solo estándares; sin reescrituras)

Pruebas HTTP con las fixtures centrales (`client`, `db_session`, `admin_headers`, `storage_double`, dobles `autospec`
del almacenamiento) y los ayudantes ya existentes (`_create_payload`, `_persist_package`); preparación con `commit()`
antes de la petición y `db_session.refresh`/`db_session.get` después (ADR-0011); aserciones sobre código HTTP, campo del
cuerpo (`base_price`), lista de `GET` y valor guardado; el borde del tercer decimal afirma `loc` del error, no su texto.
Ningún texto en español afirmado. Nada que corregir.

## Residuales y dudas

- Ninguna desviación del plan. Ningún archivo fuera de la fase. `app/repositories/service_repository.py` intacto (E(a)
  no se ejecuta).
- R7 se materializa como estaba previsto: M2 vive desde esta fase (aceptado en E0.2).
- R3 desaparece con (b): `PUT` responde `"60000.00"` (lo congela `test_be38_update_answers_the_price_with_two_decimals`).
- Para F: con (b), el RED medido es `2 failed, 795 passed`, y M8b vuelve a matar 3 casos al afirmar la fila `CREATE`.
