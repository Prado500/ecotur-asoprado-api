# Handoff — BE-50 · Fase C (regla del enlace, docstrings y tests)

- **Commit de la fase:** `86b30f2` — `fix(auth): let the verification link change an account only once`. Comparé con
  `diff` el mensaje (`git log -1 --format=%B`) contra el bloque de la fase C del plan, sin la sangría: idéntico salvo la
  línea vacía final que añade git.
- **Rama:** `item/be-50`. **Base develop:** `c478e38`. `git fetch origin` correcto; `origin/develop` y
  `merge-base HEAD origin/develop` dan `c478e38`, igual que `verificacion.md`.
- **Compuerta:** invocada según E1 como `./venv/Scripts/python.exe scripts/check.py --soft imports`. En las dos
  corridas (arranque y salida) import-linter cargó y evaluó los contratos, así que rige E1.3.
- **Precondición de C** (plan.md:187-188, E0.5): en `docs/bitacora/2026-11-19.md`, sección "BE-50 fase B: PASS…"
  (líneas 385-420), constan los pasos de David en PostgreSQL después de B (`upgrade head`, `check` → `No new upgrade
  operations detected.`, `downgrade -1`, `upgrade head`, la columna `timestamp with time zone | YES` y `count` = `0`) y
  los contratos del Mentor sobre `git archive cba3ddd` (`Contracts: 4 kept, 0 broken.`).
- **Enmiendas aplicadas:** E0 (cifras del comando 4 y de MC2 y MC4) y E1 (compuerta con `--soft imports`). Ninguna
  cambia el texto del Anexo C.

## Archivos tocados (los 5 de la fase)
- `app/services/user_service.py`:
  - import `from datetime import UTC, datetime`;
  - `verify_email_account`: docstring y cuerpo del Anexo C. La guarda de la marca va antes de `changed_fields`. Después
    se escriben la marca e `is_active`, se llama a `save_user` siempre y se audita solo `if changes:`;
  - los cinco "single-use" (`:32`, `:38`, `:70`, `:104`, `:117`), con el texto del Anexo C;
  - las dos líneas de excepción en el docstring de `recover_user_account`.
- `app/core/security.py`: docstring de `create_verification_token` (Anexo C). `Args` y `Returns` no cambian.
- `app/api/routers/user.py`: docstring de `verificar_cuenta` (Anexo C).
- `tests/test_user_service.py`: import de `UTC, datetime`, la constante `VERIFIED_AT`, C1 ampliado, C2 en lugar de
  `test_verify_email_on_active_account_writes_nothing`, y C3 y C4 nuevos.
- `tests/test_auth.py`: C5 ampliado, C6 en lugar de `test_be38_verify_email_on_active_account_returns_200_without_audit_row`,
  C7 en lugar de `test_be38_verify_email_after_admin_deactivation_writes_an_audit_row` (en su mismo sitio), y C8 a C12
  nuevos tras C7, antes de `test_verify_email_invalid_token_returns_400`.

Texto de tests y código: el del Anexo C, literal. El formato lo dejó `ruff format` (hook), sin cambios de contenido.

## Diff (`git diff --stat 86b30f2~1 86b30f2`)
```
 app/api/routers/user.py      |   9 ++-
 app/core/security.py         |   6 +-
 app/services/user_service.py |  39 +++++++----
 tests/test_auth.py           | 149 ++++++++++++++++++++++++++++++++++++++++---
 tests/test_user_service.py   |  58 +++++++++++++++--
 5 files changed, 228 insertions(+), 33 deletions(-)
```

## Compuerta de arranque (antes de tocar nada)
- Código de salida `0`. RESUMEN: los seis pasos con `✔` y `Compuerta superada.`.
- `72 files already formatted` · `All checks passed!` · `Success: no issues found in 67 source files` ·
  `Contracts: 4 kept, 0 broken.` · docs coherente · `TOTAL 1067 10 154 6 98.69%` · `799 passed, 25 warnings`.

Coincide con el cierre de B (auditoría de B: 799 · 98,69 % · ruff 0 · mypy 0 en 67 · 4 kept).

