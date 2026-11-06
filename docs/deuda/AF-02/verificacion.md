# Verificación — AF-02: residuales de `check_docs.py` (R7 de enero, `--estado`, coherencia §2b ↔ backlog)

**Veredicto:** parcial. De los cinco puntos de la fila, el 4 ya no existe (lo corrigió AF-05); 1, 2, 3 y 5 persisten.
**Los puntos 2 y 3, que son el alcance vigente, están confirmados e intactos:** "puntos 2 y 3" es el alcance acordado,
no lo que quedó tras cerrar los otros. Nadie cerró código bajo AF-02.
**Fuente del ítem:** `docs/backlog.md:165` (sección E) + `docs/deuda/AF-01/gaps.md:106` + `docs/deuda/BE-33/gaps.md:258`
+ bitácoras `2026-11-01` (l.52–53, 84–85, 198–203), `2026-11-02` (l.37, 280, 484), `2026-11-03` (l.58, 203), `2026-11-06` (l.202–204)
+ PR #81 (descripción, "Residuals")
**Fecha:** 2026-11-06

## Qué describe el ítem

Cinco defectos o huecos de `scripts/check_docs.py`, salidos de la auditoría de AF-01 y de la sesión Mentor: (1) ningún
check compara la celda de un bloque en PLAN §2b con las filas `Entra · ese bloque`; (2) R7 toma el año inicial de cada
tabla de la línea de versión, de modo que al subir PLAN a 2027 las filas pasadas no se evalúan, y además usa la fecha
local; (3) `--estado` deduce "última auditoría" de la última línea de `gaps.md`; (4) `lint-imports` sin texto
(retirado); (5) opcional: exigir bitácora por marca. Alcance al 2 nov: 2 y 3; 1 y 5 "quedan para `B-FUTURO`".

### Estado por punto

| Punto | Estado | Cómo se sabe |
|---|---|---|
| 1. Celda §2b ↔ filas | **Persiste** (fuera del alcance vigente) | Medido: sonda P1 y `FE-14` |
| 2a. R7, año inicial | **Persiste, íntegro** | Medido: sondas b, c, PLAN real |
| 2b. R7, fecha local | **Persiste; hoy sin nada que lo active** | Medido: `TZ`; leído: ningún automatismo corre `--cierre` |
| 3. `--estado` | **Persiste, íntegro y más grave que lo que dice la fila** | Medido: 14 casos, tabla sobre 9 `gaps.md` reales, mutantes |
| 4. `lint-imports` | **Ya no existe** | Medido: la compuerta de hoy imprime los 4 contratos con el venv por ruta |
| 5. Bitácora por marca | **Persiste** (opcional; hoy sin daño real) | Medido: sonda P5; 14 de 14 marcas reales tienen bitácora |

`scripts/check_docs.py` no se toca desde `f6f73a9` (1 nov), y `tests/test_check_docs.py` desde `2b27e1f` (1 nov).

## Evidencia en el código

**Punto 3**

- `scripts/check_docs.py:521-526` — única lectura de `gaps.md` del repo: `"PASS" if "PASS" in txt.splitlines()[-1] else "con gaps"`.
- `scripts/check_docs.py:497` — la docstring de `estado()` promete `Always 0: the view is informative.`; falso, ver medición.
- `scripts/check_docs.py:463-466` — `read_progress` sí captura `ValueError` para un archivo no UTF-8; `gaps.md` no tiene esa guarda.
- `tests/test_check_docs.py` — **ningún test toca la rama de `gaps.md`**: `grep -n gaps` no devuelve nada. Medido con mutantes.
- `.claude/agents/handoff-auditor.md:44-48` y `.opencode/agent/handoff-auditor.md:44-46` — fijan el formato de cada hallazgo, pero
  el veredicto se pide **en la respuesta**, no en `gaps.md`. No hay contrato de formato que el script pueda leer: esa es la causa de fondo.
- `docs/deuda/BE-33/gaps.md:290` — la línea final que el auditor añadió "para que `--estado` lea el resultado": parche declarado.

