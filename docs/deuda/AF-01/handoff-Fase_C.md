# Handoff AF-01 Fase C

Commit: `968dc25` feat(flow): add --copias and --huerfanas to check_docs.py and fix --estado for finished items
Base develop: `2647ea3` (`git fetch origin` hecho; `origin/develop` y `merge-base HEAD origin/develop` coinciden).
Compuerta medida con `venv/Scripts/python.exe scripts/check.py` (plan, decisión 7). El plan se leyó del árbol de
trabajo, con los cambios sin commitear de David (ajustes de B y `scope_files`).

## Archivos tocados
```
 scripts/check_docs.py    | 186 ++++++++++++++++++++++++++++++++++++++++----
 tests/test_check_docs.py | 195 ++++++++++++++++++++++++++++++++++++++++++++++-
 2 files changed, 364 insertions(+), 17 deletions(-)
```
`docs/deuda/AF-01/plan.md` (modificado por David) y `gaps.md` (sin trackear) no se tocaron ni se commitearon.

## Qué cambió
- R8 `list_citations(root, prefix)`: recorre `scope_files`; una entrada `archivo:línea: (cita): "texto[:80]"` por
  cada `CITATION_RE` cuyo interior (sin backticks ni paréntesis) empieza por `prefix`; orden archivo, línea, posición.
- R9 `list_orphans(root)`: `DATE_RE`, `\b\d{1,3} %`, `\b\d+ tests\b`, `\b\d+ h\b`, `\b\d+ m\b` sobre la línea sin citas,
  solo si la original no tiene ninguna cita; excluye CONTEXT §0, §2, §4, §6 y PLAN §3, §6, §7 (`lines_outside`), las
  líneas con `**Versión ` y lo que esté fuera de `scope_files`.
- `--estado`: `read_progress(path) -> Progress(state, target)` con `json.loads`. `done` (target `null` y todas las
  fases `completed`) → `ejecutado (todas las fases); pendiente de PR o mezclado`; `unreadable` → `progress.json
  ilegible`; si no, `en ejecución (objetivo: <target|?>)`.
- CLI: `--estado`, `--copias [DUEÑO]` (`nargs="?"`, `const=""`) y `--huerfanas` en un `add_mutually_exclusive_group`.
  Como la pasada bloqueante solo corre si no hay ninguno, también son excluyentes con ella. Las dos órdenes
  informativas terminan con exit 0.
- Ajuste de A: `test_unknown_flag_exits_2` pierde la mitad `--copias` y conserva `--inexistente`.
- Ajustes de B (gaps de su auditoría): (1) `"4 m, 90 %, 7 horas"` se sustituye por `"dom 90 % de avance"` y
  `"sáb 7 horas o menos"`; (2) `sesiones` → `session_prompts` en `scope_files` y Args/Returns en la docstring de
  `numbered_lines`; (3) se reutiliza `scope_files`. Los tres van en un párrafo propio del cuerpo del commit.
- Docstring del módulo: sección "Comandos informativos" (R8, R9, `--estado`) y uso de los dos flags nuevos.

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
Conteos después: `27 files would be reformatted, 104 files already formatted` · `Found 362 errors.` · `Found 44 errors
in 12 files (checked 34 source files)` · `Contracts: 4 kept, 0 broken.` (vía `venv/Scripts/lint-imports`, porque el
texto no aparece en la sección cuando la salida se redirige; es el residual ya conocido) · `249 passed, 1 warning in
11.81s` · `TOTAL 927 52 134 25 93%`. Antes: 27 · 362 · 44 · 4 kept · 219 passed · 93 %. No empeoró nada.

Archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `2 files already formatted`;
`mypy scripts/check_docs.py` → `Success: no issues found in 1 source file`. Sin CRLF.

RED: `26 failed, 78 passed` antes de implementar. Los 26 fallaron con `AttributeError` porque aún no existían
`list_citations`, `list_orphans`, `read_progress` ni `Progress`. Entre los 78 que pasaban están los 3 casos de
`test_informative_flags_are_mutually_exclusive`: antes salían con exit 2 porque `--copias` y `--huerfanas` todavía eran
flags desconocidos, no porque se comprobara la exclusión; después de implementar sí la comprueban. También pasaban los
casos nuevos de R2, porque el lookahead ya existía: ahora protegen contra quitarlo (mutantes `%` y `horas` del gap de B).
Después: `104 passed` en `tests/test_check_docs.py` (74 de A+B, +2 casos de R2 −1 sustituido, +29 de C).

