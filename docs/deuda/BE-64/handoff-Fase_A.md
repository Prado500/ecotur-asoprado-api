# Handoff — BE-64 · Fase A (ADR-0023)

- **Commit de la fase:** `0a07a47` — `docs(adr): add ADR-0023, a verification link can be asked for again` (mensaje
  exacto del plan, fase A).
- **Rama:** `item/be-64`. HEAD al arrancar: `3674c80` (commit de docs de David del 27 nov, encima de `28de107`; árbol
  limpio). **Base develop:** `b6a80ba` (`git fetch origin` correcto; `git rev-parse --short origin/develop` y
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `b6a80ba`, igual a `verificacion.md`).
- **Compuerta:** `./venv/Scripts/python.exe scripts/check.py`, sin `--soft`. Windows no bloqueó `_rustgrimp`:
  E0, punto 3, no aplicó.

## Archivos tocados
- `docs/adr/0023-el-enlace-de-verificacion-se-puede-pedir-de-nuevo.md` (nuevo): texto del Anexo A del plan (líneas
  506-590 de `plan.md`), extraído con `sed` sin reescribirlo. Única diferencia con el Anexo, comprobada con `diff`:
  `<FECHA DE APROBACIÓN>` → `19 nov 2026` (E1, punto 1).

```
3c3
< - **Estado:** aceptado (David, <FECHA DE APROBACIÓN>, al aprobar el plan de BE-64)
---
> - **Estado:** aceptado (David, 19 nov 2026, al aprobar el plan de BE-64)
```

## Diff (`git show --stat 0a07a47`)
```
 ...lace-de-verificacion-se-puede-pedir-de-nuevo.md | 85 ++++++++++++++++++++++
 1 file changed, 85 insertions(+)
```

## Comprobaciones mecánicas del plan
- Antes: `ls docs/adr/0023-*` → `ls: cannot access 'docs/adr/0023-*': No such file or directory`.
- Después: el archivo existe (85 líneas, UTF-8).
- `grep -c "<FECHA" docs/adr/0023-*.md` → `0`.
- El Anexo A dice "33 mutantes"; ninguna enmienda cambia esa cifra (E1, punto 2: 5 + 4 + 15 + 9 = 33).

## Compuerta de arranque (antes de tocar nada)
Exit 0. `72 files already formatted` · `All checks passed!` · `Success: no issues found in 67 source files` ·
`Contracts: 4 kept, 0 broken.` · `806 passed, 25 warnings in 33.57s` · `TOTAL 1071 10 156 6 98.70%` ·
`Compuerta superada.` Igual a la línea base de `verificacion.md`.

## Compuerta de salida (literal)
Código de salida: `0`.

```
72 files already formatted
All checks passed!
Success: no issues found in 67 source files
Contracts: 4 kept, 0 broken.
TOTAL                                       1071     10    156      6  98.70%
Required test coverage of 92.0% reached. Total coverage: 98.70%
806 passed, 25 warnings in 34.73s
```

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

Ratchet: pytest 806 passed (= 806, criterio de la fase); cobertura 98,70 % (= línea base); 4 kept (= línea base);
ruff 0 y mypy 0 (= línea base). No se tocó ningún `.py`, así que no hay `ruff`/`mypy` por archivo que correr.

## Tests
No aplica (el plan: documento fuera de `check_docs`). Skill `test-sanitizer`: no aplica, la fase no tiene tests.

## Residuales
Ninguno nuevo.

## Dudas
Ninguna. Siguiente: fase B, que no empieza sin el momento 1 de David (E1, punto 3: `alembic current` →
`e50a7c3d9b12 (head)` y `alembic check` → `No new upgrade operations detected.`, salida en la bitácora).
