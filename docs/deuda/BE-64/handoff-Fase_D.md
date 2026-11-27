# Handoff — BE-64 · Fase D (quién recibe un enlace nuevo y cuándo)

- **Commit de la fase:** `62c5c74` — `feat(auth): decide who may get a new verification link, and when` (mensaje
  exacto del plan, fase D, `plan.md:324-344`, extraído con `sed` sin reescribirlo; el cuerpo crudo del commit,
  `git cat-file commit HEAD`, sale idéntico con `diff`).
- **Rama:** `item/be-64`. HEAD al arrancar: `fa74b16` (árbol limpio). **Base develop:** `b6a80ba` (`git fetch origin`
  correcto; `git rev-parse --short origin/develop` y `git rev-parse --short $(git merge-base HEAD origin/develop)` =
  `b6a80ba`, igual a `verificacion.md`).
- **Requisito previo:** momento 2 de E1, punto 3, en `docs/bitacora/2026-11-27.md` (sección "BE-64: momento 2 de E1",
  10:37–10:38, commit `a3c0e90`): `Running upgrade e50a7c3d9b12 -> a64d0c2e7f15`, `check` → `No new upgrade operations
  detected.`, columna `timestamp with time zone | YES`, 0 filas llenas. No lo corrí yo.
- **Enmiendas aplicadas:** E0, E1 y E2 (E2 sustituye a E0, punto 5). Código y tests del Anexo D sin cambios, como
  manda E2, punto 2. No se tocó ningún ADR ni `plan.md`.
- **Compuerta:** `./venv/Scripts/python.exe scripts/check.py`, sin `--soft`. Windows no bloqueó `_rustgrimp`: E0,
  punto 3, no aplicó.

## Archivos tocados (4, los del plan)
- `app/repositories/user_repository.py`: `get_tourist_due_a_verification_link(email, sent_before)` tras
  `get_non_deleted_user_by_email`; solo `select`, sin `commit()`.
- `app/services/user_service.py`: `timedelta` en el import; `VerificationResend` tras `RegistrationResult`; dos líneas
  en el docstring de `register_tourist` y `verification_sent_at=datetime.now(UTC)` en su `User(...)`;
  `resend_verification_link` antes de `authenticate_user`.
- `tests/test_user_repository.py`: docstring del módulo, `timedelta`, `SENT_BEFORE` y los 10 casos de la consulta.
- `tests/test_user_service.py`: `test_register_tourist_counts_as_the_first_link_sent` y los 4 de reenvío.

Igualdad con el Anexo D: el diff se aplicó con `git apply` desde las líneas `plan.md:860-1157` (primero
`--include='tests/*'` para el RED, luego `--include='app/*'`). Los cuatro blobs del commit son `c31fa77`, `990c6e1`,
`5a9220a` y `8587f9c`, los de las líneas `index` del Anexo D (`b1b6e34..c31fa77`, `6e7d6ee..990c6e1`,
`9ce3827..5a9220a`, `40f20eb..8587f9c`; preimágenes también comprobadas antes de aplicar), y `git diff -U2` sin las
líneas `index`, comparado con `diff` contra el Anexo, sale idéntico. `git apply` no pasa por el hook de formato
(AF-18); `ruff format --check` sobre los cuatro: `4 files already formatted`.

## Diff (`git show --stat 62c5c74`)
```
 app/repositories/user_repository.py | 28 ++++++++++++
 app/services/user_service.py        | 50 ++++++++++++++++++++-
 tests/test_user_repository.py       | 70 ++++++++++++++++++++++++++++-
 tests/test_user_service.py          | 89 +++++++++++++++++++++++++++++++++++++
 4 files changed, 234 insertions(+), 3 deletions(-)
```

## Compuerta de arranque (antes de tocar nada)
Exit 0. `73 files already formatted` · `All checks passed!` · `Success: no issues found in 68 source files` ·
`Contracts: 4 kept, 0 broken.` · `810 passed, 25 warnings in 33.09s` · `TOTAL 1073 10 156 6 98.70%` ·
`Compuerta superada.` Igual al estado de salida de la fase C.

