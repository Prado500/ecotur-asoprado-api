# PLAN — AF-12: Ejecutar import-linter por su entry point en el intérprete de la compuerta y marcar en rojo un paso que no arranca (AF-13)

- **Verificación:** `docs/deuda/AF-12/verificacion.md` (veredicto `confirmada`, l.3; adenda de David del 9 nov, l.165-210).
- **Base:** `bb03f46` (= `origin/develop`); la rama `item/af-12` solo añade docs (`4aff920`, `9d2b589`).
- **Ítems que salda:** AF-12 (fase A) y AF-13 (fase B), filas `docs/backlog.md:180-181`. Precedente de dos filas en una
  carpeta: `docs/deuda/BE-01/` (P1 y A7).
- **Fecha:** 2026-11-09.

## Resumen para aprobación

La compuerta (`scripts/check.py`) lanza import-linter con `venv/Scripts/lint-imports.exe`, el lanzador que genera pip.
Smart App Control lo bloquea en tu máquina, `subprocess.call` lanza `OSError` y la compuerta muere sin RESUMEN. Así no se
puede medir ninguna fase. La **fase A** cambia solo ese paso: corre el entry point registrado
(`from importlinter.cli import lint_imports_command; lint_imports_command()`) con `-c` en el mismo intérprete, igual que los
demás pasos. Si `importlinter` no se puede importar, devuelve el sustituto con la indicación de `pip install`, que ya
existía. Los 7 casos de AF-05 se sustituyen por 5. La **fase B** (AF-13) hace que `run()` capture `OSError`: el paso sale en
rojo, los siguientes corren y el RESUMEN se imprime siempre. Son dos archivos (`scripts/check.py` y
`tests/test_check.py`) y dos commits. El riesgo principal es que el paso vuelva a quedar en verde sin verificar nada, como
en AF-05. Lo cubren el test que compara el código con el entry point instalado y el mutante MA4: un contrato roto real
tiene que poner el paso en rojo. Quedan fuera el CI, `ruff.exe`, `--fix` y `.claude/`. `AGENTS.md` y `docs/CONTEXT.md`
quedan desfasados y los corriges tú en un commit propio dentro del PR. **No hace falta ADR** (motivo en el Análisis).

## Objetivo y decisiones bloqueadas

Objetivo: que la compuerta termine siempre con RESUMEN en cualquier máquina donde el Python del venv arranque, sin
depender de un lanzador generado por pip, y sin abrir otra vez un verde vacío como el de AF-05.

1. Mecanismo: `[PY, "-c", "from importlinter.cli import lint_imports_command; lint_imports_command()"]` (adenda 2). El
   código del `-c` es solo la llamada al entry point, sin ninguna lógica.
2. Se retiran `LINT_IMPORTS_NAMES` y `find_lint_imports` (`check.py:49-74`) y el `import sysconfig` (`check.py:22`).
   Ninguno tiene ya uso.
3. El hint de instalación se conserva: `_lint_imports_cmd()` pregunta `find_spec("importlinter")` en el intérprete de la
   compuerta. Si el módulo está, devuelve el comando del entry point; si no, devuelve el sustituto
   `[PY, "-c", "import sys; sys.exit(<hint>)"]`, que sale con 1 (adenda 2).
4. Tests de A (adenda 3): se invierten `test_check.py:153` y `:180` (`"importlinter.cli" in …`). La herramienta ausente
   se prueba por dos caminos y los dos acaban en rojo: (a) `find_spec` devuelve `None` (monkeypatch), y (b) el entry point
   se ejecuta con `-S`, sin site-packages. MA4 se repite.
5. AF-13 es la fase B (adenda 4): `try/except OSError` en `run()`. El paso queda en rojo y la compuerta sigue. No hay
   arreglo en el repo para `ruff.exe`.
6. `AGENTS.md:76-77`, `AGENTS.md` §8 (l.91-92) y `docs/CONTEXT.md:181-182` los edita David en un commit propio dentro del
   PR (adenda 5). No entran en ninguna fase.
7. Fuera: el CI, `.claude/` y cualquier otro paso o herramienta (adenda 6).

## Análisis del redactor

**Qué cambia y por qué.** El paso import-linter es el único de `steps()` que no empieza por `PY` (`check.py:109`). Los
demás corren como `[PY, …]` (`check.py:106-108,110,116`). El lanzador de pip es un binario distinto en cada máquina y sin
firma, y una política de control de aplicaciones puede bloquearlo. La verificación midió `exit 126` con `--help`. El
entry point que ese lanzador llama es `importlinter.cli:lint_imports_command`
(`venv/Lib/site-packages/import_linter-2.15.dist-info/entry_points.txt:3`). Ejecutarlo con `-c` desde el Python del venv
mide lo mismo sin pasar por el lanzador. Lo comprobó la verificación: `4 kept, 0 broken`, exit 0.

