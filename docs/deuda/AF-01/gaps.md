# Gaps — AF-01

## Auditoría Fase A — 2026-11-01

Compuerta re-ejecutada con `venv/Scripts/python.exe scripts/check.py`: ruff format ✘ 27, ruff check ✘ 362, mypy ✘ 44, import-linter ✔ (4 kept), docs ✔, pytest ✔ 171 passed, cobertura 93 %. Igual a la línea base (362 · 44 · 4 · 93 %).

- [OPCIONAL] — Fase A — El trailer del commit `8d51302` es `Co-Authored-By: Claude Sonnet 5.5` y el plan dice `Claude Fable 5.1`. El resto del mensaje coincide con el plan. Lo fija la atribución del harness; no exige corrección. — `git show 8d51302`
- [OPCIONAL] — Fase A — El plan exigía 8 tests y hay 26 casos por parametrización más `test_main_on_fixture_with_error_returns_1`. Los 8 existen y pasan; el criterio "145 + 8" se cumple de sobra. — `tests/test_check_docs.py`
- [OPCIONAL] — Fase A — Con `python` del sistema (sin dependencias) la compuerta falla por `ModuleNotFoundError`; solo es válida con `venv/Scripts/python.exe` (plan, decisión 7). — salida de `python scripts/check.py`

Sin bloqueantes. Verificado: hash `8d51302` real y solo toca `pyproject.toml`, `scripts/check_docs.py` y `tests/test_check_docs.py`; `current_target` = Fase_B; `last_handoff` presente; `edit_rules` intacto; sin `os.chdir`; `--copias` exit 2 con uso; script exit 0 desde otro cwd; ruff, format y mypy en 0 sobre los archivos tocados; árbol limpio.

## Auditoría Fase B — 2026-11-01

Compuerta re-ejecutada con `venv/Scripts/python.exe scripts/check.py`: ruff format ✘ 27, ruff check ✘ 362, mypy ✘ 44, import-linter ✔ (4 kept, vía `venv/Scripts/lint-imports`), docs ✔, pytest ✔ 219 passed, cobertura 93 % (`TOTAL 927 52 134 25 93%`). Igual a la línea base (27 · 362 · 44 · 4 · 93 %) y a lo que pegó el ejecutor; los tests suben de 171 a 219.

- [OPCIONAL] — Fase B — Los casos "debe pasar" de R2 `4 m`, `90 %`, `7 horas` se escribieron como en el plan, pero en una línea sin día de la semana (`"4 m, 90 %, 7 horas"`), así que pasarían aunque no existiera el lookahead. Las alternativas `%` y `horas` del segundo lookahead no las cubre ningún test: los mutantes que las quitan dejan los 73 tests de fixtures en verde, y el repo real también queda en verde con ellos. `sáb 7 h` y `Dom 4 m` sí cubren `h` y `m`. Para que esos casos sirvan como regresión harían falta `dom 90 %` y `sáb 7 horas`. — `tests/test_check_docs.py` (`test_r2_accepts_non_schedule_lines`, caso `"4 m, 90 %, 7 horas"`); mutantes en el scratchpad del auditor
- [OPCIONAL] — Fase B — Desviación 1 aceptada: `scope_files` en minúscula en lugar de `SCOPE_FILES`, porque ruff tiene activa la regla `N` (`pyproject.toml:66`) y daría `N802`. El comportamiento no cambia. La Fase C del plan sigue escribiendo `SCOPE_FILES`; quien la implemente debe usar `scope_files`. — `scripts/check_docs.py` (`def scope_files`), `plan.md` Fase C
- [OPCIONAL] — Fase B — AGENTS §4: la variable local `sesiones` de `scope_files` es un identificador en español (copia el nombre del directorio). `numbered_lines` es pública y su docstring no tiene la sección `Returns` del estilo Google. Ruff no lo detecta. — `scripts/check_docs.py` (`scope_files`, `numbered_lines`)
- [OPCIONAL] — Fase B — El trailer del commit `da106b0` es `Co-Authored-By: Claude Opus 5.5` y el plan dice `Claude Fable 5.1`. Viene de la atribución del harness, igual que en la Fase A. El resto del mensaje coincide línea a línea con el plan (lo comprobé con `diff`). — `git show -s --format=%B da106b0`