## RED (solo los dos archivos de test, sin `app/`)
`./venv/Scripts/python.exe -m pytest -q -p no:cacheprovider`, literal (líneas `E` con la causa, `FAILED` y conteo):
```
E       AttributeError: 'UserRepository' object has no attribute 'get_tourist_due_a_verification_link'
  (×10, una por caso de test_user_repository.py)
E       assert None is not None
E               AttributeError: Mock object has no attribute 'get_tourist_due_a_verification_link'
  (×4)
FAILED tests/test_user_repository.py::test_tourist_due_a_verification_link_is_found[inactive-never-sent]
FAILED tests/test_user_repository.py::test_tourist_due_a_verification_link_is_found[active-unverified]
FAILED tests/test_user_repository.py::test_tourist_due_a_verification_link_is_found[sent-before-the-cutoff]
FAILED tests/test_user_repository.py::test_tourist_due_a_verification_link_is_found[sent-at-the-cutoff]
FAILED tests/test_user_repository.py::test_account_not_due_a_verification_link_is_not_found[admin]
FAILED tests/test_user_repository.py::test_account_not_due_a_verification_link_is_not_found[superadmin]
FAILED tests/test_user_repository.py::test_account_not_due_a_verification_link_is_not_found[soft-deleted]
FAILED tests/test_user_repository.py::test_account_not_due_a_verification_link_is_not_found[verified]
FAILED tests/test_user_repository.py::test_account_not_due_a_verification_link_is_not_found[sent-after-the-cutoff]
FAILED tests/test_user_repository.py::test_due_verification_link_lookup_matches_only_its_email
FAILED tests/test_user_service.py::test_register_tourist_counts_as_the_first_link_sent
FAILED tests/test_user_service.py::test_resend_issues_a_link_to_the_account_due_one
FAILED tests/test_user_service.py::test_resend_with_no_account_due_writes_nothing
FAILED tests/test_user_service.py::test_resend_interval_comes_from_the_settings
FAILED tests/test_user_service.py::test_resend_save_failure_propagates_without_a_link
15 failed, 810 passed, 25 warnings in 36.07s
```
(Las líneas `(×10)` y `(×4)` resumen líneas `E` idénticas repetidas; el resto es literal.) Es el esperado del plan:
`15 failed, 810 passed`, con las tres causas de la fila "D RED".

## Compuerta de salida (literal)
Exit 0. Líneas por paso:
```
73 files already formatted
--- ruff format --check: OK en 0.1s
All checks passed!
--- ruff check: OK en 0.1s
Success: no issues found in 68 source files
--- mypy: OK en 0.7s
Analyzed 56 files, 148 dependencies.
Capas: api | cli -> services -> repositories -> models KEPT
Los servicios no conocen el transporte HTTP KEPT
Los repositorios solo conocen SQLAlchemy y los modelos KEPT
Los modelos y los schemas no dependen de capas superiores KEPT
Contracts: 4 kept, 0 broken.
--- import-linter: OK en 0.2s
--- docs (coherencia): OK en 0.1s
TOTAL                                       1087     10    158      6  98.71%
825 passed, 25 warnings in 34.50s
--- pytest + cobertura: OK en 37.5s
```

Bloque RESUMEN, literal:
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
- pytest: `825 passed, 25 warnings` (0 failed). Plan: `825 passed`. ✔
- Cobertura: `98.71%` (línea base 98,70 %; plan: medido 98,71 %). ✔
- mypy: 0 errores en 68 archivos. ✔
- ruff: 0 errores; `73 files` formateados (ningún archivo nuevo). ✔
- import-linter: `4 kept, 0 broken` (línea base 4). ✔

## Ruff, mypy y criterios del plan sobre lo tocado
- `python -m ruff check <los cuatro>` → `All checks passed!`; `python -m ruff format --check <los cuatro>` →
  `4 files already formatted`; `python -m mypy <los cuatro>` → `Success: no issues found in 4 source files`.
- `grep -c "commit()" app/repositories/user_repository.py` → `3` (el método nuevo no hace commit; A3). ✔
- `grep -c "log_transaction" app/services/user_service.py` → `6` (como antes; sin auditoría del reenvío). ✔
- `grep -rn "create_verification_token(" app --include=*.py | wc -l` → `3`. ✔
- **E2, punto 4:** `grep -rn "monkeypatch.setattr(get_settings()" tests` →
  `tests/test_user_service.py:477:    monkeypatch.setattr(get_settings(), "verification_resend_interval_seconds", 300)`;
  con `| wc -l` → `1`. Es `test_resend_interval_comes_from_the_settings`, el caso que admite el addendum de ADR-0013
  (`458fc01`); ningún otro test de la fase cambia la configuración por esa vía. ✔

## Mutantes MD1–MD15 (cada uno en su copia, suite completa)
Copias `git archive HEAD` (HEAD `fa74b16`) + los cuatro archivos de la fase, en `be64D-mut/be64D-MD1` …
`be64D-MD15` del scratchpad (carpetas nuevas); intérprete del venv por ruta, cwd = la copia; `import app;
app.__file__` → `…\scratchpad\be64D-mut\be64D-MDn\app\__init__.py` en las quince. Mutante aplicado por reemplazo
exacto (el script exige que el ancla aparezca una sola vez). Las copias no tienen `.env`.

