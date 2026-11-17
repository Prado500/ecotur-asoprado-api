# Handoff — BE-58 · Fase B (las dos guardas ampliadas, sus textos, sus docstrings y sus tests)

- Commit de la fase: `72fd34b` — `fix(access-policy): block admin self-deletion and self-deactivation` (mensaje exacto
  del plan; bloque "Commit" de la fase B, plan l. 400-429, sin la sangría de dos espacios, comparado con `diff` contra
  `git log -1 --format=%B 72fd34b` sin la línea en blanco final → idéntico; trailer `Co-Authored-By` incluido; línea
  más larga, 68 columnas).
- Rama: `item/be-58`, sobre `7645e89`.
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 17 nov 2026.
- Enmiendas que aplican: E0.2 (un aviso por vía, el mismo para admin y superadmin), E0.3 (dos unitarios invertidos y
  cinco casos HTTP, sin gemelos), E0.4 (sin correcciones de dictado), E1 (`87379f1` ya cambió `AGENTS.md`; el comando 11
  lo muestra y no es hallazgo de esta fase). `AGENTS.md` no se toca en esta fase.

## Ritual de arranque

- `git status --short`: limpio. HEAD `7645e89`. `current_target` = `Fase_B`; `Fase_A` `completed` en `ccd84a4`.
  `gaps.md`: solo la auditoría de A, PASS (0 bloqueantes, 0 opcionales).
- Vigencia de la línea base: `git fetch origin` sin errores (refrescado). `git rev-parse --short origin/develop` =
  `6b168e1`; `git rev-parse --short $(git merge-base HEAD origin/develop)` = `6b168e1`; `Base develop` de
  `verificacion.md` = `6b168e1`.
- `git log --oneline 2cc8f73..HEAD -- AGENTS.md` = `87379f1 docs(agents): extend the superadmin rule to every
  administrative account (ADR-0019)` y nada más (condición de E1.2).
- Compuerta antes de tocar nada (`./venv/Scripts/python.exe scripts/check.py`, exit 0), igual a la línea base:
  RESUMEN con los seis pasos en ✔ · `TOTAL 1039 15 152 13 97.65%` · `726 passed, 8 warnings in 31.64s` ·
  `Compuerta superada.`

## Archivos tocados (los cuatro de la fase)

`git show --stat --format= 72fd34b`:

```
 app/api/routers/user.py            |   4 +-
 app/services/user_access_policy.py |  36 +++++++-----
 app/services/user_service.py       |  11 ++--
 tests/test_user_access_policy.py   | 115 +++++++++++++++++++++++++++++++++++--
 4 files changed, 140 insertions(+), 26 deletions(-)
```

`git diff --numstat` antes del commit: `2 2 routers/user.py` · `22 14 user_access_policy.py` · `6 5 user_service.py` ·
`110 5 tests/test_user_access_policy.py` = el esperado del plan (22/14, 6/5, 2/2, 110/5).

- `app/services/user_access_policy.py`: guarda de borrado (l.50) y de `is_active` (l.113) a
  `actor.role != UserRole.tourist`; los dos avisos de David partidos en dos literales (l.52-53 y l.117-118); docstring
  de la clase, de `assert_can_delete` (l.30, l.38-39) y de `assert_can_update` (l.64-67) como el dictado.
- `app/services/user_service.py`: docstrings de `delete_user_account` (l.182-183, l.195), comentario l.205 y docstring
  de `update_user_account` (l.259-260). Sin cambio de lógica.
- `app/api/routers/user.py`: docstring de `eliminar_usuario` (l.134-135).
- `tests/test_user_access_policy.py`: docstring de `TestAssertCanDelete`; U1 y U2 sustituyen a los dos be35 de admin;
  sección HTTP `# --- BE-58 regression: …` con H1, H2 (×2), H3 y H4 tras el último be36, antes de la sección C. Texto
  literal del Anexo.

## RED (tests escritos y ejecutados antes de tocar `app/`)

`./venv/Scripts/python.exe -m pytest tests/test_user_access_policy.py -k be58 -q -rA --no-cov`:

```
PASSED tests/test_user_access_policy.py::test_be58_admin_self_update_with_is_active_true_returns_200
FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_be58_admin_self_delete_is_rejected
FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be58_admin_self_deactivation_is_rejected
FAILED tests/test_user_access_policy.py::test_be58_admin_self_delete_returns_403_without_mutation
FAILED tests/test_user_access_policy.py::test_be58_admin_self_deactivation_returns_403_without_mutation[false]
FAILED tests/test_user_access_policy.py::test_be58_admin_self_deactivation_returns_403_without_mutation[with-profile-field]
FAILED tests/test_user_access_policy.py::test_be58_admin_keeps_access_after_rejected_self_removal
6 failed, 1 passed, 100 deselected in 0.55s
```

Igual al RED esperado del plan (fallan U1, U2, H1, H2 ×2 y H3; pasa H4).

## GREEN

```
-k be58 → 7 passed, 100 deselected in 0.15s
-k be35 → 15 passed, 92 deselected in 0.30s
-k be36 → 19 passed, 88 deselected in 1.41s
```

## Compuerta de salida (`./venv/Scripts/python.exe scripts/check.py`, exit 0)

```
68 files already formatted
All checks passed!
Success: no issues found in 63 source files
Contracts: 4 kept, 0 broken.
```

```
Name                                       Stmts   Miss Branch BrPart   Cover   Missing
---------------------------------------------------------------------------------------
app\db\database.py                            13      4      0      0  69.23%   31-35
app\main.py                                   57      4     18      4  89.33%   61, 72, 79, 82
app\repositories\user_repository.py           62      1      8      1  97.14%   80
app\schemas\service.py                        51      1      2      1  96.23%   120
app\schemas\user.py                           59      3     10      3  91.30%   110, 124, 188
app\services\tourist_services_service.py     104      2     34      3  96.38%   49, 290, 338->347
app\services\user_service.py                  97      0     22      1  99.16%   294->303
---------------------------------------------------------------------------------------
TOTAL                                       1039     15    152     13  97.65%

30 files skipped due to complete coverage.
Required test coverage of 92.0% reached. Total coverage: 97.65%
731 passed, 8 warnings in 28.63s
--- pytest + cobertura: OK en 31.5s

=== RESUMEN ===
  ✔ ruff format --check
  ✔ ruff check
  ✔ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta superada.
```

- pytest: 731 passed, 0 failed (726 + 5). Cobertura 97,65 % = línea base; `user_access_policy.py` al 100 % (entre los
  30 omitidos). La rama parcial de `user_service.py` es la misma de la línea base (`293->302`), desplazada una línea por
  el docstring que pasa a dos líneas.
- Archivos tocados: `ruff check` → `All checks passed!`; `ruff format --check` → `4 files already formatted`;
  `mypy` sobre los tres de `app/` → `Success: no issues found in 3 source files`.
- Ratchet: ruff 0 = 0, mypy 0 en 63 = 0 en 63, 4 kept = 4 kept, cobertura 97,65 % = 97,65 %.

## Verificación final (comandos 1-13 del plan, tras el commit)

| # | Esperado | Obtenido |
|---|---|---|
| 1 | 2 líneas, `:50` y `:113` | `user_access_policy.py:50`, `:113` |
| 2 | 4 líneas: `:50`, `:89`, `:112`, `:114` | `:50`, `:89`, `:112`, `:114` |
| 3 | `user_access_policy.py:6` | `app/services/user_access_policy.py:6` |
| 4 | 0 líneas (exit 1) | sin salida, exit 1 |
| 5 | `test_auth.py:168`, `test_user_access_policy.py:41` | idénticos |
| 6 | 13 líneas: routers 1, política 6, servicio 6 | 13: `routers/user.py:135`; política `:11, :28, :30, :39, :59, :64`; servicio `:181, :183, :195, :205, :255, :259` |
| 7 | 2 líneas (H1, H2) | `tests/test_user_access_policy.py:1229`, `:1257` |
| 8 | 10 líneas: app 6, tests 2, AGENTS.md 2 | 10: `AGENTS.md:59, :63`; `routers/user.py:135`; política `:14, :30, :64`; servicio `:183, :260`; tests `:107, :1132` |
| 9 | app 7 (política 3, servicio 3, router 1); tests 2; docs/adr 0017 y 0019 | app 7 (política `:14, :30, :64`; servicio `:183, :205, :260`; router `:135`); tests `:1232`, `:1260`; `0017-…` y `0019-…` |
| 10 | 2 líneas (`:52`, `:117`); los de BE-35 0 (exit 1) | `:52`, `:117`; segundo grep sin salida, exit 1 |
| 11 | vacío salvo `AGENTS.md` por `87379f1` (E1.2) | ` AGENTS.md \| 9 +++++----` y nada más; `git log 2cc8f73..HEAD -- AGENTS.md` = solo `87379f1` |
| 12 | `3 1 docs/adr/0017-…` | `3	1	docs/adr/0017-ningun-superadmin-se-retira-a-si-mismo.md` |
| 13 | be58 6, be35 13; 7, 15 y 19 passed | `:6`, `:13`; 7, 15 y 19 passed |
| 14 | compuerta exit 0, 731, ≥ 97,65 %, ruff 0, mypy 0 en 63, 4 kept | ver arriba |