**Por qué el exit code se propaga (leído, no supuesto).** `lint_imports_command` es un `click.command`
(`importlinter/cli.py:74-79`) que llama a `_run_check`, y esta termina en `sys.exit(exit_code)` (`cli.py:71`). En modo
standalone, `click.BaseCommand.main` (`click/core.py:1338-1449`, click 8.3.1) solo captura `ClickException`, `OSError`
EPIPE, `Exit` y `Abort` (`core.py:1420,1426,1432,1445`), y las dos últimas son `RuntimeError` (`click/exceptions.py:294,298`).
`SystemExit` no entra en ninguna, así que el código sube intacto hasta el proceso. MA4 lo demuestra en la práctica. Los
argumentos salen de `sys.argv[1:]` (`core.py:1390`). Con `-c`, `sys.argv == ["-c"]`, la lista queda vacía y el
comportamiento es el mismo que `lint-imports` sin argumentos.

**Por qué el test de equivalencia es imprescindible.** El fallo de AF-05 fue un comando click que se definía pero nunca
se ejecutaba, y el paso salía con 0. El grupo `import_linter` (`cli.py:82-88`) imprime la ayuda y también sale con 0. Si
alguien cambia la cadena del `-c` por algo parecido, ni el test con `-S` ni el de `find_spec` lo detectan (mutante MA3).
Solo lo detecta comparar `LINT_IMPORTS_CODE` con el entry point `lint-imports` que declaran los metadatos instalados
(`importlib.metadata.entry_points`).

**Orden y dependencias.** B va después de A porque comparten los dos archivos y el docstring del módulo de tests que B
reescribe es el que deja A. No hay dependencia lógica: B no usa nada de A. La regla del protocolo de que A sea la fase
más pequeña **no se cumple**: B es más corta (unas 20 líneas en `check.py` y 3 tests). Se respeta la numeración que fijó
David (adenda 2 y 4, y la fila AF-13 dice "fase B"). Tras A la compuerta ya termina con RESUMEN en esta máquina: ningún
paso lanza ya el lanzador bloqueado. Por eso la línea base "con compuerta" se toma al cerrar A, no antes (adenda 1).

**Tests que congelan comportamiento.**
- `TestLintImportsResolution` (`test_check.py:140-191`, 7 casos) congela el mecanismo binario. Se sustituye entera por
  `TestLintImportsStep` (5 casos). Desaparecen los casos de `find_lint_imports` porque la función se retira.
  `test_check.py` pasa de 31 a 29 tests y la suite de 548 a 546 tras A. No es un retroceso: los 2 casos eliminados
  probaban código que ya no existe, y la cobertura mide solo `app/` (96.11 %, sin cambio).
- `TestImportHasNoSideEffects` (`:100-114`) recarga el módulo. `find_spec` se llama dentro de `steps()` y nunca al importar,
  así que el test sigue en verde. No mover la llamada al nivel de módulo.
- `TestMainRejectsBadSoft` (`:117-137`) depende de que `main()` valide `--soft` antes de llamar a `steps()`. B no cambia
  ese orden.

**Riesgos.**
1. Verde vacío como en AF-05. Lo cubren el test 2 y el mutante MA4.
2. El test (b) usa `-S`, que da por hecho que `importlinter` solo vive en site-packages. Es cierto en el venv (medido: con
   `-S`, `ModuleNotFoundError`, exit 1) y en el Python del CI, donde pip instala en site-packages.
3. Si una política bloqueara `venv/Scripts/python.exe`, ningún arreglo en el repo serviría. Hoy arranca (lo midió la
   verificación).
4. La fase B no debe tragarse fallos que no son de arranque. Solo captura `OSError` alrededor de `subprocess.call`, y el
   test 8 congela que un comando que corre y sale con 3 siga mostrando `exit 3`.

**Qué NO se toca.**
- `verdict()`, `parse_soft()`, `_soft_arg()` ni `STEP_KEYS`.
- Los otros cinco pasos.
- `--fix` (`check.py:210-212`, fuera de `run()`; va a Residuales).
- `.azure-pipelines/ci-pipeline.yml`: el mecanismo cambia también ahí y David lo comprueba en el log (MD1).
- `ruff.exe` (rincón 2), `.claude/`, `AGENTS.md`, `docs/CONTEXT.md` y `pyproject.toml`.

**ADR: no hace falta.**
- No existe ningún ADR que fije el mecanismo de lanzamiento. AF-05 lo decidió en el backlog y en AGENTS §6, sin ADR.
- No hay patrón ni módulo nuevo, ni cambio de contrato HTTP. El paso se alinea con los otros cinco (`[PY, …]`), en la
  línea del "comando portable (`python -m …`)" de ADR-0001:71.
- La invariante que importa sigue igual: misma herramienta e intérprete, y herramienta ausente igual a rojo.
- Lo que sí cambia es una regla escrita, AGENTS §6, y eso ya va en el commit de David.
- Si David prefiere dejar constancia de "por qué no el lanzador de pip", el sitio es esa frase de AGENTS y el docstring
  de `_lint_imports_cmd`, que este plan dicta, no un ADR.

## Regla de alcance

