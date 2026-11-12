# Handoff — BE-40 · Fase A (una sola forma de inyectar la identidad bajo guard admin)

- Commit de la fase: `a138a9e` — `refactor(api): inject the admin identity through AdminDep only`
- Rama: `item/be-40`, sobre `186b589` (plan aprobado con E0).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 12 nov 2026.

## Ritual de arranque

- `git status --short`: limpio. `current_target` = `Fase_A`. Sin `gaps.md`.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `41ff01d`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `41ff01d`; `Base develop` de `verificacion.md` = `41ff01d`.
- Compuerta antes de tocar nada (exit 0), idéntica a la línea base de la verificación:
  `61 files already formatted` · `All checks passed!` · `Success: no issues found in 56 source files` ·
  `Contracts: 4 kept, 0 broken.` · `622 passed, 8 warnings` · `Total coverage: 96.47%`.

## Archivos tocados (los 3 de la fase)

`git show --stat a138a9e`:

```
 app/api/dependencies.py    | 10 ++++++++++
 app/api/routers/service.py | 23 +++++++++++------------
 app/api/routers/user.py    | 21 +++++++--------------
 3 files changed, 28 insertions(+), 26 deletions(-)
```

Resumen del diff, todo dictado por el plan:

1. `app/api/dependencies.py`: `from typing import Annotated` + línea en blanco antes de `import jwt`; al final, tras
   `get_current_admin_user`, el bloque `# --- IDENTITY ALIASES (ADR-0012, point 5) ---` con `UserDep` y `AdminDep`
   (texto literal del plan).
2. `app/api/routers/user.py`: fuera `from typing import Annotated`, `from app.models.user import User` y el bloque
   `DEPENDENCY TYPE ALIASES`; el import de `app.api.dependencies` en la forma partida que dicta el plan (`AdminDep`,
   `UserDep`, `get_current_admin_user`, `get_current_user`, `get_user_service`). El bloque `ROUTER SEGMENTATION` no cambia
   (lo reescribe la fase C).
3. `app/api/routers/service.py`: import `AdminDep, get_current_admin_user, get_service_service`; fuera
   `from app.models.user import User`. Los seis handlers usan `usuario_actual: AdminDep,`. En `crear_paquete` y
   `modificar_paquete` en su sitio; en `activar_paquete`, `desactivar_paquete`, `borrar_paquete_logico` y
   `recuperar_paquete` sube antes de `service_service`, y su línea `usuario_actual (User): …` de Args sube antes de
   `service_service (TouristServicesService): …`. El comentario de segmentación (l.15-21) no cambia.

## Tests

Sin RED posible (refactor sin cambio de comportamiento, como dicta el plan). No se añadió ni modificó ningún test. La red:
los 622 tests de la base. Checklist `test-sanitizer`: no aplica, no se tocó ningún test.

## Criterio de aceptación (con E0.1)

```
$ grep -n "usuario_actual: User = " app/api/routers/service.py app/api/routers/user.py | wc -l
0
$ grep -rnE "^(UserDep|AdminDep) = " app --include=*.py
app/api/dependencies.py:169:UserDep = Annotated[User, Depends(get_current_user)]
app/api/dependencies.py:170:AdminDep = Annotated[User, Depends(get_current_admin_user)]
```

Información (el grep original, que E0.1 sustituye): `grep -rn "usuario_actual: User = " app --include=*.py` da 1 línea,
`app/api/routers/audit.py:24:    usuario_actual: User = Depends(get_current_user),`, fuera de alcance de A; la retira la
fase B, tal como mide E0.1.

## Compuerta de salida

`./venv/Scripts/python.exe scripts/check.py` → exit 0. Bloque RESUMEN literal:

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

- pytest: `622 passed, 8 warnings in 20.39s` (0 failed). Cobertura: `Total coverage: 96.47%` (= base).
- ruff format: `61 files already formatted`; ruff check: `All checks passed!`.
- mypy: `Success: no issues found in 56 source files`.
- import-linter: `Contracts: 4 kept, 0 broken.` (los cuatro KEPT).
- Sobre los tres archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `3 files already
  formatted`; `mypy` → `Success: no issues found in 3 source files`.
- Coincide con la fila A del plan (622 passed, 96,47 %).

Suite de la copia (procedimiento común, sin mutante; `git archive` de `a138a9e` en un directorio nuevo del scratchpad,
sin `test_check*`): `333 passed, 8 warnings in 10.92s`, como la fila A.

## Residuales y dudas

- Ninguno nuevo. El hook de ruff reportó `F821` intermedios (alias usados antes de su import) durante la edición y
  eliminó solo el import `User` de `service.py`, que el plan también manda borrar; el estado final está limpio.
- Sin desviaciones del plan ni de E0.
