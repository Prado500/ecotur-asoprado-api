# Handoff — BE-37 · Fase C (`ServiceUpdate`)

- Commit de la fase: `dac6464` — `fix(schemas): reject explicit null on NOT NULL fields of ServiceUpdate` (mensaje exacto
  del plan; bloque "Commit" de la fase C, plan l. 332-352, sin la sangría de dos espacios, comparado con `diff` contra
  `git log -1 --format=%B dac6464` → idéntico; trailer `Co-Authored-By` incluido; línea más larga, 70 columnas).
- Rama: `item/be-37`, sobre `8cf2fd1` (auditoría PASS de la fase B).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 17 nov 2026.
- Enmiendas que aplican: E0.3 (11 casos en esta fase, incluido que el 422 llega antes de cualquier llamada al CDN),
  E0.5 (R1 → fila BE-60 y R2 → nota en S5: destinos de cierre, no se escriben en esta fase), E0.7 (`AGENTS.md` no se
  toca). `gaps.md` contiene las auditorías A y B, ambas PASS con 0 bloqueantes: no limitan el alcance.

## Ritual de arranque

- `git status --short`: limpio. HEAD `8cf2fd1`. `current_target` = `Fase_C`; `Fase_A` `completed` en `4c4acb7`,
  `Fase_B` `completed` en `99f48ae`.
- Vigencia de la línea base: `git fetch origin` sin errores (refrescado). `git rev-parse --short origin/develop` =
  `c3b5069`; `git rev-parse --short $(git merge-base HEAD origin/develop)` = `c3b5069`; `Base develop` de
  `verificacion.md` = `c3b5069`.
- Compuerta antes de tocar nada (`./venv/Scripts/python.exe scripts/check.py`, exit 0), igual al cierre de la fase B y
  mejor que la línea base de la verificación (731 passed, 97,65 %):
  `70 files already formatted` · `All checks passed!` · `Success: no issues found in 65 source files` ·
  `Contracts: 4 kept, 0 broken.` · `TOTAL 1046 11 152 9 98.33%` · `746 passed, 18 warnings in 31.86s`.

## Archivos tocados (los dos de la fase)

`git show --stat --format= dac6464`:

```
 app/schemas/service.py |  26 ++++++++----
 tests/test_services.py | 112 +++++++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 130 insertions(+), 8 deletions(-)
```

`git diff --numstat 8cf2fd1 dac6464` (criterio del plan: `18 8` y `112 0`):

```
18	8	app/schemas/service.py
112	0	tests/test_services.py
```

## Fidelidad al dictado

- `tests/test_services.py`: dos líneas en blanco y luego las l. 1007-1116 del plan (Anexo C) añadidas con `sed` al
  final del archivo (tras la l. 767), sin teclear.
- `app/schemas/service.py`: el diff del Anexo C (plan l. 955-1001) aplicado con `git apply` tras añadirle la cabecera
  `--- a/` / `+++ b/`; `git apply --check` limpio. `description` e `image_urls` sin cambio.

## TDD

- **RED** (tests escritos, `app/` sin tocar):
  `./venv/Scripts/python.exe -m pytest tests/test_services.py -k be37 -q` → `7 failed, 4 passed, 36 deselected in
  0.69s`. Fallan S1 ×5 (`name`, `category`, `base_price`, `max_capacity`, `is_available`) y S2 ×2 (`replace`,
  `empty`), los siete con `assert 409 == 422` (contado con `grep | uniq -c`). Pasan S3, S4 y S5 ×2. Suite completa:
  `7 failed, 750 passed, 18 warnings in 31.83s`. Igual que el plan.
- **GREEN**: el mismo comando → `11 passed, 36 deselected, 7 warnings in 0.29s`.

## Compuerta tras la fase (`./venv/Scripts/python.exe scripts/check.py`, exit 0)

Bloque RESUMEN literal:

```
=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

Líneas clave literales:

```
70 files already formatted
All checks passed!
Success: no issues found in 65 source files
Contracts: 4 kept, 0 broken.
app\main.py                                   57      1     18      1  97.33%   72
app\schemas\user.py                           58      2      8      2  93.94%   112, 126
TOTAL                                       1046     10    150      8  98.49%
757 passed, 25 warnings in 33.28s
Compuerta superada.
```

- pytest: 757 passed, 0 failed (746 + 11). Cobertura 98,49 % (≥ 98,33 % de la fase B y ≥ 97,65 % de la verificación).
  Ratchet: ruff 0, mypy 0 en 65, 4 kept. Idéntico a la copia final del plan (Mediciones, bloque 3).
- Sobre los archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `2 files already
  formatted`; `mypy app/schemas/service.py tests/test_services.py` → `Success: no issues found in 2 source files`.
- Avisos 18 → 25: el aviso deprecado de `HTTP_422_UNPROCESSABLE_ENTITY` por cada 422 nuevo (residual R2, previsto).

## Mutantes

Copia `git archive HEAD` (8cf2fd1) en el scratchpad con los dos archivos de la fase superpuestos (sin diferencias de
contenido con el repo; nunca se mutó el repo). Script `mutscripts/run_mutants.py` del scratchpad: una sustitución
exacta por mutante (debe ser única), suite completa, restauración del original. Salida literal:

```
== MA-after: 757 passed, 25 warnings in 30.28s
== MS-name: 3 failed, 754 passed, 22 warnings in 30.74s
    FAILED tests/test_services.py::test_be37_null_on_not_null_package_field_returns_422_without_side_effects[name]
    FAILED tests/test_services.py::test_be37_null_beside_new_images_touches_no_blob[replace]
    FAILED tests/test_services.py::test_be37_null_beside_new_images_touches_no_blob[empty]
== MS-category: 1 failed, 756 passed, 24 warnings in 25.49s
    FAILED tests/test_services.py::test_be37_null_on_not_null_package_field_returns_422_without_side_effects[category]
== MS-base_price: 1 failed, 756 passed, 24 warnings in 23.53s
    FAILED tests/test_services.py::test_be37_null_on_not_null_package_field_returns_422_without_side_effects[base_price]
== MS-max_capacity: 1 failed, 756 passed, 24 warnings in 27.95s
    FAILED tests/test_services.py::test_be37_null_on_not_null_package_field_returns_422_without_side_effects[max_capacity]
== MS-is_available: 1 failed, 756 passed, 24 warnings in 29.17s
    FAILED tests/test_services.py::test_be37_null_on_not_null_package_field_returns_422_without_side_effects[is_available]
== MS-description+: PATTERN NOT UNIQUE (2): 'description: str | None = Field(None, max_length=1000)'
== MS-image_urls+: 1 failed, 756 passed, 26 warnings in 29.30s
    FAILED tests/test_services.py::test_be37_null_on_image_urls_still_keeps_the_images
== M6: 757 passed, 25 warnings in 30.12s
```

MS-description+ no corrió en esa pasada: la misma línea existe en `ServiceBase` (l. 27). Repetido con
`mutscripts/run_desc.py`, que muta solo la última ocurrencia (la de `ServiceUpdate`) y restaura (`cmp` con el repo
idéntico después):

```
mutated line in: class ServiceUpdate line 118
== MS-description+: 1 failed, 756 passed, 26 warnings in 29.97s
    FAILED tests/test_services.py::test_be37_null_on_description_still_clears_it