- **Sí:** `scripts/check.py` (importaciones, l.22 y 24; bloque l.49-101; línea 109; `steps()`; `run()`) y
  `tests/test_check.py` (docstring del módulo e importaciones, l.1-16; `TestLintImportsResolution`; una clase nueva en B).
- **No:** cualquier otro archivo. Si el ejecutor necesita otro, es un hallazgo: lo anota en el handoff y se detiene.
  El commit de documentos de David (`AGENTS.md`, `docs/CONTEXT.md`) **no es una fase**.

## Fases

**Protocolo de mutación** (heredado de AF-05; no se commitea nada; Git Bash, raíz del repo). El helper sustituye un texto
exacto, corre los tests y restaura el archivo byte a byte. Antes del `git add`, `git status --short` solo debe mostrar los
archivos de la fase.

```bash
mut() { cp "$1" "$1.bak" && ./venv/Scripts/python.exe -c "import pathlib,sys; p=pathlib.Path(sys.argv[1]); s=p.read_text(encoding='utf-8'); assert sys.argv[2] in s, 'pattern not found'; p.write_text(s.replace(sys.argv[2], sys.argv[3], 1), encoding='utf-8')" "$1" "$2" "$3"; ./venv/Scripts/python.exe -m pytest -q -p no:cacheprovider "$4" 2>&1 | tail -1; mv "$1.bak" "$1"; }
NOVENV_PATH=$(echo "$PATH" | tr ':' '\n' | grep -v -i "ecotur-asoprado/venv" | paste -sd ':')
```

### Fase A — import-linter por su entry point, o paso en rojo con el hint (AF-12)

- **Archivos:** `scripts/check.py`, `tests/test_check.py`.
- **Cambios exactos en `scripts/check.py`:**
  - Importaciones: quitar `import sysconfig` (l.22) y `from collections.abc import Callable` (l.24, solo lo usaban las
    funciones que se retiran). Añadir `from importlib.util import find_spec`, en el orden que deje ruff.
  - Sustituir l.49-101 (comentario, `LINT_IMPORTS_NAMES`, `find_lint_imports`, `_lint_imports_cmd`) por:
    ```python
    # What pip's lint-imports launcher runs (entry point importlinter.cli:lint_imports_command),
    # executed here by the gate's own interpreter instead (AF-12).
    LINT_IMPORTS_CODE = "from importlinter.cli import lint_imports_command; lint_imports_command()"


    def _lint_imports_cmd() -> list[str]:
        """Build the import-linter step: the tool's entry point, or a stand-in that fails loudly.

        The entry point runs with ``-c`` in the interpreter that runs the gate, like every other
        step, instead of pip's console-script launcher: that launcher is a per-machine binary an
        application control policy may block, and then the step cannot start at all (AF-12).
        ``lint_imports_command`` exits with the contracts' result, so a broken contract is red.

        When importlinter is not importable by this interpreter, the stand-in prints what to
        install and exits 1, so ``run()`` marks the step red with the same exit-code rule as every
        other step (AF-05: a missing tool is never an empty green).

        Returns:
            The command to run for the import-linter step.
        """
        if find_spec("importlinter") is not None:
            return [PY, "-c", LINT_IMPORTS_CODE]
        hint = (
            f"importlinter is not importable by {PY}; install the dev extras in this interpreter: "
            f"{PY} -m pip install -e .[dev]"
        )
        return [PY, "-c", f"import sys; sys.exit({hint!r})"]
    ```
  - `steps()`: la l.109 pasa a `("import-linter", _lint_imports_cmd()),`. Como la función se toca, recibe este docstring
    (AGENTS §4):
    ```python
        """Return the gate's steps in execution order, each run by this interpreter (``PY``).

        Args:
            no_tests: Leave out the pytest step (``--no-tests``).

        Returns:
            ``(step name, command)`` pairs; every command starts with ``PY``.
        """
    ```
- **Cambios exactos en `tests/test_check.py`:**
  - Docstring del módulo (l.1-6):
    ```python
    """Tests for scripts/check.py: the --soft policy of the quality gate (B-CI, ADR-0005) and how the
    import-linter step is built (AF-05, AF-12).

    No real step (ruff, mypy, import-linter, pytest...) checks anything here. The only subprocesses
    are the stand-in command for a missing import-linter and the entry point under ``-S``, which
    fails at import before checking anything.
    """
    ```
  - Importaciones: quitar `import sysconfig` y añadir `from importlib.metadata import entry_points`.
  - Sustituir `TestLintImportsResolution` (l.140-191) por `TestLintImportsStep`, con el docstring
    `"""The import-linter step runs the tool's entry point in this interpreter, or fails loudly."""`.