| # | Mutante | Resultado literal | Lo matan |
|---|---|---|---|
| MD1 | `register_tourist` sin `verification_sent_at=` | `1 failed, 824 passed` | `test_register_tourist_counts_as_the_first_link_sent` |
| MD2 | consulta sin `User.role == UserRole.tourist` | `2 failed, 823 passed` | `…_is_not_found[admin]`, `[superadmin]` |
| MD3 | consulta sin `deleted_at.is_(None)` | `1 failed, 824 passed` | `…_is_not_found[soft-deleted]` |
| MD4 | consulta sin `email_verified_at.is_(None)` | `1 failed, 824 passed` | `…_is_not_found[verified]` |
| MD5 | `or_(…)` → solo `verification_sent_at <= sent_before` | `2 failed, 823 passed` | `…_is_found[inactive-never-sent]`, `[active-unverified]` |
| MD6 | `<=` → `<` | `1 failed, 824 passed` | `…_is_found[sent-at-the-cutoff]` |
| MD7 | sin la condición de hora | `1 failed, 824 passed` | `…_is_not_found[sent-after-the-cutoff]` |
| MD8 | el servicio no sella la hora | `1 failed, 824 passed` | `test_resend_issues_a_link_to_the_account_due_one` |
| MD9 | el servicio no llama a `save_user` | `2 failed, 823 passed` | `test_resend_issues_a_link…`, `test_resend_save_failure_propagates_without_a_link` |
| MD10 | intervalo fijo `timedelta(seconds=60)` | `1 failed, 824 passed` | `test_resend_interval_comes_from_the_settings` |
| MD11 | `now + interval` | `2 failed, 823 passed` | `test_resend_issues_a_link…`, `test_resend_interval_comes_from_the_settings` |
| MD12 | el reenvío escribe una fila de auditoría (`log_transaction` UPDATE tras `save_user`) | `1 failed, 824 passed` | `test_resend_issues_a_link_to_the_account_due_one` |
| MD13 | consulta exige `User.is_active.is_(False)` | `1 failed, 824 passed` | `…_is_found[active-unverified]` |
| MD14 | consulta sin `User.email == email` | `1 failed, 824 passed` | `test_due_verification_link_lookup_matches_only_its_email` |
| MD15 | `save_user` en `try/except Exception: pass` | `1 failed, 824 passed` | `test_resend_save_failure_propagates_without_a_link` |

15 muertos, 0 vivos; coinciden con la columna "Lo matan" del plan en el estado de la fase D (los tests HTTP que el
plan lista como "final: +" son de la fase E y aún no existen).

## Skill `test-sanitizer` (solo checklist, "Ecotur Enterprise Test Standards")
Sobre los dos archivos de test: (1) mocks: `user_repo` y `audit_service` son `create_autospec(…, instance=True)`
(fixtures ya existentes del módulo); la consulta se prueba contra la base de la suite, sin mock; (2) preparación con
las fábricas centralizadas `persist_user` y `make_user`, sin usuarios a mano; (3) nombres, docstrings y variables en
inglés (los correos de ejemplo son datos, no aserciones de texto); (4) ninguna aserción sobre texto humano: se afirma
sobre identidad del objeto, `None`, claims del JWT, horas y llamadas a mocks con argumentos
(`assert_awaited_once_with`, `assert_not_awaited`); (5) ABAC: el filtro por rol del dato está cubierto por
`[admin]` y `[superadmin]`. No se reescribió nada: los tests son los dictados por el Anexo D.

## Incidencias y desviaciones
- Ninguna desviación del plan ni de E2. No se tocó `plan.md`, `verificacion.md`, ningún ADR ni ningún archivo fuera
  de los cuatro de la fase.
- No leí `.env`. La suite no lo lee (el `conftest.py` raíz fija todas las variables).
- `rm -rf` está denegado por permisos: las copias de mutantes quedan en `be64D-mut/` del scratchpad.

## Residuales
Ninguno nuevo. Siguen vigentes los del plan (R1, R2, R5…); la comparación `timestamptz` en PostgreSQL sigue sin
medirse en la suite (SQLite): la cubre el momento 3 de E1, punto 3, de David, tras la auditoría de E.

## Siguiente paso
- `/auditar BE-64 D` (incluye la comprobación de E2, punto 4: `grep -rn "monkeypatch.setattr(get_settings()" tests`
  → 1).
- Después, `/implementar BE-64 E`. La fase E no tiene paso previo de David; el momento 3 (pruebas contra PostgreSQL
  con la API levantada) va después de la auditoría de E y antes de `/pr`.