```

Resultado: los nueve dieron lo mismo que la tabla del plan. MS-name 3, MS-category 1, MS-base_price 1,
MS-max_capacity 1, MS-is_available 1, MS-description+ 1, MS-image_urls+ 1, cada uno muerto por el test que se declaró.
MA-after (equivalente) y M6 (inalcanzable por HTTP, a propósito) sobreviven con 757 passed, como prevé el plan.
Los mutantes de la fase B (MU-*, MX-exclude_none, MF-falsy) ya están en `handoff-Fase_B.md` y no se repitieron.

## Verificación final (rama tras la fase C)

- #1 `NoExplicitNull` en `app` → 14 líneas: `partial_update.py` :36 :38; `service.py` :8 :117 :119 :120 :123 :124;
  `user.py` :7 :170 :173 :179 :186 :187.
- #2 `", NoExplicitNull] ="` → 10 líneas: `service.py` :117 :119 :120 :123 :124; `user.py` :170 :173 :179 :186 :187.
- #3 opcionales que admiten `None` → 9 líneas: `user.py` :65 :152 :185; `service.py` :27 :76 :93 :100 :118 :125.
- #4 `exclude_none` en `app` → sin salida (exit 1); `exclude_unset=True` en `app/services` → 3 líneas
  (`tourist_services_service.py` :282 :337, `user_service.py` :284).
- #5 `update_dict.get("is_active") is False` → 1 línea, `user_access_policy.py:114`.
- #6 `if v is None` en `app/schemas` → sin salida (exit 1).
- #7 `null` explícito en tests → 12 líneas: `test_services.py` :815 :832 :840 :853 :874; `test_user_access_policy.py`
  :190 :287; `test_user_update_null.py` :34 :95 :124 :135 :143.
- #8 `email=None` → `tests/test_email_case.py:120`; el nombre viejo → sin salida (exit 1).
- #9 `ADR-0020` en `app tests` → `partial_update.py` :6 :37, `service.py` :114, `user.py` :167, `test_email_case.py`
  :118, `test_services.py` :770, `test_user_update_null.py` :1 :67; en `docs/adr` → los archivos 0018 y 0020.
- #10 `def test_be37_` → `test_email_case.py:1`, `test_services.py:5`, `test_user_update_null.py:6`;
  `pytest -k be37 -q` → `27 passed, 730 deselected, 17 warnings in 0.73s`;
  `pytest tests/test_user_access_policy.py -k "be35 or be36 or be58" -q` → `41 passed, 66 deselected in 1.87s`.
- #11 `git diff --stat 32b8fd4 HEAD -- <lista fuera de alcance>` → salida vacía (incluye `AGENTS.md`).
- #12 `git diff --numstat 32b8fd4 HEAD -- app tests docs/adr` → exactamente 8 líneas:

```
38	0	app/schemas/partial_update.py
18	8	app/schemas/service.py
13	9	app/schemas/user.py
9	0	docs/adr/0018-un-superadmin-reactiva-a-otro.md
63	0	docs/adr/0020-null-explicito-solo-donde-la-columna-admite-vacio.md
6	5	tests/test_email_case.py
112	0	tests/test_services.py
149	0	tests/test_user_update_null.py
```

- #13 compuerta completa → la de arriba (exit 0, 757 passed, 98,49 %).

## Checklist `test-sanitizer` (solo como checklist)

Dobles del CDN `storage_double`/`classifying_storage` con `create_autospec(AzureStorageClient, instance=True)` y
`assert_not_awaited()` sobre `delete_image` y `promote_to_permanent`; fábricas centrales (`persist_user`,
`make_auth_headers`) y helpers del propio archivo (`_persist_package`, `_stored_image_urls`); nombres en inglés; se
afirma sobre código, `raw_field`, tipo de `message`, estado, imágenes y auditoría, nunca sobre texto en español; los
guards (401/403) antes del 422 quedan congelados por S5. Sin cambios a los tests dictados.

## Desviaciones, residuales y dudas

- Desviaciones respecto al plan: ninguna. RED, GREEN, numstat, compuerta, Verificación final y mutantes cuadran.
- Incidencia de herramienta, sin efecto en el resultado: el primer script de mutantes rechazó MS-description+ por
  patrón no único (línea repetida en `ServiceBase`); se repitió acotado a `ServiceUpdate` (sección Mutantes).
- Residuales: ninguno nuevo. R1-R5 del plan siguen con el destino de E0.5 (R1 → fila BE-60; R2 → nota en S5; R4: la
  viñeta de AGENTS §3 la commitea David tras la auditoría de esta fase y antes de `/pr`, E0.7); no se escriben aquí.
- Es la última fase: `current_target` pasa a `null` (no hay fase siguiente).