## TDD
- **RED.** Primero los tests del Anexo C, sin tocar `app/`. Resultado de la suite completa: `11 failed, 795 passed, 25
  warnings`, que es la cifra del plan. Fallan C1 a C11; C12 pasa, como el plan declara:
  ```
  FAILED tests/test_auth.py::test_verify_email_endpoint_activates_account
  FAILED tests/test_auth.py::test_verify_email_on_account_an_admin_activated_fills_the_mark_without_audit_row
  FAILED tests/test_auth.py::test_verify_email_after_admin_deactivation_of_an_unverified_account_activates_it
  FAILED tests/test_auth.py::test_link_used_again_after_admin_deactivation_keeps_the_account_inactive
  FAILED tests/test_auth.py::test_second_click_on_the_link_changes_nothing_and_answers_another_message
  FAILED tests/test_auth.py::test_link_finishes_the_registration_of_a_recovered_account
  FAILED tests/test_auth.py::test_link_does_not_activate_a_recovered_account_that_was_verified
  FAILED tests/test_user_service.py::test_verify_email_activates_account
  FAILED tests/test_user_service.py::test_verify_email_on_active_account_fills_the_mark_without_audit
  FAILED tests/test_user_service.py::test_verify_email_with_the_mark_filled_changes_nothing
  FAILED tests/test_user_service.py::test_verify_email_second_use_answers_another_message
  11 failed, 795 passed, 25 warnings in 34.38s
  ```
- **GREEN.** Con los cambios de `app/`: `806 passed, 25 warnings in 32.08s`.

## Compuerta de salida (literal)
Código de salida: `0`.

Paso import-linter:
```
=== import-linter ===
=============
Import Linter
=============


---------
Contracts
---------

Analyzed 56 files, 148 dependencies.
------------------------------------

Capas: api | cli -> services -> repositories -> models KEPT
Los servicios no conocen el transporte HTTP KEPT
Los repositorios solo conocen SQLAlchemy y los modelos KEPT
Los modelos y los schemas no dependen de capas superiores KEPT

Contracts: 4 kept, 0 broken.
--- import-linter: OK en 0.2s
```

RESUMEN:
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

Otras líneas de la salida:
- `Raíz del repo: C:\projects\ecotur-asoprado · Python 3.14.3`
- `72 files already formatted` · `All checks passed!` · `Success: no issues found in 67 source files`.
- `Documentación coherente (reglas: R1 comandos, R2 fechas de cronograma, R3 bloques, R4 decisiones, R5 deadline).`
- `TOTAL                                       1071     10    156      6  98.70%`
- `Required test coverage of 92.0% reached. Total coverage: 98.70%`
- `806 passed, 25 warnings in 33.84s`

**E1.2:**
- (a) exit 0: ✔.
- (b) la última línea es `Compuerta superada.`, la forma que E1.2(b) admite cuando el paso sale en verde: ✔.
- (c) no hay ningún `✘`: ✔.
- (d) no aplica, porque el paso no falló.

**E1.3:** el paso evaluó contratos, y la salida dice `Contracts: 4 kept, 0 broken.`: ✔. Pasó de 147 a 148
dependencias por el import de `datetime` en el servicio.

**Ratchet frente a la línea base** (verificacion.md: 797 · 98,69 % · ruff 0 · mypy 0 en 66 · 4 kept; cierre de B: 799 ·
98,69 % · mypy 0 en 67):

| Medida | Línea base | Fase C | Lectura |
|---|---|---|---|
| pytest | 797 (799 tras B) | 806 passed, 0 failed | +7, los del plan |
| Cobertura | 98,69 % | 98,70 % (1071 sentencias, 156 ramas) | sube |
| ruff | 0 | 0 | igual |
| mypy | 0 en 66 (67 tras B) | 0 en 67 | igual |
| Contratos | 4 kept | 4 kept, 0 broken | igual |

E0.3 midió en Linux `806 passed, 98,70 %`, lo mismo.

**Ruff y mypy sobre los archivos tocados:**
- `python -m ruff check` sobre los 5 archivos → `All checks passed!`.
- `ruff format --check` sobre los mismos 5 → `5 files already formatted`.
- `python -m mypy` sobre los mismos 5 → `Success: no issues found in 5 source files`.

## Mutantes (copias `git archive 86b30f2` en el scratchpad, una por mutante)
Cada mutante se aplicó con un script que exige que el patrón aparezca una sola vez. `diff --strip-trailing-cr` contra el
archivo del repo muestra solo el cambio buscado. Cada copia corrió la suite completa con
`C:/projects/ecotur-asoprado/venv/Scripts/python.exe -m pytest`. Antes de cada corrida comprobé que `app` se importaba
desde la copia: `os.path.dirname(app.__file__)` apuntaba a `...\scratchpad\mutC\MCn\app`.

| Mutante | Cambio | Resultado | Tests que fallan | Plan/E0 |
|---|---|---|---|---|
| MC1 | sin la guarda de la marca (las 2 líneas) | `5 failed, 801 passed` | C3, C4, C8, C9, C11 | igual |
| MC2 | sin `user.email_verified_at = datetime.now(UTC)` | `9 failed, 797 passed` | C1, C2, C4, C5, C6, C7, C8, C9, C10 | igual a E0.2 |
| MC3 | la guarda devuelve el mensaje de éxito | `3 failed, 803 passed` | C4, C8, C9 | igual |
| MC4 | la guarda lee `if user.is_active:` | `5 failed, 801 passed` | C2, C3, C6, C8, C11 | igual a E0.2 |
| MC5 | `save_user` dentro de `if changes:` | `2 failed, 804 passed` | C2, C6 | igual |
| MC6 | `log_transaction` fuera de `if changes:` | `2 failed, 804 passed` | C2, C6 | igual |

