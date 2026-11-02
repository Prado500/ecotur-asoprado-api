# Handoff AF-01 Fase D

Commit: `f6f73a9` feat(flow): add --cierre to check_docs.py with version-header and closed-day rules
Base develop: `2647ea3` (`git fetch origin` hecho; `origin/develop` y `merge-base HEAD origin/develop` coinciden).
Compuerta medida con `venv/Scripts/python.exe scripts/check.py` (plan, decisión 7). El plan se leyó del árbol de
trabajo, con los cambios sin commitear de David (ajustes de C y `scope_files`). Es la última fase del plan.

## Archivos tocados
```
 scripts/check_docs.py    | 284 +++++++++++++++++++++++++++++--
 tests/test_check_docs.py | 430 ++++++++++++++++++++++++++++++++++++++++++++++-
 2 files changed, 695 insertions(+), 19 deletions(-)
```
`docs/deuda/AF-01/plan.md` (modificado por David) y `gaps.md` (sin trackear) no se tocaron ni se commitearon.

## Qué cambió
- `git_last_commit_date(root, rel)`: `subprocess.run(["git", "log", "-1", "--format=%cs", "--", rel], cwd=root,
  capture_output=True, text=True)`. Devuelve `None` si `returncode != 0`, si la salida está vacía o si salta
  `FileNotFoundError`. `git_is_dirty(root, rel)`: `git status --porcelain -- rel`; `True`/`False`, o `None` si git falla.
- R6 `rule_version_header(root, errors, warnings, *, last_commit_date=…, is_dirty=…)` sobre `scope_files`, con
  `VERSION_RE` de la especificación §3:
  - encabezado < último commit → error en `archivo:línea`, con las dos fechas ISO;
  - sin encabezado y último commit > `ADR_0007_START` (`date(2026, 10, 28)`) → error `archivo: R6:`;
  - `is_dirty` → aviso `WARN_DIRTY` (no suspende la comparación);
  - `last is None` → aviso `WARN_UNVERIFIABLE`.
  `read_version(root, rel) -> VersionLine | None` lee la línea de versión. R6 y R7 la comparten.
- R7 `rule_closed_days_marked(root, errors, *, today=date.today)`: recorre `lines_inside(PLAN, {"3"})`. La primera
  línea de cada tabla es el encabezado: de ahí sale la columna `Cierre` y se reinician mes y año. `DAY_CELL_RE` y
  `CLOSE_MARK_RE` son los de §3. El mes se hereda de la última fila que lo nombra. El año empieza en el de la línea de
  versión de PLAN y sube cuando el mes retrocede. Si la fecha es < `today()` y `Cierre` no casa `^[✔◐✘] \d{1,2}$`,
  hay error.
- `--cierre` (`store_true`, `dest="closing"`): corre R1–R5 y R6–R7. Los avisos salen bajo `Avisos:` y no cambian el
  exit. El mensaje de éxito añade `+ cierre: R6 versión, R7 cierres`.
- Ajustes de C (gaps de su auditoría):
  1. `STATE_DONE`, `STATE_RUNNING` (plantilla con `{target}`) y `STATE_UNREADABLE` son constantes del módulo. Los
     tests de BE-01 real y del ítem terminado afirman `STATE_DONE in line` y `STATE_UNREADABLE not in line`.
  2. `read_progress` captura `ValueError`, con el test nuevo `test_estado_non_utf8_progress_is_unreadable` (byte
     `\xff`).
  3. `estado()` tiene docstring con `Args`/`Returns`.
  Los tres van en un párrafo propio del cuerpo del commit.
- Docstring del módulo: sección "Reglas de cierre" (R6, R7) y línea de uso de `--cierre`.

## Compuerta (antes = después, salvo tests)
Antes (ritual de arranque) y después, el mismo RESUMEN:
```
=== RESUMEN ===
  ✘ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff format --check, ruff check, mypy
```
Conteos después:
- `27 files would be reformatted, 105 files already formatted`
- `Found 362 errors.`
- `Found 44 errors in 12 files (checked 34 source files)`
- `Contracts: 4 kept, 0 broken.` (vía `venv/Scripts/lint-imports`; residual conocido de la redirección)
- `294 passed, 1 warning in 18.51s` (el warning es el `StarletteDeprecationWarning` de `test_services.py`, previo)
- `TOTAL 927 52 134 25 93%`

Antes: 27 · 362 · 44 · 4 kept · `249 passed` · 93 %. No empeoró nada.

Archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `2 files already formatted`;
`mypy scripts/check_docs.py tests/test_check_docs.py` → `Success: no issues found in 2 source files`. Sin CRLF.