- **Tests (RED primero).** Se escriben los 5 antes de tocar `check.py`. RED esperado: `5 failed, 24 passed` en
  `tests/test_check.py`, con `AttributeError` o `TypeError` porque `LINT_IMPORTS_CODE` y `find_spec` aún no existen y
  `_lint_imports_cmd` exige argumentos.
  1. `test_step_is_the_entry_point_regardless_of_path(monkeypatch, tmp_path)`: obtiene el comando de
     `dict(check.steps(no_tests=True))["import-linter"]` con el PATH real y con `monkeypatch.setenv("PATH", str(tmp_path))`.
     Afirma `without_path == [check.PY, "-c", check.LINT_IMPORTS_CODE]`, `"importlinter.cli" in without_path[2]` (la
     inversión de l.153) y `without_path == with_path`.
  2. `test_code_calls_the_registered_console_script()`:
     `(script,) = entry_points(group="console_scripts", name="lint-imports")` y luego
     `assert check.LINT_IMPORTS_CODE == f"from {script.module} import {script.attr}; {script.attr}()"`.
  3. `test_missing_package_yields_failing_command_with_install_hint(monkeypatch)`: un `no_spec(name: str) -> None` que
     anota el nombre en `asked` y devuelve `None`, con `monkeypatch.setattr(check, "find_spec", no_spec)`, y
     `cmd = check._lint_imports_cmd()`. Afirma:
     - `asked == ["importlinter"]`, `cmd[:2] == [check.PY, "-c"]` y `check.LINT_IMPORTS_CODE not in cmd`;
     - con `subprocess.run(cmd, capture_output=True, text=True, check=False)`: `returncode == 1`, `stdout == ""`,
       `check.PY in stderr` y `"-m pip install -e .[dev]" in stderr`.
  4. `test_missing_package_makes_the_gate_step_red(monkeypatch, capfd)`: con `find_spec` sustituido por `lambda name: None`,
     toma `cmd` de `dict(check.steps(no_tests=True))["import-linter"]` (prueba el cableado de `steps()`). Afirma
     `check.run("import-linter", cmd) is False` y `"-m pip install -e .[dev]" in capfd.readouterr().err`.
  5. `test_entry_point_without_the_package_on_sys_path_is_red(capfd)`: `cmd = check._lint_imports_cmd()` (real), con el
     comentario `# -S skips site-packages: importable when the command is built, not when it runs.`, y
     `no_site = [cmd[0], "-S", *cmd[1:]]`. Afirma `"importlinter.cli" in cmd[2]` (la inversión de l.180),
     `check.run("import-linter", no_site) is False`, y que en `err` aparecen `"ModuleNotFoundError"` e `"importlinter"`.
- **Mutaciones** (sobre la punta de la fase; pegar la última línea de cada una):
  - MA1, se pregunta por el nombre de distribución en lugar del módulo:
    `mut scripts/check.py 'find_spec("importlinter")' 'find_spec("import_linter")' tests/test_check.py` → `3 failed`
    (1, 3 y 5).
  - MA2, sin guarda:
    `mut scripts/check.py 'if find_spec("importlinter") is not None:' 'if True:' tests/test_check.py` → `2 failed` (3 y 4).
  - MA3, el grupo click, que sale con 0 mostrando la ayuda (el verde vacío de AF-05):
    `mut scripts/check.py 'import lint_imports_command; lint_imports_command()"' 'import import_linter; import_linter()"' tests/test_check.py`
    → `1 failed` (2).
  - MA5, un paso que no hace nada:
    `mut scripts/check.py '("import-linter", _lint_imports_cmd()),' '("import-linter", [PY, "-c", "pass"]),' tests/test_check.py`
    → `2 failed` (1 y 4).
  - MA4, un contrato roto real, ejecutado con la compuerta y sin el venv en el `PATH`:
    ```bash
    cp app/services/user_service.py app/services/user_service.py.bak
    printf '\nimport fastapi  # AF-12 mutation\n' >> app/services/user_service.py
    env -u VIRTUAL_ENV PATH="$NOVENV_PATH" ./venv/Scripts/python.exe scripts/check.py --no-tests --soft format,ruff,mypy 2>&1 | sed -n '/=== import-linter ===/,/--- import-linter/p'; echo "exit ${PIPESTATUS[0]}"
    mv app/services/user_service.py.bak app/services/user_service.py && git status --short app/
    ```
    Esperado: `Los servicios no conocen el transporte HTTP BROKEN`, `Contracts: 3 kept, 1 broken.`,
    `--- import-linter: FALLA (exit 1)` y `exit 1`. Con `--soft format,ruff,mypy`, el exit 1 solo puede venir de
    import-linter: la línea añadida rompe el formato y ruff a propósito. Al terminar, `git status --short app/` sale vacío.
