# PLAN — AF-01: Implementar las reglas de ADR-0008 en `scripts/check_docs.py`

- **Fecha:** 2026-11-01 · **Fuente:** `verificacion.md` (confirmada) + `especificacion.md` (R1–R9, §8) · **Rama:** `item/af-01`
- **Base:** `2647ea3` (= `origin/develop`) · HEAD de docs: `d7ef194`

## Resumen para aprobación

Se reescribe `scripts/check_docs.py` (paso "docs (coherencia)" de la compuerta) para que haga lo que ADR-0008 punto 6
le encarga y hoy no hace: fechas de cronograma fuera de PLAN §3 (con días de la semana y en todo el alcance), bloques
citados en `docs/sesiones/`, columna Decisión con exactamente un bloque y un calificador cerrado, fecha de entrega
igual a CONTEXT §2, listado de citas por dueño (`--copias`), candidatos a hecho duro sin cita (`--huerfanas`),
`--estado` que distingue "ejecutado, pendiente de PR", y, solo bajo `--cierre`, encabezado de versión (ADR-0007) y
filas de PLAN §3 cerradas sin marca. Nace `tests/test_check_docs.py` sobre fixtures en `tmp_path` (el script deja de
hacer `os.chdir` y recibe `--root`), y el script entra a `mypy.files`. Cuatro fases en un solo dominio (`flow`):
A refactor testable + CLI estricta (hoy `--copias` devuelve exit 0 en silencio), B reglas bloqueantes R2–R5,
C comandos informativos, D `--cierre`. Riesgo principal: una regex más laxa que la especificada pone en rojo el repo
vivo; mitigación: las regex de la especificación se probaron hoy contra el repo (0 hallazgos) y `test_repo_is_green`
las congela. NO se toca `scripts/check.py`, `.claude/`, `coverage.source`, `tests/conftest.py` ni CONTEXT/PLAN/backlog.

## Objetivo y decisiones bloqueadas

Que `python scripts/check_docs.py` verifique el principio de ADR-0008 (hecho duro con dueño y cita) y no el síntoma,
con tests sobre fixtures y sin dependencias nuevas; que ningún flag inexistente pase en silencio.

1. Solo biblioteca estándar (`argparse`, `re`, `json`, `subprocess`, `datetime`, `pathlib`). Nada nuevo en
   `pyproject.toml` salvo `mypy.files += ["scripts/check_docs.py"]` (especificación §0.8).
2. Las regex de R2, R4, R5, R6, R7 y de las citas son **las de la especificación**, sin relajarlas (§0.7, §2, §3, §8.2).
3. `os.chdir` desaparece; toda regla recibe `root: Path`; la CLI acepta `--root` (§0.5).
4. Flag desconocido → `argparse` imprime uso y termina con exit 2 (§8.1).
5. R6 y R7 solo corren con `--cierre`; la compuerta por defecto no depende de `date.today()` ni de `git` (§0.4).
6. El ejecutor no edita CONTEXT, PLAN, backlog ni `docs/sesiones/`; el texto viejo va a fixtures (§0.3).
7. Compuerta y tests se miden con `venv/Scripts/python.exe`, nunca con el Python del sistema (§8.3).
8. Lo que no esté auditado al cierre del día nace como `AF-02`; ninguna fase a medias cruza de día (§5).

## Análisis del redactor

**Qué se cambia y por qué.** Hoy el script tiene 4 reglas (`check_docs.py:3-12`), `os.chdir(REPO_ROOT)` al importar
(`:25`), rutas literales en cada regla, `DECISION_RE` con `.*` que acepta cualquier cola (`:72-74`), `estado()` sin caso
`current_target: null` (`:118`) y un `main()` que ignora flags desconocidos (`:133-135`). Nada de eso tiene tests
(`tests/test_check_docs.py` no existe) ni pasa por mypy (`pyproject.toml:90`). Verificado hoy leyendo el archivo y
ejecutando `--copias` (exit 0 con el mensaje de éxito viejo).

**Orden y dependencias.** La inyección de `root` (Fase A) es prerrequisito de todo test sobre fixtures; por eso va
primero y sola: cambia firmas y CLI sin tocar qué detecta cada regla, de modo que el paso "docs" de la compuerta sigue en
verde con las mismas 4 reglas y el diff se audita como refactor puro. Fase B sustituye/amplía las reglas bloqueantes
(R2–R5) y depende de `sections` y `strip_citations` de A. Fase C (R8, R9, `--estado`) depende de `strip_citations` y del
alcance de archivos de B. Fase D (R6, R7) depende de `sections` (PLAN §3) y de la versión del encabezado; es la única
con `git`/reloj, inyectados. La especificación §5 proponía tres fases (A = transversal + R2–R5); aquí A se parte en dos
(A y B) para que la primera sea la más pequeña y auditable; C y D equivalen a las fases B y C de la especificación.