**Punto 2**

- `scripts/check_docs.py:737` — `_dated_rows(lines_inside(root, rel, {"3"}), version.when.year)`: el año sale de la línea de versión.
- `scripts/check_docs.py:698` — `month, year = None, start_year`: se reinicia en cada tabla, así que el error afecta a todas.
- `scripts/check_docs.py:703-707` — monotonía dentro de la tabla: `if month is not None and named < month: year += 1`.
- `scripts/check_docs.py:719` y `:736` — `today: Callable[[], date] = date.today`, `now = today()`: fecha local de la máquina.
- `scripts/check_docs.py:32-33` y `:724` — las docstrings documentan el comportamiento actual; un cambio de la regla las deja falsas.
- `docs/deuda/AF-01/especificacion.md:173-176` — origen de la regla ("partiendo del año de la línea de versión"). ADR-0008 (l.137) no fija el año.
- `tests/test_check_docs.py:797-802` — el `_plan_section_3` de los tests usa `31 oct {year}` con tablas que empiezan en noviembre: una versión anterior a la primera fila es un caso cubierto hoy.

**Punto 1**

- `scripts/check_docs.py:228-237` — `rule_blocks` (R3) solo comprueba que el bloque citado exista en §2b.

**Punto 4 (ya no existe)**

- `scripts/check.py:95-101` y `:109` — la herramienta se busca en el directorio de scripts del intérprete; si falta, el paso sale en rojo.
- `tests/test_check.py:150-173` — tests de la herramienta ausente (`find_lint_imports`, `_lint_imports_cmd`).

**Punto 5**

- `scripts/check_docs.py:669` y `:738` — `CLOSE_MARK_RE` solo mira la forma de la marca; nada consulta `docs/bitacora/`.

## Ficheros afectados (mapa completo)

- `scripts/check_docs.py` — l.521-526 y l.497 (punto 3); l.677-715, l.719, l.724, l.736-737, l.32-33 (punto 2); l.228-237 (punto 1); l.669, l.738 (punto 5); l.60-62 (residual `reconfigure`).
- `tests/test_check_docs.py` — l.496-560 (`--estado`: solo `progress.json`, cero casos de `gaps.md`); l.755-911 (R7: fijan el comportamiento actual; l.797-802 es lo que rompe la salida literal del backlog).
- `.claude/agents/handoff-auditor.md:44-48` — escribe `gaps.md` sin línea de veredicto obligatoria.
- `.opencode/agent/handoff-auditor.md:44-46` — ídem; su l.45 manda actualizar `docs/deuda/registro.json`, que no existe.
- `docs/deuda/*/gaps.md` (9 archivos) — corpus real que la lectura debe interpretar. Son registros: no se editan.
- `docs/backlog.md:165`, `docs/CONTEXT.md:294`, `docs/PLAN.md:65` y `:141` — describen el ítem; ver "Discrepancias".

## Rincones no mencionados por la fuente

1. **R7 también falla al revés (nuevo, medido).** La fila solo describe filas que no se evalúan. Con versión `31 dic 2026` y una tabla
   que empieza en `Lun 4 ene`, futura, las filas se fechan `2026-01-04` y `2026-01-05`: **2 errores falsos**. Lo sufre el código actual y también la salida literal del backlog.
2. **La salida del backlog para el punto 2 está mal planteada (nuevo, medido).** "Mes de la primera fila > mes de la versión → año − 1" arregla enero, pero
   rompe 3 tests (`past-row-unmarked`, `bogota-table-today`, `year-jump-future-row`) y da un error falso con versión `30 nov 2026` y tabla futura en `Mar 1 dic`, que es un caso realista al fechar el régimen final. El mismo texto está en `docs/deuda/AF-01/gaps.md:106` y en la bitácora `2026-11-01` l.199.
