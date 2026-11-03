# Verificación — AF-05: el paso import-linter de check.py es un no-op sin el venv en el PATH

**Veredicto:** confirmada
**Fuente del ítem:** docs/backlog.md (§E, fila AF-05, v1.12) + docs/deuda/S1/plan.md (Residuales, punto 1)
+ docs/bitacora/2026-11-03.md (l.52–62 apertura, l.219–223 dato del CI) + fila AF-02 punto 4 (retirado)
**Fecha:** 2026-11-03

## Qué describe el ítem
`scripts/check.py` resuelve el ejecutable de import-linter con `shutil.which("lint-imports")`; si no está en el
`PATH` (venv invocado por ruta sin activar), cae a `python -m importlinter.cli lint_imports`. Ese módulo solo
define el comando `click` y no lo invoca, así que el proceso sale con 0 sin analizar nada: el paso imprime OK
sin haber corrido. En el CI no ocurre porque `UsePythonVersion` pone el directorio de scripts en el `PATH`.

## Evidencia en el código
- `scripts/check.py:48-53` — el defecto, intacto desde `d822671` (25 oct, commit que creó la compuerta):
  ```python
  exe = shutil.which("lint-imports")
  if exe:
      return [exe]
  # Fallback: módulo del paquete (por si el venv no tiene el script en PATH).
  return [PY, "-m", "importlinter.cli", "lint_imports"]
  ```
  `lint_imports` va como argv del módulo; nadie lo lee.
- `scripts/check.py:61` — `("import-linter", _lint_imports_cmd())`: único paso que se resuelve con `which`.
- `scripts/check.py:141-147` — `run()` decide OK/FALLA **solo** por el exit code de `subprocess.call(cmd)`;
  no comprueba que la herramienta haya producido salida.
- `venv/Lib/site-packages/importlinter/cli.py:74,77` (import-linter 2.15, instalado) — `@click.command()` sobre
  `def lint_imports_command(**kwargs)`; `grep -n __main__` sobre el archivo: vacío. El paquete no tiene
  `__main__.py` (listado: `__init__.py adapters api.py application cli.py configuration.py contracts domain py.typed ui`).
  `cli.py:174` define además `def lint_imports(...)`, una función Python, no un subcomando.
- `venv/Lib/site-packages/import_linter-2.15*.dist-info/entry_points.txt` — los únicos puntos de entrada son las
  consolas `import-linter = importlinter.cli:import_linter` y `lint-imports = importlinter.cli:lint_imports_command`.
- `.azure-pipelines/ci-pipeline.yml:11,19-22,25,30` — `ubuntu-latest`, `UsePythonVersion@0` (3.14), `pip install -e
  .[test,dev]` sin venv y `python scripts/check.py --soft format,ruff,mypy`. Sin venv propio, los console scripts
  quedan en el `bin` del Python del toolcache, que `UsePythonVersion` antepone al `PATH` → `which` los encuentra.
  `imports` **no** está en `--soft`: en el CI un contrato roto sí bloquearía.
- `tests/test_check.py` — cubre `parse_soft`, `verdict`, `_soft_arg`, import sin efectos y `main` con `--soft`
  inválido (clases en l.25, 55, 80, 96, 113). **Ningún test** toca `_lint_imports_cmd` ni `steps()`.

### Reproducción (sin modificar código; salida literal)
1. Fallback a mano — exit 0 y salida vacía, incluso con un argumento inexistente:
   ```
   $ ./venv/Scripts/python.exe -m importlinter.cli lint_imports
   exit=0
   $ ./venv/Scripts/python.exe -m importlinter.cli --config no_existe.toml
   exit=0
   ```
2. Ejecutable real — corre los contratos:
   ```
   $ ./venv/Scripts/lint-imports.exe
   ...
   Capas: api -> services -> repositories -> models KEPT
   Los servicios no conocen el transporte HTTP KEPT
   Los repositorios solo conocen SQLAlchemy y los modelos KEPT
   Los modelos y los schemas no dependen de capas superiores KEPT

   Contracts: 4 kept, 0 broken.
   exit=0
   ```
