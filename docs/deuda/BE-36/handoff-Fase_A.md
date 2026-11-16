# Handoff — BE-36 · Fase A (ADR-0018)

- Commit de la fase: `dfed481` — `docs(adr): add ADR-0018, a superadmin may reactivate a peer superadmin` (mensaje
  exacto del plan, trailer `Co-Authored-By` incluido; comparado con `diff` contra el bloque "Commit" de la fase A, plan
  l. 253-271, sin la sangría de dos espacios: solo difiere la línea en blanco final que añade `git log --format=%B`).
- Rama: `item/be-36`, sobre `d8e3aca` (plan aprobado con E0).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 16 nov 2026.
- Enmiendas que aplican: E0.1 (ADR-0018 aceptado; `<FECHA>` = la de la línea `Aprobado: 16 nov 2026`). E0.3: `AGENTS.md`
  no se toca en este ítem (no se tocó). E0.2 y E0.4 no afectan a esta fase.

## Ritual de arranque

- `git status --short`: limpio. HEAD `d8e3aca`. `current_target` = `Fase_A`. No existe `gaps.md`.
- Vigencia de la línea base: `git fetch origin` sin errores (refrescado). `git rev-parse --short origin/develop` =
  `09f529b`; `git rev-parse --short $(git merge-base HEAD origin/develop)` = `09f529b`; `Base develop` de
  `verificacion.md` = `09f529b`.
- Compuerta antes de tocar nada (exit 0), igual a la línea base de la verificación:
  `68 files already formatted` · `All checks passed!` · `Success: no issues found in 63 source files` ·
  `Contracts: 4 kept, 0 broken.` · `707 passed, 8 warnings in 46.49s` · `TOTAL 1038 15 152 13 97.65%`.

## Archivos tocados (el único de la fase)

`git show --stat --format= dfed481`:

```
 docs/adr/0018-un-superadmin-reactiva-a-otro.md | 70 ++++++++++++++++++++++++++
 1 file changed, 70 insertions(+)
```

`git show --numstat --format= dfed481` → `70	0	docs/adr/0018-un-superadmin-reactiva-a-otro.md`.

Cómo se comprobó el texto: el bloque dictado (plan, l. 172-241) se extrajo con `sed`, quitando los dos espacios de
sangría, y `<FECHA>` se sustituyó por `16 nov 2026`. `diff` de ese resultado contra el archivo creado → sin diferencias
(`IDENTICO`). Codificación: UTF-8, finales de línea LF.

## Criterio de aceptación

- El archivo existe con el texto dictado y `<FECHA>` sustituida: sí (diff vacío, arriba).
- `git grep -l 'ADR-0018' -- docs/adr` → `docs/adr/0018-un-superadmin-reactiva-a-otro.md` (solo ese archivo).
- `git diff --stat 62b9702 HEAD -- docs/adr/0017-ningun-superadmin-se-retira-a-si-mismo.md` → salida vacía.
- `git diff --stat` del commit = 1 archivo nuevo: sí.
- Tests (RED primero): no aplica (solo documentación, según el plan). Comprobación sustituta
  `./venv/Scripts/python.exe scripts/check.py --no-tests` → exit 0:

```
=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)

Compuerta superada.
```

## Compuerta de salida

`./venv/Scripts/python.exe scripts/check.py` (completa) → exit 0. Bloque RESUMEN literal:

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

Cifras literales de la misma ejecución:

```
68 files already formatted
All checks passed!
Success: no issues found in 63 source files
Contracts: 4 kept, 0 broken.
TOTAL                                       1038     15    152     13  97.65%
Required test coverage of 92.0% reached. Total coverage: 97.65%
707 passed, 8 warnings in 37.45s
```

Ratchet frente a la línea base (`verificacion.md`): pytest 707 passed = 707 (0 failed); cobertura 97,65 % = 97,65 %;
ruff 0 = 0; mypy 0 en 63 archivos = 0; import-linter 4 kept = 4. Ruff y mypy sobre archivos tocados: no aplica (ningún
`.py` tocado).

## Residuales y dudas

- Ninguna desviación respecto al plan ni a E0.
- Fuera de `app/`, `tests/`, ADR-0017, `AGENTS.md`, `docs/CONTEXT.md` y `docs/backlog.md`: no se tocó nada de eso.
- Los residuales R1-R3 del plan siguen abiertos tal cual (son del cierre del ítem, no de esta fase).