**Qué congela qué.** No hay tests previos del script. Los que nacen en A congelan: firma `rule(root, errors)`,
`sections` sobre `## N.`/`## 2b.`, `strip_citations` para las 8 formas de cita, R1 y el mensaje de uso con exit 2.
`test_repo_is_green` (A, ampliado en B) congela "el repo de hoy pasa": cualquier regex más laxa lo rompe. Dry run hecho
hoy con las regex de la especificación sobre el repo real: R2 → 0 hallazgos en CONTEXT, backlog, `docs/sesiones/*.md`
y PLAN fuera de §3 (`sections` da §3 = líneas 69–149); R4 → 72 celdas Decisión, 0 fallos, y los 9 casos "debe fallar"
/ 8 "debe pasar" de §2 se comportan como dice la especificación; R5 → única línea evaluada `PLAN.md:89` (`11 ene`,
con cita) y deadline legible `11 de enero de 2027`; R6 → los cuatro encabezados existentes casan con la regex y los
cuatro prompts sin versión (`documento`, `estudio`, `ingenieria-revision`, `mentor`) tienen último commit 25–26 oct
(antes del 28 oct de ADR-0007 punto 5): `--cierre` también sale en verde hoy.

**Riesgos.** (1) El archivo entra nuevo a mypy: un solo error suyo sube el total de 44 y rompe el trinquete; el
ejecutor corre `mypy scripts/check_docs.py` antes de la compuerta. (2) `sys.path.insert` seguido de `import check_docs`
en el test dispara ruff `E402`; se importa con `importlib.import_module` (ver Fase A). (3) `tests/conftest.py` tiene dos
fixtures `autouse` (`setup_database` asíncrona, `override_azure_storage_client`): los tests nuevos las heredan; si
tardan o fallan por el engine, la causa es esa y el handoff lo dice (§8.4), no se toca el conftest. (4) R5 compara
mes por prefijo de tres letras en minúscula (`enero` → `ene`) y año solo si la fecha lo trae; cualquier otra
normalización da falsos rojos. (5) Windows: mantener la reconfiguración de `stdout`/`stderr` a UTF-8 (`:27-29`).

**Qué NO se toca.** `scripts/check.py:50` (ya invoca el script), `.claude/**`, `[tool.coverage]`, `tests/conftest.py`,
CONTEXT/PLAN/backlog/sesiones, `.azure-pipelines/`. Los documentos que registran la deuda (`backlog.md:141`,
`PLAN.md:48`, `sesiones/README.md:41`, `CONTEXT.md:261`) los actualiza la sesión que cierra, no una fase.

## Regla de alcance

- **Sí:** `scripts/check_docs.py`, `tests/test_check_docs.py` (nuevo), una línea de `pyproject.toml` (`[tool.mypy] files`).
- **No:** todo lo demás. Hallazgos nuevos → sección Residuales de este plan → `docs/backlog.md` en el cierre.

## Fases

### Fase A — Raíz inyectable, CLI con `argparse`, helpers y tests base (la más pequeña)