RED: `45 failed, 104 passed` antes de implementar (`AttributeError` por `STATE_*`, `git_*`, `rule_version_header`,
`rule_closed_days_marked`, `WARN_*`; `SystemExit: 2` en `test_cierre_flag_runs_r6_r7` porque `--cierre` no existía).
Entre los que ya pasaban en RED:
- `test_default_pass_runs_no_git_and_no_closing_rules`: la pasada por defecto ya no ejecutaba git. Ahora protege
  contra correr R6/R7 siempre (mutante `closing-always-on` → 2 failed).
- Los dos casos nuevos con `--cierre` de `test_informative_flags_are_mutually_exclusive`: salían con exit 2 por flag
  desconocido. Ahora salen por la exclusión.

Después: `149 passed in 2.43s` en `tests/test_check_docs.py`. El más lento es `test_cierre_flag_runs_r6_r7` (0.25 s).

Mutantes (en el sitio, con restauración verificada por sha256 `bab33f59d830`). Todos mueren:

| Mutante | Resultado |
|---|---|
| sin `year += 1` | 1 failed |
| sin reinicio por tabla | 2 failed |
| `day <= now` | 2 failed |
| `last >= ADR_0007_START` | 1 failed |
| sin aviso dirty | 2 failed |
| `version.when <= last` | 2 failed |
| `done` imprime `STATE_UNREADABLE` | 2 failed |
| `except json.JSONDecodeError` | 1 failed |
| `--cierre` siempre activo | 2 failed |
| celda `Cierre` ausente cuenta como marcada | 1 failed |
| sin aviso `no verificable` | 3 failed |

## Criterio de aceptación y verificación final del plan (última fase)
- `grep -c "^def rule_"` → `7`.
- `grep -n "os.chdir\|def read(p: str)\|rule_no_days"` → vacío.
- El grep de símbolos exigidos devuelve todos: `rule_no_schedule_days`, `rule_deadline`, `rule_version_header`,
  `rule_closed_days_marked`, `strip_citations`, `def sections`, `--root`, `--copias`, `--huerfanas`, `--cierre`.
- `grep -n '"docs/sesiones'` → líneas 162, 186 y 192.
- `DECISION_RE` sobre el patrón de la verificación → `False`.
- `grep -n "subprocess"` → `51:import subprocess`, `543:` (dentro de `git_last_commit_date`) y `568:` (dentro de
  `git_is_dirty`). Fuera de las dos funciones `git_*` solo está el `import`.
- Desde `C:\Users`:
  - `--inexistente` → exit 2;
  - sin flags → exit 0, con el mensaje de R1–R5;
  - `--copias "CONTEXT §2"` → 15 líneas, entre ellas `docs/PLAN.md:89`; exit 0;
  - `--huerfanas` → exit 0;
  - `--cierre` → exit 0, sin avisos (los archivos del alcance están limpios) y con el mensaje
    `… R5 deadline + cierre: R6 versión, R7 cierres).`;
  - `--estado | grep "objetivo: ?"` → vacío (rc 1);
  - `--cierre --estado` → exit 2.
- `files = ["app", "scripts/check_docs.py"]` sigue en `pyproject.toml`. `mypy scripts/check_docs.py` → 0.
- Regex comparadas por programa con el texto de `especificacion.md` §3: `VERSION_RE`, `DAY_CELL_RE` y `CLOSE_MARK_RE`
  son idénticas (`True True True`).
- Trinquete igual que en B y C: 27 · 362 · 44 · 4 KEPT · 93 %.

## Desviaciones e interpretaciones (para el auditor)
1. **`test_cierre_flag_runs_r6_r7` ejecuta git de verdad, como pide el plan.** El plan lo describe "con las funciones
   reales sobre un fixture sin `.git`… git devuelve error en un directorio sin repo". Eso contradice la cabecera de
   sus propios tests ("ninguno ejecuta `git`"), la especificación §0.9 y la línea literal del commit "the tests never
   spawn a process". Seguí la descripción concreta del test. La línea del commit se dejó tal cual, porque el mensaje
   es exacto del plan. Es cierta para todos los tests de reglas, pero no para este. Para que el test no dependa del
   entorno, `GIT_CEILING_DIRECTORIES = tmp_path.parent` impide que git encuentre un repo por encima. Los demás tests
   nuevos no lanzan procesos: usan funciones falsas inyectadas o `create_autospec(subprocess.run)`.
2. **Avisos como constantes (`WARN_DIRTY`, `WARN_UNVERIFIABLE`).** El plan pide "aviso con `no verificable`". Por
   AGENTS §5, los tests afirman sobre la constante y no sobre el texto. `WARN_UNVERIFIABLE` empieza por
   `no verificable`. Es el mismo criterio que los `STATE_*` de los ajustes de C.
3. **PLAN sin línea de versión → R7 da 1 error y termina.** El plan no cubre el caso: sin versión no hay año
   inicial. Lo resolví igual que R5 con "deadline no legible", y tiene test (`test_r7_without_plan_version_reports_once`).
