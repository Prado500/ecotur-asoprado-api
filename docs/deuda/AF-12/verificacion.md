# Verificación — AF-12: la compuerta no puede depender de un `.exe` de pip

**Veredicto:** confirmada
**Fuente del ítem:** docs/backlog.md (fila `AF-12`, l.180) + bitácora `docs/bitacora/2026-11-09.md` (secciones
"Falso positivo de R7…", último punto, y "AF-12: la compuerta no puede depender de un `.exe`"). Antecedente:
fila `AF-05` (l.174) y `docs/deuda/AF-05/`.
**Fecha:** 2026-11-09

## Qué describe el ítem
`scripts/check.py` ejecuta el paso import-linter como **binario** (`venv/Scripts/lint-imports.exe`, el lanzador
que genera pip, localizado por `find_lint_imports` desde AF-05), mientras ruff, mypy y pytest van como
`[PY, "-m", …]`. Smart App Control de Windows bloquea ese lanzador (`OSError: [WinError 4551]`), el paso revienta,
la compuerta no termina y en la máquina de David no se puede medir ninguna línea base ni fase. Salida propuesta
por el ítem: llamar al entry point registrado `importlinter.cli:lint_imports_command` con el mismo intérprete y
conservar la regla de AF-05 (herramienta ausente → rojo, nunca verde vacío).

## Evidencia en el código
- `scripts/check.py:50` — `LINT_IMPORTS_NAMES: tuple[str, ...] = ("lint-imports.exe", "lint-imports")`: nombres del
  lanzador de consola que se busca.
- `scripts/check.py:53-74` — `find_lint_imports(scripts_dir, is_file)`: devuelve la ruta del `.exe` en el directorio
  de scripts del intérprete.
- `scripts/check.py:77-101` — `_lint_imports_cmd`: si lo encuentra, `return [str(exe)]` (l.96), es decir, ejecuta el
  `.exe` directamente; si no, sustituto `[PY, "-c", "import sys; sys.exit(<hint>)"]` (l.97-101).
- `scripts/check.py:109` — `("import-linter", _lint_imports_cmd(Path(sysconfig.get_path("scripts"))))`: único paso
  de `steps()` que no empieza por `PY`.
- `scripts/check.py:106-108,110,116` — los otros cinco pasos sí empiezan por `PY` (`-m ruff`, `-m mypy`,
  `scripts/check_docs.py`, `-m pytest`).
- `scripts/check.py:189-195` — `run()` hace `subprocess.call(cmd)` sin capturar `OSError`: un ejecutable bloqueado no
  marca el paso en rojo, **aborta la compuerta entera** sin RESUMEN y sin correr check_docs ni pytest. Medido en la
  línea base (traceback abajo, `check.py:192` → `OSError: [WinError 4551]`).
- `scripts/check.py:22` — `import sysconfig`, que solo usa la l.109.
- `tests/test_check.py:140-191` — `TestLintImportsResolution` (7 casos de AF-05) fija el mecanismo actual:
  - `:145-156` `test_step_resolves_from_scripts_dir_regardless_of_path`: afirma `"importlinter.cli" not in without_path`
    (l.153), `without_path[1:2] != ["-m"]` (l.154) y que el comando es `_lint_imports_cmd(Path(sysconfig.get_path("scripts")))` (l.156).
  - `:158-160` `test_finds_console_script_in_scripts_dir` (parametrizado `windows`/`posix`), `:162-170`
    `test_looks_only_inside_the_scripts_dir`, `:172-174` `test_found_tool_is_invoked_directly` (`cmd == [str(BIN / "lint-imports")]`).
  - `:176-185` `test_missing_tool_yields_failing_command_with_install_hint`: afirma `"importlinter.cli" not in " ".join(cmd)` (l.180).
  - `:187-191` `test_missing_tool_makes_the_gate_step_red`: el test "herramienta ausente → rojo" que exige AGENTS §6.
- `tests/test_check.py:1-5,14` — docstring del módulo ("resolution of the lint-imports console script (AF-05)") e
  `import sysconfig`.
- `venv/Lib/site-packages/import_linter-2.15.dist-info/entry_points.txt:3` — `lint-imports = importlinter.cli:lint_imports_command`
  (confirma el entry point que cita el ítem; import-linter 2.15).
