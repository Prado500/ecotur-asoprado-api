# Handoff — AF-02 Fase_B

**Commit:** `19d4efa` · `fix(flow): date R7 rows by nearest year and read R6-R7 in project time`
**Rama:** `item/AF-02`. **Base develop:** `e4e7d43`; `git fetch origin` refrescó, y `origin/develop` y el `merge-base`
dieron `e4e7d43`. P1 = B1 (E0.1) y E1 aplicadas; `pyproject.toml` no se toca.

## Archivos tocados

`git show --stat --format= 19d4efa`:

```
 scripts/check_docs.py    | 108 +++++++++++++++++++++++++---------
 tests/test_check_docs.py | 150 +++++++++++++++++++++++++++++++++++++++++++++--
 2 files changed, 224 insertions(+), 34 deletions(-)
```

`git show --name-only --format= 19d4efa`: `scripts/check_docs.py`, `tests/test_check_docs.py`. Mensaje comparado con
`plan.md:495-513` (`git cat-file commit`): idéntico.

Las 5 líneas borradas de los tests: el import de `datetime`, el caso `committed`, la lista de `ids` y las dos de `%cs`.
Ningún test de R7 existente cambia.

## Compuerta

Antes de tocar nada (`afe4618`), `./venv/Scripts/python.exe scripts/check.py`, exit 1: `57 files already formatted`,
`Found 9 errors.`, `Found 5 errors in 4 files (checked 35 source files)`, `Contracts: 4 kept, 0 broken.`,
`Total coverage: 96.11%`, `526 passed, 5 warnings in 17.61s`. Coincide con el cierre de la fase A.

Después, sobre `19d4efa`, exit 1:

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

```
57 files already formatted
Found 9 errors.
Found 5 errors in 4 files (checked 35 source files)
Contracts: 4 kept, 0 broken.
TOTAL                                        943     23    138     19  96.11%
Required test coverage of 92.0% reached. Total coverage: 96.11%
547 passed, 5 warnings in 18.96s
```

**Conjunto de ruff (9, todos I001, medido sobre el árbol del commit antes de commitear):** `app\api\dependencies.py:1:1`,
`app\api\routers\audit.py:1:1`, `app\core\email.py:1:1`, `app\db\database.py:1:1`, `app\repositories\user_repository.py:1:1`,
`app\schemas\audit.py:1:1`, `app\services\audit_service.py:1:1`, `app\services\user_service.py:1:1`,
`tests\test_user_service.py:3:1`.

**Conjunto de mypy (5, ídem):** `app\db\database.py:11`, `app\core\security.py:71`, `app\core\security.py:87`,
`app\services\user_service.py:124`, `app\api\dependencies.py:95`.

Ambos son exactamente los de la decisión 7. Ninguno está en los archivos de esta fase.

Archivos tocados, por separado, sobre `19d4efa`:

```
$ ruff format --check scripts/check_docs.py tests/test_check_docs.py
2 files already formatted
$ ruff check scripts/check_docs.py tests/test_check_docs.py
All checks passed!
$ mypy scripts/check_docs.py
Success: no issues found in 1 source file
$ mypy tests/test_check_docs.py
Success: no issues found in 1 source file
```

## RED y verde

- RED, solo tests escritos: `21 failed, 236 passed in 5.12s`. Reproducido después en copia desechable (script de A, tests de
  `19d4efa`): `21 failed, 236 passed in 1.49s`.
- Los 21 son exactamente los que lista el plan: los 6 de `test_git_last_commit_date`, `test_cierre_flag…`, `b`, `c`, `d`, el empate,
  los 3 de `test_project_date`, `project_today`, `cierre_r7_clock` y los 5 de R6. `a`, `e` y los otros 3 de `tie_and_impossible`
  pasan antes: son de caracterización.
- Causas, contadas sobre `--tb=line`: 8 `ValueError`, 5 `AttributeError`, 4 `AssertionError` del mock, 4 `assert` de conteo.
- Verde: `257 passed in 5.17s`; tras el commit, `257 passed in 5.23s`.

## Mutantes

Copia nueva en el scratchpad (`scripts/check_docs.py`, `tests/test_check_docs.py`, `docs/`, `.claude/commands/`), Python del venv
por ruta absoluta, `pytest tests/test_check_docs.py -q --tb=no -p no:cacheprovider`, cada mutante por separado sobre el script sin
mutar. Los textos salen de la lista de la sonda del planificador (`probes/mutants.txt`).