- **Archivos:** `scripts/check_docs.py`, `tests/test_check_docs.py` (nuevo), `pyproject.toml`.
- **Cambios exactos:**
  - Quitar `os.chdir(REPO_ROOT)` y el `import os`. `REPO_ROOT` se conserva solo como valor por defecto de `--root`.
  - `read(root: Path, rel: str) -> str`. Las cuatro reglas pasan a `rule_x(root: Path, errors: list[str]) -> None` y
    `estado(root: Path) -> int`; **misma detección que hoy** (R2–R4 se cambian en Fase B, `--estado` en C).
  - `class Section(NamedTuple): num: str; title: str; start: int; end: int` y `sections(text: str) -> list[Section]`
    a partir de `^## (\d+[a-z]?)\. (.*)$` (los `###` pertenecen al `##` anterior; `end` = línea anterior al siguiente
    `##` o última línea). `lines_inside(root, rel, nums: set[str]) -> list[tuple[int, str]]` y `lines_outside(...)`.
  - `CITATION_RE` y `strip_citations(line: str) -> str` (especificación §0.7), con o sin backticks:
    `` `?\((?:CONTEXT §\d+[a-z]?|PLAN §\d+[a-z]?|backlog (?:[A-Z]+-\d+|[A-Z]\d+)|ADR-\d{4}|AGENTS §\d+[a-z]?|README de sesiones|bitácora \d{4}-\d{2}-\d{2}|docs/deuda/(?:[A-Z]+-\d+|[A-Z]\d+)/)\)`? ``.
  - `main(argv: list[str] | None = None) -> int` con `argparse.ArgumentParser`: `--root` (`type=Path`, default
    `REPO_ROOT`) y `--estado` (`store_true`). `--copias`, `--huerfanas` y `--cierre` **no se declaran aún** (los
    declaran C y D); hasta entonces terminan con exit 2 como cualquier flag desconocido (hoy: exit 0 silencioso).
    `parse_args` deja propagar `SystemExit(2)`; `if __name__ == "__main__": sys.exit(main(sys.argv[1:]))`.
  - Mensaje de éxito: `Documentación coherente (reglas: R1 comandos, R2 días, R3 bloques, R4 decisiones).`
    (en B se renombra R2 y en D se añade el sufijo de `--cierre`). Formato de error unificado desde ya:
    `archivo:línea: R#: mensaje — "texto[:80]"` (R1 no lleva línea).
  - Docstring del módulo en estilo Google con las reglas numeradas R1–R4 y el uso (`--root`, `--estado`).
  - `pyproject.toml:90` → `files = ["app", "scripts/check_docs.py"]`.
  - `tests/test_check_docs.py`: cabecera `import importlib, sys; sys.path.insert(0, str(ROOT / "scripts"));
    check_docs = importlib.import_module("check_docs")` (evita `E402`); helper `make_repo(tmp_path, files: dict[str, str]) -> Path`
    (especificación §4: PLAN con tabla de bloques `B-FUTURO`/`B-HIGIENE` y un `## 3.`, CONTEXT con `## 2.` y fila
    `| **Deadline** | **11 de enero de 2027** … |`, backlog con tabla con columna `Decisión`, `docs/sesiones/README.md`
    con tabla de comandos, `.claude/commands/*.md` coherentes con ella). Las claves de `files` son rutas relativas a la
    raíz del fixture (`"docs/PLAN.md"`); el valor sobrescribe el contenido mínimo de esa ruta.
- **Tests (RED primero):**
  1. `test_unknown_flag_exits_2`: `pytest.raises(SystemExit)` con `main(["--inexistente"])`, `code == 2`; ídem
     `main(["--copias"])` (hoy devolvería 0). La mitad `--copias` de este test se retira en la Fase C, cuando el
     flag pasa a ser válido; queda `--inexistente`.
  2. `test_sections_numbers_and_bounds`: texto con `## 0.`, `## 2.`, `## 2b.`, `### sub`, `## 3.` → `num` en
     `["0", "2", "2b", "3"]`, el `###` queda dentro de `2b`, `end` del último = última línea.
  3. `test_lines_outside_and_inside_section_3`: líneas dentro/fuera con sus números 1-based.
  4. `test_strip_citations` (parametrizado con las 8 formas, con y sin backticks) y
     `test_strip_citations_keeps_non_citations` (`(ver arriba)` y `(bitácora ayer)` quedan).
  5. `test_rule_commands_both_directions`: fixture con `/foo.md` en disco sin fila (1 error con `R1`) y fila
     `| `/bar` |` sin archivo (1 error con `R1`).
  6. `test_main_on_fixture_root_is_green`: `main(["--root", str(root)]) == 0` sobre `make_repo` mínimo.
  7. `test_estado_accepts_root`: `main(["--estado", "--root", str(root)]) == 0` con `docs/deuda/X/plan.md`.
  8. `test_repo_is_green`: `main(["--root", str(REPO_ROOT)]) == 0` sobre el repo real (sin `git`).
- **Criterio de aceptación:** los 8 tests en verde; `venv/Scripts/python.exe scripts/check_docs.py` exit 0 desde
  cualquier cwd; `… --copias` exit 2 con mensaje de uso; `grep -n "os.chdir" scripts/check_docs.py` vacío;
  `venv/Scripts/python.exe -m mypy scripts/check_docs.py` → 0 errores y total de la compuerta ≤ 44; ruff 0 en los dos
  archivos; `scripts/check.py` con el mismo RESUMEN que la línea base (ruff format ✘ 27, ruff ✘ 362, mypy ✘ 44,
  import-linter ✔ 4, docs ✔, pytest ✔ 145 + 8).
- **Fuera de alcance de esta fase:** cambiar qué detecta cualquier regla; `--copias`, `--huerfanas`, `--cierre`;
  el caso `null` de `--estado`.