3. **`UnicodeDecodeError` (nuevo, medido).** Un `gaps.md` no UTF-8 también rompe `--estado`, con exit 1.
4. **El traceback corta la vista (nuevo, medido).** Con ítems A, B (vacío) y C, solo sale A, con exit 1: se pierden los ítems siguientes.
5. **Subcadena (nuevo, medido).** `"PASS" in` acepta `BYPASS` y `PASSWORD` en la última línea.
6. **`BE-33/progress.json:3` tiene `"current_target": "null"`, la cadena y no `null`.** `--estado` imprime `en ejecución (objetivo: null)` con 4 de 4 fases `completed`. Es un dato, no un defecto del script, y queda fuera de la fila; afecta a la misma vista.
   También salen "en ejecución" A9, S1 y SEC1 (`"cierre"`) y AF-05 (`"Auditoria"`): residual ya anotado en `docs/CONTEXT.md:292`.
7. **Residuales asignados a AF-02 en bitácoras que nunca llegaron a la fila:**
   - "Punto 6" (bitácora `2026-11-02` l.37): texto que parece cita y no tiene la forma fija. Medido: `ver CONTEXT §2` y `(CONTEXT §2 )` → exit 0 y `--copias` con 0 líneas.
   - `reconfigure` de los streams al importar (bitácora `2026-11-02` l.280; `check_docs.py:60-62`). Medido: importar el módulo pasa `sys.stdout.encoding` de `ascii` a `utf-8`.
   - Mes heredado (`docs/deuda/AF-01/handoff-Fase_D.md:168-170`, condicional: "si se quiere"). Medido: `Dom 1` tras `Sáb 31 oct` se fecha `2026-10-01`, con 1 error falso; `Lun 31 nov` se salta en silencio. La convención de PLAN lo evita.

**Lo que se buscó y no está:** R6 con zonas horarias. `%cs` usa la zona del committer, y los últimos 60 merges (incluidos los de GitHub) son `-0500`: hoy no hay desfase.

## Medido y leído

**Medido** (salida de ejecución real; todo sobre fixtures o copias en el scratchpad, nunca en el repo):

`--estado` con fixtures, usando el `check_docs.py` real y `--root`:

| Contenido de `gaps.md` | Salida | Exit |
|---|---|---|
| `[BLOQUEANTE]…` + última línea `no es PASS` | **PASS (falso)** | 0 |
| `Veredicto: GAPS (1 bloqueantes…)`, `[BLOQUEANTE]…`, última línea que menciona un PASS anterior | **PASS (falso)** | 0 |
| `[BLOQUEANTE] — … el PASS del auditor previo no vale` como última línea | **PASS (falso)** | 0 |
| `[BLOQUEANTE]…` + `BYPASS del guard` / `PASSWORD_RESET sin test` | **PASS (falso)** | 0 |
| `[BLOQUEANTE]…` como última línea, sin la palabra PASS | con gaps (acierta por azar) | 0 |
| Vacío | **`IndexError`** | **1** |
| Solo `\n` | con gaps | 0 |
| No UTF-8 | **`UnicodeDecodeError`** | **1** |
| `Veredicto: PASS…` + línea en blanco final | **con gaps (falso)** | 0 |
| `Veredicto: PASS…` + `[OPCIONAL]…` al final | **con gaps (falso)** | 0 |
| `Veredicto: pass` | con gaps | 0 |
| `Veredicto: PASS` sin salto final | PASS | 0 |

**Lo afirmado en el PR #81 queda confirmado, con una precisión:** el falso PASS no lo causa la línea `[BLOQUEANTE]`, que el script nunca lee; lo causa cualquier `PASS` en la última línea. El `IndexError` solo ocurre con cero líneas: `\n` no lo lanza.

Los 9 `gaps.md` reales, frente a `--estado`:

| Ítem | `--estado` | Veredicto en el último bloque | ¿Coincide? |
|---|---|---|---|
| A9 | con gaps | `**Veredicto: PASS (0 bloqueantes, 4 opcionales).**` (l.84) | **No** |
| AF-05 | con gaps | `Veredicto: **PASS (0 bloqueantes, 4 opcionales)**` (l.5) | **No** |
| BE-01 | con gaps | `Veredicto: PASS (0 bloqueantes, 2 opcionales)` (l.34) | **No** |
| SEC1 | con gaps | `Veredicto: PASS (0 bloqueantes, 5 opcionales)` (l.5) | **No** |
| AF-01 | PASS | `Veredicto Fase D: PASS…` (l.177, última línea) | Sí |
| BE-02 | PASS | `Veredicto Fase A: **PASS…` (l.58, última línea) | Sí |
| BE-15 | PASS | `- **Veredicto:** PASS…` (l.575); la última línea es otra frase con PASS | Sí, por una frase |
| BE-33 | PASS | `**Veredicto: PASS…` (l.176); la última línea es el parche | Sí, por el parche |
| S1 | PASS | `Veredicto: PASS…` (l.46); la última línea dice "auditadas en PASS" | Sí, por una frase |

**4 de 9 son falsos "con gaps".** Los 9 últimos bloques tienen una línea con `Veredicto` y `PASS`, en 6 formatos distintos. **Cero** `gaps.md` reales tienen un hallazgo `[BLOQUEANTE]`: no existe ningún caso negativo real como referencia.

Mutantes sobre una copia de `check_docs.py` y `test_check_docs.py` (M0: **148 passed**):

| Mutante | Resultado |
|---|---|
| M1 `--estado` siempre PASS | 148 passed (**sobrevive**) |
| M2 `--estado` siempre con gaps | 148 passed (**sobrevive**) |
| M3 rama de `gaps.md` eliminada | 148 passed (**sobrevive**) |
| M4 salida literal del backlog | **3 failed**, 145 passed |
| M5 sonda: año por distancia a la versión (más de 6 meses) | 148 passed |

R7, errores por caso (`today` inyectado):

| Caso | Correcto | Actual | M4 | M5 |
|---|---|---|---|---|
| a. v`31 dic 2026`; `28 dic`, `29`, `1 ene` sin marca; hoy 5 ene 2027 | 3 | 3 | 3 | 3 |
| b. v`2 ene 2027`; lo mismo | 3 | **0** | 3 | 3 |
| c. v`2 ene 2027`; `23 oct`, `2 nov` sin marca | 2 | **0** | 2 | 2 |
| d. v`31 dic 2026`; tabla futura `4 ene`; hoy 31 dic | 0 | **2** | **2** | 0 |
| e. v`30 nov 2026`; tabla futura `1 dic`; hoy 30 nov | 0 | 0 | **1** | 0 |
| PLAN real, hoy 6 nov | 0 | 0 | 0 | 0 |

Copia del **PLAN real**, con la marca de `Lun 2` borrada y filas `28 dic`, `1 ene` sin marca, hoy 5 ene 2027: versión `2 ene 2027` → **0 errores**; versión `31 dic 2026` → 4 errores (las tres anteriores más `Vie 6`, que hoy no tiene marca). Confirma la medición de AF-01 (`gaps.md:106`).

Reloj, por CLI con la variable `TZ` y una fila `Vie 6 nov` sin marca, entre las 15:25 y las 15:31 de Bogotá: `TZ` vacío, `COT5` y `UTC0` → hoy 6 nov, 0 errores R7; `AAA-14` → hoy 7 nov, **1 error**. Con `today` inyectado: 6 nov → 0, 7 nov → 1. **No medido en vivo:** el cruce exacto de las 19:00 en una máquina UTC; es aritmética.

Punto 1: celda con `BE-99`, fila `BE-01` en el mismo bloque → exit 0. Real: **`FE-14` es `Entra · B-FE-LISTA` (`backlog.md:136`) y no está en la celda (`PLAN.md:71`).** Mi script dio más diferencias en sentido celda → fila (ítems hechos, menciones como "mitigación de BE-14"); son ruido de mi lectura y **no** las doy por desincronización. Solo revisé a mano FE-14 y BE-14.

Punto 5: `✔ 2` sin bitácora → exit 0. Real: 14 marcas en §3, 0 sin bitácora.

Punto 4: la compuerta de hoy, con el venv por ruta y sin activar, imprime los 4 contratos (ver línea base).