- `venv/Lib/site-packages/importlinter/cli.py:51-71,74-79` — `lint_imports_command` es un `click.command` que llama a
  `_run_check`, y este termina en `sys.exit(exit_code)` (l.71) con el resultado de `lint_imports`.
- Pruebas directas (solo lectura, 9 nov, esta máquina):
  - `./venv/Scripts/lint-imports.exe --help` → exit 126 (bloqueado).
  - `./venv/Scripts/python.exe -c "from importlinter.cli import lint_imports_command; lint_imports_command()"` →
    4 contratos `KEPT`, `Contracts: 4 kept, 0 broken.`, exit 0. **El mecanismo propuesto no está bloqueado aquí.**
  - `C:/Python314/python.exe -c "from importlinter.cli import lint_imports_command; lint_imports_command()"` →
    `ModuleNotFoundError: No module named 'importlinter'`, exit 1: la regla de AF-05 (ausente → rojo) se cumple sin sustituto.

## Ficheros afectados (mapa completo)
- `scripts/check.py` — l.22, 49-101, 109: mecanismo binario de import-linter (núcleo de la deuda); l.189-195 `run()`
  sin manejo de `OSError` (por qué el bloqueo tumba la compuerta entera en vez de un paso).
- `tests/test_check.py` — l.1-5, 14, 140-191: los 7 casos de AF-05 fijan el mecanismo binario; l.153 y l.180 afirman
  explícitamente que `importlinter.cli` **no** aparece en el comando, así que la corrección los invierte por diseño.
- `AGENTS.md:76-77` — "cada paso corre con `sys.executable` y busca sus herramientas en el directorio de scripts de ese
  intérprete (AF-05, 3 nov)": describe el mecanismo que AF-12 retira. Solo lo edita un humano por PR.
- `docs/CONTEXT.md:181-182` — "Desde el 3 nov (AF-05) la compuerta local busca `lint-imports` en el directorio de scripts
  del intérprete y sale en rojo si no está": queda desfasado tras la corrección.
- `docs/backlog.md:174` (fila AF-05) — histórico; no se toca, AF-12 lo supera.

Sin efecto (comprobado): `.azure-pipelines/ci-pipeline.yml:19-31` (Ubuntu, `python scripts/check.py --soft
format,ruff,mypy`; el paso imports es estricto y seguirá siéndolo, pero el mecanismo cambia también ahí);
`pyproject.toml:41,104-136` (dependencia `import-linter>=2.1` y contratos, sin cambios); `Dockerfile` (sin referencias);
`.claude/hooks/ruff_on_edit.py:26-28` (ya usa `[sys.executable, "-m", "ruff", …]`); `scripts/check_docs.py:623,648`
(lanza `git`, ejecutable del sistema, no un lanzador de pip); `app/`, `alembic/` (sin referencias).

## Rincones no mencionados por la fuente
1. **`run()` no tolera un ejecutable que no arranca** (`scripts/check.py:192`): la fuente dice "la compuerta no termina",
   pero no señala que la causa es que `subprocess.call` lanza `OSError` sin capturar. Tras AF-12 el paso import-linter ya
   no lanzará un `.exe`, pero cualquier paso cuyo primer elemento no pueda ejecutarse (p. ej. `PY` inexistente) seguiría
   abortando sin RESUMEN. Es residual de diseño, no parte necesaria de AF-12.
2. **`[PY, "-m", "ruff"]` también ejecuta un `.exe` del directorio de scripts.** `venv/Lib/site-packages/ruff/__main__.py:10,17`
   llama a `find_ruff_bin()`, que busca `ruff.exe` en `sysconfig.get_path("scripts")` (`ruff/_find_ruff.py:14-18`) y lo
   lanza con `subprocess.run`. La afirmación del ítem "ruff, mypy y pytest corren como `[PY, "-m", …]`" es cierta en
   la forma, pero ruff sigue dependiendo de `venv/Scripts/ruff.exe`. Diferencia relevante: ese `.exe` es el binario nativo
   publicado por Astral dentro del wheel (idéntico en toda instalación de la misma versión), no un lanzador generado por pip
   con la ruta del venv embebida; hoy corre en esta máquina (paso `ruff format --check` OK en la línea base). Afecta a los
   pasos `ruff format --check`, `ruff check`, `--fix` (`check.py:211-212`) y al hook `.claude/hooks/ruff_on_edit.py:27-28`.
   No se pudo comprobar su firma Authenticode (consulta denegada por permisos en esta sesión). mypy y pytest con `-m` son
   Python puro.