- **Commit:**
  ```
  refactor(flow): make check_docs.py testable with --root and reject unknown flags

  The docs gate could not be tested: it ran os.chdir(REPO_ROOT) at import
  time and every rule read literal paths, so no rule could run against a
  fixture. It also ignored unknown flags: `--copias` returned exit 0 with
  the old success message, which would let a closing ritual believe it was
  green before the flag existed (verificacion.md, AF-01).

  - scripts/check_docs.py: every rule takes `root: Path`; new `sections`,
    `lines_inside/outside` and `strip_citations` helpers (ADR-0008 point 3
    citation forms) for the rules of the next phases; argparse CLI with
    `--root` and `--estado`, unknown flags exit 2. Detection is unchanged.
  - tests/test_check_docs.py: first tests of the script, on tmp_path
    fixtures plus `test_repo_is_green` on the real repo.
  - pyproject.toml: the script enters mypy.files (ADR-0005 ratchet).

  Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
  ```

### Fase B — Reglas bloqueantes R2–R5

- **Archivos:** `scripts/check_docs.py`, `tests/test_check_docs.py`.
- **Cambios exactos:**
  - `SCOPE_FILES(root) -> list[str]`: `docs/CONTEXT.md`, `docs/PLAN.md`, `docs/backlog.md`, `docs/sesiones/*.md`
    ordenados (especificación §0.1). Solo estos archivos para R2, R3, R5 (y R8/R9 en C, R6 en D).
  - **R2** `rule_no_schedule_days` sustituye a `rule_no_days`: regex de §2 R2 con `re.IGNORECASE`; CONTEXT, backlog y
    `docs/sesiones/*.md` enteros; PLAN con `lines_outside(root, "docs/PLAN.md", {"3"})`; línea con `strip_citations`.
    Mensaje `R2: fecha de cronograma fuera de PLAN §3`.
  - **R3** `rule_blocks`: alcance = `SCOPE_FILES`; regex sin cambios; mensaje `R3: bloque `B-X` no está definido en
    docs/PLAN.md §2b`.
  - **R4** `DECISION_RE` con `QUAL` tal como en §2 R4; `rule_decisions` conserva la partición por ` | ` y la
    localización por encabezado; mensaje `R4: decisión fuera del vocabulario (un bloque, un calificador sin bloques)`.
  - **R5** `rule_deadline`: `DATE_RE` y `TRIGGER_RE` de §2 R5. Dueño: en CONTEXT, primera línea que empieza por
    `| **Deadline** |`; primera `DATE_RE` de esa línea → `(día, mes[:3].lower(), año|None)`; si no hay fila o fecha:
    un error `R5: deadline no legible en CONTEXT §2` y la regla termina. Archivos: PLAN, backlog, `docs/sesiones/*.md`.
    Por cada disparador en la línea sin citas: fechas cuyo `start` esté en `[t.start-40, t.end+40]`; se toma la de
    menor distancia al disparador; si no hay, no se evalúa. Error si día o mes (o año, si lo trae) difieren
    (`R5: fecha de entrega "<texto>" ≠ deadline de CONTEXT §2`) o si la línea **original** no contiene `(CONTEXT §2)`
    (`R5: fecha de entrega sin cita (CONTEXT §2)`).
  - Orden en `main`: R1, R2, R3, R4, R5; mensaje de éxito `(reglas: R1 comandos, R2 fechas de cronograma, R3 bloques,
    R4 decisiones, R5 deadline)`. Docstring del módulo actualizado.
- **Tests (RED primero)** (número de errores + `R#` + `archivo:línea` en el mensaje; nunca el texto completo):
  - R2 falla: backlog `Corte el jueves 29 a las 18:00` (1); CONTEXT con `## 8. Próximo paso (sáb 31 oct, cierre)` y
    `2. Lun 2 → vie 6: …` (texto de `git show 2647ea3:docs/CONTEXT.md`, líneas 238 y 253) (2 errores);
    `docs/sesiones/x.md` con `día 11` (1). R2 pasa (0): `sáb 7 h o menos, dom descanso`; `Tope: 15 de diciembre`;
    `24 oct, e4fd14d`; `reunión lun 17:00–18:00`; `(bitácora 2026-10-29)`; `| Lun 2 | …` dentro de PLAN `## 3.`;
    `4 m`, `90 %`, `7 horas`.
  - R3 falla: `docs/sesiones/mentor.md` con `B-INEXISTENTE` (1). Pasa: bloque definido en PLAN citado en sesiones (0).
  - R4 (parametrizado): los 9 "debe fallar" de §2 R4 → 1 error cada uno con `R4` y `docs/backlog.md:N`; los 8 "debe
    pasar" → 0. Incluye el texto viejo de BE-08 (30 oct) y BE-09 (31 oct) tal como lo cita la especificación.
  - R5 falla: `entrega del 7 de noviembre` (1, mensaje contiene `≠`); `entrega el 11 ene` sin cita (1, `sin cita`);
    `**Lun 11 nov — entrega en línea** `(CONTEXT §2)`` (1); CONTEXT sin fila `Deadline` (1, `no legible`). R5 pasa (0):
    `**Lun 11 ene — entrega en línea** `(CONTEXT §2)``; `…integración con María Paula; entrega | …`; `colchón 1 más el
    domingo anterior a la entrega`; `corte de código el 18 dic y entrega el 11 ene `(CONTEXT §2)``; la fila AF-01 de
    `docs/backlog.md` de hoy copiada literal al fixture (§8.2: disparador y fechas a > 40 caracteres).
  - `test_repo_is_green` sigue en verde con R1–R5.