Juicio de las desviaciones del handoff (ninguna cambia un comportamiento exigido):
1. `scope_files`: aceptable (ver arriba).
2. Distancia de R5 medida desde el `start` de la fecha: `max(t.start - d.start, d.start - t.end, 0) <= 40` es exactamente la ventana del plan (`start` en `[t.start-40, t.end+40]`), así que la métrica es la misma que define la ventana. La especificación exige que gane `11 ene` en `corte de código el 18 dic y entrega el 11 ene`: con esta métrica la distancia es 4 contra 9 y gana `11 ene`; midiendo entre tramos sería 3 contra 4 y daría rojo. Aceptable.
3. No afirmar sobre `sin cita` ni `no legible`: AGENTS §5 está por encima del plan. Los tipos de error se siguen distinguiendo por la presencia de `≠` y por la ubicación `docs/CONTEXT.md`, y cada caso afirma 1 error. Aceptable.
4. Un solo error por disparador, y `≠` gana sobre "sin cita": lo exige el propio plan, que pide 1 error para `entrega del 7 de noviembre` sin cita. Está documentado en la docstring. Aceptable.
5. Tests extra (R2 `| Lun 2 |` fuera de §3, `Dom 4 m`; R5 año distinto e ISO; `DECISION_RE` directo; `main` conecta R2–R5): no se quitó ninguno. Aceptable.
6. `sorted(set(...))` en R3: detecta lo mismo y el orden queda determinista. Aceptable.

Sin bloqueantes. Verificado:
- `da106b0` es real y solo toca `scripts/check_docs.py` y `tests/test_check_docs.py`, sin CRLF. `a45f5e3` solo toca el handoff y `progress.json`.
- `progress.json`: es JSON válido, Fase_B `completed`/`da106b0`, `current_target` = Fase_C, `last_handoff` presente y `edit_rules` intacto.
- `SCHEDULE_DAY_RE` (con IGNORECASE), `_QUAL`, `DECISION_RE`, `DATE_RE` y `TRIGGER_RE` (con IGNORECASE) son idénticos carácter a carácter a la especificación §2 (comparación programática).
- Deadline leído del repo: `DayMonth(11, 'ene', 2027)` en `CONTEXT.md:101`.
- El fixture `_BACKLOG_AF01_ROW` es idéntico a `docs/backlog.md:141`. El fixture del CONTEXT §8 viejo coincide con `git show 2647ea3:docs/CONTEXT.md` líneas 238 y 253.
- Todos los casos de "Tests (RED primero)" del plan existen y pasan: 74 passed en `tests/test_check_docs.py`.
- Criterio de aceptación:
  - `grep -c "^def rule_"` → 5;
  - `rule_no_days` ya no aparece;
  - el patrón de `verificacion.md` sobre `DECISION_RE` → `False`;
  - `check_docs.py` lanzado desde `C:\Users` → exit 0 con el mensaje de éxito nuevo;
  - ruff, format y mypy en 0 sobre los dos archivos tocados; total de mypy 44.
- Árbol limpio fuera de `docs/deuda/`.

## Auditoría Fase C — 2026-11-01