`--cierre` sobre el repo real: exit 1 por **3 errores R6**, porque CONTEXT, PLAN y backlog siguen en versión del 5 nov con commits del 6. Es lo esperado hasta el cierre, no deuda. **0 errores R7.**

**Solo leído** (sin ejecutar): formatos de hallazgo en los prompts del auditor; especificación de AF-01; ADR-0008; bitácoras; descripción del PR #81 (`gh pr view`); la ausencia de `--cierre` en el CI y en `check.py` (`.azure-pipelines/ci-pipeline.yml:30`, `scripts/check.py:110`): solo lo pide el ritual, `docs/sesiones/README.md:51`.

## Discrepancias

1. **La fila no recoge las mediciones del punto 3.** La bitácora `2026-11-06` l.202–203 y `docs/deuda/BE-33/plan.md:682-683` dicen que van a "AF-02 punto 3, con esas dos mediciones nuevas"; `backlog.md:165` sigue diciendo solo "BE-01 sale 'con gaps' con auditoría limpia". Lo real: 4 ítems y un falso PASS.
2. **Los puntos 1 y 5 no tienen dueño fuera de la fila.** La Nota técnica dice "quedan para `B-FUTURO`", pero la Decisión es `Entra · B-TESTS` y la celda de `B-FUTURO` (`PLAN.md:79`) no los lista. R4 admite un solo bloque por fila, así que al cerrar AF-02 hay que decidir qué pasa con ellos.
3. **Residuales huérfanos:** "punto 6", `reconfigure` y mes heredado están asignados a AF-02 en bitácora o handoff, y no en la fila.
4. **La salida propuesta para el punto 2 es incorrecta** tal como está escrita (rincón 2).
5. **Referencia desplazada:** `docs/deuda/BE-33/gaps.md:258` cita `docs/backlog.md:163`; la fila está hoy en la l.165. Es un registro: no se corrige.
6. **Punto 2, segunda mitad:** la fila la presenta como riesgo activo, pero hoy nada corre `--cierre` en una máquina UTC. Es real y no se activa mientras el ritual se haga en local.
7. **`docs/PLAN.md:65`** dice "AF-02 (puntos 2 y 3) en PR propio si cabe", mientras que `:141` y la bitácora de hoy lo dan por completo. Manda lo último.

## Patrones de detección (copiables)

```bash
# Punto 3: lectura de la última línea (debe desaparecer)
grep -n 'splitlines()\[-1\]' scripts/check_docs.py
# Punto 3: tests de la rama de gaps.md (hoy vacío; debe dejar de estarlo)
grep -n 'gaps' tests/test_check_docs.py
# Punto 3: quién lee gaps.md en el código
git grep -n -E 'gaps\.md|última auditoría' -- scripts tests
# Punto 3: corpus real
grep -n -E '^## Auditor|[Vv]eredicto' docs/deuda/*/gaps.md
grep -n '\[BLOQUEANTE\]' docs/deuda/*/gaps.md
# Punto 2: origen del año y del reloj
grep -n -E 'version\.when\.year|start_year|date\.today' scripts/check_docs.py
# Punto 2: quién corre --cierre
git grep -n -e '--cierre' -- .azure-pipelines .github scripts/check.py docs/sesiones/README.md
# Efecto al importar
grep -n -E '_stream|reconfigure' scripts/check_docs.py
# Vista real
./venv/Scripts/python.exe scripts/check_docs.py --estado
```

## Línea base (`scripts/check.py` con el Python del venv por ruta, AGENTS §6)

- Base develop: `e4e7d43`
- Refrescado con `git fetch origin` (exit 0; por `fetch.prune=true` borró la referencia remota ya inexistente `origin/item/a2`).
- Rama: `item/AF-02`, en el commit `e4e7d43` (`e4e7d43a0510f55a606a58482610770a51a5bbe8`). `git merge-base HEAD origin/develop` = `git rev-parse origin/develop` = `HEAD`: **precondición cumplida; 0 commits por delante y 0 por detrás**.
- **`item/a2` ya está mezclada:** `e4e7d43` es el merge del PR #82.
- Árbol limpio al medir. Comando: `./venv/Scripts/python.exe scripts/check.py` → exit 1.

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