- **Criterio de aceptación:** tests nuevos en verde; `grep -c "^def rule_" scripts/check_docs.py` = 5;
  `grep -n "rule_no_days" scripts/check_docs.py` vacío; el patrón de la verificación sobre `DECISION_RE` imprime
  `False`; `venv/Scripts/python.exe scripts/check_docs.py` exit 0 sobre el repo; mypy 0 en el script y total ≤ 44;
  ruff 0 en los dos archivos; cobertura ≥ 93 %; import-linter 4 KEPT.
- **Fuera de alcance de esta fase:** R6–R9, `--estado`, cualquier edición de CONTEXT/PLAN/backlog aunque una regla
  nueva los pusiera en rojo (si pasa, la regex se contrasta con la especificación; si la especificación tiene razón, el
  hallazgo va al handoff y David decide).
- **Commit:**
  ```
  feat(flow): enforce ADR-0008 rules R2-R5 in check_docs.py

  check_docs.py verified the symptom, not the principle (ADR-0008,
  context): `rule_no_days` only matched "día N" in two files, blocks were
  not checked in docs/sesiones, DECISION_RE accepted any tail after the
  block (BE-08 sat in two blocks on 30 oct) and nothing compared the
  delivery date against its owner in CONTEXT §2.

  - R2 `rule_no_schedule_days`: weekday or "día" + number, citations
    stripped first, whole CONTEXT/backlog/sesiones and PLAN outside §3.
  - R3 `rule_blocks`: scope extended to docs/sesiones/*.md.
  - R4 `rule_decisions`: exactly one block plus one optional qualifier
    without blocks or vocabulary inside; "Hecho" requires its reference.
  - R5 `rule_deadline`: nearest date within ±40 chars of a trigger must
    equal the CONTEXT §2 deadline and carry the `(CONTEXT §2)` citation.
  - tests: every "must fail"/"must pass" case of especificacion.md §2,
    including the old BE-08/BE-09 rows and CONTEXT §8 header as fixtures.

  Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
  ```

### Fase C — Comandos informativos `--copias`, `--huerfanas` y `--estado` para ítems terminados

- **Archivos:** `scripts/check_docs.py`, `tests/test_check_docs.py`.
- **Cambios exactos:**
  - `--copias [DUEÑO]` (`nargs="?"`, `const=""`): `list_citations(root, prefix: str) -> list[str]` recorre
    `SCOPE_FILES`, imprime `archivo:línea: <cita>: "<texto[:80]>"` por cada `CITATION_RE` cuyo interior (sin backticks ni
    paréntesis) empiece por `prefix`; orden archivo, línea. Exit 0 siempre.
  - `--huerfanas`: `list_orphans(root) -> list[str]`; patrones `DATE_RE`, `\b\d{1,3} %`, `\b\d+ tests\b`, `\b\d+ h\b`,
    `\b\d+ m\b` sobre la línea sin citas y solo si la original no contiene ninguna cita; excluye con `lines_outside`
    CONTEXT §0, §2, §4, §6 y PLAN §3, §6, §7, las líneas que contienen `**Versión ` y los archivos fuera de `SCOPE_FILES`.
    Imprime `archivo:línea: candidato a hecho duro sin cita: "<fragmento>" — "<línea[:80]>"`. Exit 0 siempre.
    (La especificación §3 R9 nombra CONTEXT §2, §4, §6; §0 se añade porque es el mapa hecho → dueño y lista hechos por
    diseño; si David prefiere la lista literal, se quita `"0"` y nada más cambia.)
  - `--estado`: `progress.json` se lee con `json.loads` (hoy regex). Si `current_target` es `None` y todas las fases
    tienen `status == "completed"` → `ejecutado (todas las fases); pendiente de PR o mezclado`; en otro caso
    `en ejecución (objetivo: <current_target|?>)`. JSON inválido → `progress.json ilegible`. Resto igual.
  - Los tres flags son mutuamente excluyentes entre sí y con la pasada bloqueante (`add_mutually_exclusive_group`).