3. **Docs que describen el mecanismo** (`AGENTS.md:76-77`, `docs/CONTEXT.md:181-182`): no los cita la fila; quedarán
   inexactos tras la corrección.

## Patrones de detección (copiables)
```bash
# El paso import-linter como binario (debe desaparecer)
git grep -n -E 'lint-imports\.exe|LINT_IMPORTS_NAMES|find_lint_imports|_lint_imports_cmd' -- scripts tests
# Pasos de steps() que no empiezan por el intérprete (debe quedar vacío salvo la línea de la lista)
grep -n -E '^\s+\("[^"]+", \[' scripts/check.py | grep -v '\[PY'
grep -n -E '_lint_imports_cmd\(|sysconfig\.get_path\("scripts"\)' scripts/check.py
# Tests que fijan el mecanismo binario o prohíben el entry point
grep -n -E '"importlinter\.cli" not in|lint-imports\.exe|find_lint_imports|sysconfig' tests/test_check.py
# Docs que describen el mecanismo
grep -n -E 'directorio de scripts|busca .lint-imports.' AGENTS.md docs/CONTEXT.md
# Comprobación funcional del mecanismo propuesto y de la regla de AF-05
./venv/Scripts/python.exe -c "from importlinter.cli import lint_imports_command; lint_imports_command()"; echo "exit $?"   # 4 kept, exit 0
C:/Python314/python.exe -c "from importlinter.cli import lint_imports_command; lint_imports_command()"; echo "exit $?"     # ModuleNotFoundError, exit 1
```

## Línea base (`scripts/check.py` con el Python del venv por ruta, AGENTS §6)
- Base develop: `bb03f46` (`git fetch origin` OK; `git merge-base HEAD origin/develop` = `git rev-parse origin/develop`
  = `bb03f46343f8dd6f7d0838f58fffe43f28e039b4`; la rama solo añade `4aff920`, docs).
- Comando: `./venv/Scripts/python.exe scripts/check.py` → **exit 1, la compuerta ya falla antes de tocar nada y no
  termina**: revienta en el paso import-linter, sin bloque RESUMEN.

```
Raíz del repo: C:\projects\ecotur-asoprado · Python 3.14.3

=== ruff format --check ===
57 files already formatted
--- ruff format --check: OK en 0.3s

=== ruff check ===
… (8 × I001 Import block is un-sorted or un-formatted)
Found 8 errors.
--- ruff check: FALLA (exit 1) en 0.1s

=== mypy ===
… (9 × [arg-type] "str | None": app\db\database.py:11, app\core\security.py:71,87,
   app\services\user_service.py:124, app\api\dependencies.py:95, tests\test_user_service.py:105,203,280,298)
Found 9 errors in 5 files (checked 53 source files)
--- mypy: FALLA (exit 1) en 1.6s

=== import-linter ===
Traceback (most recent call last):
  File "C:\projects\ecotur-asoprado\scripts\check.py", line 230, in <module>
    sys.exit(main(sys.argv[1:]))
  File "C:\projects\ecotur-asoprado\scripts\check.py", line 213, in main
    results = {name: run(name, cmd) for name, cmd in steps(no_tests)}
  File "C:\projects\ecotur-asoprado\scripts\check.py", line 192, in run
    code = subprocess.call(cmd)
  File "C:\Python314\Lib\subprocess.py", line 395, in call
  File "C:\Python314\Lib\subprocess.py", line 1038, in __init__
  File "C:\Python314\Lib\subprocess.py", line 1552, in _execute_child
    hp, ht, pid, tid = _winapi.CreateProcess(executable, args,
OSError: [WinError 4551] An Application Control policy has blocked this file
```

