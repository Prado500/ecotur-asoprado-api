## Auditoría Fase A — 2026-11-09

**Veredicto Fase A: PASS (0 bloqueantes, 1 opcionales).**

[OPCIONAL] — Fase A — La "ejecución inestable" de la duda 1 del handoff no es un test inestable. Es un fallo determinista del paso import-linter cuando el stdout de la compuerta es el dispositivo `NUL` de Windows (`> /dev/null` en Git Bash). El spinner de rich que usa import-linter (`venv/Lib/site-packages/importlinter/application/use_cases.py:127`, `_get_spinner` l.231) detecta una consola heredada, escribe con cp1252 y lanza `UnicodeEncodeError`. El subproceso sale con 1 y la compuerta da exit 1. `check.py` reconfigura a UTF-8 solo sus propios streams (`scripts/check.py:40-41`), y el subproceso no lo hereda. No es una regresión de la fase: el lanzador de pip falla igual. Ningún archivo del repo invoca la compuerta con salida a `NUL`. Destino: backlog/Residuales (p. ej., `PYTHONIOENCODING=utf-8` en el entorno de los pasos, o documentar que no se redirige a `/dev/null` en Windows). Fuera del alcance de AF-12 — evidencia: `check.py --soft ruff,mypy > /dev/null 2>&1` → exit 1 en 3 de 3; `> /dev/null` solo stdout → exit 1 en 2 de 2, con la traza `rich/_win32_console.py:402 … cp1252.py:19 … UnicodeEncodeError: 'charmap' codec can't encode characters in position 0-2` dentro de `<string>, line 1 … lint_imports_command()`; la misma orden a fichero → exit 0 en 6 de 6 (`546 passed`, `Compuerta superada; tolerados en rojo: ruff check, mypy`); a tubería (`| cat > /dev/null`) → exit 0. Sin cambios de la fase: `venv/Scripts/lint-imports.exe > /dev/null` → exit 1 y `> fichero` → exit 0; el entry point con `-c` da los mismos dos resultados. `git grep -E 'check\.py[^|]*(>\s*/dev/null|>\s*NUL)'` → vacío.

Puntos juzgados sin hallazgo:

- **Compuerta re-ejecutada por el auditor** (`./venv/Scripts/python.exe scripts/check.py`, exit 1, con RESUMEN): `✔ ruff format --check`,
  `✘ ruff check` (`Found 8 errors.`, los 8 I001 en `app/` de la línea base), `✘ mypy` (`Found 9 errors in 5 files (checked 53
  source files)`), `✔ import-linter` (`Contracts: 4 kept, 0 broken.`), `✔ docs (coherencia)`, `✔ pytest + cobertura`
  (`546 passed, 5 warnings`, `TOTAL 943 23 138 19 96.11%`), `Compuerta NO superada: ruff check, mypy`. Coincide con
  el criterio de aceptación (`plan.md:235-240`) y con la línea base (`verificacion.md:117,123,146-149`): cobertura igual,
  contratos iguales, ruff/mypy sin aumento. 548 → 546 es la baja prevista y aceptada (`plan.md:76`, E0.2).
- **Archivos tocados:** `ruff check scripts/check.py tests/test_check.py` → `All checks passed!`; `ruff format --check` →
  `2 files already formatted`; `mypy scripts/check.py tests/test_check.py` → `Success: no issues found in 2 source files`.
- **Commit `6ee6923`:** el mensaje es idéntico al de `plan.md:250-278` (`diff` del bloque del plan frente a
  `git log -1 --format=%B`: solo cambia el salto de línea final que añade git). Toca solo `scripts/check.py` y `tests/test_check.py`
  (`git show --stat`; paso 8 de la Verificación final: `git diff --stat 9d2b589 -- . ':(exclude)docs'` → los mismos 2 archivos).
  `run()` no cambia: el diff no tiene ningún hunk en `scripts/check.py:170-176`, y `subprocess.call(cmd)` sigue sin `try`
  (`:173`). Están todos los cambios exactos: importaciones (`:22-23`), `LINT_IMPORTS_CODE` y `_lint_imports_cmd()` con el
  texto literal del plan (`:48-80`), `steps()` con docstring y `("import-linter", _lint_imports_cmd()),` (`:77-90`). En los tests:
  docstring del módulo, `entry_points` en lugar de `sysconfig` y `TestLintImportsStep` con los 5 casos (`tests/test_check.py:141-205`).