- **Criterio de aceptación:**
  - `./venv/Scripts/python.exe -m pytest tests/test_check.py -q` → `29 passed`.
  - `./venv/Scripts/python.exe scripts/check.py` (la compuerta completa) **termina e imprime RESUMEN**:
    - `✔ ruff format --check`, `✘ ruff check` (`Found 8 errors.`) y `✘ mypy` (`Found 9 errors in 5 files`), igual que la
      línea base (trinquete de ADR-0005);
    - `✔ import-linter` con `Contracts: 4 kept, 0 broken.` dentro de su bloque, `✔ docs (coherencia)` y
      `✔ pytest + cobertura` con `546 passed`, 0 failed y `TOTAL … 96.11%`;
    - la salida termina con `Compuerta NO superada: ruff check, mypy` y exit 1.
  - `./venv/Scripts/python.exe scripts/check.py --soft ruff,mypy` → exit 0 y
    `Compuerta superada; tolerados en rojo: ruff check, mypy`.
  - MA1, MA2, MA3 y MA5 dan el número de fallos indicado, y MA4 da rojo. Todas se restauran.
- **Fuera de alcance de esta fase:**
  - `run()` y `OSError` (fase B).
  - Los otros cinco pasos, `--fix`, el CI y `ruff.exe`.
  - `AGENTS.md` y `docs/CONTEXT.md` (commit de David).
- **Commit:**
  ```
  fix(check): run import-linter via its entry point, not pip's launcher

  The import-linter step was the only gate step that did not start with
  the gate's interpreter: it ran venv/Scripts/lint-imports.exe, the
  per-machine launcher pip generates. Windows Smart App Control blocks
  that unsigned binary (OSError: [WinError 4551]), so the gate died
  before printing its summary and no baseline or phase could be measured
  on that machine (backlog AF-12).

  - scripts/check.py: the step now runs the registered entry point,
    importlinter.cli:lint_imports_command, with -c in the interpreter
    that runs the gate, like the other steps. click lets the command's
    sys.exit through, so a broken contract still exits 1. When
    find_spec("importlinter") finds nothing in that interpreter, the
    existing stand-in prints the pip install -e .[dev] hint and exits 1,
    so a missing tool is still red, never an empty green (AF-05).
    find_lint_imports, LINT_IMPORTS_NAMES and the sysconfig import are
    gone; steps() gains a docstring.
  - tests/test_check.py: the 7 AF-05 cases that pinned the console
    script (and forbade importlinter.cli in the command) become 5: the
    step is the entry point with or without the venv on PATH; the -c
    code matches the installed lint-imports entry point (guards against
    the empty-green click group); a missing package yields the stand-in
    with the hint and a red step through steps(); the real entry point
    under -S (no site-packages) is a red step.

  run() still lets an OSError escape; that is AF-13, the next commit.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase B — un paso que no arranca sale en rojo y la compuerta sigue (AF-13)

- **Archivos:** `scripts/check.py`, `tests/test_check.py`.
- **Cambios exactos en `scripts/check.py`:** `run()` (l.189-195 de la base) queda así:
  ```python
  def run(name: str, cmd: list[str]) -> bool:
      """Run one gate step and print its outcome; a step that cannot start is a red step.

      A command that cannot be started (missing, or blocked by an application control policy)
      raises ``OSError`` from ``subprocess``; it is reported as a failure instead of aborting the
      gate, so the remaining steps and the summary still run (AF-13).

      Args:
          name: Step name, as printed in the header and the summary.
          cmd: Command to run; its exit code decides the outcome.

      Returns:
          True if the command ran and exited with 0, False otherwise.
      """
      print(f"\n=== {name} ===", flush=True)
      t0 = time.perf_counter()
      try:
          code = subprocess.call(cmd)
      except OSError as exc:
          print(f"check.py: cannot start {cmd[0]}: {exc}", file=sys.stderr, flush=True)
          outcome = f"FALLA ({type(exc).__name__})"
          passed = False
      else:
          passed = code == 0
          outcome = "OK" if passed else f"FALLA (exit {code})"
      dt = time.perf_counter() - t0
      print(f"--- {name}: {outcome} en {dt:.1f}s", flush=True)
      return passed
  ```
- **Cambios exactos en `tests/test_check.py`:**
  - Docstring del módulo:
    ```python
    """Tests for scripts/check.py: the --soft policy of the quality gate (B-CI, ADR-0005), how the
    import-linter step is built (AF-05, AF-12) and how a step that cannot start is reported (AF-13).

    No real step (ruff, mypy, import-linter, pytest...) checks anything here. The only subprocesses
    are the stand-in command for a missing import-linter, the entry point under ``-S``, which fails
    at import before checking anything, and trivial ``-c`` commands for run() and main().
    """
    ```
  - Clase nueva `TestRunReportsUnstartableStep`, después de `TestLintImportsStep`, con el docstring
    `"""A step whose command cannot start is a red step, not a crash of the gate (AF-13)."""`.
- **Tests (RED primero).** RED esperado: `2 failed, 30 passed`. El 6 y el 7 fallan con `FileNotFoundError`; el 8 es un
  test de guarda que ya pasa antes y después.
  6. `test_unstartable_command_is_a_red_step(tmp_path, capfd)`: con `missing = tmp_path / "no-such-tool"`, afirma
     `check.run("x", [str(missing)]) is False`. Además, alguna línea de `out` empieza por `"--- x: "` y contiene
     `"(FileNotFoundError)"`, y `str(missing) in err`.
  7. `test_main_runs_later_steps_and_prints_summary(monkeypatch, tmp_path, capfd)`: se hace `monkeypatch.chdir(tmp_path)`
     (así se restaura el cwd que `main()` fija) y se sustituye `check.steps` por
     `lambda no_tests: [("unstartable", [str(tmp_path / "no-such-tool")]), ("after", [check.PY, "-c", "pass"])]`. Afirma
     `check.main([]) == 1`, y que `out` contiene `"=== after ==="`, `"✘ unstartable"` y `"✔ after"`.
  8. `test_command_that_runs_and_fails_reports_its_exit_code(capfd)`: afirma
     `check.run("x", [check.PY, "-c", "import sys; sys.exit(3)"]) is False` y `"(exit 3)" in out`.
- **Mutaciones:**
  - MB1, no se captura:
    `mut scripts/check.py 'except OSError as exc:' 'except ValueError as exc:' tests/test_check.py` → `2 failed` (6 y 7).
  - MB2, se pierde el exit code:
    `mut scripts/check.py 'else f"FALLA (exit {code})"' 'else "FALLA"' tests/test_check.py` → `1 failed` (8).
  - MB3, el incidente real (solo en Windows, si Smart App Control sigue activo). Se vuelve a apuntar el paso al lanzador
    bloqueado y se corre la compuerta:
    ```bash
    cp scripts/check.py scripts/check.py.bak
    ./venv/Scripts/python.exe - <<'EOF'
    import pathlib
    p = pathlib.Path("scripts/check.py")
    s = p.read_text(encoding="utf-8")
    old = '("import-linter", _lint_imports_cmd()),'
    new = '("import-linter", [str(Path(PY).with_name("lint-imports.exe"))]),'
    assert old in s, "pattern not found"
    p.write_text(s.replace(old, new, 1), encoding="utf-8")
    EOF
    ./venv/Scripts/python.exe scripts/check.py --no-tests 2>&1 | sed -n '/=== import-linter ===/,$p'; echo "exit ${PIPESTATUS[0]}"
    mv scripts/check.py.bak scripts/check.py && git status --short scripts/
    ```
    Esperado:
    - `check.py: cannot start …lint-imports.exe: [WinError 4551] …` y `--- import-linter: FALLA (OSError)`;
    - después `=== docs (coherencia) ===` y `=== RESUMEN ===` con `✘ import-linter`, y `exit 1`;
    - al terminar, `git status --short scripts/` vacío.
    Si la política ya no bloquea, se anota en el handoff y los tests 6 y 7 son la evidencia.
- **Criterio de aceptación:**
  - `./venv/Scripts/python.exe -m pytest tests/test_check.py -q` → `32 passed`.
  - La compuerta completa da el mismo RESUMEN que el de A, con `549 passed` y `96.11%`.
  - `--soft ruff,mypy` → exit 0.
  - MB1 y MB2 dan el número de fallos indicado; MB3 da el resultado esperado o queda anotada.
- **Fuera de alcance de esta fase:**
  - El mecanismo de import-linter (fase A).
  - `subprocess.call` de `--fix` (`check.py:211-212`), que va a Residuales.
  - Unificar el idioma de la salida (residual de AF-05).
  - El CI y `ruff.exe`.
- **Commit:**
  ```
  fix(check): mark a step that cannot start red instead of aborting

  run() called subprocess.call without handling OSError, so a step whose
  command could not start (missing, or blocked by an application control
  policy, as lint-imports.exe was on 9 Nov) raised out of main(): the
  gate died with a traceback, the remaining steps never ran and no
  summary was printed (backlog AF-13, found while verifying AF-12).

  - scripts/check.py: run() catches OSError around the call, prints the
    command and the error on stderr, reports the step as failed with the
    exception type and returns False, so the other steps run and the
    summary ends with exit 1. A command that runs and fails still
    reports its exit code. run() gains a docstring.
  - tests/test_check.py: an unstartable command is a red step; main()
    keeps running later steps and prints the summary with that step red
    (both red before this change); a command that exits 3 still shows
    exit 3.

  python -m ruff still launches ruff's own ruff.exe; if a policy ever
  blocked it, the gate would now say so in red instead of dying.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

