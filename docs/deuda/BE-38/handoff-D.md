# Handoff — BE-38 · Fase D (`PUT /servicios/{id}`, activar/desactivar sin cambio y el orden de las imágenes, R1)

- Fecha: 18 nov 2026. Rama `item/be-38`. Commit de la fase: `53ea731`.
- Plan: `docs/deuda/BE-38/plan.md`, fase D y Anexo D; aprobado con E0. La fase D se aplicó con el texto del plan tal
  cual: el test de precio afirma `{"old": "50000.00", "new": "60000"}`; la línea que la opción (b) reescribe es de la
  fase E y no se tocó.
- E0.4: el `alembic check` contra PostgreSQL lo corre David antes y después de esta fase (la pasada de "antes" está en
  `docs/bitacora/2026-11-18.md`). Este ejecutor no lo corrió ni lo esperó.

## Ritual de arranque

- `git status --short`: limpio. HEAD `71c4b6f`. `current_target` = `Fase_D`.
- Vigencia de la línea base: `git fetch origin` correcto. `git rev-parse --short origin/develop` = `290a942`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `290a942`; `Base develop` de `verificacion.md` = `290a942`.
  Coinciden los dos.
- Compuerta antes de tocar nada (exit 0, todos los pasos con ✔): `71 files already formatted` · `All checks passed!` ·
  `Success: no issues found in 66 source files` · `Contracts: 4 kept, 0 broken.` ·
  `TOTAL 1051 10 150 7 98.58%` · `773 passed, 25 warnings`. Igual al GREEN de la fase C; no peor.

## Archivos tocados (4, los del plan)

- `app/services/tourist_services_service.py`: import de `changed_fields`; `toggle_package_status` calcula `estado`
  primero y muta, guarda y audita solo dentro de `if service.is_available != is_available:` (respuesta sin cambio);
  `update_package_details`: `changes = changed_fields(service, update_dict)` antes del bucle `setattr`,
  `old_urls = [image.image_url for image in service.images]` antes de `images.clear()`, paso 2.8
  (`if definitive_urls != old_urls: changes["image_urls"] = {"old": old_urls, "new": definitive_urls}`) y el bloque de
  auditoría con `if changes:` / `changes=changes` (sale `payload_changes`). Docstrings de los dos métodos.
- `app/models/service.py`: `order_by=lambda: ServiceImage.id` en `TouristService.images` (R1) y dos líneas de docstring.
- `tests/test_services.py`: import de `AuditAction`; `test_be37_null_on_description_still_clears_it` afirma el formato
  `{"old", "new"}`; `test_be37_null_on_image_urls_still_keeps_the_images` añade `audits == []`; sección BE-38 al final con
  `_audit_rows`, `_columns` y los 15 casos nuevos del Anexo D.
- `tests/test_models_schema.py`: `test_service_images_load_in_stored_order` (R1).

Texto copiado del diff literal del Anexo D. `git diff --numstat` antes del commit: `5 1` (`app/models/service.py`),
`27 16` (`tourist_services_service.py`), `8 0` (`test_models_schema.py`), `225 2` (`test_services.py`); el plan dicta
`27 16`, `5 1`, `225 2`, `8 0`: idénticos. Nota de proceso: el hook de ruff (`--fix`) borra un import mientras aún no se
usa; se repuso tras escribir el código que lo usa, y el diff final es el del Anexo.

`git show --stat --format= 53ea731`:

```
 app/models/service.py                    |   6 +-
 app/services/tourist_services_service.py |  43 +++---
 tests/test_models_schema.py              |   8 ++
 tests/test_services.py                   | 227 ++++++++++++++++++++++++++++++-
 4 files changed, 265 insertions(+), 19 deletions(-)
```

(+265 −19, el `numstat` de la tabla de fases del plan.)

## RED (solo los tests, suite completa, `pytest -q -rf -p no:cacheprovider`)

