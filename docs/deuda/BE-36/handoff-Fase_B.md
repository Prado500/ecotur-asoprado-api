# Handoff — BE-36 · Fase B (excepción `is_peer_reactivation`, docstrings y tests)

- Commit de la fase: `53f1660` — `fix(access-policy): let a superadmin reactivate a peer superadmin` (mensaje exacto del
  plan; comparado con `diff` contra el bloque "Commit" de la fase B, plan l. 350-379, sin la sangría de dos espacios, y
  `git log -1 --format=%B` sin la línea en blanco final → idéntico; trailer `Co-Authored-By` incluido).
- Rama: `item/be-36`, sobre `f5fc1f4` (auditoría de la fase A, PASS).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 16 nov 2026.
- Enmiendas que aplican: E0.1 (superadmin en la papelera sigue 403; reactivar a un par activo da 200, sin condición
  sobre el estado actual; todos los tests en `tests/test_user_access_policy.py`). E0.3: `AGENTS.md` no se tocó.

## Ritual de arranque

- `git status --short`: limpio. HEAD `f5fc1f4`. `current_target` = `Fase_B`. `gaps.md`: fase A PASS, sin bloqueantes.
- Vigencia de la línea base: `git fetch origin` sin errores (refrescado). `git rev-parse --short origin/develop` =
  `09f529b`; `git rev-parse --short $(git merge-base HEAD origin/develop)` = `09f529b`; `Base develop` de
  `verificacion.md` = `09f529b`.
- Compuerta antes de tocar nada (exit 0), igual a la línea base: `68 files already formatted` · `All checks passed!` ·
  `Success: no issues found in 63 source files` · `Contracts: 4 kept, 0 broken.` ·
  `TOTAL 1038 15 152 13 97.65%` · `707 passed, 8 warnings in 33.60s`.

## Archivos tocados (los 3 de la fase)

`git show --stat --format= 53f1660`:

```
 app/services/user_access_policy.py |  22 +++-
 app/services/user_service.py       |   5 +
 tests/test_user_access_policy.py   | 244 ++++++++++++++++++++++++++++++++++++-
 3 files changed, 267 insertions(+), 4 deletions(-)
```

- `tests/test_user_access_policy.py`: imports (`get_password_hash` tras la l.18; `User, UserRole` en la l.21), los 6
  unitarios del Anexo al final de `TestAssertCanUpdate` y la sección HTTP del Anexo tras la l.951. Texto copiado del
  Anexo del plan con un script (no a mano): sin cambios de ruff format.
- `app/services/user_access_policy.py`: el bloque dictado sustituye `:69-71` (el `raise` intacto); docstring de la clase
  (l.14 termina en `(ADR-0017). One` + dos líneas) y de `assert_can_update` (l.53 → tres líneas).
- `app/services/user_service.py`: solo docstrings (tres líneas tras la l.259; dos tras la l.334). Sin cambio de lógica.

## RED (tests escritos y ejecutados antes de tocar `app/`)

`./venv/Scripts/python.exe -m pytest tests/test_user_access_policy.py -k be36 -q`:

```
FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be36_superadmin_can_reactivate_peer_superadmin
FAILED tests/test_user_access_policy.py::test_be36_recovered_superadmin_reactivated_by_peer_can_log_in
FAILED tests/test_user_access_policy.py::test_be36_superadmin_provisioned_inactive_is_reactivated_by_peer_and_logs_in
3 failed, 15 passed, 83 deselected in 2.17s
```

Cuadra con el plan (`3 failed, 15 passed`; U1, H1, H2). Motivo de cada fallo (`--tb=line`): U1 lanza
`AuthorizationError` en `user_access_policy.py:72` (guarda de jerarquía); H1 y H2 fallan en
`assert reactivated.status_code == 200` (`assert 403 == 200`), tras pasar ya `login_before == 403`.

## GREEN

