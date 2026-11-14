# Handoff — BE-34 · Fase G (BE-51: correo en minúsculas, `CHECK` y su migración)

- Commit de la fase: `9c9edd2` — `fix(users): store every email in lowercase, enforced by the database` (mensaje exacto
  del plan, l. 1882-1905, sin la sangría del bloque; `diff <(git log -1 --format=%B) <mensaje dictado>` → solo la línea en
  blanco final que añade `%B`). Trailer `Co-Authored-By` incluido.
- Rama: `item/be-34`, sobre `06c8929` (auditoría de F, PASS).
- Ejecutor: Claude Opus 5.5 (`fase-ejecutor`), 14 nov 2026.
- Enmiendas que aplican: E2 (mecanismo), E3 (aprobación de G; 3.3 se queda el test del 404 con otra grafía; 3.4 se
  borra `mixed_case_domain`; 3.5 migración en batch sobre SQLite propio; 3.6 Q1 = 0 en `develop`, precondición
  cumplida). E4 (fase H): nada hecho; `tests/test_bootstrap_superadmin_command.py` sin tocar.

## Ritual de arranque

- `git status --short`: limpio. HEAD `06c8929`. `current_target` = `Fase_G`. `gaps.md`: A–F PASS, 0 bloqueantes.
- Vigencia de la línea base: `git fetch origin` correcto (refrescado). `git rev-parse --short origin/develop` = `4f10660`;
  `git rev-parse --short $(git merge-base HEAD origin/develop)` = `4f10660`; `Base develop` de `verificacion.md` = `4f10660`.
- Compuerta antes de tocar nada (exit 0), igual a la fila F del plan: `67 files already formatted` ·
  `All checks passed!` · `Success: no issues found in 62 source files` · `Contracts: 4 kept, 0 broken.` ·
  `675 passed, 8 warnings` · `TOTAL 1031 17 148 14 97.37%` · `Compuerta superada.`

## Archivos tocados (los 5 de la fase)

`git show --stat --format= 9c9edd2`:

```
 ...b51f3c9e2a64_users_email_stored_in_lowercase.py |  35 +++
 app/models/user.py                                 |   5 +-
 app/schemas/user.py                                |  14 +-
 tests/test_email_case.py                           | 299 +++++++++++++++++++++
 tests/test_user_response.py                        |   2 -
 5 files changed, 348 insertions(+), 7 deletions(-)
```

`git show --numstat --format= 9c9edd2` (= criterio de aceptación, los cinco):

```
35	0	alembic/versions/b51f3c9e2a64_users_email_stored_in_lowercase.py
4	1	app/models/user.py
10	4	app/schemas/user.py
299	0	tests/test_email_case.py
0	2	tests/test_user_response.py
```

Cómo se escribió:
- `tests/test_email_case.py` (l. 1553-1851 del plan) y la migración (l. 1513-1547) se extrajeron con `sed` quitando los
  5 espacios de sangría del bloque (0 líneas no vacías sin esa sangría). Al no pasar por el hook, se corrió a mano:
  `ruff format --check` → `1 file already formatted`, `ruff check` → `All checks passed!`, `mypy` → `Success` (test).
  UTF-8, 0 `\r`.
- `app/schemas/user.py`: con `Edit`; los imports (`Annotated`, `AfterValidator`) entraron en la misma edición que
  `LowercaseEmail`, que los usa, así que el hook no borró nada (numstat `10 4` = plan).
- `app/models/user.py`: con un script de Python (import y `__table_args__` en la misma escritura, LF conservado);
  `ruff format --check` y `ruff check` pasados a mano.
- `tests/test_user_response.py`: con `Edit`, solo las dos líneas dictadas.

## Tests (RED → GREEN)

Comando de las tres etapas: `./venv/Scripts/python.exe -m pytest tests/test_email_case.py tests/test_user_response.py -q -p no:cacheprovider -rf --tb=no`.

1. Tests escritos (pasos 4 y 5), sin código: `13 failed, 15 passed, 2 warnings, 2 errors in 3.42s` (= plan). Los 2
   errores, los de la migración (archivo inexistente). Pasan los 13 de `test_user_response.py`,
   `test_a_patch_with_a_null_email_keeps_it_null` y `test_verification_token_in_another_case_is_rejected`.
2. Con los schemas (paso 1): `1 failed, 27 passed, 2 warnings, 2 errors in 1.33s` (= plan); solo
   `FAILED tests/test_email_case.py::test_database_rejects_an_email_with_an_uppercase_letter`.
3. Con el modelo y la migración (pasos 2 y 3): `30 passed, 2 warnings in 1.40s` (= plan).