3. **El fallback da verde con un contrato roto.** Config sintética en el scratchpad (fuera del repo) con un
   contrato `forbidden` `app.api` → `app.services`, que el código viola:
   ```
   $ ./venv/Scripts/lint-imports.exe --config <scratch>/broken_contract.toml --no-cache
   -   app.api.routers.service -> app.services.tourist_services_service (l.13)
   -   app.api.routers.user -> app.services.user_service (l.11)
   exit=1
   $ ./venv/Scripts/python.exe -m importlinter.cli lint_imports --config <scratch>/broken_contract.toml --no-cache
   exit=0
   ```
4. **La compuerta sin `venv/Scripts` en el PATH** (`env -u VIRTUAL_ENV PATH=<PATH sin .../venv/Scripts>
   ./venv/Scripts/python.exe scripts/check.py --no-tests`). Resolución previa en ese entorno:
   `which lint-imports = None` y `cmd = ['C:\\projects\\ecotur-asoprado\\venv\\Scripts\\python.exe', '-m',
   'importlinter.cli', 'lint_imports']`. Salida del paso, literal (no hay nada entre las dos líneas):
   ```
   === import-linter ===
   --- import-linter: OK en 0.2s
   ```
   y en el RESUMEN `✔ import-linter`. Control con el venv en el PATH: el mismo paso imprime los 4 contratos y
   `Contracts: 4 kept, 0 broken.` antes de `--- import-linter: OK en 0.2s`.
5. **El defecto es exclusivo de import-linter, no de la forma de invocar herramientas.** Los demás pasos usan
   `[PY, "-m", <mod>]` sin `which`: `python -m ruff|mypy|pytest --version` → exit 0 (tienen `__main__`), y un módulo
   ausente da exit 1 (`python -m modulo_inexistente` → exit=1), es decir, rojo, nunca verde silencioso. Dato útil:
   `python -m importlinter` (el paquete) también da exit 1 (`No module named importlinter.__main__; 'importlinter'
   is a package and cannot be directly executed`); el verde silencioso nace de apuntar a `importlinter.cli`, que sí
   es importable.