| Paso | Resultado |
|---|---|
| ruff format --check | OK: `57 files already formatted` |
| ruff check | **FALLA: `Found 9 errors.`**, todos I001: 8 en `app/` (`api/dependencies.py`, `api/routers/audit.py`, `core/email.py`, `db/database.py`, `repositories/user_repository.py`, `schemas/audit.py`, `services/audit_service.py`, `services/user_service.py`) y `tests/test_user_service.py` |
| mypy | **FALLA: `Found 5 errors in 4 files (checked 35 source files)`**: `db/database.py:11`, `core/security.py:71`, `:87`, `services/user_service.py:124`, `api/dependencies.py:95` |
| import-linter | OK: **4 KEPT, 0 BROKEN** (`Contracts: 4 kept, 0 broken.`) |
| docs (coherencia) | OK: R1–R5 |
| pytest | **438 passed, 0 failed**, 5 warnings, en 17.73 s |
| cobertura | **96.11 %** (mínimo 92 %); `source = ["app"]`, así que `scripts/` no se mide |

**La compuerta ya falla antes de tocar nada**, por ruff y mypy, en archivos ajenos a AF-02 (rojo que CONTEXT atribuye a A4). Ni `scripts/check_docs.py` ni `tests/test_check_docs.py` aportan errores.

## Conclusión para el planificador

**Debe resolver (puntos 2 y 3):** que `--estado` informe el veredicto de la **última auditoría** a partir de su bloque, sin depender de la última línea, sin traceback (vacío, no UTF-8) y cumpliendo "siempre 0"; y que R7 fije el año sin depender de que la versión y la tabla compartan año, en los dos sentidos (casos b, c y d). Son dos cambios independientes en `scripts/check_docs.py` y `tests/test_check_docs.py`: caben en una fase por punto, con RED primero (M1–M3 sobreviven hoy). La fecha límite del punto 2 es la primera edición de PLAN en enero.

**No debe tocar:** los `gaps.md` existentes, incluida la línea de `BE-33/gaps.md:290`; `app/`; `.claude/` y `AGENTS.md` (`fase-ejecutor.md:67` lo prohíbe al ejecutor). Fuera del alcance vigente: puntos 1 y 5, "punto 6", `reconfigure`, salvo decisión de David; el plan debe decir adónde van, porque hoy solo la Nota técnica les da destino (discrepancia 2).

**Riesgos:**
- **No copiar la salida del backlog:** rompe 3 tests y da un error falso en un caso realista (M4). M5 demuestra que se puede sin tocar los 148 tests, pero es una sonda, no una recomendación ni una solución revisada.
- **Parser ingenuo:** buscar `[BLOQUEANTE]` da falso positivo con `BE-33/gaps.md:258` (mención dentro de un `[OPCIONAL]`) y, sin distinguir mayúsculas, también con `BE-33/gaps.md:141`, `BE-15/gaps.md:368` y `:688` ("no es bloqueante"); buscar `GAPS` choca con `# GAPS — BE-15` (`BE-15/gaps.md:1`); hay `RESUELTO (<hash>)` en la convención; `Sin bloqueantes.` y `0 bloqueantes` son el caso limpio. Hay 6 formatos de veredicto, y bloques antiguos sin ninguno (A9 Fase A; AF-01 A–C).
- **Sin contrato, el parser queda frágil:** los prompts del auditor no exigen línea de veredicto en `gaps.md`. Fijarlo toca `.claude/` y, por tanto, le corresponde a David; el plan debe decidirlo de forma explícita. Los negativos solo se podrán probar con fixtures, porque no hay ninguno real.
- `test_repo_is_green` (`tests/test_check_docs.py:130`) corre sobre los docs reales, y la cobertura no mide `scripts/`: la compuerta no delatará un test ausente; hay que comprobarlo con mutantes.

## Adenda — decisiones de David antes de planear (6 nov 2026, 15:55, sesión Mentor)