Compuerta re-ejecutada con `venv/Scripts/python.exe scripts/check.py`: ruff format ✘ 27 (`27 files would be reformatted, 105 files already formatted`), ruff check ✘ 362, mypy ✘ 44 (`Found 44 errors in 12 files (checked 34 source files)`), import-linter ✔ (`Contracts: 4 kept, 0 broken.`, vía `venv/Scripts/lint-imports`), docs ✔, pytest ✔ `249 passed, 1 warning`, cobertura 93 % (`TOTAL 927 52 134 25 93%`). Igual a la línea base (27 · 362 · 44 · 4 · 93 %) y a lo que pegó el ejecutor; los tests suben de 219 a 249. El "105 already formatted" frente al 104 del handoff es `handoff-Fase_C.md`, escrito después de medir (ruff format también recorre los `.md`: `ruff format --check -v .` lo lista).

- [OPCIONAL] — Fase C — El texto de `--estado` para un ítem terminado no lo protege ningún test. El plan pedía que la salida "contenga `ejecutado`". Por AGENTS §5 el ejecutor afirma sobre `read_progress` y sobre la ausencia de `?` en la línea. Cambié la rama `done` de `estado()` para que imprima `progress.json ilegible`, y los 104 tests siguen en verde. La conversión de `Progress.state` a texto queda sin cobertura de comportamiento. Una forma de cubrirla sin afirmar sobre español: comparar la línea `done` con la línea de un `progress.json` ilegible (deben ser distintas), o sacar los textos a constantes y afirmar sobre ellas. — `tests/test_check_docs.py` (`test_estado_all_completed_and_null_target`, `test_estado_on_real_repo_be01`); `scripts/check_docs.py` (`estado`, rama `progress.state == "done"`); mutante en el scratchpad del auditor (`mutant_c2.py done_text` → `104 passed`)
- [OPCIONAL] — Fase C — `read_progress` solo captura `json.JSONDecodeError`. Un `progress.json` que no es UTF-8 lanza `UnicodeDecodeError` y `--estado` termina con traceback en lugar de mostrar `progress.json ilegible`. Las dos excepciones son subclases de `ValueError`. Es un borde que el plan no exige. — `scripts/check_docs.py` (`read_progress`, `except json.JSONDecodeError`); prueba del auditor con el byte `\xff` → `UnicodeDecodeError`
- [OPCIONAL] — Fase C — `estado()` cambió su cuerpo en esta fase y su docstring sigue en una línea, sin `Args`/`Returns` (AGENTS §4, función pública refactorizada). Ruff no lo detecta. — `scripts/check_docs.py` (`def estado`, docstring)
- [OPCIONAL] — Fase C — El trailer del commit `968dc25` es `Co-Authored-By: Claude Opus 5.5` y el plan dice `Claude Fable 5.1`. Viene de la atribución del harness, como en A y B. Comparé con `diff` el bloque del plan y `git show -s --format=%B 968dc25`: el resto coincide línea a línea. La única diferencia es el párrafo "Phase B audit adjustments…", que el plan pide de forma expresa. — `git show -s --format=%B 968dc25`

Juicio de las desviaciones del handoff (ninguna cambia un comportamiento exigido):
1. `read_progress`/`Progress` añadidos para no afirmar sobre texto en español: AGENTS §5 está por encima del plan y es la superficie mínima necesaria. Aceptable. Deja sin cubrir la conversión a texto (primer OPCIONAL).
2. `current_target: null` sin fases cuenta como `running`: si un `progress.json` no tiene fases, la regla "todas `completed`" se cumpliría sin que haya nada hecho. Es una lectura prudente, tiene su caso en `test_read_progress_edges[null-target-no-phases]` y el mutante que quita la guarda lo detecta (1 failed). Aceptable.
3. `--huerfanas` imprime una entrada por línea con el primer fragmento: el formato del plan tiene un solo `"<fragmento>"` por entrada, así que es coherente. Aceptable.
4. `<cita>` sin backticks y con paréntesis; el filtro se aplica al interior: así lo dice el plan. El mutante sin `strip("`")` lo detecta (2 failed). Aceptable.
5. `dest` en inglés (`citation_owner`, `orphans`); los flags `--copias`/`--huerfanas` son contrato de la CLI: AGENTS §4. Aceptable.
6. Tests extra (29 de C en total, 6 de ellos del plan): no se quitó ninguno; amplían bordes y controles positivos. Aceptable.
7. Trailer de coautoría: aceptable (cuarto OPCIONAL).
8. Nombres de test con el flag (`test_copias_*`…): vienen del plan y siguen el precedente de A. Aceptable.