- **Desviación 1 (SIM300) confirmada como forzada y equivalente.** La forma del plan, pasada por ruff con la configuración del
  repo, da `SIM300 [*] Yoda condition detected` (exit 1). La igualdad es simétrica, y MA3 la hace caer
  (`tests/test_check.py:159-161`).
- **Desviación 2 (Smart App Control ya no bloquea):** sin la reproducción "antes rojo / después verde", la evidencia de que
  la fase resuelve el incidente es estructural. Basta: (a) paso 4 de la Verificación final → `True` (todo paso empieza por
  `PY`); (b) test 1 congela `[PY, "-c", LINT_IMPORTS_CODE]` con y sin PATH; (c) experimento del auditor: con
  `venv/Scripts/lint-imports.exe` renombrado temporalmente, `check.py --no-tests --soft ruff,mypy` → `Contracts: 4 kept, 0 broken.`,
  `--- import-linter: OK`, exit 0. La compuerta ya no depende del lanzador, ni bloqueado ni ausente. El binario se restauró
  (`sha256sum -c` OK). Consecuencia para B: MB3 probablemente no reproducirá `WinError 4551`. El plan ya lo prevé (`plan.md:364`).
- **Mutaciones repetidas por el auditor** (helper `mut` del plan): MA1 → `3 failed, 26 passed` (tests 1, 3, 5); MA2 →
  `2 failed, 27 passed` (3, 4); MA3 → `1 failed, 28 passed` (2); MA5 → `2 failed, 27 passed` (1, 4). MA4 (contrato roto real,
  sin venv en PATH) → `Los servicios no conocen el transporte HTTP BROKEN`, `Contracts: 3 kept, 1 broken.`,
  `--- import-linter: FALLA (exit 1)`, `exit 1`. Restauración byte a byte: `sha256sum -c` OK en `scripts/check.py` y
  `app/services/user_service.py`, y `git status --short` vacío.
- **Verificación final, pasos aplicables tras A:** paso 1 vacío; paso 2 vacío y `tests/test_check.py:2`; paso 3
  `2/2 · 2/3 · 2/2 · 2/2` como espera el plan.
- **`progress.json`:** JSON válido; `Fase_A` `completed` con `6ee6923` (hash real, `git show --stat` lo confirma);
  `current_target` `Fase_B`; `last_handoff` presente; `edit_rules` intacto. El registro va en commit aparte (`13a060d`), que toca
  solo `progress.json` y `handoff-Fase_A.md`.
- **Árbol:** `git status --short` limpio al empezar y al terminar la auditoría (salvo este `gaps.md`).
- **AGENTS:** docstrings Google en `_lint_imports_cmd` y `steps()`. Ninguna aserción sobre texto en español. Los tests no
  usan `Mock`: `find_spec` se sustituye con funciones puras vía `monkeypatch`, así que `spec=` no aplica. `check.py` está fuera
  de las capas de `import-linter`.

## Auditoría Fase B — 2026-11-09

**Veredicto Fase B: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. El OPCIONAL de la fase A (import-linter con stdout a `NUL` en Windows) sigue igual y fuera de alcance. Esta
auditoría guardó la compuerta en un fichero del scratchpad y nunca la redirigió a `/dev/null`.

Puntos juzgados sin hallazgo:

- **Compuerta re-ejecutada por el auditor** (`./venv/Scripts/python.exe scripts/check.py`, salida a fichero, exit 1, con RESUMEN):
  `✔ ruff format --check`, `✘ ruff check` (`Found 8 errors.`), `✘ mypy` (`Found 9 errors in 5 files (checked 53 source files)`),
  `✔ import-linter` (`Contracts: 4 kept, 0 broken.`), `✔ docs (coherencia)`, `✔ pytest + cobertura` (`549 passed, 5 warnings`,
  `TOTAL 943 23 138 19 96.11%`), `Compuerta NO superada: ruff check, mypy`. Coincide con el criterio de aceptación
  (`plan.md:365-369`) y con la línea base tras A (`gaps.md`, Auditoría Fase A): cobertura igual, 4 contratos KEPT, ruff/mypy sin
  aumento, 546 + 3 = 549 (E0.2). `--soft ruff,mypy` → exit 0, `549 passed`, `Compuerta superada; tolerados en rojo: ruff check, mypy`.
- **Archivos tocados:** `ruff check scripts/check.py tests/test_check.py` → `All checks passed!`; `ruff format --check` →
  `2 files already formatted`; `mypy scripts/check.py tests/test_check.py` → `Success: no issues found in 2 source files`.
- **Commit `5cbdec1`:** el mensaje es idéntico a `plan.md:377-398`. El `diff` del bloque del plan (sin la sangría) frente a
  `git log -1 --format=%B` solo da el salto de línea final que añade git. `git show --stat` muestra solo `scripts/check.py` (27)
  y `tests/test_check.py` (51).
- **`run()` literal:** el `diff` de `plan.md:286-313` frente a `scripts/check.py:170-197` sale vacío. El `try/except OSError`
  rodea solo a `subprocess.call` (`:186-189`), el aviso va a stderr (`:190`), el resultado es `FALLA (<tipo>)` (`:191`) y la
  función devuelve `False` (`:192`). El diff de la fase no tiene hunks fuera de `run()`. `--fix` (`:211-212`), `steps()` y
  `main()` no cambian. El docstring del módulo de tests coincide con `plan.md:318-324` (`diff` vacío). La clase
  `TestRunReportsUnstartableStep` está después de `TestLintImportsStep` y lleva el docstring del plan (`tests/test_check.py:208-248`).
- **TDD repetido por el auditor:** con `scripts/check.py` de `5cbdec1^` y los tests de la fase → `2 failed, 30 passed`
  (tests 6 y 7, `FileNotFoundError: [WinError 2]`). El test 8 pasa: es la guarda. Con el código de la fase → `32 passed`.
- **Mutaciones repetidas por el auditor** (helper `mut` de `plan.md:122`): MB1 → `2 failed, 30 passed` (6, 7); MB2 →
  `1 failed, 31 passed` (8). `sha256sum -c` da OK en `scripts/check.py` y `tests/test_check.py` tras cada una.
- **MB3 (desviación 1):** el guion literal sigue sin reproducir el bloqueo. Con el lanzador real, `✔ import-linter`, RESUMEN y
  exit 1 por ruff/mypy, porque Smart App Control ya no bloquea. `plan.md:364` lo prevé, así que los tests 6 y 7 son la evidencia.
  El auditor completó esa evidencia con tres pruebas, todas restauradas byte a byte (`sha256sum -c` OK y
  `git status --short scripts/` vacío):
  - **Variante del ejecutor repetida** (paso apuntado a `lint-imports-absent.exe`):
    `check.py: cannot start …\venv\Scripts\lint-imports-absent.exe: [WinError 2] …`, `--- import-linter: FALLA
    (FileNotFoundError)`, después `=== docs (coherencia) ===` y el RESUMEN con `✘ import-linter`, exit 1.
  - **WinError 4551 simulado** (sin tocar archivos): `subprocess.call` sustituido en memoria por una función que lanza
    `OSError(22, …, 'lint-imports.exe', 4551)`. `run()` da `check.py: cannot start lint-imports.exe: [WinError 4551] An
    Application Control policy has blocked this file…`, `--- import-linter: FALLA (OSError)` y devuelve `False`. Es la forma
    exacta que espera `plan.md:361`.
  - **Conclusión:** el criterio "MB3 da el resultado esperado o queda anotada" se cumple.