4. **Fixture del R7 que falla.** El plan escribe `| Lun 2 | … | |`. Como el mes se reinicia en cada tabla (lo dice el
   plan), esa fila sola no tiene mes y se ignora. Le precede `| Dom 1 nov | … | ✔ 1 |`, como en el PLAN de hoy. Detrás
   va `| Mar 3 | hoy | |`, que es borde: la fila de hoy no necesita marca.
5. **Caso de salto de año.** El caso del plan (`Sáb 2 ene … ✔ 2` con hoy = 31 dic) pasa igual sin el salto de año,
   porque la fila está marcada. Se conserva y añado `year-jump-future-row` (la misma fila con `Cierre` vacío), que sí
   falla sin el salto: es el mutante `sin year += 1`.
6. **`--cierre` entra en el grupo excluyente.** Renombré la variable `informative` → `mode`. Con eso `--cierre --estado`
   da exit 2 en lugar de ignorar `--cierre` en silencio, como pide el espíritu de §8.1. El plan no lo decía. Tiene dos
   casos en `test_informative_flags_are_mutually_exclusive`.
7. **Bordes que el plan no fija:**
   - fecha de encabezado imposible (`31 nov 2026`) → se trata como sin línea de versión (tiene test);
   - fecha imposible en una fila de R7, o fila anterior a que la tabla nombre un mes → se ignora;
   - celda `Cierre` ausente → cuenta como vacía, es decir, sin marca (tiene test).
8. **Superficie nueva no nombrada en el plan:**
   - públicas: `read_version`/`VersionLine` (R6 y R7 comparten la lectura de la versión), `ADR_0007_START`,
     `WARN_*`;
   - privadas: `_dated_rows` y `_cells`.
   `dest="closing"` está en inglés (AGENTS §4), como `citation_owner`/`orphans` en C.
9. **`STATE_*`: solo los tres estados de `progress.json`.** "verificado", "planeado", handoffs y auditoría siguen en
   línea. El plan lista `STATE_DONE, STATE_RUNNING, STATE_UNREADABLE…`. `STATE_RUNNING` es plantilla
   (`{target}` → `?` si falta).
10. **Tests extra, ninguno quitado** (45 nuevos en total):
    - `test_git_last_commit_date` (4) y `test_git_is_dirty` (4), con `assert_called_once_with` sobre la línea de git;
    - `test_r6_asks_git_about_every_scope_file`, con `call_args_list` sobre los 5 archivos del alcance;
    - en R6: los bordes `header-newer`, `unversioned-on-adr-0007-day` e `impossible-header-date`;
    - en R7: `year-by-monotony`, `year-resets-per-table`, `missing-cierre-cell`, `month-resets-per-table`,
      `no-cierre-column`, `test_r7_closing_mark_shape` (7) y `test_r7_ignores_tables_outside_section_3`;
    - `test_default_pass_runs_no_git_and_no_closing_rules` y
      `test_cierre_flag_fails_on_unmarked_closed_day_and_keeps_warnings`;
    - `STATE_RUNNING` en `test_estado_in_progress`.
11. **Trailer del commit:** `Co-Authored-By: Claude Opus 5.5`. Lo fija la atribución del harness, igual que en A, B y
    C; el plan escribe `Claude Fable 5.1`. Comparé con `diff` el bloque del plan y `git show -s --format=%B`: solo
    difieren el trailer y el párrafo "Phase C audit adjustments…", que el plan pide de forma expresa.

## Residuales / notas
- `--cierre` sale en verde hoy, 1 nov. Desde el 2 nov saldrá en rojo mientras la fila `Lun 2` de PLAN §3 no tenga su
  marca: es lo que la regla debe hacer.
- Herencia de mes: una fila `Dom 1` sin mes detrás de `Sáb 31 oct` heredaría `oct`. La convención del PLAN nombra el
  mes en la primera fila de cada mes (`Dom 1 nov`) y la regla es la de la especificación. Si se quiere inferir el mes
  cuando el día retrocede, iría a `AF-02`.
- Los cuatro prompts de `docs/sesiones/` siguen sin línea de versión (último commit 25–26 oct). Hoy pasan; su primera
  edición debe nacer con versión, o R6 la marcará (ya en Residuales del plan).
- `scripts/check.py` no se tocó: la compuerta solo ejecuta la pasada por defecto, sin `--cierre`, que queda fuera de
  alcance.
- El cierre documental del ítem (backlog, PLAN §2b `B-CHECK-DOCS`, README de sesiones, CONTEXT, bitácora) es de la
  sesión que cierra (Residuales del plan).
- Los scripts de parcheo y de mutantes viven en el scratchpad, fuera del repo, porque los heredocs largos rompen el
  envoltorio de la shell (igual que en C).