Sin bloqueantes. Verificado:
- `968dc25` es real y solo toca `scripts/check_docs.py` y `tests/test_check_docs.py`, sin CRLF. `892b7df` solo toca `handoff-Fase_C.md` y `progress.json`.
- `progress.json`:
  - es JSON válido;
  - Fase_C `completed`/`968dc25`;
  - `current_target` = Fase_D;
  - `last_handoff` presente;
  - `edit_rules` idéntico al de `c95a145`.
- Árbol limpio fuera de `docs/deuda/`: solo `plan.md` (cambios de David) y este `gaps.md`.
- Archivos tocados:
  - `ruff check` → `All checks passed!`;
  - `ruff format --check` → `2 files already formatted`;
  - `mypy scripts/check_docs.py tests/test_check_docs.py` → `Success: no issues found in 2 source files`.
- Cambios exactos presentes en el diff:
  - `list_citations` recorre `scope_files`;
  - `list_orphans` usa los 5 patrones del plan, la exclusión de líneas con cita, CONTEXT §0/2/4/6 y PLAN §3/6/7 vía `lines_outside`, y `**Versión `;
  - `--estado` lee con `json.loads`, tiene el caso `done` y el caso `progress.json ilegible`;
  - `add_mutually_exclusive_group` con los tres flags, y la pasada bloqueante solo corre si no hay ninguno;
  - `--copias` usa `nargs="?"` y `const=""`.
- Ajuste de A: `test_unknown_flag_exits_2` ya no tiene la mitad `--copias` y conserva `--inexistente`.
- Ajustes de B (alcance aprobado en el `plan.md` del árbol de trabajo):
  1. `"4 m, 90 %, 7 horas"` se sustituyó por `"dom 90 % de avance"` y `"sáb 7 horas o menos"`. Los mutantes del lookahead ahora mueren:
     - sin `%`: `1 failed` en `[dom 90 % de avance]`;
     - con `h(?:oras?)?` → `h`: `1 failed` en `[sáb 7 horas o menos]`;
     - control sin mutar: `16 passed`.
  2. `sesiones` → `session_prompts`; `numbered_lines` tiene `Args` y `Returns`.
  3. `scope_files` se reutiliza. No queda ningún `SCOPE_FILES` ni otra función de alcance.
- Los 6 tests de "Tests (RED primero)" del plan existen y pasan: 104 passed en `tests/test_check_docs.py`.
- Criterio de aceptación:
  - `--estado | grep "objetivo: ?"` → vacío (grep rc=1). BE-01 → `ejecutado (todas las fases); pendiente de PR o mezclado`.
  - `--copias "CONTEXT §2"` → 15 líneas, entre ellas `docs/PLAN.md:89`.
  - `--huerfanas` → exit 0 (48 candidatos). `--copias` sin filtro → 53.
  - `--estado --copias` → exit 2. `--inexistente` → exit 2.
  - Sin flags, lanzado desde `C:\Users` → exit 0.
  - Trinquete igual que en B.
- No es la última fase (Fase_D pendiente): la "Verificación final" del plan no aplica todavía.

## Auditoría Fase D — 2026-11-01