- **`progress.json`:** JSON válido. `Fase_B` está `completed` con `5cbdec1`, un hash real (`git cat-file -t` → `commit`);
  `last_handoff` está presente y `edit_rules` intacto. El diff de `a2c38eb` toca solo `current_target`, `Fase_B.status`,
  `Fase_B.commit` y `last_handoff`, los campos que permite `edit_rules`. `allowed_statuses` y las descripciones no cambian.
  `current_target: null` es la convención de cierre: 12 `progress.json` de `docs/deuda/` la usan. El registro va en un commit
  aparte (`a2c38eb`), que toca solo `progress.json` y `handoff-Fase_B.md`.
- **Desviación 2 (paso 8 con `AGENTS.md`):** `git diff --stat 9d2b589 -- . ':(exclude)docs'` muestra `AGENTS.md | 6`,
  `scripts/check.py | 96` y `tests/test_check.py | 123`. Desde `9d2b589`, el único commit que toca `AGENTS.md` es `3e47d99`
  (`git log 9d2b589..HEAD -- AGENTS.md`), el commit de documentos de David. E0.6 (`plan.md:511-516`) lo adelantó a antes de B.
  Ninguna fase tocó `AGENTS.md`, y la expectativa del paso 8 quedó desfasada por la enmienda.
- **Verificación final completa (cierre del ítem; la repitió el auditor):**
  - Paso 1: vacío.
  - Paso 2: vacío y `tests/test_check.py:2`.
  - Paso 3: `2/2 · 2/3 · 2/2 · 2/2`.
  - Paso 4: `True`.
  - Paso 5:
    - El entry point en el venv da `Contracts: 4 kept, 0 broken.` y exit 0.
    - En `C:/Python314` da `ModuleNotFoundError` y exit 1.
    - `C:/Python314/python.exe scripts/check.py --no-tests` da `importlinter is not importable by C:\Python314\python.exe; …`
      y `--- import-linter: FALLA (exit 1)`.
  - Paso 6: sin el venv en el PATH, 4 KEPT y `--- import-linter: OK`.
  - Paso 7: MA4 repetida → `Los servicios no conocen el transporte HTTP BROKEN`, `Contracts: 3 kept, 1 broken.`,
    `--- import-linter: FALLA (exit 1)`, exit 1. `app/services/user_service.py` restaurado (`sha256sum -c` OK).
  - Paso 8: ver desviación 2.
  - Paso 9: `32 passed` · `Found 8 errors.` · `Found 9 errors in 5 files (checked 53 source files)`.
  - Pasos 10 y 11: ver arriba.
  - Paso 12: vacío (`grep` exit 1).
  - **Conclusión:** la deuda (lanzador de pip en la compuerta, `OSError` que la aborta) no aparece en ningún rincón medido.
    `scripts/check_docs.py --estado` → `AF-12: … ejecutado (todas las fases) … última auditoría: PASS`.
- **Pendiente humano (no es una fase ni un hallazgo):** el ritual de cierre de E0.4/E0.2 y del párrafo de `plan.md:458-460`.
  Incluye las filas AF-12/AF-13 de `docs/backlog.md:180-181` a `Hecho`, la fila AF-14 `Sale → B-FUTURO` y PLAN §6 548 → 549.
  Queda también MD1, la revisión del log del CI en el PR.
- **AGENTS:** `run()` tiene docstring Google. Los tests no afirman sobre texto en español: comprueban `is False`, el tipo
  de excepción, el código de salida, la ruta y los marcadores `✘`/`✔` con el nombre del paso. No usan `Mock`:
  `check.steps` se sustituye con una lambda vía `monkeypatch`, así que `spec=` no aplica. `chdir` se restaura con
  `monkeypatch`. `check.py` está fuera de las capas de `import-linter`.
- **Árbol:** `git status --short` limpio al empezar y al terminar la auditoría, salvo este `gaps.md`.