`test-sanitizer` como checklist: sin mocks nuevos (usa `mock_send_email` de `tests/conftest.py`); usuarios por
`persist_user`/`make_user` (también los de la base propia de la migración, vía `_add`); nombres en inglés; aserciones
sobre códigos, claves `{"detail"}`, filas y llamadas con argumentos, ningún texto en español. No se reescribió nada.

## Mutantes (procedimiento común; un directorio nuevo por copia, `git archive HEAD` de `9c9edd2`)

Directorios: `scratchpad/copy_G_9c9edd2_<CLEAN|MG1..MG8>`. Suite sin `test_check*`.

- Copia limpia: `402 passed, 8 warnings in 20.39s` (= fila G).
- MG1 (`str.lower` → `str.strip`): `11 failed, 391 passed, 8 warnings` (= tabla). FAILED:
  `test_every_email_input_arrives_lowercased[UserBase]`, `[UserLogin]`, `[UserUpdate]`,
  `test_a_non_ascii_local_part_is_lowercased_too`, `test_registration_stores_the_email_in_lowercase`,
  `test_registration_rejects_an_email_taken_in_another_case`, `test_provisioning_rejects_an_email_taken_in_another_case`,
  `test_bootstrap_rejects_an_email_taken_in_another_case`, `test_login_accepts_the_email_typed_in_another_case`,
  `test_patch_stores_a_new_email_in_lowercase`, `test_patch_changing_only_the_case_keeps_the_email`.
- MG2 (`UserBase` con `EmailStr`): `5 failed, 397 passed, 8 warnings` (= tabla). FAILED:
  `test_every_email_input_arrives_lowercased[UserBase]`, `test_registration_stores_the_email_in_lowercase`,
  `test_registration_rejects_an_email_taken_in_another_case`, `test_provisioning_rejects_an_email_taken_in_another_case`,
  `test_bootstrap_rejects_an_email_taken_in_another_case`.
- MG3 (`UserLogin` con `EmailStr`): `3 failed, 399 passed, 8 warnings` (= tabla). FAILED:
  `test_every_email_input_arrives_lowercased[UserLogin]`, `test_a_non_ascii_local_part_is_lowercased_too`,
  `test_login_accepts_the_email_typed_in_another_case`.
- MG4 (`UserUpdate` con `EmailStr | None`): `3 failed, 399 passed, 8 warnings` (= tabla). FAILED:
  `test_every_email_input_arrives_lowercased[UserUpdate]`, `test_patch_stores_a_new_email_in_lowercase`,
  `test_patch_changing_only_the_case_keeps_the_email`.
- MG5 (sin `__table_args__`): `1 failed, 399 passed, 8 warnings, 2 errors` (= tabla). FAILED:
  `test_database_rejects_an_email_with_an_uppercase_letter`. Los 2 errores, en el fixture `pre_migration_db` de los dos
  tests de la migración: `ValueError: No such constraint: 'ck_users_email_lowercase'` (el `downgrade()` no la encuentra).
- MG6 (`'email = email'`): `1 failed, 401 passed, 8 warnings` (= tabla). FAILED:
  `test_migration_stops_on_an_email_with_an_uppercase_letter`.
- MG7 (`drop_constraint` → `pass`): `2 failed, 400 passed, 8 warnings` (= tabla). FAILED:
  `test_migration_adds_the_check_and_its_downgrade_drops_it`, `test_migration_stops_on_an_email_with_an_uppercase_letter`.
- MG8 (`activate_user` con `func.lower` a ambos lados): `1 failed, 401 passed, 8 warnings` (= tabla). FAILED, solo:
  `test_verification_token_in_another_case_is_rejected`.

Los ocho, muertos con la cifra exacta de la tabla. El repo no se tocó: cada mutante vive solo en su copia.

## Compuerta de salida (`./venv/Scripts/python.exe scripts/check.py`, exit 0)

Líneas clave:

```
68 files already formatted
All checks passed!
Success: no issues found in 63 source files
Contracts: 4 kept, 0 broken.
TOTAL                                       1034     15    148     13  97.63%
691 passed, 8 warnings in 28.77s
```

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

Frente a la fila G del plan (691 passed · 97,63 % (1034) · 68 files · 63 source files · 402 en la copia): igual en todo.
Ratchet frente a F: tests 675 → 691, cobertura 97,37 % → 97,63 %, contratos 4 kept = 4, ruff y mypy 0 errores.