| Id | Cambio | Salida medida | Plan |
|---|---|---|---|
| M0 | sin mutar (al empezar y al terminar) | `257 passed` / `257 passed` | 257 passed |
| MB1 | candidatos = `(anchor.year,)` | `5 failed, 252 passed` | 5 |
| MB2 | `project_today` → `date.today()` | `2 failed, 255 passed` | 2 |
| MB3 | `rule_closed_days_marked`: `today=date.today` | `1 failed, 256 passed` | 1 |
| MB4 | `project_date` → `.astimezone(UTC)` | `9 failed, 248 passed` | 9 |
| MB5 | R6 sin convertir | `4 failed, 253 passed` | 4 |
| MB6 | fórmula de la fila, con monotonía | `6 failed, 251 passed` | 6 |
| MB7 | candidatos en orden inverso | `1 failed, 256 passed` | 1 |
| MB8 | sin `year − 1` | `3 failed, 254 passed` | 3 |
| MB9 | sin `year + 1` | `2 failed, 255 passed` | 2 |
| MB10 | el `except` de `_date_near` no captura `ValueError` | `3 failed, 254 passed` | 3 |
| MB11 | `hours=-4` | `3 failed, 254 passed` | 3 |
| MB12 | vuelta a `%cs` | `7 failed, 250 passed` | 7 |
| MB13 | `max` en vez de `min` | `13 failed, 244 passed` | 13 |
| MB14 | quitar `if day is None` | `2 failed, 255 passed` | 2 |
| MB15 | anchor = 1 ene del año de la versión | `5 failed, 252 passed` | 5 |

Los 15 mueren, con los conteos del plan.

## `--cierre` diferencial

Script de A sacado con `git show afe4618:scripts/check_docs.py`, `--root` al repo. Medido con `HEAD` en `afe4618` (árbol con la
fase sin commitear) y repetido sobre `19d4efa`: bytes idénticos en ambas salidas. `docs/CONTEXT.md` sigue en `d7de2d6`
(`2026-11-06T00:37:13Z`).

Script de A, exit 1:

```
Documentación desincronizada:
  - docs/CONTEXT.md:8: R6: encabezado de versión (2026-11-05) anterior al último commit (2026-11-06) — "> **Versión 3.6 — 5 nov 2026.** Cambios de esta versión: bitácora `2026-11-05` ("
  - docs/PLAN.md:3: R6: encabezado de versión (2026-11-05) anterior al último commit (2026-11-06) — "> **Versión 2.5 — 5 nov 2026.** Cambios de esta versión: bitácora `2026-11-05` ("
  - docs/backlog.md:3: R6: encabezado de versión (2026-11-05) anterior al último commit (2026-11-06) — "> **Versión 1.15 — 5 nov 2026.** Cambios de esta versión: bitácora `2026-11-05` "
```

Script de B, exit 1:

```
Documentación desincronizada:
  - docs/PLAN.md:3: R6: encabezado de versión (2026-11-05) anterior al último commit (2026-11-06) — "> **Versión 2.5 — 5 nov 2026.** Cambios de esta versión: bitácora `2026-11-05` ("
  - docs/backlog.md:3: R6: encabezado de versión (2026-11-05) anterior al último commit (2026-11-06) — "> **Versión 1.15 — 5 nov 2026.** Cambios de esta versión: bitácora `2026-11-05` "
```

`diff`: la única diferencia es la línea de `docs/CONTEXT.md:8`. Sin líneas R7 en ninguna de las dos. Ningún error nuevo. El exit 1 es
por los dos errores R6 esperados hasta el cierre: no es regresión.

## Reloj por CLI

Fixture sin git con `| Vie 6 nov | hoy | |` sin marca y versión `6 nov 2026`, `--cierre --root <fixture>`. La hora se midió en la
misma ejecución, con el mismo intérprete:

```
=== TZ=AAA-14
local 2026-11-07T12:41:44 | utc 2026-11-06T22:41:44+00:00 | bogota 2026-11-06T17:41:44-05:00
--- script A
Documentación desincronizada:
  - docs/PLAN.md:15: R7: fila de PLAN §3 cerrada sin marca en Cierre — "| Vie 6 nov | hoy | |"
exit=1
--- script nuevo
Documentación coherente (reglas: R1 comandos, R2 fechas de cronograma, R3 bloques, R4 decisiones, R5 deadline + cierre: R6 versión, R7 cierres).
exit=0
=== TZ=UTC0
local 2026-11-06T22:41:45 | utc 2026-11-06T22:41:45+00:00 | bogota 2026-11-06T17:41:45-05:00
--- script A
Documentación coherente (reglas: R1 comandos, R2 fechas de cronograma, R3 bloques, R4 decisiones, R5 deadline + cierre: R6 versión, R7 cierres).
exit=0
--- script nuevo
Documentación coherente (reglas: R1 comandos, R2 fechas de cronograma, R3 bloques, R4 decisiones, R5 deadline + cierre: R6 versión, R7 cierres).
exit=0
```

`TZ=AAA-14`, 17:41 de Bogotá, dentro de la ventana 05:00-24:00: script de A → 1 error R7, nuevo → 0, como pide el plan.

**`TZ=UTC0` no discrimina a esta hora:** a las 17:41 de Bogotá el día UTC todavía es 6 nov, así que los dos dan 0. El plan solo lo
exige tras las 19:00. **El cruce real de las 19:00 en una máquina UTC no está medido por CLI**; lo cubren `_utc_now` congelado y MB2,
MB3 y MB4.

## Verificación final