- **Tests (RED primero):**
  - `test_copias_lists_all_and_filters`: tres citas en dos archivos (`(CONTEXT §2)`, `` `(PLAN §3)` ``,
    `(ADR-0008)`); sin filtro 3 líneas en orden archivo, línea; con `CONTEXT §2` 1 línea; `main([...]) == 0`.
  - `test_copias_ignores_out_of_scope`: cita en `docs/adr/x.md` no sale.
  - `test_huerfanas_reports_uncited_fact_only`: `cobertura 93 %` sin cita sale; `93 % (PLAN §6)` no; `**Versión 1.0 — 1
    nov 2026.**` no; `93 %` dentro de PLAN `## 6.` no; `main([...]) == 0`.
  - `test_estado_all_completed_and_null_target` (fixture `docs/deuda/X/progress.json` con `current_target: null` y
    dos `completed`) → la salida contiene `ejecutado` y no `objetivo: ?`; `test_estado_in_progress` (target
    `"Fase_B"`) → `objetivo: Fase_B`.
  - `test_estado_on_real_repo_be01`: sobre `REPO_ROOT`, la línea `BE-01:` contiene `ejecutado` (fixture real,
    `docs/deuda/BE-01/progress.json`).
- **Criterio de aceptación:** tests en verde; `venv/Scripts/python.exe scripts/check_docs.py --estado | grep "objetivo: ?"`
  vacío; `… --copias "CONTEXT §2"` lista al menos `docs/PLAN.md:89`; `… --huerfanas` exit 0; trinquete igual que B.
- **Fuera de alcance de esta fase:** R6, R7, `--cierre`; convertir huérfanas en error; editar `docs/sesiones/README.md:41`.
- **Ajuste de tests de la Fase A:** `test_unknown_flag_exits_2` pierde la mitad `main(["--copias"])` (ahora válido) y
  conserva `--inexistente`.
- **Commit:**
  ```
  feat(flow): add --copias and --huerfanas to check_docs.py and fix --estado for finished items

  ADR-0008 point 6 makes the closing ritual list the citations of every
  owner touched that day; until now that was a manual grep (README of
  sessions, step 3) and orphan facts had no mechanism at all (addendum,
  point 3). `--estado` also reported "en ejecución (objetivo: ?)" for
  BE-01, whose four phases are completed and whose target is null
  (CONTEXT §8 point 4).

  - `--copias [owner]`: fixed-form citations per file and line, optionally
    filtered by owner prefix. Informative, exit 0.
  - `--huerfanas`: candidate hard facts without a citation on the line,
    excluding the owner sections. Noisy by design, never exit 1.
  - `--estado`: progress.json parsed as JSON; null target with all phases
    completed reads "ejecutado; pendiente de PR o mezclado".

  Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
  ```

### Fase D — `--cierre`: encabezado de versión (R6) y filas cerradas sin marca (R7)

- **Archivos:** `scripts/check_docs.py`, `tests/test_check_docs.py`.
- **Cambios exactos:**
  - `git_last_commit_date(root: Path, rel: str) -> date | None` (`subprocess.run(["git", "log", "-1", "--format=%cs",
    "--", rel], cwd=root, capture_output=True, text=True)`; `None` si `returncode != 0`, salida vacía o
    `FileNotFoundError`) y `git_is_dirty(root, rel) -> bool | None` (`git status --porcelain -- rel`).
  - **R6** `rule_version_header(root, errors, warnings, *, last_commit_date=git_last_commit_date, is_dirty=git_is_dirty)`
    sobre `SCOPE_FILES`; `VERSION_RE` de §3; fecha del encabezado → `date`; `last is None` → aviso `no verificable`;
    encabezado < último commit → error `R6: encabezado de versión (<fecha>) anterior al último commit (<fecha>)`; sin
    encabezado y último commit > `date(2026, 10, 28)` → error `R6: sin línea de versión (ADR-0007)`; `is_dirty` → aviso
    `cambios sin commitear: la versión se sube en el cierre` (nunca error, nunca suspende la comparación).
  - **R7** `rule_closed_days_marked(root, errors, *, today=date.today)`: tablas de `lines_inside(root, "docs/PLAN.md",
    {"3"})`; columna `Cierre` por encabezado; primera celda con `DAY_CELL_RE` de §3; **el estado de mes y año se reinicia en cada tabla** (la
    primera fila de cada tabla nombra el mes: `Vie 23 oct`, `Dom 1 nov`); mes heredado de la última fila que lo
    nombra; año inicial = el de la línea de versión de PLAN; si el mes es menor que el anterior, año + 1; filas que no
    casan (`(se fecha …)`, encabezado, separador) se ignoran; fecha < `today()` y `Cierre` sin `^[✔◐✘] \d{1,2}$` →
    error `R7: fila de PLAN §3 cerrada sin marca en Cierre`.
  - `--cierre` (`store_true`): corre R1–R5 **y** R6–R7; los avisos se imprimen bajo `Avisos:` y no cambian el exit;
    mensaje de éxito añade `+ cierre: R6 versión, R7 cierres`.