Archivos tocados, uno por uno: `ruff check app/schemas/user.py app/models/user.py tests/test_email_case.py
tests/test_user_response.py` → `All checks passed!`; `ruff format --check` (los cuatro) → `4 files already formatted`;
`mypy` (los cuatro) → `Success: no issues found in 4 source files`. La migración está en `extend-exclude`
(`pyproject.toml:61`, `alembic/versions`) y fuera de mypy, como dice el plan; pasarla explícita a `ruff check` da 5
avisos de estilo de la plantilla (`UP035`, `I001`, `3×UP007`), los mismos que da la migración existente
`2cc4b57c136c` (más otros), y con `--force-exclude` → sin archivos que revisar. No se tocó: el plan dicta el estilo de
`script.py.mako`.

## Verificación final (pasos que el plan asigna al ejecutor: 10 a 18; el 19 es de David)

- **10** `git grep -n -E 'func\.lower|_same_email|ix_users_email_lower|ilike|casefold' -- app alembic tests` → sin
  salida, exit 1 (= plan).
- **11** `git grep -n 'User\.email ==' -- app` → 3 líneas (= plan):
  ```
  app/repositories/user_repository.py:18:        stmt = select(User).where(or_(User.cedula == cedula, User.email == email))
  app/repositories/user_repository.py:44:        stmt = select(User).where(User.email == email, User.deleted_at.is_(None))
  app/repositories/user_repository.py:56:        stmt = select(User).where(User.email == email)
  ```
- **12** `git grep -n 'LowercaseEmail' -- app` → 4 líneas en `app/schemas/user.py`: `:22`, `:39`, `:134`, `:166` (= plan).
- **13** `git grep -c 'ck_users_email_lowercase' -- app alembic tests` → (= plan)
  ```
  alembic/versions/b51f3c9e2a64_users_email_stored_in_lowercase.py:2
  app/models/user.py:1
  app/schemas/user.py:1
  tests/test_email_case.py:2
  ```
- **14** `alembic heads` (URL ficticia) → `b51f3c9e2a64 (head)`, exit 0 (= plan).
- **15** `alembic upgrade 2cc4b57c136c:b51f3c9e2a64 --sql` → exit 0; contiene
  `ALTER TABLE users ADD CONSTRAINT ck_users_email_lowercase CHECK (email = lower(email));` dentro de `BEGIN;` / `COMMIT;`
  junto a `UPDATE alembic_version SET version_num='b51f3c9e2a64' WHERE alembic_version.version_num = '2cc4b57c136c';`
  (= SQL literal del plan). Además, el `downgrade b51f3c9e2a64:2cc4b57c136c --sql` da
  `ALTER TABLE users DROP CONSTRAINT ck_users_email_lowercase;`.
- **16** `git diff --name-only 2bf29e5 -- app tests alembic docs/adr` (`<sha E>` = `2bf29e5`) → exactamente 6 (= plan):
  la migración, `app/models/user.py`, `app/schemas/user.py`, `docs/adr/0016-correo-en-minusculas.md`,
  `tests/test_email_case.py`, `tests/test_user_response.py`.
- **17** Patrón 2 de BE-34 → 9 líneas, 114 coincidencias (= plan): `.env.example:6` · `app/cli/bootstrap_superadmin.py:19` ·
  `app/core/config.py:12` · `app/repositories/user_repository.py:1` · `app/services/superadmin_bootstrap.py:3` ·
  `tests/test_bootstrap_superadmin_command.py:16` · `tests/test_config.py:41` · `tests/test_email_case.py:5` ·
  `tests/test_superadmin_bootstrap.py:11`.
- **18** Compuerta → exit 0; 691 passed, 8 warnings; TOTAL 1034 stmts, 97.63 %; 68 files; 63 source files; 4 kept (arriba).
- Pasos 6 y 7 tras G (el plan dice cómo cambian): el 6 lista solo la migración, `app/models/user.py` y
  `app/schemas/user.py` (`3 files changed, 49 insertions(+), 5 deletions(-)`); el 7 da 17 archivos (los 12 de A–E,
  ADR-0016, `app/models/user.py`, `app/schemas/user.py`, `tests/test_email_case.py`, `tests/test_user_response.py`).
- **19** (de David, antes de `/pr`): no ejecutado; pendiente.

## Residuales y dudas

- `progress.json`: `current_target` pasa a `Fase_H`, la siguiente según E4, pero esa clave no existe aún en `phases`:
  la añade el planificador (E4, punto 6) y H no se ejecuta sin E5. Si se prefiere otro valor hasta entonces, lo decide
  la sesión Mentor.
- Paso 19 (PostgreSQL local de David: `alembic upgrade head`, `alembic check`, consulta a `pg_constraint`) y Q1 antes de
  promover a `staging` y `main`: siguen pendientes, como dice el plan. R12 sigue vigente (todo lo de esta fase corrió
  sobre SQLite, salvo el SQL fuera de línea).
- Ninguna desviación del plan. Ningún hallazgo nuevo.
