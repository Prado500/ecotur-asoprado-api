# Verificación — AF-01: reglas de ADR-0008 en `scripts/check_docs.py`

**Veredicto:** confirmada
**Fuente del ítem:** docs/backlog.md §E (fila `AF-01`, línea 141) + `docs/PLAN.md` §2b (fila `B-CHECK-DOCS`, línea 48)
+ ADR-0008 punto 6 y addendum "Punto 3, mecanismo provisional" + `docs/deuda/AF-01/especificacion.md` (commit `ca9a71e`)
**Fecha:** 2026-11-01

## Qué describe el ítem

`scripts/check_docs.py` (paso "docs (coherencia)" de `scripts/check.py`) solo tiene 4 reglas y ninguna de las que
ADR-0008 punto 6 le encarga: días de cronograma fuera de PLAN §3 (incluido PLAN mismo fuera de §3), fecha de entrega en
PLAN igual a CONTEXT §2, bloque citado definido en §2b (en todo el alcance), encabezado de versión (ADR-0007), fila de
PLAN §3 cerrada sin marca, `--copias` por dueño y copia de hecho duro sin cita. Además la regla de la columna Decisión
(`DECISION_RE`) deja pasar cualquier cola tras el bloque, por lo que una fila pudo estar en dos bloques (BE-08, 31 oct).
La especificación del 1 nov (misma carpeta) fija R1–R9 y los cambios transversales; este documento verifica que la deuda
existe tal como se describe y mide la línea base.

## Evidencia en el código

- `scripts/check_docs.py:3-12` — el docstring enumera exactamente 4 reglas (comandos, "día N" en backlog/CONTEXT,
  bloques, Decisión). No hay ninguna de las siete reglas nuevas del ítem.
- `scripts/check_docs.py:24-25` — `REPO_ROOT = Path(__file__)...; os.chdir(REPO_ROOT)` al importar. Las reglas no
  reciben `root`; no se pueden ejecutar sobre fixtures (especificación §0.5).
- `scripts/check_docs.py:32-33` — `def read(p: str)` lee rutas relativas al cwd; rutas literales en `:37-38`, `:53`,
  `:63`, `:65`, `:83`, `:106`.
- `scripts/check_docs.py:52-59` — `rule_no_days`: solo `docs/backlog.md` y `docs/CONTEXT.md`; regex `\bdías? [0-9]`.
  No cubre días de la semana (`lun 2`, `sáb 31`), ni `docs/sesiones/*.md`, ni PLAN fuera de §3. Es lo que el ADR-0008
  (Contexto, línea 20-21) llama "verificar el síntoma y no el principio".
- `scripts/check_docs.py:62-69` — `rule_blocks`: alcance `backlog`, `CONTEXT`, `PLAN`; falta `docs/sesiones/*.md`
  (ADR-0008 punto 7 incluye `docs/sesiones/` en el alcance).
- `scripts/check_docs.py:72-74` — `DECISION_RE = ^\*\*(Entra · `B-…`|Sale → `B-FUTURO`|Decidir en `B-…`|Hecho \().*\*\*$`.
  El `.*` acepta cualquier cola. Comprobado ejecutando el regex actual sobre los casos "debe fallar" de la
  especificación §2 R4: aceptan (True) `**Entra · \`B-ORDEN\` (backend) y \`B-FE-RESERVAS\` (cliente)**`,
  `**Decidir en \`B-HIGIENE\` (verificar lo que existe; luego \`B-FUTURO\`)**`, `**Entra · \`B-X\` (a) (b)**`,
  `**Hecho (ADR-0003; re-verificación en \`B-TESTS\`)**` y `**Entra · \`B-X\` cualquier cola libre**`. Solo rechaza
  `**Hecho**` y la celda sin negrita.
- `scripts/check_docs.py:77-101` — `rule_decisions`: particiona celdas por ` | ` y localiza la columna por el
  encabezado. Hoy hay 4 tablas con columna `Decisión` en el backlog (A, A2, B, E), como dice la especificación.