- **Tests (RED primero)** (todos con funciones inyectadas; ninguno ejecuta `git`):
  - R6 falla: encabezado `31 oct 2026` con `last_commit_date` → `2026-11-01`, `is_dirty` → `False` (1 error, 0 avisos) y
    con `is_dirty` → `True` (1 error, 1 aviso); `mentor.md` sin versión con último commit `2026-10-31` (1 error).
    R6 pasa: `1 nov 2026` con `2026-11-01` (0); el mismo con `is_dirty` → `True` (0 errores, 1 aviso); sin versión con
    último commit `2026-10-27` (0); `last_commit_date` → `None` (0 errores, 1 aviso con `no verificable`).
  - R7 falla: `today` → `2026-11-03`, tabla con `| Lun 2 | … | |` bajo `## 3.` (1 error con `docs/PLAN.md:N`).
    R7 pasa: `today` → `2026-11-01` con la tabla de Bogotá copiada de PLAN de hoy (fila del día sin marca → 0); la tabla
    "Días cerrados" de hoy (0); `| Jue 31 dic | … | ✔ 31 |` seguida de `| Sáb 2 ene | … | ✔ 2 |` con versión de 2026 y
    `today` → `2026-12-31` (0: el año salta a 2027); fila `| (se fecha el vie 6) | | |` ignorada.
  - `test_cierre_flag_runs_r6_r7`: `main(["--cierre", "--root", root])` con las funciones reales sobre un fixture sin
    `.git` → exit 0 y aviso `no verificable` (git devuelve error en un directorio sin repo → `None`); no se ejecuta
    sobre el repo real para no depender del estado del árbol.
- **Criterio de aceptación:** tests en verde; `venv/Scripts/python.exe scripts/check_docs.py` (sin `--cierre`) no
  ejecuta `git` (verificable con `grep -n "subprocess" scripts/check_docs.py` solo dentro de las dos funciones `git_*`);
  `… --cierre` sobre el repo real exit 0 hoy (contrastado en el análisis); trinquete igual que B y C.
- **Fuera de alcance de esta fase:** comprobar que exista `docs/bitacora/AAAA-MM-DD.md` por cada marca (opcional en
  la especificación; se deja para `AF-02` si David lo quiere); meter `--cierre` en `scripts/check.py`.
- **Commit:**
  ```
  feat(flow): add --cierre to check_docs.py with version-header and closed-day rules

  ADR-0007 asks that a living document's version line never predate its
  last commit, and ADR-0008 point 6 that every PLAN §3 row already in the
  past carries a closing mark. Both depend on git and on today's date, so
  they run only under `--cierre` (closing ritual) and never in the default
  gate, which stays deterministic (ADR-0001).

  - R6 `rule_version_header`: header date >= last commit date; files
    without a header are an error only if committed after 28 oct 2026;
    dirty tree and missing git are warnings, never a false red.
  - R7 `rule_closed_days_marked`: rows of PLAN §3 dated before today need
    `[✔◐✘] N` in `Cierre`; month inherited per table, year by monotony.
  - git and clock are injected so the tests never spawn a process.

  Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
  ```

## Verificación final