## Criterio de aceptación
- `venv/Scripts/python.exe scripts/check_docs.py --estado | grep "objetivo: ?"` → vacío. La línea de BE-01 es
  `BE-01: verificado → planeado → ejecutado (todas las fases); pendiente de PR o mezclado → handoffs: Fase_A, Fase_B,
  Fase_C, Fase_D → última auditoría: con gaps`.
- `… --copias "CONTEXT §2"` → 15 líneas, entre ellas `docs/PLAN.md:89: (CONTEXT §2): "- **Lun 11 ene — entrega en
  línea** …"`; exit 0.
- `… --huerfanas` → exit 0, 48 candidatos sobre el repo real. `… --copias` sin filtro → 53 citas.
- `… --inexistente` → exit 2 con el uso; `… --estado --copias` → exit 2 (`not allowed with argument --estado`).
- `… check_docs.py` sin flags → exit 0, mismo mensaje de éxito que en B.
- Trinquete igual que en B: 27 · 362 · 44 · 4 KEPT · 93 %.

## Desviaciones e interpretaciones (para el auditor)
1. **`--estado` sin afirmar sobre texto en español (AGENTS §5).** El plan pide que la salida "contenga `ejecutado` y no
   `objetivo: ?`" y que `objetivo: Fase_B` aparezca. Para no afirmar sobre texto en español, el estado se calcula en
   `read_progress`, que devuelve `Progress(state, target)` con estados en inglés (`done` / `running` / `unreadable`), y
   los tests afirman sobre ese valor. Sobre la salida de `main` solo se comprueba lo que no es texto en español: que la
   línea del ítem exista, que no contenga `?` en el caso terminado y que contenga el código `Fase_B` en el caso en
   curso. En `BE-01` real se hace lo mismo. `read_progress` y `Progress` no estaban en el plan: es la función mínima
   que permite probar esto sin afirmar sobre el texto.
2. **`target: null` sin fases** cuenta como `running`, no como `done`. Si no hay fases, "todas las fases completed" se
   cumpliría sin que haya nada hecho, así que exijo al menos una fase. Hay un test para ese caso.
3. **`--huerfanas`: una entrada por línea**, con el primer fragmento (el de menor posición) como `<fragmento>`. La
   especificación no dice si debe salir una entrada por línea o una por fragmento. Elegí una por línea para no repetir
   la misma línea varias veces en una salida que ya es ruidosa.
4. **Formato de `<cita>` en `--copias`:** se imprime la cita sin backticks y con paréntesis (`(CONTEXT §2)`). El filtro
   se aplica al interior, como dice el plan.
5. **`dest` en inglés** (`citation_owner`, `orphans`) para los flags nuevos (AGENTS §4). Los flags en sí (`--copias`,
   `--huerfanas`) son el contrato de la CLI. `--estado` conserva su `dest` de la Fase A.
6. **Tests extra, ninguno quitado:**
   - `test_informative_flags_are_mutually_exclusive`, 3 casos;
   - `test_copias_lists_every_citation_of_a_line_in_order`;
   - `test_copias_with_unknown_owner_lists_nothing`;
   - `test_huerfanas_patterns_report_first_fragment`, 5 casos, uno por patrón;
   - `test_huerfanas_skips_owner_sections`, 7 casos, uno por sección dueña;
   - `test_huerfanas_reports_non_owner_section`, control positivo en CONTEXT §8;
   - `test_read_progress_edges`, 5 casos: target `null` con fases sin terminar, sin fases, target fijado, JSON
     inválido y JSON que no es un objeto.
   La exclusión de `docs/adr/` en huérfanas se comprueba dentro de `test_huerfanas_reports_uncited_fact_only`.
7. **Trailer del commit:** `Co-Authored-By: Claude Opus 5.5`. Lo fija la atribución del harness, igual que en A y B;
   el plan escribe `Claude Fable 5.1`. El resto del mensaje es el del plan, más el párrafo de los ajustes de B que el
   propio plan pide.
8. Los nombres `test_copias_*`, `test_huerfanas_*` y `test_estado_*` vienen del plan y llevan el nombre del flag, que
   es contrato de la CLI. Siguen el precedente de `test_estado_accepts_root` de la Fase A.

## Residuales / notas
- `--estado` sigue diciendo `última auditoría: con gaps` para BE-01 y AF-01, porque mira solo la última línea de
  `gaps.md`. Es el comportamiento que el plan conserva (Residuales).
- `--huerfanas` da 48 candidatos en el repo real. Lo revisa la sesión que cierra; no es error de la compuerta.
- `scripts/check.py` no se tocó: la compuerta solo ejecuta la pasada bloqueante.
- Al escribir el script de parcheo con un heredoc largo, el envoltorio de la shell falló. Lo escribí en un archivo del
  scratchpad, fuera del repo.
