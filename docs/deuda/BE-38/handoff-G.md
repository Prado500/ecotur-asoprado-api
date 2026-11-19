# Handoff — BE-38 · Fase G (ADR-0021 y comentarios de `app/models/audit.py`)

- Fecha: 19 nov 2026. Rama `item/be-38`. Commit de la fase: `e3cdc4b`.
- Plan: `docs/deuda/BE-38/plan.md`, fase G y Anexo G, **con las enmiendas aprobadas** (instrucción literal de David:
  "Rige la sección "Enmiendas aprobadas" de plan.md: E0 (opción b; ADR-0021 con el punto 8 de la opción b, fecha 18 nov
  2026), E1 y E2."). E1 (mutantes en copias) no aplica: la fase G no tiene mutantes. E2 solo afecta a la cifra de
  `tests/test_services.py` en el comando 16 (abajo).

## Ritual de arranque

- `git status --short` al empezar: `M docs/PLAN.md`, `M docs/bitacora/2026-11-19.md`, `?? docs/commit-msg-1119-apertura-2.txt`,
  cambios de David ajenos a la fase, declarados por el orquestador; no se tocaron ni se añadieron. Durante la fase David
  los commiteó (`6e8919f docs(apertura): 19 nov, quota and working hours declared`, solo `docs/PLAN.md` y
  `docs/bitacora/2026-11-19.md`); el commit de la fase queda encima de `6e8919f`. HEAD al empezar: `d18b83e`.
- `current_target` = `Fase_G`. `gaps.md` sin `[BLOQUEANTE]` (F: PASS, 1 opcional).
- Vigencia de la línea base: `git fetch origin` correcto. `git rev-parse --short origin/develop` = `290a942`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `290a942`; `Base develop` de `verificacion.md` =
  `290a942`. Coinciden (repetido tras el commit: igual).
- Compuerta antes de tocar nada (exit 0, todos ✔): `71 files already formatted` · `All checks passed!` ·
  `Success: no issues found in 66 source files` · `Contracts: 4 kept, 0 broken.` · `TOTAL 1066 10 154 6 98.69%` ·
  `797 passed, 25 warnings`. Igual al GREEN de F; no peor.

## Archivos tocados (2, los del plan)

- `docs/adr/0021-la-auditoria-registra-solo-lo-que-cambio.md` (nuevo): texto del Anexo G (plan l.2526–2609) con
  `<FECHA>` = `18 nov 2026` (E0.1) y las tres sustituciones de la opción (b) (punto 8, segunda consecuencia,
  alternativa 6). Comprobación: en el scratchpad se reconstruyó el archivo esperado (Anexo G (a) con la fecha, más el
  diff (a)→(b) del plan l.2615–2651 aplicado con `patch -p1`: `patching file ...`, sin rechazos) y `diff` contra el del
  repo → sin salida (`IDENTICAL`). 84 líneas, la más larga 100 caracteres (medido con el intérprete).
- `app/models/audit.py`: docstring de `AuditLog`, comentario de `changes` (sin `old_values`) y traducción de
  `# "User" o "TouristService"`. Las líneas `+`/`-` de `git diff` comparadas con `diff` contra las del Anexo G
  (plan l.2491–2520): idénticas.

`git show --stat --format= e3cdc4b`:

```
 app/models/audit.py                                |  8 +--
 ...021-la-auditoria-registra-solo-lo-que-cambio.md | 84 ++++++++++++++++++++++
 2 files changed, 88 insertions(+), 4 deletions(-)
```

`git diff --cached --numstat` antes del commit: `4 4` (`app/models/audit.py`) y `84 0` (ADR). Plan: `84 0` y `4 4`,
+88 −4. Idénticos. Mensaje del commit: `diff` contra plan l.506–519 (sin la sangría del bloque) → sin salida.

## RED / GREEN (fase documental)

- RED: no hay; el plan no dicta tests ("Tests: ninguno nuevo (documental). Comprobación sustituta: compuerta completa").
- GREEN — compuerta completa (`./venv/Scripts/python.exe scripts/check.py`, exit 0), con la fase en el árbol (contenido
  idéntico al commiteado):

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
797 passed, 25 warnings in 32.69s
--- pytest + cobertura: OK en 36.8s

=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

- pytest `797 passed` (plan (b): 797), cobertura 98,69 % (plan: 98,69 %; ≥ 98,49 % de la línea base). 25 avisos, como
  la base. Contratos 4 kept, 0 broken; ruff 0 y mypy 0 en 66 (= base).
- Archivo de código tocado: `ruff check app/models/audit.py` → `All checks passed!`; `ruff format --check` → `1 file
  already formatted`; `mypy app/models/audit.py` → `Success: no issues found in 1 source file`.