## Verificación final

En Git Bash desde la raíz, al cerrar la fase B y antes del commit de documentos de David. Los conteos incluyen el texto
que dicta este plan (comentarios, docstrings y tests).

```bash
# 1. Mecanismo binario retirado (esperado: vacío)
git grep -n -E 'lint-imports\.exe|LINT_IMPORTS_NAMES|find_lint_imports|sysconfig' -- scripts tests
# 2. Ningún test prohíbe el entry point (esperado: vacío); aserciones invertidas (esperado: tests/test_check.py:2)
git grep -n '"importlinter\.cli" not in' -- tests
git grep -c '"importlinter\.cli" in' -- tests/test_check.py
# 3. Inventario (esperado, en este orden: check.py:2 test_check.py:2 · check.py:2 test_check.py:3 ·
#    check.py:2 test_check.py:2 · check.py:2 test_check.py:2)
git grep -c 'importlinter\.cli' -- scripts/check.py tests/test_check.py
git grep -c 'LINT_IMPORTS_CODE' -- scripts/check.py tests/test_check.py
git grep -c 'find_spec' -- scripts/check.py tests/test_check.py
git grep -c '_lint_imports_cmd' -- scripts/check.py tests/test_check.py
# 4. Todos los pasos empiezan por el intérprete (esperado: True; en la base da False)
./venv/Scripts/python.exe -c "import sys; sys.path.insert(0, 'scripts'); import check; print(all(cmd[0] == check.PY for _, cmd in check.steps(no_tests=False)))"
# 5. Mecanismo y regla de AF-05 (patrones de la verificación). Esperado: "Contracts: 4 kept, 0 broken." y exit 0 ·
#    ModuleNotFoundError y exit 1 · hint "importlinter is not importable by C:\Python314\python.exe; …" y
#    "--- import-linter: FALLA (exit 1)" (si C:\Python314 no existe, se anota; los tests 3 y 4 son la evidencia)
./venv/Scripts/python.exe -c "from importlinter.cli import lint_imports_command; lint_imports_command()"; echo "exit $?"
C:/Python314/python.exe -c "from importlinter.cli import lint_imports_command; lint_imports_command()"; echo "exit $?"
C:/Python314/python.exe scripts/check.py --no-tests 2>&1 | sed -n '/=== import-linter ===/,/--- import-linter/p'
# 6. Sin el venv en el PATH (esperado: 4 contratos KEPT y "--- import-linter: OK")
NOVENV_PATH=$(echo "$PATH" | tr ':' '\n' | grep -v -i "ecotur-asoprado/venv" | paste -sd ':')
env -u VIRTUAL_ENV PATH="$NOVENV_PATH" ./venv/Scripts/python.exe scripts/check.py --no-tests 2>&1 | sed -n '/=== import-linter ===/,/--- import-linter/p'
# 7. Contrato roto → rojo: MA4 de la fase A (el auditor la repite y restaura byte a byte)
# 8. Nada fuera del alcance cambió (esperado: solo scripts/check.py y tests/test_check.py)
git diff --stat 9d2b589 -- . ':(exclude)docs'
# 9. Tests y trinquete (esperado: 32 passed · Found 8 errors. · Found 9 errors in 5 files …)
./venv/Scripts/python.exe -m pytest tests/test_check.py -q
./venv/Scripts/python.exe -m ruff check . | grep -E '^Found'
./venv/Scripts/python.exe -m mypy | tail -1
# 10. Compuerta: termina con RESUMEN; ✘ solo ruff check y mypy; 549 passed; 96.11 %; 4 kept; exit 1
./venv/Scripts/python.exe scripts/check.py
# 11. La misma tolerando la deuda ajena (esperado: exit 0, "tolerados en rojo: ruff check, mypy")
./venv/Scripts/python.exe scripts/check.py --soft ruff,mypy; echo "exit $?"
# 12. Tras el commit de documentos de David (esperado: vacío; hoy 3 líneas: AGENTS.md:77, CONTEXT.md:181-182)
grep -n -E 'directorio de scripts|busca .lint-imports.' AGENTS.md docs/CONTEXT.md
```