Compuerta re-ejecutada con `venv/Scripts/python.exe scripts/check.py`: ruff format ✘ 27 (`27 files would be reformatted, 106 files already formatted`), ruff check ✘ 362 (`Found 362 errors.`), mypy ✘ 44 (`Found 44 errors in 12 files (checked 34 source files)`), import-linter ✔ (`Contracts: 4 kept, 0 broken.`, vía `venv/Scripts/lint-imports`), docs ✔, pytest ✔ `294 passed, 1 warning`, cobertura 93 % (`TOTAL 927 52 134 25 93%`). Igual a la línea base (27 · 362 · 44 · 4 · 93 %) y a lo que pegó el ejecutor; los tests suben de 249 a 294. El "106 already formatted" frente al 105 del handoff es `handoff-Fase_D.md`, commiteado en `b10e56d` después de medir (`ruff format --check -v .` incluye los `.md`).

- [OPCIONAL] — Fase D — `test_cierre_flag_runs_r6_r7` ejecuta `git` de verdad. El plan lo pide así, pero contradice la cabecera de sus propios tests ("ninguno ejecuta `git`") y la especificación §0.9 ("Los tests no corren `git` ni subprocesos"). Además, la línea del commit "the tests never spawn a process" es falsa para este test. `GIT_CEILING_DIRECTORIES` no protege frente a `GIT_DIR`: con `GIT_DIR` definido, que es el entorno de un hook de git o de `git rebase -x`, el test cae (`1 failed`; R6 lee la historia del repo real). Hoy no hay hooks (`.git/hooks` solo trae los `.sample` y no hay `.pre-commit-config`), así que la compuerta no se ve afectada. Hay dos salidas, y la decide David: `monkeypatch.delenv("GIT_DIR", raising=False)` (y `GIT_WORK_TREE`), o retirar el test, porque `test_cierre_flag_fails_on_unmarked_closed_day_and_keeps_warnings` ya cubre el cableado con `create_autospec(subprocess.run)`. — `tests/test_check_docs.py:951-962`; `GIT_DIR=<repo>/.git venv/Scripts/python.exe -m pytest tests/test_check_docs.py::test_cierre_flag_runs_r6_r7` → `1 failed`
- [OPCIONAL] — Fase D — R7 no ve una parte de las filas cuando la línea de versión de PLAN cambia de año. El año inicial de cada tabla sale de esa línea (literal del plan y de la especificación §3), así que, si PLAN sube a `2 ene 2027`, una tabla que empieza en `Lun 28 dic` se fecha en 2027-12-28 y no se evalúa. Con `today` = 2027-01-05 y tres filas pasadas sin marca (`Lun 28 dic`, `Mar 29`, `Vie 1 ene`): versión `31 dic 2026` → 3 errores; versión `2 ene 2027` → 0 errores. Es justo la semana que la especificación quería proteger, y el problema aparece en la primera edición de PLAN en enero, antes del deadline del 11 ene. Cumple el plan: va a Residuales/`AF-02`. Una salida posible: si el mes de la primera fila es mayor que el de la versión, año − 1. — `scripts/check_docs.py` (`rule_closed_days_marked`, `version.when.year`; `_dated_rows`); prueba del auditor en el scratchpad (`runner/r7_year.py`)
- [OPCIONAL] — Fase D — El trailer del commit `f6f73a9` es `Co-Authored-By: Claude Opus 5.5` y el plan dice `Claude Fable 5.1`. Viene de la atribución del harness, como en A, B y C. Comparé con `diff` el bloque del plan (líneas 321-336) y `git show -s --format=%B f6f73a9`: el resto coincide línea a línea. La única diferencia es el párrafo "Phase C audit adjustments…", que el plan pide de forma expresa. — `git show -s --format=%B f6f73a9`

