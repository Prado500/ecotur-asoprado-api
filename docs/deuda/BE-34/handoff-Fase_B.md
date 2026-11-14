# Handoff — BE-34 · Fase B (ADR-0015)

- Commit de la fase: `b08491b` — `docs(adr): add ADR-0015, the first superadmin comes from a manual command` (mensaje
  exacto del plan, trailer `Co-Authored-By` incluido; comparado con `diff` contra el bloque "Commit" de la fase B: solo
  difiere la línea en blanco final que añade `git log --format=%B`).
- Rama: `item/be-34`, sobre `4b2230a` (plan aprobado entero: E0, E1, E2, E3).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 14 nov 2026.
- Enmiendas que aplican: E0 fija la fecha de la línea "Estado" en **13 nov 2026**; E0.3/E2 (punto 1) fijan la cifra 675
  en el texto dictado (ya estaba en el cuerpo del plan, l. 299). Nada más de B cambia por E1–E3.

## Ritual de arranque

- `git status --short`: limpio. HEAD `4b2230a`. `current_target` = `Fase_B`. `gaps.md`: Fase A PASS, 0 bloqueantes.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `4f10660`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `4f10660`; `Base develop` de `verificacion.md` = `4f10660`.
- Compuerta antes de tocar nada (exit 0), igual a la fila A del plan:
  `61 files already formatted` · `All checks passed!` · `Success: no issues found in 56 source files` ·
  `Contracts: 4 kept, 0 broken.` · `639 passed, 8 warnings` · `TOTAL 965 19 136 16 96.82%`.

## Archivos tocados (el único de la fase)

`git show --stat --format= b08491b`:

```
 docs/adr/0015-bootstrap-del-primer-superadmin.md | 76 ++++++++++++++++++++++++
 1 file changed, 76 insertions(+)
```

`git show --numstat --format= b08491b` → `76	0	docs/adr/0015-bootstrap-del-primer-superadmin.md`.

Cómo se escribió: el bloque dictado (plan, l. 228-303) se extrajo con `sed`, quitando los dos espacios de sangría del
bloque de lista, y `<FECHA>` se sustituyó por `13 nov 2026`. Comprobación:
`diff <(sed -n '228,303p' plan.md | sed 's/^  //') docs/adr/0015-bootstrap-del-primer-superadmin.md` → una sola
diferencia, la línea 3:

```
< - **Estado:** aceptado (David, <FECHA>, al aprobar el plan de BE-34)
> - **Estado:** aceptado (David, 13 nov 2026, al aprobar el plan de BE-34)
```

Codificación: `UTF-8 text`, 0 `\r` (LF), termina en `\n`. La cifra de la Evidencia es `de 638 a 675 tests` (E0.3/E2).

## Tests (RED → GREEN)

No aplica (documento, plan: "Tests (RED primero): no aplica"). Sin mutantes para esta fase. `test-sanitizer`: no aplica,
no hay pruebas nuevas.

## Compuerta de salida (`./venv/Scripts/python.exe scripts/check.py`, exit 0)

Líneas clave:

```
61 files already formatted
All checks passed!
Success: no issues found in 56 source files
Contracts: 4 kept, 0 broken.
--- docs (coherencia): OK en 0.1s
TOTAL                                        965     19    136     16  96.82%
639 passed, 8 warnings in 22.91s
```

Bloque RESUMEN literal:

```
=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

Frente a la fila B del plan (639 passed · 96,82 % (965) · 61 files · 56 source files · 350 en la copia): igual en todo.
Ratchet: tests 639 = 639, cobertura 96,82 % = 96,82 %, contratos 4 kept = 4, ruff y mypy 0 errores (ningún `.py` tocado).

Suite de la copia (procedimiento común, directorio nuevo `scratchpad/copyB_b08491b`, `git archive HEAD` tras el commit,
sin `test_check*`): `350 passed, 8 warnings in 14.85s`.

## Criterio de aceptación

| Criterio | Medido |
|---|---|
| Compuerta como la fila B | exit 0, `Compuerta superada.`, 639 passed, 96.82 % (965), 61 files, 56 source files, 4 kept, 8 warnings |
| `git show --stat --format= <sha B>` lista solo el ADR | 1 file changed: `docs/adr/0015-bootstrap-del-primer-superadmin.md` |
| La línea "Estado" lleva una fecha real, no `<FECHA>` | `aceptado (David, 13 nov 2026, al aprobar el plan de BE-34)`; `grep FECHA` → 0 |

## Fuera de alcance respetado

`AGENTS.md`, `docs/CONTEXT.md`, el manual técnico (R1, R4, R5) y ADR-0013: sin tocar. Ningún archivo de `app/`, `tests/`
ni de otras fases.

## Residuales y dudas

- Ninguno nuevo. R9 queda resuelto como preveía E2 (punto 1): B se commiteó con la cifra 675.
- `docs/adr/` no tiene índice que actualizar (no hay README en la carpeta); `check_docs` pasó sin cambios.