| Medida | Línea base (`bb03f46`, medición complementaria) | Tras A | Tras B |
|---|---|---|---|
| RESUMEN de la compuerta | no se imprime (aborta) | sí | sí |
| ruff / mypy | 8 I001 / 9 en 5 archivos | igual | igual |
| import-linter | 4 kept (fuera de la compuerta) | 4 kept, `✔` en la compuerta | igual |
| `test_check.py` / suite | 31 / 548 passed | 29 / 546 | 32 / 549 |
| Cobertura (`app/`) | 96.11 % | 96.11 % | 96.11 % |
| check_docs | exit 0 | `✔` | `✔` |

**Paso manual de David (MD1, en el PR a `develop`).** En Azure DevOps, abrir el log del paso "Compuerta de calidad
(scripts/check.py)". Bajo `=== import-linter ===` tienen que aparecer los 4 contratos y `Contracts: 4 kept, 0 broken.`
antes de `--- import-linter: OK`, y el RESUMEN debe mostrar `✔ import-linter`. Si aparece `importlinter is not importable
by …`, pip no instaló en el intérprete del CI: no se mezcla y se replanifica.

**Commit de documentos de David (no es una fase):** los textos de la adenda 5 en `AGENTS.md:76-77` (§6) y en §8
(l.91-92), y en `docs/CONTEXT.md:181-182`. Al marcar las filas AF-12 y AF-13 como `Hecho (PR de AF-12, fase A/B)` en
`docs/backlog.md` se aplica el ritual de cierre.

## Residuales

