# Handoff — BE-38 · Fase F (el alta de un paquete audita lo guardado, BE-61)

- Fecha: 18 nov 2026. Rama `item/be-38`. Commit de la fase: `284b3af`.
- Plan: `docs/deuda/BE-38/plan.md`, fase F, Anexo F **y la enmienda E2** (instrucción literal de David: "Rige la
  sección "Enmiendas aprobadas" de plan.md: E0 (opción b), E1 (mutantes en copias git archive, nunca en el árbol del
  repo) y E2 (el test del tercer decimal cubre también ServiceCreate; orden de aplicación en E2.7)").

## Ritual de arranque

- `git status --short`: limpio. HEAD `018f8de`. `current_target` = `Fase_F`. `gaps.md` sin `[BLOQUEANTE]` abiertos.
- Vigencia de la línea base: `git fetch origin` correcto. `git rev-parse --short origin/develop` = `290a942`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `290a942`; `Base develop` de `verificacion.md` = `290a942`.
  Coinciden los dos.
- Compuerta antes de tocar nada (exit 0, todos los pasos con ✔): `71 files already formatted` · `All checks passed!` ·
  `Success: no issues found in 66 source files` · `Contracts: 4 kept, 0 broken.` · `TOTAL 1064 10 154 6 98.69%` ·
  `796 passed, 25 warnings`. Igual al GREEN de la fase E; no peor.

## Archivos tocados (2, los del plan)

- `app/services/tourist_services_service.py`: import de `audit_value`; en `create_tourist_package`, `stored` con
  `audit_value(getattr(saved, field))` por cada campo del volcado y `stored["image_urls"]` con las URL de
  `saved.images`; `changes=stored`; dos líneas de docstring.
- `tests/test_services.py`: (E2) import de `ServiceCreate` y `test_be38_schema_keeps_rejecting_a_third_decimal` sobre los
  dos DTO; (Anexo F) `test_create_package_promotes_temporal_url` afirma la fila `CREATE` completa y amplía su
  docstring; sección `# === BE-61` con `test_be61_create_audits_every_promoted_url_in_order` al final del archivo.

Orden de aplicación (E2.7): el diff de E2 primero (`git apply`, limpio); después los dos primeros hunks de tests del
Anexo F (`git apply`: `Hunk #1 succeeded at 457 (offset 2 lines)`, `Hunk #2 succeeded at 474 (offset 2 lines)`); el
tercero (bloque BE-61), tal cual, al final del archivo, tras `test_be38_schema_keeps_rejecting_a_third_decimal`; el hunk
de `app/` del Anexo F al final (GREEN), `Applied patch ... cleanly`. Comparación de las líneas `+`/`-` del `git diff`
antes del commit contra las del Anexo F más E2 (ordenadas): `diff` sin salida (idénticas).

`git diff --numstat` antes del commit: `7 3` (`app/services/tourist_services_service.py`) y `63 7`
(`tests/test_services.py`). El plan: `7 3` y, con E2.4, `63 7`; total `+70 −10`. Idénticos.

`git show --stat --format= 284b3af`:

```
 app/services/tourist_services_service.py | 10 +++--
 tests/test_services.py                   | 70 ++++++++++++++++++++++++++++----
 2 files changed, 70 insertions(+), 10 deletions(-)
```

## RED (solo los tests, suite completa, `pytest -q -rf -p no:cacheprovider`)

```
FAILED tests/test_services.py::test_create_package_promotes_temporal_url - As...
FAILED tests/test_services.py::test_be61_create_audits_every_promoted_url_in_order
2 failed, 795 passed, 25 warnings in 31.74s
```

Plan (E0.2 y E2.4, opción (b)): `2 failed, 795 passed`, los dos tests citados. Coincide. El test de E2 pasa antes y
después, como dice E2.4.

## GREEN — compuerta completa (`./venv/Scripts/python.exe scripts/check.py`, exit 0)

```
71 files already formatted
All checks passed!
Success: no issues found in 66 source files
Contracts: 4 kept, 0 broken.
Name                                       Stmts   Miss Branch BrPart   Cover   Missing
---------------------------------------------------------------------------------------
app\db\database.py                            13      4      0      0  69.23%   31-35
app\main.py                                   57      1     18      1  97.33%   72
app\repositories\user_repository.py           53      1      6      1  96.61%   67
app\schemas\user.py                           58      2      8      2  93.94%   112, 126
app\services\tourist_services_service.py     110      2     38      2  97.30%   51, 301
---------------------------------------------------------------------------------------
TOTAL                                       1066     10    154      6  98.69%

33 files skipped due to complete coverage.
Required test coverage of 92.0% reached. Total coverage: 98.69%
797 passed, 25 warnings in 32.40s
--- pytest + cobertura: OK en 35.8s

=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

- pytest: `797 passed` (plan (b): 797). Cobertura: 98,69 % (plan: 98,69 %; ≥ 98,49 % de la línea base y ≥ 98,69 % de la
  fase E). Avisos: 25, como la base.
- Sobre los archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `2 files already formatted`;
  `mypy` → `Success: no issues found in 2 source files`.
- Contratos: 4 kept, 0 broken (= línea base). Totales ruff 0 y mypy 0 (= línea base).
- Comprobaciones de la Verificación final que ya aplican tras F (`git grep`):
  - Comando 11: `app/schemas/service.py:11`, `:61`, `:147` (plan, (b): `:11 :61 :147`).
  - Comando 14: `test_auth.py:3`, `test_services.py:12`, `test_user_update_audit.py:5`; `-k "be38 or be61"` →
    `36 passed, 761 deselected` (plan, (b): idéntico).
  - Comando 15 con `app/repositories/service_repository.py` añadido (E0.2): salida vacía.
  - Comando 1 (`log_transaction(` en `app`): 13 líneas (plan: 13).

## Mutantes de la fase: M14, M8b, M13base, M13dpbase (E1 y E2.5)

Dónde: una copia `git archive 284b3af | tar -x` por mutante en
`C:\Users\dalde\AppData\Local\Temp\claude\3d697dd508bd54e7\a4fa5001-8462-4038-9d68-363052399d29\scratchpad\copiesF\<id>`,
más una prístina (`copiesF\pristine`). Cada mutante aplicado con `scratchpad\tools\mutate.py` (reemplazo exacto con
recuento comprobado = 1); `diff -ru pristine <id>` muestra solo la línea o el bloque mutado. Suite completa con el Python
del venv del repo por ruta (`pytest -q -rf -p no:cacheprovider`, cwd = la copia). La sonda de import en `copiesF\M13base`
cita `...\scratchpad\copiesF\M13base\app\schemas\service.py` en su traceback: la copia importa su propio código. Repo:
`git status --short` vacío y `git diff --quiet HEAD -- app tests` → 0 después de los mutantes. Salida literal:

```
== M14 (284b3af):
    FAILED tests/test_services.py::test_create_package_promotes_temporal_url - As...
    FAILED tests/test_services.py::test_be61_create_audits_every_promoted_url_in_order
    2 failed, 795 passed, 25 warnings in 31.74s
== M8b (284b3af):
    FAILED tests/test_services.py::test_create_package_promotes_temporal_url - As...
    FAILED tests/test_services.py::test_be38_create_answers_the_price_with_two_decimals[integer]
    FAILED tests/test_services.py::test_be38_create_answers_the_price_with_two_decimals[one-decimal]
    3 failed, 794 passed, 25 warnings in 33.54s
== M13base (284b3af):
    FAILED tests/test_services.py::test_be38_schema_keeps_rejecting_a_third_decimal
    1 failed, 796 passed, 25 warnings in 32.56s
== M13dpbase (284b3af):
    FAILED tests/test_services.py::test_be38_schema_keeps_rejecting_a_third_decimal
    1 failed, 796 passed, 25 warnings in 32.62s
```

Motivo del fallo de M13base y M13dpbase (test aislado en su copia): `Failed: DID NOT RAISE <class
'pydantic_core._pydantic_core.ValidationError'>` en `tests\test_services.py:1193`: muere por la regla (redondeo
silencioso), no por un error colateral.

Mutaciones (diff contra la copia prístina):
- M14: `stored["image_urls"] = [image.image_url for image in saved.images]` → `stored["image_urls"] = raw_urls`.
- M8b: sin el `format_base_price` de `ServiceBase`.
- M13base: el `format_base_price` de `ServiceBase` con `@field_validator("base_price", mode="before")` y cuerpo
  `return v if v is None else Decimal(str(v)).quantize(_CENTS)` (el mismo cuerpo que el ejecutor de E y el auditor de E
  usaron para M13/M13base).
- M13dpbase: sin `decimal_places=2` en `ServiceBase.base_price`.

Contraste con el plan: M14 `2 failed` (plan: "fila `CREATE` y BE-61", los mismos dos); M8b `3 failed` (plan: "precio de
alta ×2, fila `CREATE`", los mismos tres: vuelve a matar la fila, como anticipó el handoff de E); M13base y M13dpbase
mueren con el test de E2 (E2.5), con la misma causa que midió la sesión Mentor (`DID NOT RAISE`).

## Checklist `test-sanitizer` (solo estándares; sin reescrituras)

Tests HTTP con las fixtures centrales (`client`, `db_session`, `admin_headers`, `storage_double` con dobles `autospec`
del almacenamiento) y los ayudantes ya existentes (`_create_payload`, `_audit_rows`); aserciones sobre código HTTP,
URL de la respuesta, llamadas al doble con argumentos y en orden (`await_args_list`) y la fila `CREATE` completa. Los
valores en español de la fila (`name`, `description`) son datos guardados del payload, no texto humano de un mensaje;
los dicta el Anexo F. El test de E2 afirma `loc` del error, no su texto. Nombres y docstrings en inglés. Nada que corregir.

## Desviaciones, residuales y dudas

- **Mensaje de commit (E2.1):** E2 pide "el mensaje que dicta el plan más una viñeta al final de la lista", pero el
  mensaje de F no tiene lista. Se añadió la viñeta literal (`  - tests/test_services.py: the third-decimal guard also
  covers ServiceCreate.`) como último párrafo del cuerpo, antes del trailer `Co-Authored-By`; el resto del mensaje es
  idéntico al del plan. Si la auditoría lo quiere en otro sitio, es solo texto del commit.
- Ninguna otra desviación. Ningún archivo fuera de la fase; `app/repositories/service_repository.py` intacto (comando 15).
- R7 sin cambios (M2 vive desde E, aceptado en E0.2; no se volvió a medir en F, no es criterio de la fase).
- Para G: la suite y la cobertura deben seguir en `797 passed` · 98,69 % (documental).
