# Handoff — BE-39 · Fase A (inventario: toda ruta es protegida o pública)

- **Commit de la fase:** `d89e942` — `test(guards): list every route as protected or public and pin the list`
- **Ejecutor:** fase-ejecutor (Claude Opus 5.5), 11 nov 2026.

## Ritual de arranque

- `git status --short`: limpio. `HEAD` = `72492af` (plan aprobado con E0 y E1).
- `current_target` = `Fase_A`. No existía `gaps.md`.
- Vigencia de la línea base: `git fetch origin` correcto. `git rev-parse --short origin/develop` = `3ca990a`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `3ca990a`. Ambos iguales a `Base develop` de
  `verificacion.md`.
- Compuerta antes de tocar nada: exit 0, `579 passed`, `Total coverage: 96.29%`, 6 pasos ✔. Igual a la línea base.

## Archivos tocados

- `tests/test_route_guards.py` (nuevo). Idéntico, byte a byte, al bloque "Cambios exactos" de la fase A del plan
  (`diff` del bloque extraído de `plan.md:163-252`, sin la sangría de dos espacios, contra el archivo: sin diferencias).
  El hook de formato no lo modificó.

`git show --stat d89e942`:

```text
 tests/test_route_guards.py | 90 ++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 90 insertions(+)
```

## Mutantes (procedimiento común del plan)

Cada copia, en un directorio nuevo y vacío del scratchpad (`fa_nomut`, `fa_m10`, `fa_m11`), extraída con
`git -C C:/projects/ecotur-asoprado archive HEAD | tar -x -C <dir>` (HEAD = `72492af`), con
`tests/test_route_guards.py` copiado encima desde el árbol de trabajo. `find <dir> -name 'test_*probe*'`: vacío en las
tres. `diff -r -q` de `app/` contra el árbol de trabajo: solo el archivo mutado más `app/api/__init__.py`, que difiere
únicamente en el fin de línea (CRLF en el árbol de trabajo, LF en el índice y en la copia; `git ls-files --eol`:
`i/lf w/crlf`). Comando, desde cada `<dir>`:
`C:/projects/ecotur-asoprado/venv/Scripts/python.exe -m pytest -q -p no:cacheprovider -rf --ignore=tests/test_check.py --ignore=tests/test_check_docs.py`.

| Estado | Edición | Resultado (literal) | Esperado por el plan |
|---|---|---|---|
| Sin mutante | — | `291 passed, 5 warnings in 12.17s` | 291 passed |
| M10 | `app/main.py`: añadidas al final `@app.get("/ping")` / `async def ping():` / `    return {}` | `1 failed, 290 passed, 5 warnings in 11.97s` | 1 failed, 290 passed |
| M11 | `app/api/routers/service.py`: borrada `@admin_router.get("/admin/inactivos", response_model=list[ServiceListResponse])` | `2 failed, 289 passed, 5 warnings in 11.57s` | 2 failed, 289 passed |

`FAILED` literales:

```text
===== fa_m10
FAILED tests/test_route_guards.py::test_every_route_is_listed_as_protected_or_public
1 failed, 290 passed, 5 warnings in 11.97s
===== fa_m11
FAILED tests/test_route_guards.py::test_every_route_is_listed_as_protected_or_public
FAILED tests/test_services.py::test_inactive_column_returns_off_rule_package
2 failed, 289 passed, 5 warnings in 11.57s
```

## Criterio de aceptación

- `pytest tests/test_route_guards.py -q -p no:cacheprovider` → `1 passed in 0.03s`.
- `ruff check tests/test_route_guards.py` → `All checks passed!`; `mypy tests/test_route_guards.py` →
  `Success: no issues found in 1 source file`.
- Compuerta completa (`./venv/Scripts/python.exe scripts/check.py`), exit 0. Cifras de la fila A del plan:
  `61 files already formatted` · `All checks passed!` · `Success: no issues found in 56 source files` ·
  `Contracts: 4 kept, 0 broken.` · `Required test coverage of 92.0% reached. Total coverage: 96.29%` ·
  `580 passed, 5 warnings in 18.99s`.

Bloque RESUMEN literal:

```text
=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

| Métrica | Línea base | Fin de A | Plan (fila A) |
|---|---|---|---|
| pytest | 579 passed | 580 passed | 580 passed |
| Cobertura | 96,29 % | 96,29 % | 96,29 % |
| ruff format | 60 files | 61 files | 61 files |
| ruff check | 0 errores | 0 errores | 0 |
| mypy | 55 source files, 0 errores | 56 source files, 0 errores | 56 |
| import-linter | 4 kept | 4 kept | 4 kept |

## Checklist test-sanitizer (Ecotur Enterprise Test Standards)

Sin mocks ni fixtures en esta fase (el test lee `app.routes`, no hace peticiones). Nombres en inglés. No hay
aserciones sobre texto humano; las rutas en español son contrato público (AGENTS §4, excepción b). Nada que corregir.

## Desviaciones respecto del plan

Ninguna en código, cifras ni mensaje de commit (usado letra a letra, con `<MODELO EJECUTOR>` → `Claude Opus 5.5`).

## Residuales y dudas

- **Observación sobre el mensaje de commit (no es desviación):** dice "The rejection tests that read the table come in
  the next two commits (BE-39)". Tras E0 son tres fases más (B, C, D), aunque D no añade un test de rechazo sino uno de
  paso; E0 fijó que los commits de A, B y C no cambian, así que se usó tal cual.
- Fuera de alcance, sin tocar: tests de rechazo (B, C), `tests/test_audit.py`, `app/`.
- Directorios de scratchpad de esta fase: `fa_nomut`, `fa_m10`, `fa_m11` (y `fa_gate.txt`). No se pueden borrar
  (`rm -rf` denegado); la fase B debe crear directorios nuevos, como dicta el plan.