`-k be36` → `18 passed, 83 deselected in 1.46s`. Archivos tocados: `ruff check` → `All checks passed!`;
`ruff format --check` → `3 files already formatted`; `mypy` → `Success: no issues found in 3 source files`.

## Compuerta completa (`./venv/Scripts/python.exe scripts/check.py`, exit 0)

```
68 files already formatted
All checks passed!
Success: no issues found in 63 source files
Contracts: 4 kept, 0 broken.
app\services\user_service.py                  97      0     22      1  99.16%   293->302
TOTAL                                       1039     15    152     13  97.65%
725 passed, 8 warnings in 32.88s
=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

Ratchet: 707 → 725 passed (707 + 18); cobertura 97,65 % = línea base (1038 → 1039 sentencias, 15 sin cubrir, igual);
ruff 0, mypy 0 en 63 archivos, 4 kept, como la línea base. `user_access_policy.py` no aparece en la tabla: está entre
los `30 files skipped due to complete coverage` (100 %). La rama sin cubrir de `user_service.py` es la misma de la base
(`290->299`), desplazada tres líneas por el docstring (`293->302`).

## Mutantes (copia de `app/`, `tests/`, `conftest.py` y `pyproject.toml` en el scratchpad; nunca en el repo)

`-k be36` contra cada mutante de `user_access_policy.py`, restaurado al final (`18 passed`):

```
== N1: 3 failed, 15 passed   (U1, H1, H2)
== N2: 1 failed, 17 passed   (U6 test_be36_admin_cannot_reactivate_superadmin)
== N3: 18 passed             (equivalente, declarado en el plan)
== N4: 2 failed, 16 passed   (U4, H5)
== N5: 7 failed, 11 passed   (U3 with-profile-field, with-role, role-only, empty; H3 ×3)
== N6: 3 failed, 15 passed   (U2, U3 null, H4)
```

Igual a lo que predice el plan: N1, N2, N4, N5 y N6 muertos; N3 vivo (equivalente).

## Verificación final del plan (comandos 1–12, tras el commit)

1 → `app/services/user_service.py:363` (1 línea). 2 → `app/repositories/user_repository.py:63` (1 línea). 3 → exit 1,
sin salida. 4 → 2 líneas (`user_access_policy.py:75`, `:85`). 5 → `:79` y `:80`. 6 → 4 líneas (router `:234`, política
`:113`, servicio `:332`, `:359`). 7 → 2 líneas (`user_repository.py:83`, `user_service.py:362`). 8 → `27`.
9 → app 5 líneas (`user_access_policy.py:16, :57, :74`; `user_service.py:262, :339`); tests exit 1; docs/adr solo
`docs/adr/0018-un-superadmin-reactiva-a-otro.md`; ADR-0017 en app `7`. 10 → `app/schemas/user.py:130`. 11 → salida
vacía. 12 → `tests/test_user_access_policy.py:12` y `18 passed`. 13 → la compuerta de arriba.

## test-sanitizer (checklist)

Tests dictados por el plan, sin reescribir: fábricas `make_user`, `persist_user`, `make_auth_headers`; sin mocks; sin
aserciones sobre texto en español (código, claves y tipo de `detail`); `refresh`/`select` tras las peticiones
(ADR-0011); mutación de estado y auditoría exacta en cada caso HTTP.

## Desviaciones, residuales y dudas

- Desviaciones respecto al plan: ninguna. Todas las cifras (RED, 725, cobertura, mutantes, comandos 1–12) cuadran.
- Residuales del plan sin cambio: R1 (cliente Flutter, E0.4), R2 (viñeta de AGENTS §3 y `docs/CONTEXT.md` al cierre;
  E0.3: la viñeta va después de la auditoría de esta fase), R3 (dato para BE-55).
- Ruff/mypy en código no tocado: nada que reportar (ambos en 0).
- Context7 no conectó en esta sesión; no hizo falta (sin API nueva).