## Mutantes (17, tabla del plan)

Copia `git archive 72fd34b` en el scratchpad de la sesión (nunca en el repo; comprobado que la copia importa su propio
`app/` y que su suite da `731 passed` sin mutar). Un mutante por ejecución sobre `app/services/user_access_policy.py`,
suite completa (`pytest -q -p no:cacheprovider --no-cov -rf`), restaurado al final. Salida literal:

```
== R1: 3 failed, 728 passed, 8 warnings in 30.36s
    FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_be58_admin_self_delete_is_rejected
    FAILED tests/test_user_access_policy.py::test_be58_admin_self_delete_returns_403_without_mutation
    FAILED tests/test_user_access_policy.py::test_be58_admin_keeps_access_after_rejected_self_removal
== M1: 2 failed, 729 passed, 8 warnings in 30.36s
    FAILED tests/test_auth.py::test_self_soft_delete_keeps_row_and_blocks_login
    FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_self_delete_tourist_is_allowed
== SD: 7 failed, 724 passed, 8 warnings in 29.61s
    FAILED tests/test_auth.py::test_self_soft_delete_keeps_row_and_blocks_login
    FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_self_delete_tourist_is_allowed
    FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_be35_superadmin_self_delete_is_rejected
    FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_be35_self_delete_guard_identifies_the_actor_by_cedula
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_delete_returns_403_without_mutation
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_self_delete_returns_403_with_another_superadmin_active
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_keeps_access_after_rejected_self_removal
== AD: 5 failed, 726 passed, 8 warnings in 28.13s
    FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_be35_superadmin_self_delete_is_rejected
    FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_be35_self_delete_guard_identifies_the_actor_by_cedula
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_delete_returns_403_without_mutation
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_self_delete_returns_403_with_another_superadmin_active
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_keeps_access_after_rejected_self_removal
== ASD: 731 passed, 8 warnings in 28.45s
== M2: 1 failed, 730 passed, 8 warnings in 29.18s
    FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_be35_self_delete_guard_identifies_the_actor_by_cedula
== M8: 8 failed, 723 passed, 8 warnings in 29.27s
    FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_be35_superadmin_self_delete_is_rejected
    FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_be35_self_delete_guard_identifies_the_actor_by_cedula
    FAILED tests/test_user_access_policy.py::TestAssertCanDelete::test_be58_admin_self_delete_is_rejected
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_delete_returns_403_without_mutation
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_self_delete_returns_403_with_another_superadmin_active
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_keeps_access_after_rejected_self_removal
    FAILED tests/test_user_access_policy.py::test_be58_admin_self_delete_returns_403_without_mutation
    FAILED tests/test_user_access_policy.py::test_be58_admin_keeps_access_after_rejected_self_removal
== R5: 4 failed, 727 passed, 8 warnings in 29.40s
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be58_admin_self_deactivation_is_rejected
    FAILED tests/test_user_access_policy.py::test_be58_admin_self_deactivation_returns_403_without_mutation[false]
    FAILED tests/test_user_access_policy.py::test_be58_admin_self_deactivation_returns_403_without_mutation[with-profile-field]
    FAILED tests/test_user_access_policy.py::test_be58_admin_keeps_access_after_rejected_self_removal
== M5: 731 passed, 8 warnings in 28.57s
== SU: 7 failed, 724 passed, 8 warnings in 28.62s
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be35_superadmin_self_deactivation_is_rejected
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be35_self_deactivation_guard_identifies_the_actor_by_cedula
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[false]
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[coerced-false]
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[with-profile-fields]
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_self_deactivation_returns_403_with_another_superadmin_active
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_keeps_access_after_rejected_self_removal
== AU: 7 failed, 724 passed, 8 warnings in 28.65s
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be35_superadmin_self_deactivation_is_rejected
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be35_self_deactivation_guard_identifies_the_actor_by_cedula
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[false]
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[coerced-false]
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[with-profile-fields]
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_self_deactivation_returns_403_with_another_superadmin_active
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_keeps_access_after_rejected_self_removal
== ASU: 731 passed, 8 warnings in 29.20s
== M3: 3 failed, 728 passed, 8 warnings in 29.42s
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be35_superadmin_self_update_with_is_active_true_is_allowed
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_self_update_with_is_active_true_returns_200
    FAILED tests/test_user_access_policy.py::test_be58_admin_self_update_with_is_active_true_returns_200
== M4: 3 failed, 728 passed, 8 warnings in 30.16s
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_admin_can_mutate_is_active
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be35_superadmin_can_deactivate_lower_rank_account
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_deactivates_lower_rank_account_returns_200
== M6: 731 passed, 8 warnings in 28.59s
== M7: 1 failed, 730 passed, 8 warnings in 29.11s
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be35_self_deactivation_guard_identifies_the_actor_by_cedula
== M9: 11 failed, 720 passed, 8 warnings in 30.05s
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be35_superadmin_self_deactivation_is_rejected
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be35_self_deactivation_guard_identifies_the_actor_by_cedula
    FAILED tests/test_user_access_policy.py::TestAssertCanUpdate::test_be58_admin_self_deactivation_is_rejected
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[false]
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[coerced-false]
    FAILED tests/test_user_access_policy.py::test_be35_sole_superadmin_self_deactivation_returns_403_without_mutation[with-profile-fields]
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_self_deactivation_returns_403_with_another_superadmin_active
    FAILED tests/test_user_access_policy.py::test_be35_superadmin_keeps_access_after_rejected_self_removal
    FAILED tests/test_user_access_policy.py::test_be58_admin_self_deactivation_returns_403_without_mutation[false]
    FAILED tests/test_user_access_policy.py::test_be58_admin_self_deactivation_returns_403_without_mutation[with-profile-field]
    FAILED tests/test_user_access_policy.py::test_be58_admin_keeps_access_after_rejected_self_removal
```