- `scripts/check_docs.py:104-130` — `estado()`: `:118` busca `"current_target"\s*:\s*"([^"]+)"`; con `null` no hay
  comillas → `objetivo: ?`. Salida real hoy: `BE-01: verificado → planeado → en ejecución (objetivo: ?) → handoffs: …`
  aunque `docs/deuda/BE-01/progress.json:3` es `"current_target": null` y las cuatro fases están `completed`
  (CONTEXT §8 punto 4: "`--estado` no distingue mezclado").
- `scripts/check_docs.py:133-148` — `main()` solo reconoce `--estado`; no hay `--root`, `--copias`, `--huerfanas` ni
  `--cierre`. Cualquier flag desconocido se ignora en silencio: `python scripts/check_docs.py --copias` imprime el
  mensaje de éxito de las 4 reglas y devuelve exit 0 (comprobado hoy con `--copias`, `--huerfanas` y `--cierre`).
- `scripts/check_docs.py` (todo el archivo) — no existe `rule_deadline`, `rule_version_header`,
  `rule_closed_days_marked`, `strip_citations`, `sections` ni `lines_outside` (grep sin resultados; ver patrones).
- `tests/` — no existe `tests/test_check_docs.py`; `grep -rl "check_docs" tests/ app/ alembic/` devuelve vacío. El
  script no tiene ningún test.
- `pyproject.toml:90` — `[tool.mypy] files = ["app"]`: `scripts/check_docs.py` no está bajo mypy.
  `pyproject.toml:135` — `[tool.coverage.run] source = ["app"]` (la especificación decide no cambiarlo).
  `pyproject.toml:58-61` — `[tool.ruff]` sin excluir `scripts/`: ruff sí lo lee (confirmado: el archivo actual no
  figura entre los 362 errores ni entre los 27 sin formatear).
- `scripts/check.py:50` — `("docs (coherencia)", [PY, "scripts/check_docs.py"])`: la integración en la compuerta ya
  existe; hoy ese paso está en verde con las 4 reglas actuales.
- `.azure-pipelines/ci-pipeline.yml` — el CI ejecuta solo `pytest -v`; ni `check.py` ni `check_docs.py` (es
  `B-CI`, fuera de este ítem).
- `docs/adr/0008-copias-derivadas-con-cita-al-dueno.md:56-62` — punto 6: lista las reglas que debe tener el script y
  declara el `grep` manual como mecanismo provisional "hasta que esas reglas existan". `:104-105` (addendum):
  "`scripts/check_docs.py` todavía no detecta copias sin cita ni lista citas por dueño".
- `docs/adr/0007-versionado-de-documentos-vivos.md:56` — "Mitigación mecánica posible: `scripts/check_docs.py`
  comprueba que la [versión…]" (regla R6, hoy inexistente).
- `docs/sesiones/README.md:41` — paso 3 del ritual de cierre: "`scripts/check_docs.py` cuando tenga la regla;
  mientras tanto, `grep -n "(CONTEXT §2)"…`".
- `docs/CONTEXT.md:261` — pendientes de flujo: "YAML estricto en `check_docs.py`; `--estado` no distingue mezclado".

## Ficheros afectados (mapa completo)

- `scripts/check_docs.py` — único archivo con la deuda ejecutable: 4 reglas, `os.chdir` al importar, `DECISION_RE`
  permisivo, `estado()` sin caso `null`, CLI sin flags nuevos. Se reescribe.
- `tests/test_check_docs.py` — no existe; debe nacer (especificación §4).
- `pyproject.toml` — `[tool.mypy] files = ["app"]` (línea 90): añadir `"scripts/check_docs.py"`. Nada más.
- `scripts/check.py:50` — ya invoca el script; **no se toca** (especificación §6).
- `docs/CONTEXT.md`, `docs/PLAN.md`, `docs/backlog.md`, `docs/sesiones/*.md` — son la *entrada* de las reglas, no
  archivos a editar por el ejecutor (especificación §0.3). Hoy pasan los `grep` equivalentes de R2–R5 (ver abajo).
- `docs/deuda/BE-01/progress.json` — fixture real del defecto de `--estado` (`current_target: null`, 4 `completed`);
  no se edita.
- Documentos que registran la deuda y cambian en el cierre, no en las fases: `docs/backlog.md:141` (fila AF-01),
  `docs/PLAN.md:48` (celda `B-CHECK-DOCS`), `docs/sesiones/README.md:41` (quitar el `grep` provisional cuando exista
  `--copias`), `docs/CONTEXT.md:261` (pendiente `--estado`).