- Criterio de aceptación: `old_values` 0 en `app/models/audit.py` (comando 9, exit 1); `git grep -n "<FECHA>" -- docs/adr`
  → sin salida (exit 1).

## Verificación final (tras el commit `e3cdc4b`; cifras de la opción (b), E0.2)

| # | Esperado (plan, (b)) | Obtenido |
|---|---|---|
| 1 | 13 líneas: user_service 6, tourist_services_service 5, bootstrap 1, audit_service 1 | 13: `user_service.py` :97 :154 :228 :316 :388 :449; `tourist_services_service.py` :74 :141 :176 :218 :354; `superadmin_bootstrap.py:66`; `audit_service.py:57` |
| 2 | 3: user_service :302 y :308; tourist_services_service :292 | idéntico |
| 3 | 0 (exit 1) | 0 (exit 1) |
| 4 | 4: audit_service:28; user_service :150 :308; tourist_services_service :293 | idéntico |
| 5 | user_service 2, tourist_services_service 1 | idéntico |
| 6 | 1, tourist_services_service.py:136 | idéntico |
| 7 | 10; pares :94/:97, :447/:449, bootstrap :64/:66 | idéntico |
| 8 | 6: audit_repository:16; service_repository :17 :93; user_repository :50 :73 :101 | idéntico |
| 9 | `old_values` 0 (exit 1); `ADR-0021` en audit.py :28 :43 | idéntico |
| 10 | 1, app/models/service.py:52 | idéntico |
| 11 | 3: schemas/service.py :11 :61 :147 | idéntico |
| 12 | 14 (auth 2, services 3, policy 5, user_service 2, update_audit 1, update_null 1); "BE-38" en la política 0 | idéntico; 0 (exit 1) |
| 13 | app 11 (audit.py :28 :43; service.py :30; audit_service :17 :33; tourist_services_service :35 :116 :267; user_service :114 :281 :412); tests 8 (auth :131; services 4; policy :1215; user_service :452; update_audit :4); docs/adr: el 0021 | idéntico (tests/test_services.py :462 :904 :1124 :1199); `docs/adr/0021-la-auditoria-registra-solo-lo-que-cambio.md` |
| 14 | auth 3, services 12, update_audit 5; `36 passed, 761 deselected` | idéntico; `36 passed, 761 deselected in 1.20s` |
| 15 | salida vacía (con `app/repositories/service_repository.py` añadido) | vacía (exit 0) |
| 16 | 15 líneas ("Mediciones", 5, (b)) | 15 líneas; 14 idénticas, `tests/test_services.py` `348 4` frente a `336 4` (abajo) |
| 17 | exit 0; 71 formatted; ruff 0; mypy 0 en 66; 4 kept; 797 passed; 98,69 %; 25 avisos | idéntico (bloque GREEN arriba) |

Salida literal del comando 16:

```
4	4	app/models/audit.py
5	1	app/models/service.py
0	13	app/repositories/user_repository.py
15	0	app/schemas/service.py
44	0	app/services/audit_service.py
33	18	app/services/tourist_services_service.py
35	11	app/services/user_service.py
84	0	docs/adr/0021-la-auditoria-registra-solo-lo-que-cambio.md
67	0	tests/test_auth.py
8	0	tests/test_models_schema.py
348	4	tests/test_services.py
22	6	tests/test_user_access_policy.py
82	13	tests/test_user_service.py
152	0	tests/test_user_update_audit.py
1	1	tests/test_user_update_null.py
```

## Desviaciones, residuales y dudas

- **Comando 16, `tests/test_services.py`: `348 4` en vez de `336 4`.** La cifra del plan ("Mediciones", 5) se midió
  antes de E2; E2.4 cambió el `numstat` de F en `tests/test_services.py` (`46 2` → `63 7`, `17 5` de E2) pero no
  reescribió esa línea de "Mediciones". Contra `6cae238` las 5 líneas que E2 quita las había añadido E (no estaban en la
  base), así que se ve solo el neto: 336 + 17 − 5 = 348, borradas 4 sin cambio. No es una diferencia de código: es la
  consecuencia aritmética de E2, aprobada. No se "arregló" nada.
- Commit de David en medio de la fase (`6e8919f`, solo `docs/PLAN.md` y la bitácora); no toca archivos de la fase ni
  de la Verificación final. El archivo sin seguimiento `docs/commit-msg-1119-apertura-2.txt` ya no existe en el árbol;
  no lo borró esta sesión.
- `test-sanitizer`: no aplica (ningún test tocado).
- Pendiente humano (no es fase): el paso de David antes de mezclar (panel de auditoría y qué envía la pantalla de
  edición en `image_urls`, E0.5); R6, la viñeta de AGENTS §3 tras la auditoría de G; R2 y R4, notas en BE-26 y BE-49
  (E0.6); `alembic check` de E0.4 si no consta ya en la bitácora.