Los 17 coinciden con la tabla del plan en conteo y en nombres: 13 muertos; ASD, M5 y ASU vivos (equivalentes,
declarados) y M6 vivo a propósito (BE-37). Mutaciones aplicadas tal como las describe la tabla (M4: `actor.role != …`
sin `is_self_update`; M9: `False and is_self_update and …`).

## test-sanitizer (solo checklist)

Sin mocks; fábricas `make_user`, `persist_user`, `make_auth_headers`; nombres en inglés; contrato `{"detail"}` con
`set(body) == {"detail"}` e `isinstance(..., str)`, sin aserción sobre el texto en español; bordes ABAC (PATCH mixto,
`is_active: true` que pasa, token vivo tras el rechazo); `commit` antes de la petición (`persist_user`) y `refresh`
después (ADR-0011). Nada reescrito: los tests son el Anexo literal.

## Residuales y dudas

- Sin desviaciones respecto al plan. Ningún archivo fuera de los cuatro de la fase.
- E1: `AGENTS.md` aparece en el comando 11 solo por `87379f1` (commit de David previo a la fase B); no es hallazgo.
  Entre `87379f1` y `72fd34b` AGENTS §3 describió una regla que el código aún no cumplía (E1.3: se declara en el PR).
- Residuales del plan sin cambio: R1 (aviso sin salida para un superadmin; nota en BE-55, al cierre), R2 (`docs/CONTEXT.md`
  al cierre; la viñeta de AGENTS ya está por E1), R3 (nota FE-01 ya presente), R4 (M6 vivo, BE-37).