```bash
# Reglas presentes (esperado: 7 = R1..R7) y símbolos de la deuda ausentes (esperado: vacío)
grep -c "^def rule_" scripts/check_docs.py
grep -n "os.chdir\|def read(p: str)\|rule_no_days" scripts/check_docs.py
# Reglas y flags exigidos (esperado: todos con resultado)
grep -n "rule_no_schedule_days\|rule_deadline\|rule_version_header\|rule_closed_days_marked\|strip_citations\|def sections\|--root\|--copias\|--huerfanas\|--cierre" scripts/check_docs.py
grep -n '"docs/sesiones' scripts/check_docs.py
# DECISION_RE estricto (esperado: False)
venv/Scripts/python.exe -c "import sys; sys.path.insert(0,'scripts'); import check_docs as m; print(bool(m.DECISION_RE.match('**Entra · \`B-ORDEN\` (backend) y \`B-FE-RESERVAS\` (cliente)**')))"
# Flags desconocidos (esperado: exit 2) y comandos nuevos (esperado: exit 0)
venv/Scripts/python.exe scripts/check_docs.py --inexistente; echo "exit $?"
venv/Scripts/python.exe scripts/check_docs.py; echo "exit $?"
venv/Scripts/python.exe scripts/check_docs.py --copias "CONTEXT §2"; echo "exit $?"
venv/Scripts/python.exe scripts/check_docs.py --huerfanas; echo "exit $?"
venv/Scripts/python.exe scripts/check_docs.py --cierre; echo "exit $?"
# --estado sin "objetivo: ?" (esperado: vacío)
venv/Scripts/python.exe scripts/check_docs.py --estado | grep "objetivo: ?"
# Tests y mypy sobre el script
ls tests/test_check_docs.py
grep -n '^files = \[' pyproject.toml          # esperado: files = ["app", "scripts/check_docs.py"]
venv/Scripts/python.exe -m pytest tests/test_check_docs.py -q
venv/Scripts/python.exe -m mypy scripts/check_docs.py
# Compuerta completa (línea base: ruff 362 · mypy 44 · 4 KEPT · 93 % · docs ✔ · 145 + N tests)
venv/Scripts/python.exe scripts/check.py
```

## Residuales

- `lint-imports` no vuelca su texto dentro de la sección `=== import-linter ===` cuando `check.py` se redirige a
  fichero (verificación, "Rincones"). Fuera de AF-01 → fila `AF-0x` en `docs/backlog.md` §E.
- El CI (`.azure-pipelines/ci-pipeline.yml`) ejecuta solo `pytest -v`, ni `check.py` ni `check_docs.py` → ya es `B-CI`.
- `tests/conftest.py` aplica dos fixtures `autouse` (una asíncrona que crea/borra tablas) a tests puros como los de
  `check_docs` → `B-TESTS` (especificación §8.4).
- Cierre documental del ítem (lo hace la sesión que cierra, no una fase): `docs/backlog.md:141` (fila AF-01 → `Hecho`),
  `docs/PLAN.md:48` (celda `B-CHECK-DOCS`), `docs/sesiones/README.md:41` (sustituir el `grep` provisional por
  `--copias`), `docs/CONTEXT.md:261` (quitar "`--estado` no distingue mezclado"), bitácora `2026-11-01` (§7 de la
  especificación), y una fila `AF-02` si queda fase sin auditar o si se quiere la comprobación opcional de R7
  (`docs/bitacora/AAAA-MM-DD.md` por marca).
- Los cuatro prompts de `docs/sesiones/` no tienen línea de versión (último commit 25–26 oct 2026): válido hoy por
  ADR-0007 punto 5; la primera edición de cualquiera de ellos debe nacer como `1.0` o R6 lo marcará bajo `--cierre`.
- `rule_decisions` asume que ninguna celda contiene ` | ` interno (docstring actual); se conserva. `estado()` decide
  `PASS`/`con gaps` mirando la última línea de `gaps.md`; se conserva.

## Referencias

Solo biblioteca estándar de Python 3.14 (decisión bloqueada 1); no hubo API con duda ni aviso de deprecación, por lo que
no se consultó Context7. Documentación oficial de los módulos usados:

- `argparse` · Python 3.14 · https://docs.python.org/3.14/library/argparse.html (`nargs="?"`, `const`,
  `add_mutually_exclusive_group`; `parse_args` termina con exit 2 ante argumentos no reconocidos)
- `re` · Python 3.14 · https://docs.python.org/3.14/library/re.html (lookaheads negativos, `re.IGNORECASE`)
- `json` · Python 3.14 · https://docs.python.org/3.14/library/json.html (`json.loads`, `JSONDecodeError`)
- `subprocess` · Python 3.14 · https://docs.python.org/3.14/library/subprocess.html (`run(..., capture_output=True,
  text=True, cwd=...)`)
- `datetime` · Python 3.14 · https://docs.python.org/3.14/library/datetime.html (`date.fromisoformat`, `date.today`)
- `typing.NamedTuple` · Python 3.14 · https://docs.python.org/3.14/library/typing.html#typing.NamedTuple

**ADR propuesto:** ninguno. Las decisiones del ítem están registradas en ADR-0008 (reglas, forma de la cita, alcance),
ADR-0007 (encabezado de versión), ADR-0001 (determinismo: R6/R7 fuera de la compuerta por defecto) y en
`especificacion.md` §0. Si David quiere que la separación "compuerta por defecto determinista / `--cierre` con git y
reloj" quede como decisión formal, sería un addendum a ADR-0008 redactado en el cierre, no por el ejecutor.
