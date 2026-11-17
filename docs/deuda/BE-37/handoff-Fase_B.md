# Handoff — BE-37 · Fase B (marcador `NoExplicitNull` y `UserUpdate`)

- Commit de la fase: `99f48ae` — `fix(schemas): reject explicit null on NOT NULL fields of UserUpdate` (mensaje exacto
  del plan; bloque "Commit" de la fase B, plan l. 279-304, sin la sangría de dos espacios, comparado con `diff` contra
  `git log -1 --format=%B 99f48ae` → idéntico; trailer `Co-Authored-By` incluido; línea más larga, 69 columnas).
- Rama: `item/be-37`, sobre `05f4022` (auditoría PASS de la fase A).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 17 nov 2026.
- Enmiendas que aplican: E0.2 (`_NULL_MESSAGE = "Este campo no puede quedar vacío."`, ya en el Anexo B), E0.3 (16 casos
  en esta fase), E0.4 (cuarto rechazo 403 → 422, caso `superadmin-on-peer-is_active`), E0.7 (`AGENTS.md` no se toca).
  `gaps.md` solo contiene la auditoría PASS de la fase A: no limita el alcance.

## Ritual de arranque

- `git status --short`: limpio. HEAD `05f4022`. `current_target` = `Fase_B`; `Fase_A` `completed` en `4c4acb7`.
- Vigencia de la línea base: `git fetch origin` sin errores (refrescado). `git rev-parse --short origin/develop` =
  `c3b5069`; `git rev-parse --short $(git merge-base HEAD origin/develop)` = `c3b5069`; `Base develop` de
  `verificacion.md` = `c3b5069`.
- Compuerta antes de tocar nada (`./venv/Scripts/python.exe scripts/check.py`, exit 0), igual a la línea base:
  `68 files already formatted` · `All checks passed!` · `Success: no issues found in 63 source files` ·
  `Contracts: 4 kept, 0 broken.` · `TOTAL 1039 15 152 13 97.65%` · `731 passed, 8 warnings in 29.76s`.

## Archivos tocados (los cuatro de la fase)

`git show --stat --format= 99f48ae`:

```
 app/schemas/partial_update.py  |  38 +++++++++++
 app/schemas/user.py            |  22 +++---
 tests/test_email_case.py       |  11 +--
 tests/test_user_update_null.py | 149 +++++++++++++++++++++++++++++++++++++++++
 4 files changed, 206 insertions(+), 14 deletions(-)
```

`git diff --numstat 05f4022 99f48ae` (criterio del plan: `38 0`, `13 9`, `149 0`, `6 5`):

```
38	0	app/schemas/partial_update.py
13	9	app/schemas/user.py
6	5	tests/test_email_case.py
149	0	tests/test_user_update_null.py
```

## Fidelidad al dictado

- `app/schemas/partial_update.py` y `tests/test_user_update_null.py`: extraídos con `sed` de las líneas del Anexo B
  (plan l. 668-705 y l. 799-947), sin teclear; `_NULL_MESSAGE` en la l. 13 con el texto de E0.2.
- `app/schemas/user.py` y `tests/test_email_case.py`: `git diff` igual hunk a hunk a los del Anexo B.

## TDD

- **RED** (tests escritos, `app/` sin tocar):
  `./venv/Scripts/python.exe -m pytest tests/test_user_update_null.py tests/test_email_case.py -k be37 -q` →
  `12 failed, 4 passed, 16 deselected in 0.98s`. Fallan el test del correo (`DID NOT RAISE`), U2, H1 ×9 y H2; los
  códigos de partida medidos: `assert 409 == 422` ×5 (email, first_name, last_name, role e is_active sobre admin),
  `assert 403 == 422` ×4 (superadmin-on-self-role, admin-on-tourist-role, tourist-on-self-is_active,
  superadmin-on-peer-is_active) y `assert 409 == 422` en H2. Pasan U1, H3 ×2 y H4. Suite completa:
  `12 failed, 734 passed, 8 warnings in 28.48s`. Igual que el plan.
- **GREEN**: el mismo comando → `16 passed, 16 deselected, 10 warnings in 0.41s`.

## Compuerta tras la fase (`./venv/Scripts/python.exe scripts/check.py`, exit 0)

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

Líneas clave literales:

```
70 files already formatted
All checks passed!
Success: no issues found in 65 source files
Contracts: 4 kept, 0 broken.
app\schemas\user.py                           58      2      8      2  93.94%   112, 126
TOTAL                                       1046     11    152      9  98.33%
746 passed, 18 warnings in 31.07s
Compuerta superada.
```

- pytest: 746 passed, 0 failed (731 + 15). Cobertura 98,33 % (≥ 97,65 %). Ratchet: ruff 0, mypy 0, 4 kept.
- Sobre los archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `4 files already formatted`;
  `mypy` → `Success: no issues found in 4 source files`.
- Avisos 8 → 18: el aviso deprecado de `HTTP_422_UNPROCESSABLE_ENTITY` por cada 422 nuevo (residual R2, previsto).

## Mutantes (copia `git archive` + los cuatro archivos de la fase, en el scratchpad; suite completa por mutante)

Script `mutants_b.sh` del scratchpad: un `sed` por mutante sobre la copia, suite completa, restauración del original;
la copia sin mutar da `746 passed, 18 warnings`. Salida literal:

```
== MU-email: 2 failed, 744 passed, 17 warnings in 29.06s
    FAILED tests/test_email_case.py::test_be37_a_patch_with_a_null_email_is_rejected
    FAILED tests/test_user_update_null.py::test_be37_null_on_not_null_field_returns_422_without_mutation[superadmin-on-admin-email]
== MU-first_name: 1 failed, 745 passed, 17 warnings in 43.18s
    FAILED tests/test_user_update_null.py::test_be37_null_on_not_null_field_returns_422_without_mutation[superadmin-on-admin-first_name]
== MU-last_name: 1 failed, 745 passed, 17 warnings in 41.20s
    FAILED tests/test_user_update_null.py::test_be37_null_on_not_null_field_returns_422_without_mutation[superadmin-on-admin-last_name]
== MU-role: 5 failed, 741 passed, 14 warnings in 33.48s
    FAILED tests/test_user_update_null.py::test_be37_every_null_field_is_reported
    FAILED tests/test_user_update_null.py::test_be37_null_on_not_null_field_returns_422_without_mutation[superadmin-on-admin-role]
    FAILED tests/test_user_update_null.py::test_be37_null_on_not_null_field_returns_422_without_mutation[superadmin-on-self-role]
    FAILED tests/test_user_update_null.py::test_be37_null_on_not_null_field_returns_422_without_mutation[admin-on-tourist-role]
    FAILED tests/test_user_update_null.py::test_be37_null_beside_a_valid_field_changes_nothing
== MU-is_active: 4 failed, 742 passed, 15 warnings in 29.72s
    FAILED tests/test_user_update_null.py::test_be37_every_null_field_is_reported
    FAILED tests/test_user_update_null.py::test_be37_null_on_not_null_field_returns_422_without_mutation[superadmin-on-admin-is_active]
    FAILED tests/test_user_update_null.py::test_be37_null_on_not_null_field_returns_422_without_mutation[tourist-on-self-is_active]
    FAILED tests/test_user_update_null.py::test_be37_null_on_not_null_field_returns_422_without_mutation[superadmin-on-peer-is_active]
== MU-phone+: 2 failed, 744 passed, 20 warnings in 30.38s
    FAILED tests/test_user_update_null.py::test_be37_null_on_phone_still_clears_it[superadmin-on-admin]
    FAILED tests/test_user_update_null.py::test_be37_null_on_phone_still_clears_it[tourist-on-self]
== MX-exclude_none: 2 failed, 744 passed, 18 warnings in 31.28s
    FAILED tests/test_user_update_null.py::test_be37_null_on_phone_still_clears_it[superadmin-on-admin]
    FAILED tests/test_user_update_null.py::test_be37_null_on_phone_still_clears_it[tourist-on-self]
== MF-falsy: 10 failed, 736 passed, 28 warnings in 30.01s
    FAILED tests/test_auth.py::test_tourist_self_is_active_change_returns_403_without_mutation
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[false]
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[with-profile-fields]
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_self_deactivation_returns_403_with_another_superadmin_active
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_keeps_access_after_rejected_self_removal
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_deactivates_lower_rank_account_returns_200
    FAILED tests/test_user_access_policy.py::test_be36_peer_superadmin_deactivation_still_returns_403
    FAILED tests/test_user_access_policy.py::test_be58_admin_self_deactivation_returns_403_without_mutation[false]
    FAILED tests/test_user_access_policy.py::test_be58_admin_self_deactivation_returns_403_without_mutation[with-profile-field]
    FAILED tests/test_user_access_policy.py::test_be58_admin_keeps_access_after_rejected_self_removal
```

Resultado: los ocho murieron con los mismos tests que declara la tabla del plan (MU-email 2, MU-first_name 1,
MU-last_name 1, MU-role 5, MU-is_active 4, MU-phone+ 2, MX-exclude_none 2, MF-falsy 10). Los totales suman 746 y
no 757 porque la copia tiene solo la fase B; el plan midió la tabla con B y C.

## Verificación final aplicable tras B

- #1 `git grep -n "NoExplicitNull" -- app` → 8 líneas (`partial_update.py` :36 :38; `user.py` :7 :170 :173 :179 :186
  :187); las 6 de `service.py` llegan en C.
- #2 `", NoExplicitNull] ="` → 5 líneas, todas de `UserUpdate` (`user.py` :170 :173 :179 :186 :187).
- #6 `git grep -n "if v is None" -- app/schemas/user.py` → sin salida (exit 1).
- #8 `email=None` → `tests/test_email_case.py:120`; el nombre viejo → sin salida (exit 1).
- #9 `ADR-0020` en `app tests` → `partial_update.py` :6 :37, `user.py` :167, `test_email_case.py` :118,
  `test_user_update_null.py` :1 :67.
- #10 `def test_be37_` → `test_email_case.py:1`, `test_user_update_null.py:6`.
- #11 (más `app/schemas/service.py` y `tests/test_services.py`) → salida vacía.

## Desviaciones, residuales y dudas

- Desviaciones respecto al plan: ninguna. Todas las cifras (RED, GREEN, numstat, compuerta, mutantes) cuadran.
- Incidencia de herramienta, sin efecto en el resultado: el hook `ruff_on_edit` avisó F821 en los estados intermedios
  (primer `Edit` antes de añadir el import, en `test_email_case.py` y en `user.py`); el estado final pasa ruff, ruff
  format y mypy.
- Residuales: ninguno nuevo. R1-R5 del plan siguen con el destino de E0.5.