- RESUMEN: **no se imprime** (la compuerta aborta).
- ruff: 8 errores (todos I001). mypy: 9 errores en 5 archivos. Ambos son la deuda conocida de A4/BE-32 (CONTEXT §5,
  trinquete ADR-0005), ajena a AF-12.
- Contratos KEPT/BROKEN: **no medidos por la compuerta** (el paso revienta). Medición complementaria fuera de la
  compuerta con el mecanismo propuesto: `./venv/Scripts/python.exe -c "from importlinter.cli import lint_imports_command; lint_imports_command()"`
  → `Contracts: 4 kept, 0 broken.`, exit 0.
- pytest y cobertura: **no medidos por la compuerta**. Medición complementaria con el comando exacto del paso:
  `./venv/Scripts/python.exe -m pytest -q --cov=app --cov-report=term-missing:skip-covered` → **548 passed, 0 failed**
  (5 warnings), `TOTAL 943 23 138 19 96.11%`. Cobertura: **96.11 %**.
- check_docs complementario: `./venv/Scripts/python.exe scripts/check_docs.py` → exit 0, "Documentación coherente".

## Conclusión para el planificador
El plan debe cambiar **solo el mecanismo** del paso import-linter en `scripts/check.py` (l.49-101 y 109) a
`[PY, "-c", "from importlinter.cli import lint_imports_command; lint_imports_command()"]`, y rehacer
`TestLintImportsResolution` en `tests/test_check.py` (l.140-191): l.153 y l.180 hoy **prohíben** `importlinter.cli` en el
comando y deben invertirse; los casos de `find_lint_imports` desaparecen con la función. Debe conservar un test que corra
el paso con la herramienta ausente y lo vea en rojo (AGENTS §6; sirve un intérprete o `sys.path` sin `importlinter`,
p. ej. `-S`, que no carga site-packages, o un intérprete sin dev extras), y repetir el mutante MA4 de AF-05 (`docs/deuda/AF-05/plan.md:241-249`) para
probar que click propaga `Contracts: 3 kept, 1 broken.` → exit 1. Ojo: el hint de instalación (`pip install -e .[dev]`)
se pierde si el sustituto se retira; decidir si basta el `ModuleNotFoundError`. NO tocar `run()`/`OSError` (rincón 1),
ruff vía `ruff.exe` (rincón 2) ni el CI: son residuales para `B-FUTURO`. `AGENTS.md:76-77` y `docs/CONTEXT.md:181-182`
quedan desfasados; AGENTS solo por PR humano. Riesgo: la línea base debe tomarse ya con el paso nuevo, porque hoy la
compuerta no produce RESUMEN ni medición de contratos en esta máquina.

## Adenda — decisiones de David antes de planear (9 nov 2026, 15:01, sesión Mentor)

Resuelve lo que la conclusión deja abierto. El planificador las toma como dadas; lo demás (fases, tests, commits) es
suyo. Regla del verificador: no reescribir, añadir. Texto de David sobre el alcance: «quiero hacer AF-13 de una vez […]
es mala idea dejar abierta una puerta que se puede cerrar en nuestra cara sin previo aviso».

1. **Veredicto aceptado: confirmada. Línea base aceptada por medición complementaria.** Sobre `bb03f46` (=
   `origin/develop`; `4aff920` encima solo toca `docs/`): 548 passed · 96,11 % · ruff 8 (I001, A4) · mypy 9 (`str | None`, A4) ·
   `Contracts: 4 kept, 0 broken.` · `check_docs` exit 0. Son las mismas cifras de PLAN §6 del 7 nov sobre `a7991a4` y el código
   de `app/`, `tests/` y `scripts/` no cambió desde entonces. El ejecutor mide "antes" sabiendo que la compuerta aborta en
   import-linter sin RESUMEN: **eso es el defecto, no un retroceso**. El criterio de aceptación de cada fase es la compuerta
   **completa, con RESUMEN**, con estas mismas cifras (ruff 8 y mypy 9 por el trinquete de ADR-0005; cobertura y contratos
   no bajan).