```
FAILED tests/test_models_schema.py::test_service_images_load_in_stored_order
FAILED tests/test_services.py::test_be37_null_on_description_still_clears_it
FAILED tests/test_services.py::test_be37_null_on_image_urls_still_keeps_the_images
FAILED tests/test_services.py::test_be38_unchanged_package_update_returns_200_without_audit_row[name-same]
FAILED tests/test_services.py::test_be38_unchanged_package_update_returns_200_without_audit_row[name-normalized]
FAILED tests/test_services.py::test_be38_unchanged_package_update_returns_200_without_audit_row[price-same-value]
FAILED tests/test_services.py::test_be38_unchanged_package_update_returns_200_without_audit_row[available-same]
FAILED tests/test_services.py::test_be38_unchanged_package_update_returns_200_without_audit_row[description-null-already-null]
FAILED tests/test_services.py::test_be38_unchanged_package_update_returns_200_without_audit_row[empty-images-without-images]
FAILED tests/test_services.py::test_be38_resent_image_list_returns_200_without_audit_row
FAILED tests/test_services.py::test_be38_reordered_image_list_audits_the_new_order
FAILED tests/test_services.py::test_be38_partial_package_change_audits_only_the_changed_field
FAILED tests/test_services.py::test_be38_price_change_audits_old_and_new_values
FAILED tests/test_services.py::test_be38_image_change_audits_the_stored_urls
FAILED tests/test_services.py::test_be38_status_route_without_change_returns_200_without_audit_row[activate-active]
FAILED tests/test_services.py::test_be38_status_route_without_change_returns_200_without_audit_row[deactivate-inactive]
16 failed, 773 passed, 25 warnings in 26.18s
```

Plan: `16 failed, 773 passed`, misma lista ("Mediciones", 1). Coincide caso por caso; las dos guardas de estado
(`test_be38_status_route_with_change_audits_the_action` ×2) pasan desde el inicio, como dice el plan.

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
TOTAL                                       1055     10    154      6  98.68%
789 passed, 25 warnings in 35.44s

=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

- pytest: `789 passed` (plan: 789). Cobertura: 98,68 % (plan: 98,68 %, `TOTAL 1055 10 154 6`, idéntico; ≥ 98,49 % de la
  línea base de la verificación y ≥ 98,58 % de la fase C). Avisos: 25, como la base.
- Sobre los archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → ya formateados (paso de la
  compuerta); `mypy` → `Success: no issues found in 4 source files`.
- Contratos: 4 kept, 0 broken (= línea base).
- Comprobaciones de la Verificación final que ya aplican tras D (`git grep`):
  - Comando 3 (`if update_dict:|payload_changes|activation_success|activate_user|changes=update_dict` en `app tests`):
    sin salida, exit 1.
  - Comando 5 (`if changes:`): `tourist_services_service.py:1`, `user_service.py:2` (el plan: 2 y 1).
  - Comando 6: `app/services/tourist_services_service.py:132`. Comando 4: `tourist_services_service.py:289`. El plan
    cita `:136` y `:293`, números de la copia final: la fase F añade 4 líneas netas más arriba (`create_tourist_package`,
    +7 −3). Diferencia esperada, no desviación.
  - Comando 10: `app/models/service.py:52` (plan: `:52`).

## Mutantes de la fase: M2, M3p, M6, M7, M9 y M10

Sobre el árbol de trabajo de la fase D (antes del commit), con un script del scratchpad que muta un archivo, corre la
suite completa (`pytest -q -rf -p no:cacheprovider`) y restaura los bytes originales (md5 comprobado por mutante;
`git diff --numstat` igual antes y después). Salida literal:

```
== M2 (app/services/audit_service.py): 1 failed, 788 passed, 25 warnings in 33.00s
    FAILED tests/test_services.py::test_be38_unchanged_package_update_returns_200_without_audit_row[price-same-value]
== M3p (app/services/tourist_services_service.py): 3 failed, 786 passed, 25 warnings in 33.04s
    FAILED tests/test_services.py::test_be37_null_on_description_still_clears_it
    FAILED tests/test_services.py::test_be38_partial_package_change_audits_only_the_changed_field
    FAILED tests/test_services.py::test_be38_price_change_audits_old_and_new_values
== M6 (app/services/tourist_services_service.py): 2 failed, 787 passed, 25 warnings in 33.70s
    FAILED tests/test_services.py::test_be38_status_route_without_change_returns_200_without_audit_row[activate-active]
    FAILED tests/test_services.py::test_be38_status_route_without_change_returns_200_without_audit_row[deactivate-inactive]
== M7 (app/services/tourist_services_service.py): 1 failed, 788 passed, 25 warnings in 32.24s
    FAILED tests/test_services.py::test_be38_image_change_audits_the_stored_urls
== M9 (app/services/tourist_services_service.py): 1 failed, 788 passed, 25 warnings in 33.50s
    FAILED tests/test_services.py::test_be38_reordered_image_list_audits_the_new_order
== M10 (app/models/service.py): 1 failed, 788 passed, 25 warnings in 34.33s
    FAILED tests/test_models_schema.py::test_service_images_load_in_stored_order
```

Mutaciones: M2 `if getattr(entity, field) != value` → `if audit_value(getattr(entity, field)) != audit_value(value)`;
M3p `changes = changed_fields(...)` después del bucle `setattr`; M6 `if service.is_available != is_available:` →
`if True:`; M7 `"new": definitive_urls` → `"new": raw_urls`; M9 `if definitive_urls != old_urls:` →
`if set(definitive_urls) != set(old_urls):`; M10 sin la línea `order_by=lambda: ServiceImage.id,`.

Los seis mueren, con exactamente los casos que el plan nombra ("Mediciones", 4). Contraste de cifras:
- M2: `1 failed, 788 passed`, idéntico a la medición del plan sobre la copia de la fase D. (Sobre la copia final (b)
  vive: riesgo 4, R7; eso ocurre tras la fase E, no aquí.)
- M3p 3, M6 2, M7 1, M9 1, M10 1 casos fallidos: los mismos que en las copias finales A–G; solo cambia el número de
  `passed` (786–788 aquí frente a 790–796 allí), porque la suite final es mayor. Ningún caso fallido falta ni sobra:
  ningún test que complete estos mutantes nace en una fase posterior.

## Checklist `test-sanitizer` (solo estándares; sin reescrituras)

Pruebas HTTP con las fixtures centrales (`client`, `db_session`, `admin_headers`, `storage_double`/`classifying_storage`,
dobles `autospec` del cliente de almacenamiento, infraestructura externa); preparación con `commit()` antes de la
petición y `db_session.refresh` después (ADR-0011); aserciones sobre código, estructura del cuerpo (`id`, `images`,
`set(response.json()) == {"success", "message"}`), estado refrescado, filas de `AuditLog` y llamadas al CDN
(`assert_awaited_once_with(TEMP_URL)`, `assert_not_awaited`); ningún texto en español afirmado (el mensaje de la ruta de
estado solo se comprueba por clave). El test de R1 es de mapeo, como dicta el plan (en SQLite el orden ya es el de
`id`). Nada que corregir.

## Residuales y dudas

- Ninguna desviación del plan. Ningún archivo fuera de la fase.
- Pendiente humano (E0.4): segunda pasada de `alembic current` / `alembic check` de David tras la auditoría de D; debe
  dar la misma salida que la de "antes" registrada en `docs/bitacora/2026-11-18.md`.
- R2 sigue: reenviar la misma lista recrea las filas de `service_images` (ahora sin fila de auditoría); destino, nota
  en BE-26 (E0.6); no se toca el backlog en esta fase.
- Con la opción (b), la fase E reescribe la línea `"new": "60000"` de `test_be38_price_change_audits_old_and_new_values`
  a `"new": "60000.00"`; tras E, M2 deja de morir (aceptado en E0.2).