1. **`--fix` sigue sin protección** (`check.py:210-212`): llama a `subprocess.call` fuera de `run()`. Un `OSError` ahí
   aborta igual que antes de AF-13. Hoy solo lanza `PY -m ruff`, que corre `ruff.exe`, el binario de ruff (rincón 2).
   Destino: `B-FUTURO`. Fila sugerida: "AF-14 · `--fix` de `check.py` no captura `OSError` (residual de AF-12/AF-13) ·
   Baja · Sale → `B-FUTURO`".
2. **El docstring de uso de `check.py` (l.4-7) dice `python scripts/check.py` a secas**, la forma que AF-07 retiró de los
   prompts y de AGENTS. Destino: anotarlo en la fila AF-07 o en la de AF-14 sugerida. Baja.
3. **`ruff.exe` a través de `python -m ruff`** (rincón 2 de la verificación): sin arreglo en el repo. Ya está anotado en
   la fila AF-13; no hace falta fila nueva.
4. **La salida de la compuerta mezcla inglés y español** (residual sin fila de AF-05): la fase B añade una línea en inglés
   en stderr (`check.py: cannot start …`), con el mismo estilo que `check.py:207`. Sin cambio de destino.

## Referencias

Context7 no estaba disponible en esta sesión. Las APIs se confirmaron leyendo el código instalado en el venv:

- import-linter · 2.15 · `venv/Lib/site-packages/import_linter-2.15.dist-info/entry_points.txt:3`
  (`lint-imports = importlinter.cli:lint_imports_command`), `importlinter/cli.py:51-79` (`_run_check` → `sys.exit`,
  l.71) y `:82-88` (el grupo `import_linter`, que sale con 0) · https://import-linter.readthedocs.io/en/stable/
- click · 8.3.1 · `venv/Lib/site-packages/click/core.py:1338-1449` (`main`: `sys.argv[1:]` en l.1390; las excepciones
  capturadas en l.1420-1449) y `click/exceptions.py:294,298` (`Abort`/`Exit` son `RuntimeError`) ·
  https://click.palletsprojects.com/en/stable/api/#click.BaseCommand.main
- Python · 3.14.3 · `importlib.util.find_spec` (`C:/Python314/Lib/importlib/util.py:69`) ·
  https://docs.python.org/3.14/library/importlib.html#importlib.util.find_spec
- Python · 3.14.3 · `importlib.metadata.entry_points` (`C:/Python314/Lib/importlib/metadata/__init__.py:999`) ·
  https://docs.python.org/3.14/library/importlib.metadata.html#entry-points
- Python · 3.14.3 · opción `-S` (sin `site`) · https://docs.python.org/3.14/using/cmdline.html#cmdoption-S.
  Medido por el redactor (solo lectura): `./venv/Scripts/python.exe -S -c "from importlinter.cli import …"` →
  `ModuleNotFoundError`, exit 1.

## Enmiendas aprobadas

### E0 — 9 nov 2026, 15:51 (David, sesión Mentor; regla del retoque, README de sesiones)

Texto literal de David: «ok entonces A -> B, asegúrate que ya todo esté listo para proceder así».

**Plan aprobado con el orden A → B tal como está escrito.** El Mentor había propuesto B → A (mejor medición "antes" de la
fase A, que hoy aborta sin RESUMEN; ADR-0001 C3); David lo descartó porque obligaba a llevar el commit de documentos al
final y a recalcular conteos y `progress.json`. La adenda 1 ya acepta que la primera fase se mida "antes" sin RESUMEN.

1. **Decisión abierta 1 (orden):** A → B, sin cambios.
2. **Decisión abierta 2 (conteos):** aceptados: `tests/test_check.py` 31 → 29 → 32; suite 548 → 546 → 549; cobertura 96,11 %
   en todo momento. En el cierre, PLAN §6 anota 548 → 549 y la verificación de A4 partirá de 549.
3. **Decisión abierta 3 (texto del hint):** aceptado tal como está en la fase A.
4. **Decisión abierta 4 (AF-14):** sí, en el ritual de cierre de hoy, `Sale → B-FUTURO`, con los dos residuales 1 y 2
   (`--fix` sin captura de `OSError`; docstring de uso de `check.py:4-7` con `python` a secas). No se anota en AF-07 (está
   `Hecho`).
5. **Decisión abierta 5 (MD1):** sí; David revisa el log del CI del PR antes de mezclar.
6. **Decisión abierta 6 y momento del commit de documentos (corrige la Verificación final, l.403 y paso 12):** el commit
   de documentos de David (`AGENTS.md:76-77` y l.91-92; `docs/CONTEXT.md:181-182`, textos de la adenda 5) va **después de la
   auditoría PASS de la fase A y antes de `/implementar AF-12 B`**, no al final de la rama: en ese punto el mecanismo que
   la frase describe ya existe en la rama, y el auditor de B corre el paso 12 tal como está escrito y lo encuentra vacío.
   Un commit solo de documentos no mueve la compuerta ni la base que compara el ejecutor (ADR-0005). El párrafo "Commit de
   documentos de David (no es una fase)" se lee con este momento.

Sin cambios en fases, tests, mutaciones, commits ni `progress.json` (`current_target: Fase_A`).