Sobre `19d4efa` (V1-V7 medidas sobre el árbol antes de commitear, mismo contenido):

| V | Salida | Plan |
|---|---|---|
| V1 | `0` | 0 |
| V2 | `0` | 0 |
| V3 | `%cs` `0` y `0`; `%cI` `2` y `2` | 0 y 0; 2 y 2 |
| V4 | `0` | 0 |
| V5 | `1` | 1 |
| V6 | `1` y `1` | 1 y 1 |
| V7 | `0` y `0` | 0 y 0 |
| V8 | `9` y `0` | 9 y 0 |
| V9 | `257 passed in 5.23s` | 257 passed |
| V10 | `docs/deuda/AF-02/gaps.md` | como mucho ese |
| V11 | ver "Compuerta" | 547, 96.11 %, 4 kept, 9, 5, exit 1 solo por ruff check y mypy |

## Desviaciones respecto al plan

1. **E1, dos líneas en vez de una.** El plan elide con `…` el resto del paréntesis, que dice `excluyentes entre sí y con la pasada
   bloqueante`. Lo conservé: esa frase no es falsa y E1 no pide quitarla. Con ella, la línea no cabe en 100 columnas y pasa a dos:
   ```text
   Comandos informativos (exit 0, salvo la excepción declarada en `estado()`: un `progress.json` que
   el sistema no deja leer; excluyentes entre sí y con la pasada bloqueante):
   ```
2. **El mensaje de commit no menciona E1.** El plan no lo prevé; se conserva el mensaje exacto, y queda declarado aquí.
3. **`scripts/check_docs.py` da +79/−29 (`git diff --numstat`), no +69/−22** como estima "Orden". No es criterio de aceptación; no
   medí de dónde sale la diferencia, salvo las 2 líneas de E1.
4. **Referencias de línea del plan desplazadas por la fase A** (`:29-33`, `:724`, l.602, l.944, l.580-606, l.943-948): apliqué los
   cambios por contenido. El texto es el del plan.
5. **Añadidos en los tests que el plan no nombra:** la constante `_DEC_JAN_ROWS`; los ids de los casos que el plan no nombra; el
   prefijo `docs/PLAN.md:…: R7: ` en `year_is_the_nearest`; el número de línea en `cierre_r7_clock`; y `docs/PLAN.md:3: R6: ` en la de
   R6. Los conteos no cambian.
6. **`progress.json:13`, `description` de `Fase_B`:** cambié `Needs David's answer to P1.` por `P1 resolved: B1, fixed offset
   (E0.1).`, con el aviso del orquestador y el hallazgo 14 de la auditoría de A. `edit_rules` no nombra `description`.
7. **`current_target` pasa a `null`,** no a una fase: B es la última. Es la forma de `eaf2303` y la que `read_progress` lee como "done".

## Residuales

- Los 5 de R6 fallan en RED por `ValueError` con el sello vecino (`2026-10-27T12:00:00-05:00`), que el `date.fromisoformat` antiguo no
  lee, y no por el suyo propio: el RED no distingue entre los 5. Lo que prueba cada frontera es MB4 (9), MB5 (4) y MB11 (3).
- `--cierre` sigue dando exit 1 hasta el ritual de cierre, por `docs/PLAN.md:3` y `docs/backlog.md:3`. Es dato, no código.
- `docs/CONTEXT.md:294` y `docs/backlog.md:165` siguen con el dueño que el plan fija (sesión de cierre). No los toqué.
- Proceso: el hook `ruff_on_edit` borra un import sin uso en cuanto se añade. Tuve que repetir el de `UTC` y `datetime` en los tests
  cuando ya se usaban. Durante las ediciones también señaló `F821` transitorios; el resultado final está limpio.

## Checklist `test-sanitizer` (solo los estándares)

Mock de `subprocess.run` con `create_autospec` en `cierre_r7_clock` y en los 5 de R6; lo demás, sin mocks. Fixtures con `make_repo` y
helpers locales del módulo. Nombres en inglés; lo que está en español son filas de PLAN, datos de entrada, no aserciones. Se afirma
sobre conteos, prefijos `archivo:línea: R6|R7: ` y fechas. Puntos 4 y 5 (contratos JSON, ABAC) no aplican. Nada reescrito.

## Medido y leído

**Medido:** compuerta antes y después; RED, dos veces; verde; 15 mutantes con M0 antes y después; `--cierre` con ambos scripts, sobre los
dos `HEAD`; reloj por CLI con `TZ=AAA-14` y `TZ=UTC0`; V1-V11; ruff y mypy de los dos archivos; stat y mensaje del commit.
**Solo leído:** los números de la columna "Plan"; `probes/mutants.txt`; `gaps.md` de A; la fila de `backlog.md` no la abrí entera.
**No medido:** el cruce de las 19:00 en una máquina UTC por CLI; el CI en `ubuntu-latest` y la forma de su `%cI`; B2, descartada.

## Dudas

Ninguna bloqueante. Es la última fase del plan: falta `/auditar AF-02 Fase_B`.