Resuelve lo que la conclusión deja abierto. El planificador las toma como dadas; lo demás (fases, tests, commits) es
suyo. Regla del verificador: no reescribir, añadir.

1. **Veredicto aceptado: parcial. Alcance de este plan: puntos 2 y 3 de la fila, completos.** Nada más de la fila ni de
   los residuales entra.
2. **Punto 3, `--estado`, veredicto de la última auditoría:** se lee del **último bloque** `## Auditoría Fase …` de
   `gaps.md`, no de la última línea del archivo. El parser acepta los seis formatos ya existentes en los nueve
   `gaps.md` reales (línea que empieza por `**Veredicto` o contiene `Veredicto:` seguido de `PASS` o `GAPS`, con o sin
   negrita) y el formato de contrato que David fija hoy en `handoff-auditor.md`: **`**Veredicto Fase X: PASS (0
   bloqueantes, N opcionales).**`** o **`**Veredicto Fase X: GAPS (N bloqueantes, M opcionales).**`** como primera línea
   del bloque. Bloque sin línea de veredicto → `sin veredicto` (A9 fase A, AF-01 A–C existen así); archivo vacío o no
   UTF-8 → `ilegible`; **nunca traceback, siempre exit 0** (el docstring de l.497 pasa a ser verdad). Coincidencia por
   palabra completa: `BYPASS`/`PASSWORD` no son `PASS`; "no es bloqueante" y `[BLOQUEANTE]` dentro de un `[OPCIONAL]` no
   cuentan como bloqueante (`BE-33/gaps.md:141,258`). Los `gaps.md` existentes **no se editan**, incluido
   `BE-33/gaps.md:290`.
3. **La otra mitad de `--estado` ("en ejecución" en ítems cerrados) es un problema de datos, fuera del plan:** David
   pone `current_target: null` (JSON `null`, sin comillas) en los cinco `progress.json` (A9, AF-05, S1, SEC1, BE-33) en
   un commit propio de esta rama antes de la fase A. El plan no cambia cómo `--estado` interpreta `progress.json`.
4. **Punto 2, R7, el año: no se usa la fórmula de la fila** (rompe 3 tests y falla el caso "versión de diciembre, tabla
   de enero"). Diseño: para cada fila, el año es el que deja su fecha **más cerca** de la fecha de la línea de versión
   (candidatos: año de la versión, −1, +1); el planificador lo especifica y lo prueba con los cinco casos de la
   verificación (a–e) más los 148 tests existentes intactos (`tests/test_check_docs.py:755-911`). Fecha límite del
   punto: antes de la primera edición de PLAN en enero.
5. **Punto 2b, el huso, entra, y para R6 y R7:** `today()` y la fecha de commit que R6 compara se evalúan en
   `America/Bogota` (`zoneinfo`, stdlib), no en la hora local de la máquina; test con `TZ=UTC` a las 19:00+ de Bogotá
   para R7 y con una fecha de commit en UTC del día siguiente para R6 (caso real: fe de erratas del 5 nov). Una sola
   causa, una sola corrección.
6. **Fuera de alcance, con destino:** puntos 1 y 5 de la fila, "punto 6" (regla de cita con forma fija, bitácora 2 nov)
   y `reconfigure` (`check_docs.py:60`) → fila nueva **AF-08** en el cierre de hoy, `Sale → B-FUTURO`, primera en el
   orden de rescate de los AF. `.claude/`, `AGENTS.md` y `.opencode/` no se tocan (David edita `handoff-auditor.md` con
   la línea de contrato en rama aparte, con AF-07). `app/` no se toca. Sin excepción a ADR-0005: los archivos de AF-02 no
   tienen rojo heredado.
7. **Fases y prueba:** dos fases, una por punto (A = punto 3, B = punto 2 + 2b), tests RED primero en
   `tests/test_check_docs.py` con el esquema de AF-01; como la cobertura no mide `scripts/`, cada fase demuestra sus
   tests con mutantes (los M1–M3 de la verificación para `--estado`; para R7, año fijo y hora local) y lo deja en el
   handoff.
