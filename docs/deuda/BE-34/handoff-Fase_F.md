# Handoff — BE-34 · Fase F (ADR-0016)

- Commit de la fase: `4eba2d2` — `docs(adr): add ADR-0016, every email is stored in lowercase` (mensaje exacto del plan,
  trailer `Co-Authored-By` incluido; comparado con `diff` contra el bloque "Commit" de la fase F, l. 1458-1476, sin
  sangría: solo difiere la línea en blanco final que añade `git log --format=%B`).
- Rama: `item/be-34`, sobre `a631612` (plan aprobado A → G con E0, E2 y E3; E4 añade H, aún no escrita).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 14 nov 2026.
- Enmiendas que aplican: E3 punto 1 fija la fecha de la línea "Estado" en **14 nov 2026**; E3 punto 2 añadió dos líneas
  en "Consecuencias" (85 → 87), ya presentes en el bloque dictado de la fase F. E4 (fase H): nada que hacer en F.

## Ritual de arranque

- `git status --short`: limpio. HEAD `a631612`. `current_target` = `Fase_F`. `gaps.md`: fases A–E PASS, 0 bloqueantes.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `4f10660`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `4f10660`; `Base develop` de `verificacion.md` = `4f10660`.
- Compuerta antes de tocar nada (exit 0), igual a la fila E del plan:
  `67 files already formatted` · `All checks passed!` · `Success: no issues found in 62 source files` ·
  `Contracts: 4 kept, 0 broken.` · `675 passed, 8 warnings` · `TOTAL 1031 17 148 14 97.37%`.

## Archivos tocados (el único de la fase)

`git show --stat --format= 4eba2d2`:

```
 docs/adr/0016-correo-en-minusculas.md | 87 +++++++++++++++++++++++++++++++++++
 1 file changed, 87 insertions(+)
```

`git show --numstat --format= 4eba2d2` → `87	0	docs/adr/0016-correo-en-minusculas.md`.

Cómo se escribió: el bloque dictado (plan, l. 1362-1448) se extrajo con `sed`, quitando los dos espacios de sangría del
bloque de lista (0 líneas no vacías sin esa sangría), y `<FECHA>` se sustituyó por `14 nov 2026`. Comprobación:
`diff <(sed -n '1362,1448p' plan.md | sed -E 's/^  //') docs/adr/0016-correo-en-minusculas.md` → una sola diferencia,
la línea 3:

```
< - **Estado:** aceptado (David, <FECHA>, al aprobar las fases F y G del plan de BE-34)
> - **Estado:** aceptado (David, 14 nov 2026, al aprobar las fases F y G del plan de BE-34)
```

Codificación: UTF-8, 0 `\r` (LF), termina en `\n`, 0 líneas con espacios finales. `grep -c FECHA` → 0.

## Tests (RED → GREEN)

No aplica (documento; plan: "Tests (RED primero): no aplica", `check_docs` no lee `docs/adr`). Sin mutantes para esta
fase. `test-sanitizer`: no aplica, no hay pruebas nuevas.

## Compuerta de salida (`./venv/Scripts/python.exe scripts/check.py`, exit 0)

Líneas clave:

```
67 files already formatted
All checks passed!
Success: no issues found in 62 source files
Contracts: 4 kept, 0 broken.
TOTAL                                       1031     17    148     14  97.37%
675 passed, 8 warnings in 19.32s
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

Frente a la fila F del plan (675 passed · 97,37 % (1031) · 67 files · 62 source files · 386 en la copia): igual en todo.
Ratchet: tests 675 = 675, cobertura 97,37 % = 97,37 %, contratos 4 kept = 4, ruff y mypy 0 errores (ningún `.py` tocado).

Suite de la copia (procedimiento común, directorio nuevo `scratchpad/copy_F_4eba2d2`, `git archive HEAD` tras el commit,
sin `test_check*`): `386 passed, 8 warnings in 14.63s`.

## Criterio de aceptación

| Criterio | Medido |
|---|---|
| Compuerta como la fila F | exit 0, `Compuerta superada.`, 675 passed, 97.37 % (1031), 67 files, 62 source files, 4 kept, 8 warnings |
| `git show --numstat --format= <sha F>` → `87	0	docs/adr/0016-correo-en-minusculas.md` | `87	0	docs/adr/0016-correo-en-minusculas.md` |
| La línea "Estado" lleva una fecha real, no `<FECHA>` | `aceptado (David, 14 nov 2026, al aprobar las fases F y G del plan de BE-34)` |

## Fuera de alcance respetado

El código (fase G), ADR-0015, `AGENTS.md`, `docs/CONTEXT.md` y la fila BE-51 del backlog: sin tocar. Nada de la fase H.

## Residuales y dudas

- Ninguno nuevo. `docs/adr/` no tiene índice que actualizar; `check_docs` pasó sin cambios.
