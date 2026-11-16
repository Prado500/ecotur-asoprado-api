# Handoff — BE-35 · Fase A (ADR-0017)

- Commit de la fase: `7de0808` — `docs(adr): add ADR-0017, superadmins never remove their own account` (mensaje exacto
  del plan, trailer `Co-Authored-By` incluido; comparado con `diff` contra el bloque "Commit" de la fase A, plan l. 218-236:
  solo difiere la línea en blanco final que añade `git log --format=%B`).
- Rama: `item/be-35`, sobre `3cf22fc` (plan aprobado con E0).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 16 nov 2026.
- Enmiendas que aplican: E0.1 (ADR-0017 aceptado; `<FECHA>` = la de la línea `Aprobado: 16 nov 2026`). E0.2-E0.6 tocan
  solo la fase B o residuales.

## Ritual de arranque

- `git status --short`: limpio. HEAD `3cf22fc`. `current_target` = `Fase_A`. No existe `gaps.md`.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `87b9905`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `87b9905`; `Base develop` de `verificacion.md` = `87b9905`.
- Compuerta antes de tocar nada (exit 0), igual a la línea base de la verificación:
  `68 files already formatted` · `All checks passed!` · `Success: no issues found in 63 source files` ·
  `Contracts: 4 kept, 0 broken.` · `691 passed, 8 warnings in 28.64s` · `TOTAL 1034 15 148 13 97.63%`.

## Archivos tocados (el único de la fase)

`git show --stat --format= 7de0808`:

```
 .../0017-ningun-superadmin-se-retira-a-si-mismo.md | 70 ++++++++++++++++++++++
 1 file changed, 70 insertions(+)
```

`git show --numstat --format= 7de0808` → `70	0	docs/adr/0017-ningun-superadmin-se-retira-a-si-mismo.md`.

Cómo se comprobó el texto: el bloque dictado (plan, l. 139-208) se extrajo con `sed`, quitando los dos espacios de
sangría, y `<FECHA>` se sustituyó por `16 nov 2026`. `diff` de ese resultado contra el archivo creado → sin diferencias
(`IDENTICAL`). Codificación: UTF-8.

## Criterio de aceptación

- El archivo existe con el texto dictado y `<FECHA>` sustituida: sí (diff vacío, arriba).
- `git grep -c 'ADR-0017' -- docs/adr` → `docs/adr/0017-ningun-superadmin-se-retira-a-si-mismo.md:1` (esperado: lo mismo).
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

## Compuerta completa tras el cambio

`./venv/Scripts/python.exe scripts/check.py` → exit 0. Líneas de cifras:

```
68 files already formatted
All checks passed!
Success: no issues found in 63 source files
Contracts: 4 kept, 0 broken.
TOTAL                                       1034     15    148     13  97.63%
Required test coverage of 92.0% reached. Total coverage: 97.63%
691 passed, 8 warnings in 27.93s
=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

Ratchet contra la línea base (`verificacion.md`): pytest 691 passed / 0 failed (=); cobertura 97,63 % (=); contratos
4 kept / 0 broken (=); ruff 0 (=); mypy 0 en 63 archivos (=). Esperado por el plan: "compuerta completa en verde con
691 passed": cumplido. `ruff`/`mypy` sobre archivos tocados: no aplica (el único archivo es Markdown).

## Residuales y dudas

- Ninguna desviación respecto al plan.
- Observación (no bloqueante): la línea de título del ADR mide más de 100 columnas; es Markdown, `check_docs` no
  escanea `docs/adr` (lo dice el propio plan) y el texto es el dictado, así que no se tocó.
- Los residuales R1-R4 del plan siguen como están; ninguno es de esta fase.
- `test-sanitizer`: no aplica (la fase no crea ni toca tests).