Juicio de las desviaciones del handoff (ninguna cambia un comportamiento exigido):
1. Test con git real: sigue la descripción concreta del plan. Aceptable; su fragilidad es el primer OPCIONAL.
2. `WARN_DIRTY`/`WARN_UNVERIFIABLE` como constantes: AGENTS §5 está por encima del plan, con el mismo criterio que los `STATE_*`. `WARN_UNVERIFIABLE` empieza por `no verificable`. Aceptable.
3. PLAN sin línea de versión → 1 error de R7 y fin: sin versión no hay año inicial; es el mismo patrón que "deadline no legible" en R5 y tiene test. Aceptable.
4. Fixture de R7 que falla con `| Dom 1 nov | … | ✔ 1 |` delante de `| Lun 2 | … | |`: el plan reinicia el mes en cada tabla, así que `Lun 2` sola no tiene mes. Era necesario. Aceptable.
5. `year-jump-future-row` añadido: el caso del plan (`Sáb 2 ene … ✔ 2`) pasa también sin el salto de año. El caso nuevo mata el mutante `sin year += 1` (lo comprobé). Aceptable.
6. `--cierre` dentro del grupo excluyente: `--cierre --estado` → exit 2 (lo comprobé), en lugar de ignorar un flag en silencio. Va en el espíritu de §8.1. Aceptable.
7. Bordes no fijados (fecha imposible en el encabezado o en una fila, celda `Cierre` ausente): tienen tratamiento prudente y test. Aceptable.
8. Superficie nueva (`read_version`, `VersionLine`, `ADR_0007_START`, `WARN_*`, `_dated_rows`, `_cells`): en inglés y mínima. Aceptable.
9. Solo tres `STATE_*`: el plan escribe "…". Aceptable.
10. Tests extra: 15 funciones nuevas y ninguna quitada (lo comprobé comparando los nombres con `968dc25`). Aceptable.

Sin bloqueantes. Verificado:
- `f6f73a9` es real y solo toca `scripts/check_docs.py` y `tests/test_check_docs.py`, sin CRLF. `b10e56d` solo toca `handoff-Fase_D.md` y `progress.json`.
- `progress.json`:
  - es JSON válido;
  - las cuatro fases están `completed` con hashes reales (`8d51302`, `da106b0`, `968dc25`, `f6f73a9`);
  - `current_target` = `null` (última fase);
  - `last_handoff` presente;
  - `edit_rules` y `allowed_statuses` idénticos a los de `c95a145`.
- Árbol limpio fuera de `docs/deuda/`: solo `plan.md` (cambios de David, aprobados) y este `gaps.md`.
- Archivos tocados:
  - `ruff check` → `All checks passed!`;
  - `ruff format --check` → `2 files already formatted`;
  - `mypy scripts/check_docs.py tests/test_check_docs.py` → `Success: no issues found in 2 source files`.
- RED reproducido: los tests de D contra el script de `968dc25` dan `45 failed, 104 passed`, como dice el handoff. Después: `149 passed` en `tests/test_check_docs.py`.
- Cambios exactos presentes en el diff:
  - `git_last_commit_date` con la línea exacta de `subprocess.run` del plan y `None` ante `returncode != 0`, salida vacía o `FileNotFoundError`;
  - `git_is_dirty` → `bool | None`;
  - R6 con la firma del plan, recorre `scope_files`, con sus dos mensajes, el aviso dirty que no suspende la comparación y el aviso `no verificable`;
  - R7 con la firma del plan, recorre `lines_inside(PLAN, {"3"})`, localiza `Cierre` por encabezado, reinicia mes y año por tabla, hereda el mes, calcula el año por monotonía desde la versión e ignora `(se fecha …)`;
  - `--cierre` `store_true` corre R1–R7, imprime los avisos bajo `Avisos:` sin cambiar el exit y añade el sufijo `+ cierre: R6 versión, R7 cierres`;
  - docstring del módulo con R6, R7 y el uso de `--cierre`.
- `VERSION_RE`, `DAY_CELL_RE` y `CLOSE_MARK_RE` son idénticas carácter a carácter a la especificación §3 (comparación programática).
- `_PLAN_CLOSED_DAYS_TABLE` y `_PLAN_BOGOTA_TABLE` son copia literal de `docs/PLAN.md` (comprobado con `in`).
- Ajustes de C (alcance aprobado en el `plan.md` del árbol):
  1. `STATE_DONE`, `STATE_RUNNING` y `STATE_UNREADABLE` son constantes, y los dos tests piden `STATE_DONE in line` y `STATE_UNREADABLE not in line`. El mutante `done → STATE_UNREADABLE` ahora da `2 failed` (antes, 104 en verde).
  2. `except ValueError`, con `test_estado_non_utf8_progress_is_unreadable`. El mutante `except json.JSONDecodeError` da `1 failed`.
  3. `estado()` tiene `Args`/`Returns`.