### Afirmación sobre el CI
Coherente con la definición del pipeline (ver arriba), pero el log no lo he leído yo: la evidencia de que en el
CI corre (`Contracts: 4 kept, 0 broken.` antes de `--- import-linter: OK en 0.2s` en el paso "Compuerta de
calidad" del PR #74) es de segunda mano (`docs/bitacora/2026-11-03.md:219-223`). Con el YAML actual, el CI no
entra al fallback salvo que el paso de instalación cambie (por ejemplo, un venv creado dentro del job e invocado
por ruta).

## Ficheros afectados (mapa completo)
- `scripts/check.py` — l.48-53 (resolución con `which` + fallback no-op), l.61 (único consumidor), l.141-147
  (`run` confía solo en el exit code).
- `tests/test_check.py` — sin cobertura de la resolución de herramientas; aquí iría el test que reproduce el no-op.
- `.azure-pipelines/ci-pipeline.yml` — no afectado hoy; define el escenario en que el defecto no se manifiesta.
- `AGENTS.md:60` — nombra `lint-imports` como parte de la compuerta (texto, no código; no requiere cambio).
- `docs/deuda/S1/plan.md:55` (decisión 8) y l.190, 287, 421 — mitigación vigente: correr
  `./venv/Scripts/lint-imports.exe` aparte. Dejará de ser necesaria tras el arreglo; no se edita en este ítem.

Sin ocurrencias de `lint-imports`, `importlinter` ni `shutil.which` en `app/`, `alembic/`, `.claude/` ni
`.opencode/agent|command`. `pyproject.toml:100-128` solo contiene la configuración `[tool.importlinter]`
(4 contratos), correcta.

## Rincones no mencionados por la fuente
- **`run()` no distingue "no corrió" de "pasó"** (`scripts/check.py:144-147`). La causa raíz es doble: el
  fallback apunta a un módulo que no ejecuta nada y la compuerta acepta exit 0 sin señal de trabajo hecho.
- **Riesgo latente de `which` primero:** si hubiera otro `lint-imports` antes en el `PATH` (Python global), la
  compuerta lo usaría con otro intérprete y otras dependencias. Hoy no existe: `C:\Python314\Scripts`,
  `C:\Program Files\Python312\Scripts` y `%APPDATA%\Python\Python312\Scripts` no tienen `lint-imports`. La
  corrección que propone la fila (buscar junto a `sys.executable` antes de `which`) lo cierra también.
- **Portabilidad del nombre:** en Windows el binario es `venv/Scripts/lint-imports.exe`; en el CI (Linux) es
  `<bin>/lint-imports` sin extensión, junto a `sys.executable`. Comprobado en local:
  `Path(sys.executable).parent.glob('lint-imports*')` → `['lint-imports.exe']`.
- **Registros históricos sin medir:** todo "4 KEPT" tomado de la compuerta con el venv sin activar no fue medido
  por ella (según la bitácora del 3 nov: SEC1, A9 y la verificación de S1). No se puede determinar desde el código
  qué handoffs corrieron así; ficheros que citan KEPT: `docs/deuda/{A9,AF-01,BE-01,S1,SEC1}/*`. Hoy, con el venv en
  el PATH, los 4 contratos están KEPT (línea base abajo), así que no hay rotura oculta en `develop`.
- `scripts/check_docs.py:543-578` usa `subprocess.run(["git", ...])` con `except FileNotFoundError: return None`:
  degradación consciente y documentada en el docstring, no el mismo patrón (no da verde por herramienta ausente
  en un paso de la compuerta). Fuera de alcance.

## Patrones de detección (copiables)
```bash
# El fallback y la resolución por PATH (debe quedar vacío tras el arreglo, salvo lo que el plan decida conservar)
grep -n -E 'importlinter\.cli|shutil\.which' scripts/check.py
# Cualquier otro uso en el repo
grep -rn -E 'lint-imports|lint_imports|importlinter|shutil\.which' scripts .claude .azure-pipelines tests app alembic pyproject.toml
# Reproducción del no-op (hoy exit=0 y salida vacía)
./venv/Scripts/python.exe -m importlinter.cli lint_imports; echo "exit=$?"
# La compuerta sin el venv en el PATH: el paso debe imprimir "Contracts: N kept, M broken." (o salir en rojo)
NOVENV_PATH=$(echo "$PATH" | tr ':' '\n' | grep -v -i "ecotur-asoprado/venv" | paste -sd ':')
env -u VIRTUAL_ENV PATH="$NOVENV_PATH" ./venv/Scripts/python.exe scripts/check.py --no-tests 2>&1 | sed -n '/=== import-linter ===/,/--- import-linter/p'
# Contrato roto sintético (config fuera del repo): el paso debe dar exit 1
./venv/Scripts/lint-imports.exe --config <ruta>/broken_contract.toml --no-cache; echo "exit=$?"
```

## Línea base (python scripts/check.py)
- Base develop: `217e58f` (`git fetch origin` OK; `git merge-base HEAD origin/develop` = `git rev-parse
  origin/develop` = `217e58f9e3846e6da70216881bf3be6c43182ab9`; rama `item/af-05`, árbol limpio).
- Comando: `./venv/Scripts/python.exe scripts/check.py` (desde la raíz; la sesión tenía `VIRTUAL_ENV` y
  `venv/Scripts` en el PATH, así que el paso import-linter **sí** corrió de verdad). Exit 1.
- Cabecera: `Raíz del repo: C:\projects\ecotur-asoprado · Python 3.14.3`

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
- pytest: `369 passed, 5 warnings in 18.15s` (0 failed).
- Cobertura total: `94.81%` (`Required test coverage of 92.0% reached. Total coverage: 94.81%`).
- ruff format: `52 files already formatted`. ruff check: `Found 60 errors.`
- mypy: `Found 10 errors in 5 files (checked 35 source files)`.
- import-linter: `Contracts: 4 kept, 0 broken.` (4 KEPT, 0 BROKEN), impreso antes de `--- import-linter: OK en 0.2s`.
- La compuerta ya falla antes de tocar nada (ruff check y mypy en rojo: deuda conocida, trinquete ADR-0005;
  coincide con lo esperado tras S1: ruff 60, mypy 10). Ni ruff ni mypy son objeto de este ítem.

## Conclusión para el planificador
- Resolver: que el paso import-linter de `scripts/check.py` ejecute de verdad la herramienta con independencia del
  `PATH` (buscarla junto a `sys.executable`, `Scripts\lint-imports.exe` en Windows y `bin/lint-imports` en POSIX,
  antes de `shutil.which`) y que, si no la encuentra, el paso salga en **rojo con mensaje**, sin ningún fallback a
  `-m importlinter.cli`. Test RED primero en `tests/test_check.py` que reproduzca el no-op (la resolución hoy
  devuelve `[PY, "-m", "importlinter.cli", "lint_imports"]` con un PATH sin el venv).
- Diseño testeable: la resolución debería ser una función pura (sin subprocess) que reciba el directorio del
  intérprete y/o un `which` inyectable, como ya se hizo con `parse_soft`/`verdict`; evita tests que dependan del
  PATH real de la máquina o del CI.
- No tocar: los pasos ruff/mypy/pytest (`-m` es correcto y falla en rojo si falta el módulo), `verdict`/`--soft`,
  el YAML del CI, `pyproject.toml`, `.claude/` (AF-06 y el hook son otro ítem), ni los 60 ruff / 10 mypy existentes.
- Riesgos: romper el CI si la búsqueda junto a `sys.executable` no contempla el nombre sin `.exe` en Linux; cambiar
  `run()` para todos los pasos amplía el alcance (si se decide exigir salida/señal, que sea solo para este paso y
  justificado). Comprobación final: la compuerta con PATH sin venv debe imprimir `Contracts: 4 kept, 0 broken.` y la
  reproducción 3 (contrato roto sintético) debe dar rojo con el comando que resuelva la compuerta.

## Adenda — decisiones de David antes de planear (3 nov 2026, sesión Mentor)

Resuelve lo que la conclusión deja abierto. El planificador las toma como dadas; lo demás (fases, tests, commits) es
suyo.

1. **Solo en el directorio de scripts del intérprete que corre la compuerta; sin `which`.** Ese directorio es el que
   devuelve `sysconfig.get_path("scripts")`: donde pip instala los console scripts de *ese* intérprete
   (`venv\Scripts\lint-imports.exe` en Windows, `venv/bin/lint-imports` en POSIX y en el toolcache del CI). Allí y en
   ningún otro sitio. Si no está, el paso sale en rojo con un mensaje que diga qué instalar en ese intérprete
   (`pip install -e .[dev]`). Razón: en el CI `lint-imports` también vive en ese directorio (`UsePythonVersion`), así
   que `which` no cubre ningún caso real del proyecto y sí abre el que la propia verificación nombra (un `lint-imports`
   de otro Python antes en el `PATH`, corriendo el contrato con otro intérprete). Una herramienta por intérprete, sin
   adivinar: el mismo criterio que ADR-0001 aplica a `ruff`, `mypy` y `pytest` con `-m`. Sin fallback a
   `-m importlinter.cli`.
   *Corrección del 3 nov, 16:10:* la primera redacción decía "junto a `sys.executable`" y el plan la llevó a
   `Path(sys.executable).parent`, que coincide con `sysconfig` en todos los modos del proyecto pero no en un Python
   global de Windows (`C:\Python314` frente a `C:\Python314\Scripts`, comprobado por el planificador). Se fija
   `sysconfig.get_path("scripts")` porque expresa la intención (la herramienta de este intérprete) con la API que la
   define, y hace innecesario el cuidado con `.resolve()` y el symlink de `venv/bin/python` en POSIX (`sysconfig`
   responde por `sys.prefix`, no por la ruta del binario). La función pura sigue recibiendo el directorio y la función
   de existencia; solo cambia quién le pasa el directorio.
2. **"Contrato roto → rojo" es mutación de auditoría, no test permanente.** Un test que rompa un contrato de capas
   tendría que meter un import prohibido en `app/`; eso no entra en la suite. Va como mutación del auditor (import
   temporal entre capas, compuerta en rojo, archivo restaurado byte a byte), como MA1–MA4 de S1. El test permanente es
   el del no-op (`tests/test_check.py`): intérprete sin la herramienta → el comando resultante no es `-m
   importlinter.cli` y el paso falla con mensaje.
3. **El nombre sin `.exe` se prueba en test, no "lo comprobará el CI".** La función pura recibe el directorio del
   intérprete (y la función de existencia) y devuelve el candidato correcto para Windows y para Linux; dos casos en el
   mismo test, sin necesitar Linux. El CI verde es confirmación, no la prueba.