## Rincones no mencionados por la fuente

- **Flags desconocidos pasan en silencio** (`check_docs.py:133-135`): hoy `--copias`, `--huerfanas` y `--cierre`
  devuelven exit 0 con el mensaje de las reglas viejas. Un ritual de cierre que invoque `--copias` antes de que exista
  cree que está en verde. El plan debería hacer que un argumento no reconocido sea error (p. ej. `argparse`).
- **El repo vivo está hoy en verde para R2–R5** con el `grep` equivalente: R2 sobre CONTEXT, backlog y `docs/sesiones/`
  (citas quitadas) → 0 hallazgos; en PLAN todos los matches (`:86`, `:89`, `:96-103`, `:119-124`, `:135`) caen dentro
  de §3 (líneas 69–149). R3: `docs/sesiones/*.md` no usa ningún `B-…`. R4: ninguna celda Decisión con `B-` dentro de
  paréntesis. R5: la única línea con disparador y fecha es `PLAN.md:89` (`Lun 11 ene — entrega en línea (CONTEXT §2)`,
  válida). Confirma la decisión 3 de la especificación: lo que debe fallar va en fixtures, no en el repo.
- **Riesgo R5 en `docs/backlog.md:141`:** la propia fila AF-01 contiene el disparador `entrega` ("fecha de entrega en
  PLAN…") y fechas `30 oct`/`31 oct` en la misma línea, a más de 100 caracteres. Con la ventana ±40 de la especificación
  no se evalúa; si el plan relaja la ventana ("cualquier fecha de la línea"), esa fila se pone en rojo. Mantener la
  semántica de ventana y añadir este caso como "debe pasar".
- **Formato real de PLAN §3 para R7:** tabla "Días cerrados" `| Vie 23 oct | … | ✔ 23 |` … `| Sáb 31 | … | ◐ 31 |`
  (`PLAN.md:94-104`, mes heredado); tabla Bogotá `| Dom 1 nov | … | — | |` con `Cierre` vacío (`:117-124`); filas
  `| (se fecha el vie 6) | | |` (`:135`) y `| (se fecha al cerrar Prado) | | | |` (`:146`). Coincide con lo que la
  especificación asume (primera celda `Dow N [mes]`, filas `(se fecha …)` ignoradas, columna `Cierre` por encabezado).
- **Entorno de la compuerta:** `python scripts/check.py` con el Python del sistema (`C:\Python314`) falla por módulos
  ausentes (mypy, importlinter, jwt), no por el código; la medida válida es con `venv/Scripts/python.exe`. Ya está en
  CONTEXT §8.4 ("README: compuerta con el venv activo"); el ejecutor y el auditor deben usar el venv o el handoff
  reportará rojos falsos.
- `lint-imports` no vuelca su texto dentro de la sección `=== import-linter ===` cuando `check.py` se redirige a
  fichero (solo aparece la línea `--- import-linter: OK`); los contratos se leyeron ejecutando `lint-imports` aparte.
  Fuera de alcance de AF-01; se anota para el backlog.

## Patrones de detección (copiables)

```bash
# Estado del script: reglas presentes (hoy 4) y símbolos de la deuda
grep -c "^def rule_" scripts/check_docs.py
grep -n "os.chdir\|def read(p: str)\|rule_no_days\|DECISION_RE" scripts/check_docs.py
# Reglas y flags que el ítem exige y hoy no existen (deuda resuelta cuando TODOS dan resultado)
grep -n "rule_no_schedule_days\|rule_deadline\|rule_version_header\|rule_closed_days_marked\|strip_citations\|def sections\|--root\|--copias\|--huerfanas\|--cierre" scripts/check_docs.py
# DECISION_RE permisivo (deuda viva mientras imprima True)
venv/Scripts/python.exe -c "import sys; sys.path.insert(0,'scripts'); import check_docs as m; print(bool(m.DECISION_RE.match('**Entra · \`B-ORDEN\` (backend) y \`B-FE-RESERVAS\` (cliente)**')))"
# Flags desconocidos aceptados en silencio (deuda viva mientras el exit sea 0 con el mensaje de éxito)
venv/Scripts/python.exe scripts/check_docs.py --copias; echo "exit $?"
# --estado con current_target null
venv/Scripts/python.exe scripts/check_docs.py --estado | grep "objetivo: ?"
# Sin tests ni mypy sobre el script
ls tests/test_check_docs.py
grep -n '^files = \[' pyproject.toml
# Alcance de rule_blocks / rule_no_days (deben incluir docs/sesiones y PLAN fuera de §3)
grep -n '"docs/sesiones' scripts/check_docs.py
```

## Línea base (python scripts/check.py)

- Base develop: `2647ea3` (refrescado con `git fetch origin`; `merge-base HEAD origin/develop` = `2647ea3` =
  `origin/develop`: precondición cumplida). HEAD `ca9a71e` (`item/af-01`, 2 commits de solo docs sobre develop).
- Comando: `venv/Scripts/python.exe scripts/check.py` (ejecutado desde `C:\projects\ecotur-asoprado`). Un primer
  intento con `python scripts/check.py` usó `C:\Python314\python.exe` sin dependencias (mypy, import-linter y pytest
  fallaron por `ModuleNotFoundError`) y se descarta como medida.
- RESUMEN literal:

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

- pytest: `145 passed, 1 warning in 10.80s`.
- Cobertura total: `TOTAL 927 52 134 25 93%` → **93 %**.
- ruff format: `27 files would be reformatted, 98 files already formatted`. ruff check: `Found 362 errors.`
- mypy: `Found 44 errors in 12 files (checked 33 source files)`.
- import-linter: `Contracts: 4 kept, 0 broken.` (leído con `venv/Scripts/lint-imports.exe`; dentro de `check.py` el
  paso marcó OK sin volcar el texto).
- docs (coherencia): `Documentación coherente: …` exit 0 (4 reglas actuales).
- **La compuerta ya falla antes de tocar nada** (ruff format, ruff check, mypy), igual que la línea base del trinquete
  de ADR-0005 / PLAN §6 (362 · 44 · 4 KEPT · 93 %). Criterio del ítem: ruff ≤ 362, mypy ≤ 44 con el script nuevo
  dentro de `mypy.files`, 4 KEPT, cobertura ≥ 93 %, 145 + N tests en verde, paso docs en verde.

## Conclusión para el planificador

Debe resolver, en `scripts/check_docs.py` + `tests/test_check_docs.py` + una línea de `pyproject.toml`, lo que fija la
especificación: quitar `os.chdir` y pasar `root: Path` a cada regla (`--root`), R2 con días de la semana y alcance
ampliado (PLAN fuera de §3 por `sections`, `docs/sesiones/`), R3 con `docs/sesiones/`, R4 con calificador cerrado sin
bloques ni vocabulario dentro, R5 deadline con ventana ±40 y cita `(CONTEXT §2)`, luego R8/R9/`--estado` y por último
R6/R7 bajo `--cierre` con `git` y reloj inyectados. Añadir rechazo de flags desconocidos (hoy exit 0 silencioso).
No debe tocar `scripts/check.py`, `.claude/`, `coverage.source`, ni CONTEXT/PLAN/backlog (el texto viejo va a fixtures).
Riesgos: cualquier regex más laxa que la especificada pone en rojo el repo vivo (p. ej. R5 sin ventana sobre
`backlog.md:141`; R2 sin lookahead de unidades sobre CONTEXT §2 `sáb 7 h`); el archivo entra nuevo a mypy, así que un
solo error suyo rompe el trinquete 44; medir siempre con `venv/Scripts/python.exe`, no con el Python del sistema.

## Adenda (sesión Mentor, 1 nov 18:20; verificación revisada y aprobada por David a las 18:19)

Los rincones de este informe que entran en el plan están consolidados como requisitos en
`docs/deuda/AF-01/especificacion.md` §8 (flags desconocidos → `argparse` y exit 2 en Fase A; caso "debe pasar" de R5 con
`backlog.md:141`; compuerta solo con el venv), junto con dos observaciones que este informe no cubrió (fixtures
`autouse` de `tests/conftest.py`; `ruff` ignora `D` en `tests/**`). El planificador lee §8 además de la conclusión de
arriba. El hallazgo de `lint-imports` queda para el backlog en el cierre del día.
