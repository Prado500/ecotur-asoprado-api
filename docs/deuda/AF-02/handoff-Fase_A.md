# Handoff — AF-02 Fase_A

**Commit:** `dc57ac0` · `fix(flow): read --estado verdict from the last audit block of gaps.md`
**Rama:** `item/AF-02`. **Base develop:** `e4e7d43`; `git fetch origin` refrescó, y `origin/develop` y el `merge-base`
dieron `e4e7d43`. E0 leída y aplicada (P2 no se codifica, se declara en la docstring).

## Archivos tocados

`git show --stat --format= dc57ac0`:

```
 scripts/check_docs.py    |  61 +++++++++++++--
 tests/test_check_docs.py | 192 +++++++++++++++++++++++++++++++++++++++++++++++
 2 files changed, 247 insertions(+), 6 deletions(-)
```

`git show dc57ac0 -- tests/test_check_docs.py`: 0 líneas borradas; ningún test existente cambia.

## Compuerta

Antes de tocar nada (`9121f27`), `./venv/Scripts/python.exe scripts/check.py`, exit 1: `57 files already formatted`,
`Found 9 errors.`, `Found 5 errors in 4 files (checked 35 source files)`, `Contracts: 4 kept, 0 broken.`,
`Total coverage: 96.11%`, `438 passed, 5 warnings in 12.70s`. Coincide con la línea base de `verificacion.md`.

Después, con el contenido exacto del commit (árbol sin commitear aún), exit 1:

```
Required test coverage of 92.0% reached. Total coverage: 96.11%
526 passed, 5 warnings in 19.28s
--- pytest + cobertura: OK en 22.3s

=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff check, mypy
```

```
57 files already formatted
Found 9 errors.
Found 5 errors in 4 files (checked 35 source files)
Contracts: 4 kept, 0 broken.
TOTAL                                        943     23    138     19  96.11%
```

**Conjunto de ruff (9, todos I001, medido):** `app\api\dependencies.py:1:1`, `app\api\routers\audit.py:1:1`,
`app\core\email.py:1:1`, `app\db\database.py:1:1`, `app\repositories\user_repository.py:1:1`, `app\schemas\audit.py:1:1`,
`app\services\audit_service.py:1:1`, `app\services\user_service.py:1:1`, `tests\test_user_service.py:3:1`.

**Conjunto de mypy (5, medido):** `app\db\database.py:11`, `app\core\security.py:71`, `app\core\security.py:87`,
`app\services\user_service.py:124`, `app\api\dependencies.py:95`.

Ambos conjuntos son exactamente los de la decisión 7. Ninguno está en los archivos de esta fase.

Archivos tocados, por separado:

```
$ ruff format --check scripts/check_docs.py tests/test_check_docs.py
2 files already formatted
$ ruff check scripts/check_docs.py tests/test_check_docs.py
All checks passed!
$ mypy scripts/check_docs.py
Success: no issues found in 1 source file
$ mypy tests/test_check_docs.py
Success: no issues found in 1 source file
```

## RED y verde

- RED, solo tests escritos: `88 failed, 148 passed in 3.79s`.
- Verde: `236 passed in 4.60s`.

## Mutantes

Copia nueva en el scratchpad (`scripts/check_docs.py`, `tests/test_check_docs.py`, `docs/`, `.claude/commands/`), Python del
venv por ruta absoluta, `pytest tests/test_check_docs.py -q --tb=no -p no:cacheprovider`, cada mutante por separado sobre el
script sin mutar.

| Id | Cambio | Salida medida | Plan |
|---|---|---|---|
| M0 | sin mutar (al empezar y al terminar) | `236 passed` / `236 passed` | 236 passed |
| MA1 | `return "pass"` al entrar | `49 failed, 187 passed` | 49 |
| MA2 | `return "gaps"` al entrar | `63 failed, 173 passed` | 63 |
| MA3 | el `append` de `estado()` pasa a la sentencia `pass` | `10 failed, 226 passed` | 10 |
| MA4 | `starts[-1]` → `starts[0]` | `3 failed, 233 passed` | 3 |
| MA5 | sin `\b` | `1 failed, 235 passed` | 1 |
| MA6 | sin `^` y con `.search` | `2 failed, 234 passed` | 2 |
| MA7 | `reversed(lines[…])` | `2 failed, 234 passed` | 2 |
| MA8 | solo `except ValueError` | `1 failed, 235 passed` | 1 |
| MA9 | solo `except OSError` | `2 failed, 234 passed` | 2 |
| MA10 | sin `if not text.strip()` | `4 failed, 232 passed` | 4 |
| MA11 | buscar en `lines` enteras | `4 failed, 232 passed` | 4 |
| MA12 | sin `if not starts` | `1 failed, 235 passed` | 1 |
| MA13 | lógica antigua al entrar en la función | `46 failed, 190 passed` | **48** |
| MA14 | `AUDIT_BLOCK_RE` = `^## ` | `1 failed, 235 passed` | 1 |
| MA15 | etiquetas `pass` y `gaps` intercambiadas | `1 failed, 235 passed` | 1 |
| MA16 | `re.I` en `VERDICT_RE` | `1 failed, 235 passed` | 1 |

Los 16 mueren.

## `--estado` y verificaciones

`./venv/Scripts/python.exe scripts/check_docs.py --estado` sobre el repo, exit 0:

```
A2: verificado
A9: verificado → planeado → ejecutado (todas las fases); pendiente de PR o mezclado → handoffs: Fase_A, Fase_B → última auditoría: PASS
AF-01: verificado → planeado → ejecutado (todas las fases); pendiente de PR o mezclado → handoffs: Fase_A, Fase_B, Fase_C, Fase_D → última auditoría: PASS
AF-02: verificado → planeado → en ejecución (objetivo: Fase_A)
AF-05: verificado → planeado → ejecutado (todas las fases); pendiente de PR o mezclado → handoffs: Fase_A → última auditoría: PASS
BE-01: verificado → planeado → ejecutado (todas las fases); pendiente de PR o mezclado → handoffs: Fase_A, Fase_B, Fase_C, Fase_D → última auditoría: PASS
BE-02: verificado → planeado → ejecutado (todas las fases); pendiente de PR o mezclado → handoffs: Fase_A → última auditoría: PASS
BE-07: verificado
BE-15: verificado → planeado → ejecutado (todas las fases); pendiente de PR o mezclado → handoffs: Fase_A, Fase_B, Fase_C, Fase_D, Fase_D_bis, Fase_E, Fase_F → última auditoría: PASS
BE-33: verificado → planeado → ejecutado (todas las fases); pendiente de PR o mezclado → handoffs: Fase_A, Fase_B, Fase_C, Fase_D → última auditoría: PASS
S1: verificado → planeado → ejecutado (todas las fases); pendiente de PR o mezclado → handoffs: Fase_A, Fase_B, Fase_C → última auditoría: PASS
SEC1: verificado → planeado → ejecutado (todas las fases); pendiente de PR o mezclado → handoffs: A → última auditoría: PASS
```

Antes de la fase, A9, AF-05, BE-01 y SEC1 decían `con gaps` (medido). V8: `9` y `0`. V1: `0`. V4: `0`. V7: `0` y `0`. V10: vacío.
V3, V5, V6, V9 y V11 son de la verificación final, tras la fase B: no aplican aún.

Fixture por CLI (A con PASS, B vacío, C con GAPS), `--estado --root <fixture>`, exit 0, sin traceback:

```
A: última auditoría: PASS
B: última auditoría: ilegible
C: última auditoría: con gaps
```

## Desviaciones respecto al plan

1. **MA13 da 46, no 48.** Muere igual. Lo apliqué como `text = path.read_text(...)` y `return "pass" if "PASS" in
   text.splitlines()[-1] else "gaps"` al entrar en la función. El plan no da el texto del mutante ni el de sus fixtures, así que
   no sé qué diferencia produce los 2 casos. No cambié tests para acercarme a 48.
2. **RED: no "todos por función ausente".** De los 88, 86 fallan con `AttributeError` por `read_last_audit` y 1 por
   `AUDIT_LABELS`. `test_estado_prints_every_item_and_never_raises` falla con `IndexError` en el `check_docs.py:525` antiguo, el
   traceback que esta fase corrige. El conteo sí coincide.
3. **Docstring de `estado()` (E0.2).** E0 da el texto en español y con "Siempre 0". Lo escribí en inglés (AGENTS §4, y el resto de
   esa docstring lo está) y sin la cadena `Always 0`, porque V4 exige que esa cadena no exista. El contenido es el de E0: 0, con
   la excepción declarada del `progress.json` que el sistema operativo impide leer. Prevalece sobre el texto de `:497` del cuerpo.
4. **`scripts/check_docs.py` da +55/−6 (`git diff --numstat`), no +51/−4** como estima "Orden". La docstring de E0 ocupa más
   líneas que el texto de `:497`; es mi explicación, no la medí contra la sonda del plan.
5. **Añadidos en los tests que el plan no nombra:** la constante `_REAL_AUDITED_ITEMS`, `captured.err == ""` en
   `test_estado_prints…`, y `assert separator == next_block` en `test_read_last_audit_real_block_without_verdict` (si el corte
   real desapareciera, el test falla en vez de pasar en falso). Los conteos no cambian.
6. **Lectura de MA3:** "pasa a `pass`" lo interpreté como la sentencia de Python; da los 10 del plan. Con
   `AUDIT_LABELS["pass"]` serían menos fallos por construcción (no lo medí).

## Residuales

- **`scripts/check_docs.py:19`** dice `Comandos informativos (exit 0 siempre; …)` y cubre a `--estado`: contradice la excepción que
  declara E0.2. No estaba en los cambios exactos del plan y no lo toqué. Destino sugerido: una línea en la fase B o en AF-08.
- `docs/CONTEXT.md:294` queda obsoleta con esta fase; el plan la asigna a la sesión de cierre. No la toqué.
- El hook `ruff_on_edit` también corre sobre archivos del scratchpad: señaló E501 en el script de mutantes, que no está en el repo.
- Un comando mío con `rm -rf` sobre una carpeta del scratchpad fue denegado por permisos. Lo repetí sin `rm`, sobre una carpeta nueva.

## Checklist `test-sanitizer` (solo los estándares)

Sin mocks. Fixtures con `make_repo` y helpers locales del módulo. Nombres en inglés; las líneas en español son datos de entrada
copiados de `gaps.md` reales, no aserciones. Se afirma con `STATE_AUDIT`, `AUDIT_LABELS` y los literales `AuditVerdict`. Puntos 4 y 5
(contratos JSON, ABAC) no aplican. Nada reescrito.

## Medido y leído

**Medido:** compuerta antes y después, RED, verde, mutantes, `--estado` antes y después, fixture CLI, V1, V4, V7, V8, V10, ruff y
mypy de los dos archivos, stat del commit.
**Solo leído:** los números de la columna "Plan" y la tabla de los 9 reales con sus líneas; los comprobé solo por la salida de
`--estado`, salvo A9 y AF-01, cuyas líneas de veredicto vi con `grep`.

## Dudas

Ninguna bloqueante. La fase B no se ha tocado.
