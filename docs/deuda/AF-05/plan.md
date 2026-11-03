# PLAN — AF-05: Ejecutar `lint-imports` desde el directorio de scripts del intérprete y poner el paso en rojo si no está

- **Fecha:** 2026-11-03 · **Fuente:** `verificacion.md` (confirmada; la **Adenda de David**, puntos 1-3, manda sobre la
  "Conclusión para el planificador") + fila AF-05 de `docs/backlog.md` v1.12 · **Rama:** `item/af-05` (PR propio)
- **Base develop:** `217e58f` (la de la verificación; el ejecutor la re-comprueba en su ritual de arranque)
- **Aprobado por David el 3 nov 2026, con cinco enmiendas** (ver la sección final "Enmiendas aprobadas antes de
  `/implementar`"). Ya están aplicadas en todo el cuerpo del plan.

## Resumen para aprobación

Hoy, si `lint-imports` no está en el `PATH` (el venv invocado por ruta sin activar, que es el modo del flujo desde el
2 nov), `scripts/check.py` cae a `python -m importlinter.cli lint_imports`. Ese módulo no ejecuta nada y sale con 0, así
que la compuerta imprime `✔ import-linter` sin haber comprobado ni un contrato. Se cambia por una función pura,
`find_lint_imports`, que busca la herramienta **solo** en el directorio de scripts del intérprete que corre la compuerta
(`sysconfig.get_path("scripts")`, donde pip instala sus console scripts: `lint-imports.exe` en Windows, `lint-imports` en
Linux) y nunca en el `PATH`. Si no la encuentra, el paso ejecuta un comando sustituto que imprime qué instalar y sale con
1, de modo que `run()`, sin cambios, lo marca en rojo. Una sola fase, dos archivos (`scripts/check.py`,
`tests/test_check.py`), un commit `fix(check)` y 7 casos de test nuevos (el primero reproduce el no-op y está rojo hoy).
**Riesgo principal:** que en el CI (Linux) la herramienta no esté en el directorio de scripts del intérprete. Si pasara,
el CI de este PR saldría en **rojo con mensaje**, nunca en verde falso; lo confirma David en el log (paso manual MD1).
**No se tocan** `run()`, `verdict`/`--soft`, los pasos `-m` de ruff/mypy/pytest, el YAML del CI, `pyproject.toml`,
`.claude/` (AF-06) ni los 60 errores de ruff / 10 de mypy heredados. No hace falta ADR.

## Objetivo y decisiones bloqueadas

Que el paso import-linter de la compuerta ejecute de verdad la herramienta del intérprete que corre la compuerta, con
independencia del `PATH`, y que su ausencia sea un rojo con mensaje y nunca un verde.

1. **Solo en `sysconfig.get_path("scripts")`; sin `shutil.which`** (adenda, punto 1, enmendada por David el 3 nov). Es el
   directorio donde pip instala los console scripts del intérprete que corre la compuerta. La herramienta no se busca en
   ningún otro sitio. Desaparecen `shutil.which` y el `import shutil`, y entra `import sysconfig`.
2. **Sin fallback a `-m importlinter.cli`** (adenda, punto 1). No se usa ni ese módulo ni `-m importlinter` (que da exit 1).
3. **Herramienta ausente → rojo con mensaje.** El mensaje nombra el directorio buscado y el comando exacto de instalación
   en ese intérprete (`<PY> -m pip install -e .[dev]`). Se implementa en `_lint_imports_cmd`/`steps()`; **`run()` no
   cambia** (ver Análisis, "Dónde vive el rojo").
4. **Búsqueda pura y testeable:** `find_lint_imports(scripts_dir, is_file)` recibe el directorio y la función de
   existencia; no lanza subprocesos ni lee el `PATH` ni `sysconfig`. Los nombres de Windows y de Linux se prueban en el
   **mismo test**, en cualquier SO (adenda, punto 3). Se prueba primero `lint-imports.exe` y después `lint-imports`, sin
   consultar el SO. Solo el llamador, en `steps()`, consulta `sysconfig`.
5. **"Contrato roto → rojo" es una mutación de auditoría, no un test permanente** (adenda, punto 2): MA4 abajo.
6. **Python por ruta** (`./venv/Scripts/python.exe …` en bash), nunca `python` a secas ni `activate` (precedente S1,
   decisión 8). Trinquete ADR-0005: 0 errores de ruff y de mypy en los dos archivos tocados (hoy ya están en 0).

## Análisis del redactor

**Comprobado hoy en `f62b7ba`.** El defecto descrito está en `scripts/check.py:48-53` (`which` + fallback); `:61` es su
único consumidor y `:141-147` es `run()`, que decide solo por el exit code. `:20` importa `shutil` solo para ese `which`.
`tests/test_check.py` tiene 24 tests verdes y ninguno toca `_lint_imports_cmd` ni `steps()`. `venv/Scripts` contiene
`lint-imports.exe` (e `import-linter.exe`). Los dos archivos tocados están en 0 de ruff, 0 de mypy y formateados; los
totales son ruff 60 y mypy 10. `scripts/check.py` está en `[tool.mypy].files`. La cobertura mide solo `app`, así que este
ítem no la mueve.

**Por qué `sysconfig.get_path("scripts")` (enmienda 1).** Es el directorio de los console scripts del intérprete en
ejecución. Mantiene el criterio de la adenda, "una herramienta por intérprete", y lo aplica al sitio donde pip la instala
de verdad. Medido el 3 nov:
- Venv: `sys.executable` = `C:\projects\ecotur-asoprado\venv\Scripts\python.exe` y `sysconfig` scripts =
  `C:\projects\ecotur-asoprado\venv\Scripts`. Coinciden. Esquema por defecto `venv`; `lint-imports.exe` existe ahí.
- Python global: `sys.executable` = `C:\Python314\python.exe` y `sysconfig` scripts = `C:\Python314\Scripts`. **Difieren**.
  Ese Python no tiene import-linter (`ModuleNotFoundError: No module named 'importlinter'`), así que el rojo con mensaje
  es lo correcto allí.

Con `Path(sys.executable).parent`, que era la propuesta de la adenda y queda descartada, el Python global de Windows
buscaría en el sitio equivocado. Además, en un venv POSIX dependería de no resolver el enlace simbólico de `bin/python`.
`sysconfig` no tiene ninguno de los dos problemas. En un venv POSIX devuelve `venv/bin` y en el Python del toolcache del
CI devuelve `<prefix>/bin`. `sysconfig.get_path` devuelve `str`, y `mypy --strict` acepta `Path(sysconfig.get_path("scripts"))`
(sondeado).

**Sondeo** (scripts en el scratchpad, sin tocar el repo) con la firma propuesta. Con el directorio de scripts del venv
devuelve `['…\venv\Scripts\lint-imports.exe']`. Con un `is_file` falso que solo acepta `lint-imports` devuelve
`\x\bin\lint-imports`: es el caso Linux, ejecutado en Windows. Con un directorio vacío cuyo nombre lleva un apóstrofo, el
sustituto sale con `rc 1` e imprime en stderr el directorio y `… -m pip install -e .[dev]`. `mypy --strict` acepta
`is_file: Callable[[Path], bool] = Path.is_file`.

**Dónde vive el rojo (evaluación pedida).** Hay cuatro formas de que "no encontrado" acabe en rojo:
- (a) **Elegida: comando sustituto en `_lint_imports_cmd`.** Devuelve `[PY, "-c", "import sys; sys.exit(<mensaje>)"]`.
  `sys.exit` con una cadena la escribe en stderr y sale con 1. El mensaje aparece dentro de la sección
  `=== import-linter ===`, `run()` lo marca `FALLA (exit 1)` con la misma regla que a los demás pasos, y `verdict` y
  `--soft imports` lo tratan como cualquier rojo. Coste: un `-c` de una línea que hay que explicar en el docstring.
- (b) `run()` acepta "comando o error". Ensancha el tipo de `steps()` y de `run()` para todos los pasos y toca `main`:
  justo el aumento de alcance que la verificación pide evitar.
- (c) Lanzar una excepción en `steps()`. Aborta la compuerta antes de correr nada y rompe el contrato de `verdict` ("every
  step has already run"). Además, `--soft imports` ya no podría tolerarlo.
- (d) Devolver la ruta esperada aunque no exista. `subprocess.call` lanza `FileNotFoundError`: traceback y compuerta
  abortada, sin mensaje útil.

Con (a), "un paso que no encuentra su herramienta sale en rojo" vale para todos los pasos sin tocar `run()`: los
`-m ruff|mypy|pytest` ya salen con 1 si falta el módulo (verificación, reproducción 5).

**Qué congela qué.** Los 24 tests actuales congelan `parse_soft`, `verdict`, `_soft_arg`, el import sin efectos y `main`
con `--soft` inválido, y no cambian. Los nuevos congelan:
1. Que el comando del paso es el mismo con y sin el venv en el `PATH`, que sale del directorio de scripts del intérprete
   y que nunca es el fallback `-m`. Es la reproducción del no-op.
2. Los dos nombres de plataforma.
3. Que la búsqueda no sale del directorio dado.
4. Que, si la herramienta está, se invoca directamente.
5. Que, si falta, el sustituto sale con 1 y da el mensaje, y que `run()` lo marca en rojo.

La rotura de un contrato la vigila MA4 (adenda, punto 2).

**Forma del RED** (sobre `f62b7ba`): el test 1 falla **por aserción** con el comando
`[PY, '-m', 'importlinter.cli', 'lint_imports']`, que es el no-op reproducido con un `PATH` sin el venv. Los tests 2 a 6
fallan con `AttributeError` (`find_lint_imports` no existe) o `TypeError` (`_lint_imports_cmd` hoy no acepta argumentos).
Salida esperada: `7 failed, 24 passed`.

**Portabilidad Linux.** El CI (`ubuntu-latest`, `UsePythonVersion@0`, `pip install -e .[test,dev]` sin venv) instala
`lint-imports` en el directorio de scripts del Python del toolcache, que es lo que devuelve `sysconfig.get_path("scripts")`
(`<toolcache>/x64/bin`). Encaja con el YAML y con el log del PR #74 (bitácora del 3 nov, l.219-222), pero ningún agente
puede leer el log del CI de este PR: lo confirma David (MD1). La única forma de que el CI no la encuentre es que pip
hubiera instalado en el esquema de usuario (`~/.local/bin`). En ese caso, `imports` no está en `--soft` y el CI saldría en
rojo con el directorio buscado en el mensaje: un fallo ruidoso, nunca silencioso.

**Riesgos.**
1. El CI: ver el párrafo anterior.
2. El hook formatea con el ruff del `PATH` (AF-06). Antes de la compuerta, el ejecutor corre
   `./venv/Scripts/python.exe -m ruff format` y `… ruff check --fix` sobre los dos archivos (precedente S1, riesgo e).
3. `docs/bitacora/2026-11-03.md` tiene cambios de David sin commitear y **no se añade** al commit: `git add` solo de los
   dos archivos de la fase.
4. Las mutaciones se aplican por Bash, nunca con Edit/Write, para no disparar el hook.

**Qué NO se toca.** `run()`, `main()`, `verdict`, `parse_soft`, `_soft_arg`, `STEP_KEYS`, los otros cinco pasos,
`_prepare_process`, `.azure-pipelines/`, `pyproject.toml`, `.claude/`, `AGENTS.md`, `scripts/check_docs.py` y `app/`.
Tampoco los documentos que citan la mitigación (`docs/deuda/S1/plan.md` decisión 8 y los handoffs históricos). La fila
AF-05, la bitácora y PLAN §3 los actualiza la sesión de cierre.

## Regla de alcance

- **Sí:** en `scripts/check.py`, `_lint_imports_cmd`, la nueva `find_lint_imports`, la constante `LINT_IMPORTS_NAMES`, la
  línea `import-linter` de `steps()` y los imports: sale `shutil`; entran `sysconfig` y `Callable`. En
  `tests/test_check.py`, una clase nueva, el import de `sysconfig` y `subprocess`, y el docstring del módulo.
- **No:** todo lo demás. Los hallazgos nuevos van a Residuales.

## Fases

**Protocolo de mutación** (no se commitea nada). Sustituye un texto exacto por Bash, corre los tests y restaura el
archivo byte a byte. Antes del `git add`, `git status --short` solo debe mostrar los dos archivos de la fase y
`docs/bitacora/2026-11-03.md`, que es de David y no se añade.

```bash
mut() { cp "$1" "$1.bak" && ./venv/Scripts/python.exe -c "import pathlib,sys; p=pathlib.Path(sys.argv[1]); s=p.read_text(encoding='utf-8'); assert sys.argv[2] in s, 'pattern not found'; p.write_text(s.replace(sys.argv[2], sys.argv[3], 1), encoding='utf-8')" "$1" "$2" "$3"; ./venv/Scripts/python.exe -m pytest -q -p no:cacheprovider "$4" 2>&1 | tail -1; mv "$1.bak" "$1"; }
NOVENV_PATH=$(echo "$PATH" | tr ':' '\n' | grep -v -i "ecotur-asoprado/venv" | paste -sd ':')
```

### Fase A — `lint-imports` desde el directorio de scripts del intérprete, o paso en rojo (única fase, la más pequeña)

- **Archivos:** `scripts/check.py`, `tests/test_check.py`.
- **Cambios exactos:**
  - `scripts/check.py`: se quita `import shutil` y se añaden `import sysconfig` y `from collections.abc import Callable`
    (el orden lo pone ruff). El `_lint_imports_cmd` actual (l.48-53) se sustituye por:
    ```python
    # Console script names of import-linter: a Windows install has the .exe, a POSIX one the bare name.
    LINT_IMPORTS_NAMES: tuple[str, ...] = ("lint-imports.exe", "lint-imports")


    def find_lint_imports(scripts_dir: Path, is_file: Callable[[Path], bool] = Path.is_file) -> Path | None:
        """Return the lint-imports console script installed in ``scripts_dir``, or None.

        Pure on purpose (the existence check is injected) so both platform names can be unit
        tested on any OS. Only ``scripts_dir`` is searched, never the PATH: the contracts must be
        checked by the import-linter of the interpreter that runs the gate (backlog AF-05).

        Args:
            scripts_dir: Where pip installs the running interpreter's console scripts
                (``sysconfig.get_path("scripts")``: ``venv/Scripts`` on Windows, ``bin`` on POSIX).
            is_file: Existence check; ``Path.is_file`` outside tests.

        Returns:
            The first path of ``LINT_IMPORTS_NAMES`` that exists in ``scripts_dir``, or None.
        """
        for name in LINT_IMPORTS_NAMES:
            candidate = scripts_dir / name
            if is_file(candidate):
                return candidate
        return None


    def _lint_imports_cmd(scripts_dir: Path, is_file: Callable[[Path], bool] = Path.is_file) -> list[str]:
        """Build the import-linter step: the console script, or a stand-in that fails loudly.

        There is no module fallback: the package's cli module only defines the click command, so
        running it exits 0 having checked nothing. When the script is missing, the stand-in
        prints what to install and exits 1, so ``run()`` marks the step red with the same
        exit-code rule as every other step.
        """
        exe = find_lint_imports(scripts_dir, is_file)
        if exe is not None:
            return [str(exe)]
        hint = (
            f"lint-imports not found in {scripts_dir}; install the dev extras in this interpreter: "
            f"{PY} -m pip install -e .[dev]"
        )
        return [PY, "-c", f"import sys; sys.exit({hint!r})"]
    ```
    y en `steps()` la línea del paso pasa a ser:
    ```python
    ("import-linter", _lint_imports_cmd(Path(sysconfig.get_path("scripts")))),
    ```
    Son exactos los nombres `LINT_IMPORTS_NAMES`, `find_lint_imports` y `_lint_imports_cmd`, sus firmas, el orden de los
    nombres, el llamador `Path(sysconfig.get_path("scripts"))`, el `-c` con `sys.exit` y el texto
    `-m pip install -e .[dev]`. La redacción de docstrings y comentarios es orientativa (inglés, Google Style), pero **no**
    debe contener `importlinter.cli` (Verificación final, paso 1). Si `ruff format` parte alguna firma o la línea de
    `steps()`, los grep y las mutaciones de abajo se aplican sobre el texto resultante. No cambia nada más del archivo.
  - `tests/test_check.py`: el docstring del módulo pasa a decir que cubre la política `--soft` (B-CI, ADR-0005) y la
    resolución de `lint-imports` (AF-05), y que no se ejecuta ningún paso real: el único subproceso es el sustituto de una
    herramienta ausente. Se añaden `import subprocess` e `import sysconfig` y, al final, `class TestLintImportsResolution`
    con `BIN = Path("/fake/bin")`.
- **Tests (RED primero)** (nombres exactos; se afirma sobre comandos, rutas, exit codes y booleanos; el único texto que se
  comprueba es el comando de instalación y una ruta, nunca prosa):
  1. `test_step_resolves_from_scripts_dir_regardless_of_path`: toma
     `with_path = dict(check.steps(no_tests=True))["import-linter"]`, hace `monkeypatch.setenv("PATH", str(tmp_path))` (un
     `PATH` sin el venv: el escenario de AF-05) y toma `without_path` de la misma forma. Aserciones:
     `"importlinter.cli" not in without_path`, `without_path[1:2] != ["-m"]`, `without_path == with_path` y
     `without_path == check._lint_imports_cmd(Path(sysconfig.get_path("scripts")))`.
  2. `test_finds_console_script_in_scripts_dir`, parametrizado sobre `name`: `"lint-imports.exe"` (id `windows`) y
     `"lint-imports"` (id `posix`). Aserción: `check.find_lint_imports(BIN, lambda p: p == BIN / name) == BIN / name`.
  3. `test_looks_only_inside_the_scripts_dir`: `is_file` registra cada ruta en una lista y devuelve `False`. El resultado
     es `None` y la lista es `== [BIN / "lint-imports.exe", BIN / "lint-imports"]` (ni `PATH` ni otros directorios).
  4. `test_found_tool_is_invoked_directly`:
     `check._lint_imports_cmd(BIN, lambda p: p.name == "lint-imports") == [str(BIN / "lint-imports")]`.
  5. `test_missing_tool_yields_failing_command_with_install_hint`: `cmd = check._lint_imports_cmd(tmp_path)`, sobre un
     directorio real y vacío y con el `is_file` por defecto. `cmd[:2] == [check.PY, "-c"]` y
     `"importlinter.cli" not in " ".join(cmd)`. `subprocess.run(cmd, capture_output=True, text=True, check=False)` da
     `returncode == 1`, `stdout == ""`, `str(tmp_path) in stderr` y `"-m pip install -e .[dev]" in stderr`.
  6. `test_missing_tool_makes_the_gate_step_red`: con `capfd`,
     `check.run("import-linter", check._lint_imports_cmd(tmp_path)) is False` y
     `str(tmp_path) in capfd.readouterr().err`.

  RED esperado sobre `f62b7ba` (pegar la salida en el handoff): `7 failed, 24 passed`. El 1 falla por aserción con
  `[PY, '-m', 'importlinter.cli', 'lint_imports']`, que es el no-op. Los demás fallan por `AttributeError` o `TypeError`.
  Son 6 funciones y 7 casos. Camino feliz: 2 y 4. Fallos: 5 y 6. Bordes: 1 (`PATH` sin venv) y 3 (no sale del directorio).
- **Mutaciones** (sobre la punta de la fase; pegar la última línea de cada una; cada una debe dar ≥ 1 failed o el rojo
  indicado):
  - MA1, se quita el nombre POSIX:
    `mut scripts/check.py '("lint-imports.exe", "lint-imports")' '("lint-imports.exe",)' tests/test_check.py`
    → falla `[posix]` (y también 3 y 4).
  - MA2, vuelve el fallback:
    `mut scripts/check.py 'return [PY, "-c", f"import sys; sys.exit({hint!r})"]' 'return [PY, "-m", "importlinter.cli", "lint_imports"]' tests/test_check.py`
    → fallan 5 y 6.
  - MA3, se busca fuera del directorio de scripts:
    `mut scripts/check.py '_lint_imports_cmd(Path(sysconfig.get_path("scripts")))' '_lint_imports_cmd(Path.cwd())' tests/test_check.py`
    → falla 1.
  - MA4, contrato roto (adenda, punto 2), con la compuerta y sin el venv en el `PATH`:
    ```bash
    cp app/services/user_service.py app/services/user_service.py.bak
    printf '\nimport fastapi  # AF-05 mutation\n' >> app/services/user_service.py
    env -u VIRTUAL_ENV PATH="$NOVENV_PATH" ./venv/Scripts/python.exe scripts/check.py --no-tests 2>&1 | sed -n '/=== import-linter ===/,/--- import-linter/p'; echo "exit ${PIPESTATUS[0]}"
    mv app/services/user_service.py.bak app/services/user_service.py && git status --short app/
    ```
    Esperado: `Los servicios no conocen el transporte HTTP BROKEN`, `Contracts: 3 kept, 1 broken.`,
    `--- import-linter: FALLA (exit 1)` y `exit 1`. Después, `git status --short app/` debe salir vacío.
- **Criterio de aceptación:**
  - `./venv/Scripts/python.exe -m pytest tests/test_check.py -q` → `31 passed`. La suite completa pasa de 369 a
    **376 passed** (+7), con 0 failed. Cobertura ≥ 94.81 %; no se mueve porque mide solo `app`.
  - La compuerta **sin el venv en el `PATH`** imprime los 4 contratos y `Contracts: 4 kept, 0 broken.` entre
    `=== import-linter ===` y `--- import-linter: OK`. Es el mismo caso que hoy da OK vacío. Comando:
    `env -u VIRTUAL_ENV PATH="$NOVENV_PATH" ./venv/Scripts/python.exe scripts/check.py --no-tests`.
  - Prueba de punta a punta con un intérprete sin la herramienta:
    `C:/Python314/python.exe scripts/check.py --no-tests 2>&1 | sed -n '/=== import-linter ===/,/--- import-linter/p'`.
    Debe mostrar la línea `lint-imports not found in C:\Python314\Scripts; … -m pip install -e .[dev]` y
    `--- import-linter: FALLA (exit 1)`. Los demás pasos también salen en rojo con ese Python, y es lo esperado: no tiene
    las dependencias. Si `C:\Python314` no existe en la máquina, se anota y el test 5 sirve de evidencia.
  - MA1-MA4 dan el rojo indicado y los archivos quedan restaurados: `git diff --stat` solo muestra los dos de la fase.
  - Trinquete: `ruff check` y `ruff format --check` sobre los dos archivos → 0 y OK;
    `./venv/Scripts/python.exe -m mypy scripts/check.py tests/test_check.py` → `Success`. Totales: ruff `Found 60
    errors.` y mypy `Found 10 errors in 5 files`.
  - `./venv/Scripts/python.exe scripts/check.py` → import-linter imprime `Contracts: 4 kept, 0 broken.`, docs ✔ y pytest
    376 ✔. Los rojos de ruff y mypy son heredados y no cambian.
- **Fuera de alcance de esta fase:** `run()`, `main()`, `verdict`, `--soft`, los otros pasos, el YAML del CI,
  `pyproject.toml`, `.claude/` (AF-06), `AGENTS.md` (AF-04), los documentos históricos que citan la mitigación y
  cualquier error heredado de ruff o mypy.
- **Paso posterior (David):** MD1 (abajo).
- **Commit:** el trailer `Co-Authored-By` lo añade la sesión ejecutora con su modelo; el resto es literal. Se prepara con
  `git add scripts/check.py tests/test_check.py`.
  ```
  fix(check): run lint-imports from the scripts dir or fail the step

  The import-linter step resolved its tool with shutil.which and, when
  lint-imports was not on PATH (the venv invoked by path without being
  activated, the workflow's mode since 2 Nov), fell back to
  python -m importlinter.cli lint_imports. That module only defines the
  click command and never runs it, so the step exited 0 having checked
  nothing and the gate reported the layer contracts as green (backlog
  AF-05). CI was unaffected: UsePythonVersion puts its bin dir on PATH.

  - scripts/check.py: find_lint_imports() looks for lint-imports.exe
    (Windows) or lint-imports (POSIX) only in the scripts directory of
    the interpreter that runs the gate, sysconfig.get_path("scripts"),
    where pip installs that interpreter's console scripts. It never
    searches PATH, so the contracts are checked by the import-linter
    installed with that interpreter. When it is missing, the step runs
    a stand-in that names the directory and the pip install -e .[dev]
    command and exits 1, so run() marks it red with the same exit-code
    rule as every other step. run(), verdict() and --soft are
    unchanged; the module fallback and the shutil import are gone and
    sysconfig is imported instead.
  - tests/test_check.py: the step resolves to the same command with and
    without the venv on PATH, from the scripts directory, and never to
    the module fallback (red before this change); both platform names
    are found through an injected existence check; the lookup never
    leaves the given directory; a missing tool yields exit 1 with the
    install hint and a red step.

  The other steps keep python -m: a missing module there already exits 1.
  ```

## Verificación final

```bash
# 1. Patrones de la verificación (esperado: vacío · vacío)
grep -n -E 'importlinter\.cli|shutil\.which' scripts/check.py
grep -rn -E 'importlinter\.cli|shutil\.which' scripts app alembic .claude .azure-pipelines pyproject.toml
# 2. Origen del directorio (esperado: 1 línea en steps() · vacío · vacío)
grep -n 'sysconfig.get_path("scripts")' scripts/check.py
grep -n -E 'Path\(PY\)\.parent|Path\(sys\.executable\)\.parent' scripts/check.py
grep -n 'shutil' scripts/check.py
# 3. Inventario (esperado: check.py con LINT_IMPORTS_NAMES/find_lint_imports/_lint_imports_cmd; tests/test_check.py
#    solo en aserciones negativas "importlinter.cli" not in ...; pyproject solo [tool.importlinter] y la dependencia)
grep -rn -E 'lint-imports|lint_imports|importlinter|shutil\.which' scripts .claude .azure-pipelines tests app alembic pyproject.toml
# 4. Reproducción del no-op: la compuerta sin el venv en el PATH (esperado: 4 contratos + "Contracts: 4 kept, 0 broken.")
NOVENV_PATH=$(echo "$PATH" | tr ':' '\n' | grep -v -i "ecotur-asoprado/venv" | paste -sd ':')
env -u VIRTUAL_ENV PATH="$NOVENV_PATH" ./venv/Scripts/python.exe scripts/check.py --no-tests 2>&1 | sed -n '/=== import-linter ===/,/--- import-linter/p'
# 5. Contrato roto → rojo: MA4 de la Fase A (la re-ejecuta el auditor y restaura byte a byte)
# 6. Nada fuera del alcance cambió desde la base (esperado: solo scripts/check.py, tests/test_check.py y docs/deuda/AF-05/)
git diff 217e58f --stat
# 7. Tests y trinquete (esperado: 31 passed · 0 · OK · Success · Found 60 errors. · Found 10 errors in 5 files)
./venv/Scripts/python.exe -m pytest tests/test_check.py -q
./venv/Scripts/python.exe -m ruff check scripts/check.py tests/test_check.py
./venv/Scripts/python.exe -m ruff format --check scripts/check.py tests/test_check.py
./venv/Scripts/python.exe -m mypy scripts/check.py tests/test_check.py
./venv/Scripts/python.exe -m ruff check . | grep -E '^Found'
./venv/Scripts/python.exe -m mypy | tail -1
# 8. Compuerta (línea base: 369 ✔ · 94.81 % · ruff ✘ 60 · mypy ✘ 10 · 4 KEPT). Esperado: 376 ✔ · 94.81 % · igual el resto
./venv/Scripts/python.exe scripts/check.py
```

**Paso manual de David** (ningún agente puede leer el log del CI):

- **MD1, en el PR de `item/af-05` a `develop`:** en Azure DevOps, abrir el log del paso "Compuerta de calidad
  (scripts/check.py)". Bajo `=== import-linter ===` deben aparecer los 4 contratos y `Contracts: 4 kept, 0 broken.` antes
  de `--- import-linter: OK`, y en el RESUMEN `✔ import-linter`. Si en su lugar aparece `lint-imports not found in
  <directorio>`, pip no instaló en el directorio de scripts del intérprete del CI (por ejemplo, porque instaló en el
  esquema de usuario). En ese caso no se mezcla y se replanifica. Pegar las líneas en la bitácora; la descripción del PR
  puede citarlas.

## Residuales

1. **`run()` sigue confiando solo en el exit code en todos los pasos.** Hoy basta: los `-m` dan exit 1 si falta el módulo
   y `check_docs.py` es un script del repo. Un paso futuro que se invoque con algo que "sale con 0 sin hacer nada"
   repetiría AF-05. Destino: una línea en la nota técnica de AF-05 al cierre ("un paso nuevo se prueba con su
   herramienta ausente"), sin fila nueva.
2. **Mitigación caducada en los documentos.** La fila AF-05 ("venv activo y línea `Contracts:` en cada handoff") y la
   decisión 8 del plan de S1 ("import-linter aparte con `lint-imports.exe`") dejan de hacer falta con el merge. El plan
   de S1 es histórico y no se edita. En el cierre, la fila AF-05 pasa a `Hecho` y la bitácora registra que caduca la
   regla "¿la línea base se midió con el venv en el `PATH`?" (bitácora del 3 nov, l.260-262).
3. **Salida de `check.py` en dos idiomas.** El mensaje nuevo está en inglés (AGENTS §4: código y salida de herramientas
   de desarrollo), mientras que `FALLA`, `Raíz del repo` y `RESUMEN` siguen en español. Es preexistente y cosmético.
   Destino: ninguno, salvo que David quiera unificarlo (fila `Sale → B-FUTURO`).

## Referencias

- **Context7 no estuvo disponible en esta sesión** (el subagente no tenía la herramienta MCP). Cada comportamiento se
  contrastó con el código y los metadatos **instalados** en el `venv` y con los sondeos del scratchpad. Para confirmarlo
  con Context7, las bibliotecas son `/seddonym/import-linter` y la documentación de CPython.
- import-linter · 2.15 · el único punto de entrada es la consola `lint-imports` (`entry_points.txt`); `cli.py` no tiene
  `__main__` · https://import-linter.readthedocs.io/en/stable/usage.html
- Python · 3.14.3 · `sysconfig.get_path("scripts")` (elegido: directorio de los console scripts del intérprete; esquema
  `venv` dentro de un venv) · https://docs.python.org/3.14/library/sysconfig.html#installation-paths
- Python · 3.14.3 · `sys.exit(<str>)`: imprime en stderr y sale con 1 · https://docs.python.org/3.14/library/sys.html#sys.exit
- Python · 3.14.3 · `venv`: scripts en `Scripts` (Windows) o `bin` (POSIX) · https://docs.python.org/3.14/library/venv.html
- Packaging · console scripts como entry points (`.exe` en Windows, sin extensión en POSIX) ·
  https://packaging.python.org/en/latest/specifications/entry-points/
- pytest · 9.0.2 · `monkeypatch.setenv` y `capfd` (captura la salida de subprocesos a nivel de descriptor) ·
  https://docs.pytest.org/en/stable/how-to/monkeypatch.html · https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html
- Azure Pipelines · `UsePythonVersion@0` (antepone al `PATH` el intérprete del toolcache y su directorio de scripts) ·
  https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/use-python-version-v0

**ADR propuesto: ninguno.** Es la corrección de un defecto de la compuerta, no un patrón, módulo ni contrato nuevo. "Una
herramienta por intérprete" es el mismo criterio que ADR-0001 ya aplica a ruff, mypy y pytest con `-m`. Las decisiones
(sin `which`, sin fallback, rojo con mensaje, mutación en lugar de test permanente) están registradas con autor y fecha
en la adenda de `verificacion.md`, y la del directorio de scripts en la sección siguiente. La única elección local, el
comando sustituto en lugar de cambiar `run()`, está justificada en el Análisis y se revierte sin coste.

## Enmiendas aprobadas antes de `/implementar` (David, 3 nov 2026)

David aprobó el plan con cinco cambios, que ya están aplicados en todo el cuerpo de arriba: resumen, decisiones,
análisis, cambios exactos, tests, mutaciones, Verificación final, MD1, Residuales, Referencias y commit.

1. **El directorio de búsqueda es `sysconfig.get_path("scripts")`, no `Path(PY).parent`** (decisión 1). La alternativa
   que la versión anterior del plan descartaba pasa a ser la elegida, con la misma evidencia más la medida de la sesión
   principal: en el venv, `sys.executable` y el directorio de scripts coinciden (`…\venv\Scripts`). En el Python global
   difieren (`C:\Python314` frente a `C:\Python314\Scripts`), y además ese Python no tiene `importlinter`
   (`ModuleNotFoundError`). El llamador en `steps()`, el test 1, la mutación MA3 y el grep 2 de la Verificación final se
   ajustan a ese origen. El parámetro de las dos funciones pasa a llamarse `scripts_dir`.
2. **Se elimina la antigua decisión 5** (`Path(PY).parent` sin `.resolve()` por el enlace simbólico de `bin/python` en
   POSIX): con `sysconfig` deja de aplicar. Las decisiones 6 y 7 pasan a ser la 5 y la 6.
3. **Desaparece el antiguo Residual 1** (la diferencia de directorios del Python global de Windows): `sysconfig` la
   cubre. Los demás se renumeran del 1 al 3.
4. **Los tests no cambian de forma:** la misma firma inyectada (directorio y función de existencia), las mismas 6 funciones
   y 7 casos, y el mismo RED esperado (`7 failed, 24 passed`). Solo cambia lo que depende del origen del directorio. Por
   coherencia con ese origen se renombran tres tests: el 1 pasa de `…_from_interpreter_dir_…` a
   `…_from_scripts_dir_…`; el 2, de `…_next_to_interpreter` a `…_in_scripts_dir`; y el 3, de
   `…_interpreter_directory` a `…_scripts_dir`.
5. **Subject del commit alineado con la decisión 1** (David, 3 nov 2026): pasa de `fix(check): run lint-imports from
   the interpreter dir or fail the step` a `fix(check): run lint-imports from the scripts dir or fail the step` (66
   caracteres). El cuerpo no cambia.