- Tests de "Tests (RED primero)" del plan: todos existen y pasan.
  - R6: falla con 31 oct/1 nov, dirty False y True; falla con `mentor.md` sin versión y commit del 31 oct. Pasa con mismo día, mismo día dirty, sin versión el 27 oct y `None`.
  - R7: falla con `Lun 2` sin marca el 3 nov. Pasa con la tabla de Bogotá y con "Días cerrados" el 1 nov, con el salto `31 dic → 2 ene` y con `(se fecha el vie 6)`.
  - `test_cierre_flag_runs_r6_r7` existe y pasa.
- 18 mutantes del auditor (en copias del scratchpad, sin tocar el repo); todos mueren:
  - R7: `day <= now`, sin `year += 1`, sin reinicio por tabla, año = `today().year`, fuera de §3, `CLOSE_MARK_RE` sin `$`;
  - R6: `>= ADR_0007_START`, `version.when <= last`, sin aviso dirty, dirty que suspende la comparación, solo PLAN, sin aviso `no verificable`;
  - `git_is_dirty` que ignora `returncode`, `--cierre` siempre activo, avisos que cambian el exit, `done → UNREADABLE`, `running` sin target, `except JSONDecodeError`;
  - control sin mutar: `149 passed`.
- AGENTS §4/§5: identificadores, docstrings y comentarios en inglés (`dest="closing"`). Docstrings Google en las funciones públicas nuevas. Mocks con `create_autospec`. Ninguna aserción sobre texto en español: los tests afirman sobre `R#`, `archivo:línea`, fechas ISO y constantes.
- Criterio de aceptación: `grep -n "subprocess"` → `51` (import), `543` (`git_last_commit_date`) y `568` (`git_is_dirty`). `test_default_pass_runs_no_git_and_no_closing_rules` confirma que la pasada por defecto no llama a `subprocess.run`. `--cierre` sobre el repo real → exit 0, sin avisos, también desde `C:\Users`. Contrastado a mano: PLAN tiene versión 31 oct y último commit 31 oct; CONTEXT y backlog, 1 nov y 1 nov; README de sesiones, 31 oct y 31 oct; los cuatro prompts no tienen versión y su último commit es del 25–26 oct. Trinquete igual que en B y C.
- Verificación final del plan (última fase), comando a comando:
  - `grep -c "^def rule_"` → `7`;
  - `grep -n "os.chdir\|def read(p: str)\|rule_no_days"` → vacío (rc 1);
  - el grep de símbolos exigidos devuelve los diez;
  - `grep -n '"docs/sesiones'` → líneas 162, 186 y 192;
  - `DECISION_RE` sobre el patrón de la verificación → `False`;
  - `--inexistente` → exit 2 con uso;
  - sin flags → exit 0;
  - `--copias "CONTEXT §2"` → exit 0, 15 líneas, entre ellas `docs/PLAN.md:89`;
  - `--huerfanas` → exit 0 (48);
  - `--cierre` → exit 0;
  - `--estado | grep "objetivo: ?"` → vacío (rc 1);
  - `tests/test_check_docs.py` existe;
  - `pyproject.toml:90` → `files = ["app", "scripts/check_docs.py"]`;
  - `pytest tests/test_check_docs.py` → `149 passed`;
  - `mypy scripts/check_docs.py` → `Success`;
  - compuerta igual a la línea base.

Veredicto Fase D: PASS (0 bloqueantes, 3 opcionales).