Los seis, **muertos**.

## Verificación final (C es la última fase; Git Bash, árbol de `86b30f2`)
| # | Comando (resumen) | Resultado | Esperado |
|---|---|---|---|
| 1 | `single-use` en app y tests | `0` | 0 |
| 2 | guarda / `changed_fields` | `159:` / `162:` | 1 y 1; la guarda antes |
| 3 | mensajes en app / en tests | `1`, `1` / `0` | 1, 1 / 0 |
| 4 | patrón de dato nuevo | `7` | 7 (E0.2; el plan decía 8) |
| 5 | nombres viejos de los tests | `0` | 0 |
| 6 | `BE-50` en `.py` | `app/models/user.py:57`, `tests/test_migration_email_verified_at.py:1`, `alembic/versions/e50a7c3d9b12_users_email_verified_at.py:1` | esos 3 |
| 7 | tests que golpean el enlace | `tests/test_auth.py`, `tests/test_email.py`, `tests/test_email_case.py` | esos 3 |
| 8 | escritores de `is_active` | `8` | 8 |
| 9 | `email_verified_at` en app / escrituras / schemas | `5` / `app/services/user_service.py:163: user.email_verified_at = datetime.now(UTC)` / `0` | 5 / 1 / 0 |
| 10 | descendientes de `b51f3c9e2a64` | `1` | 1 |
| 11 | ADR | `docs/adr/0022-la-marca-de-correo-verificado-decide-el-enlace.md`; `<FECHA` = `0` | 1 archivo; 0 |
| 12 | `git diff --name-only 4f9e29e HEAD -- app alembic tests docs/adr` | los 10 archivos del plan, ni uno más | los 10 |
| 13 | compuerta | ver "Compuerta de salida" | exit 0; 806; ≥ 98,69 %; ruff 0; mypy 0; 4 kept |

## skill `test-sanitizer` (solo como checklist, sobre los dos archivos de test)
Los tests nuevos y reescritos ya cumplen los cinco estándares, así que no reescribí nada:
1. Mocks: los unitarios usan los fixtures `user_repo` y `audit_service` que ya existían (`create_autospec`). Los de
   integración no usan mocks.
2. Fixtures DRY: los usuarios salen de `make_user` y `persist_user`, y las cabeceras de `make_auth_headers`.
3. Inglés: todos los nombres, variables y docstrings están en inglés.
4. Contratos de datos: se afirma sobre el código HTTP, las claves (`{"success", "message"}`), la marca, `is_active` y las
   filas de auditoría. El segundo mensaje se compara como distinto del primero, nunca por su texto. El comando 3 da 0
   textos en español en los tests.
5. ABAC: C12 prueba que un PATCH de admin con la clave `email_verified_at` no escribe la marca ni la expone.

## Desviaciones y hallazgos
- **El hook quitó un import mientras escribía los tests.** Mi primera edición añadió `UTC, datetime` al import de
  `tests/test_user_service.py` antes de usarlos. El `ruff check --fix` del hook los borró por no usados (F401), y la
  siguiente edición, que ya los usaba, dio F821. Volví a añadir el import. Pasó lo mismo en `app/services/user_service.py`,
  en orden inverso: el cuerpo antes que el import. Es inocuo, porque el estado final es el del Anexo C, pero el auditor
  lo puede ver en la secuencia. No cambia nada del plan.
- **`current_target` queda en `null`.** C es la última fase, y es el valor que tienen las 22 carpetas de deuda cerradas.
- Aparte de eso, ninguna. RED, GREEN, mutantes y comandos coinciden con el plan corregido por E0.

## Residuales
- Los del plan (R1 a R6) siguen como están. R3 (qué muestra el cliente Flutter tras el segundo clic) y R5 (la viñeta
  de AGENTS §3) son de David antes del PR.
- Ninguno nuevo.

## Pendientes para David
1. `/auditar BE-50 C`.
2. E1.5: el Mentor mide los contratos sobre `git archive 86b30f2` en Linux. En esta máquina ya salieron
   `4 kept, 0 broken`.
3. R3: comprobar en el cliente Flutter qué muestra la pantalla tras el segundo clic, antes de mezclar.
4. R5: la viñeta de AGENTS §3, después de la última auditoría (decisión 13).
5. `/pr`. La descripción declara E1 como evidencia estructural, como manda E1.5.