2. **Mecanismo (fase A):** el paso import-linter pasa a `[PY, "-c", "from importlinter.cli import lint_imports_command;
   lint_imports_command()"]`, como los otros tres pasos (`check.py:106-116`). Se retiran `LINT_IMPORTS_NAMES` y
   `find_lint_imports` (`check.py:50-74`). **El hint de instalación se conserva, explícito y en Python normal** (David,
   15:12): `_lint_imports_cmd` deja de buscar el `.exe` y pregunta `importlib.util.find_spec("importlinter")` en el
   intérprete que corre la compuerta; si el módulo está, devuelve el comando del entry point; si no, el sustituto que ya
   existe (`check.py:97-101`: `[PY, "-c", "import sys; sys.exit('… pip install -e .[dev]')"]`), que sale en rojo con el
   mensaje. Nada de lógica dentro de la cadena del `-c`.
3. **Tests de la fase A:** `TestLintImportsResolution` (`tests/test_check.py:140-191`) se rehace; `:153` y `:180` se
   invierten (`"importlinter.cli" in …`). Dos caminos de herramienta ausente, los dos en rojo (AGENTS §6): (a) `find_spec`
   devuelve `None` (monkeypatch) → el comando es el sustituto con hint y, ejecutado, sale 1 con el texto `pip install`; (b) el
   módulo está al construir el comando pero no al ejecutarlo: el comando real del entry point corrido con `sys.executable -S`
   (sin `site-packages`) → `ModuleNotFoundError`, exit ≠ 0. El mutante **MA4** de AF-05 (`docs/deuda/AF-05/plan.md:241-249`:
   contrato roto real → `Contracts: 3 kept, 1 broken.`) se repite y debe dar exit 1 y paso en rojo: es la prueba de que
   `importlinter/cli.py:71` propaga el código.
4. **Rincón 1 entra como fase B, con fila propia: AF-13** (creada hoy en el backlog, `Entra · B-TESTS`; se salda en este
   ítem, precedente `docs/deuda/BE-01/` con P1 y A7). `run()` (`check.py:189-195`) envuelve `subprocess.call(cmd)` en
   `try/except OSError`: imprime el error, marca el paso `FALLA` y devuelve `False`; los pasos siguientes corren y el RESUMEN
   se imprime con exit 1. Test RED primero: `run("x", ["<binario inexistente>"])` hoy lanza `FileNotFoundError` (subclase de
   `OSError`); después devuelve `False`, y un test de `main`/RESUMEN comprueba que la salida contiene el resumen con ese paso
   en rojo. Mismos dos archivos que la fase A. **Rincón 2 no tiene arreglo en el repo** (`ruff.exe` es el binario propio
   de ruff, firma sin comprobar; si una política lo bloquea, con AF-13 la compuerta lo dirá en rojo en vez de morir): nota
   en la fila AF-13, nada en el código.
5. **Documentos desfasados:** `AGENTS.md:76-77` y `docs/CONTEXT.md:181-182` los edita David en un commit propio dentro del
   PR de este ítem (precedente AF-04): «cada paso corre con `sys.executable` e **importa** su herramienta de ese intérprete
   (`-m` o entry point; AF-05 y AF-12); con otro intérprete la compuerta sale en rojo, no mide otra cosa». **La "regla que
   falta" para AGENTS §6** (qué hacer cuando la compuerta aborta sin RESUMEN) **no se escribe**: con AF-13 la compuerta no
   puede abortar sin RESUMEN; un mecanismo, no prosa (ADR-0001). **Además, en AGENTS §8** (l.91-92, "el estado del ítem es lo
   que existe en esa carpeta"), una frase que haga explícito lo que BE-01 dejó implícito con P1 y A7 (David, 15:12): «Una fila
   del backlog puede saldarse como fase del ítem de otra cuando la verificación de este la midió y comparten archivos; la fila
   lo dice (`Hecho (PR de <ID>, fase X)`), la carpeta es una y el PR es uno». Es la razón por la que AF-13 vive en
   `docs/deuda/AF-12/` y no en una carpeta propia.
6. **Alcance y tamaño:** dos fases, dos archivos (`scripts/check.py`, `tests/test_check.py`), más el commit de documentos de
   David; nada en el CI ni en `.claude/`. Fuera: cualquier otro paso o herramienta.
