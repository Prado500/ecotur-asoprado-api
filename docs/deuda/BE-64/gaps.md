# Gaps — BE-64

## Auditoría Fase A — 2026-11-27
**Veredicto Fase A: PASS (0 bloqueantes, 0 opcionales).**
Sin hallazgos.

### Evidencia

**Árbol y commits.** `git status --short` → vacío (antes y después de la compuerta). `git log --oneline -3`:
`9235fdd docs(progress): record BE-64 Fase_A completion`, `0a07a47 docs(adr): add ADR-0023, a verification link can be
asked for again`, `3674c80 docs(apertura): 27 nov, opening log after a week away; BE-65 severity`.

**Base de la fase.** El padre de `0a07a47` es `3674c80` (`git show --format=%P`), no `28de107`, que era el HEAD tras la
aprobación. `git diff --name-only 28de107 3674c80` → solo `docs/CONTEXT.md`, `docs/PLAN.md`, `docs/backlog.md`,
`docs/bitacora/2026-11-27.md`: ningún archivo de código ni de `docs/adr` ni de `docs/deuda/BE-64`, así que la línea base
de `verificacion.md` y el comando 15 de la Verificación final (`git diff --name-only 22328ce HEAD -- app alembic tests
conftest.py .env.example docs/adr`) no cambian.

**Commit de la fase (`0a07a47`).** Hash real (`git cat-file -t` → `commit`). `git show --stat 0a07a47` → 1 archivo,
`docs/adr/0023-el-enlace-de-verificacion-se-puede-pedir-de-nuevo.md`, 85 inserciones; `git diff --name-only 3674c80
0a07a47` → solo ese archivo. Mensaje: `diff` entre plan.md:209-223 (sin la sangría de dos espacios) y
`git log -1 --format=%B 0a07a47` (sin la línea vacía final de git) → idéntico, `Co-Authored-By` incluido.

**Cambios exactos (Anexo A + E1.1).** `diff` entre plan.md:506-590 con `<FECHA DE APROBACIÓN>` sustituido por
`19 nov 2026` y `git show 0a07a47:docs/adr/0023-…md` → idéntico. El texto lleva E0.2 (decisión 1 con `MessageResponse`,
alternativa 8) y E0.1 (nota de AGENTS §4 (b)); la cifra de mutantes es 33, la que confirma E1.2. `grep -c "<FECHA"
docs/adr/0023-*.md` → `0`. `ls docs/adr/0023*` → un solo archivo; no hay otro ADR con el número 0023. UTF-8, 85 líneas,
termina en salto de línea. `git diff 0a07a47 HEAD -- docs/adr` → vacío (nadie lo tocó después).

**Segundo commit (`9235fdd`).** Toca solo `docs/deuda/BE-64/handoff-Fase_A.md` y `docs/deuda/BE-64/progress.json`, con
`docs(progress): record BE-64 Fase_A completion`, como manda el protocolo de `fase-ejecutor` y como hicieron BE-50 y
BE-38. Ningún archivo de otra fase.

**progress.json.** JSON válido. `Fase_A`: `completed`, `commit: "0a07a47"`. `current_target`: `Fase_A` → `Fase_B`.
`last_handoff` presente. `edit_rules` y `allowed_statuses` sin cambios (`git diff 0a07a47 9235fdd --
docs/deuda/BE-64/progress.json`: solo cambian `current_target`, `status`, `commit` y `last_handoff`).

**Handoff.** Las cifras de la compuerta que pega (`806 passed`, `98.70%`, `4 kept`, 72/67 archivos) coinciden con las
de esta re-ejecución. La diferencia con el Anexo que declara (solo la línea 3) es la que mide el `diff` de arriba.

**Compuerta re-ejecutada por el auditor** (`./venv/Scripts/python.exe scripts/check.py`, sin `--soft`). Código de salida
`0`. Windows no bloqueó `_rustgrimp`: E0.3 no aplica.

Paso import-linter (literal, extracto):
```
Analyzed 56 files, 148 dependencies.
------------------------------------

Capas: api | cli -> services -> repositories -> models KEPT
Los servicios no conocen el transporte HTTP KEPT
Los repositorios solo conocen SQLAlchemy y los modelos KEPT
Los modelos y los schemas no dependen de capas superiores KEPT

Contracts: 4 kept, 0 broken.
--- import-linter: OK en 0.2s
```

RESUMEN (literal):
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

Otras líneas: `72 files already formatted` · `All checks passed!` · `Success: no issues found in 67 source files` ·
`Documentación coherente (...)` · `TOTAL 1071 10 156 6 98.70%` · `Required test coverage of 92.0% reached. Total
coverage: 98.70%` · `806 passed, 25 warnings in 34.93s`.

**Ratchet frente a la línea base** (verificacion.md:114-118, 139: 806 passed · 98,70 % · ruff 0 · mypy 0 en 67 · 4 kept):
pytest 806, 0 failed (= criterio de la fase, `806 passed`); cobertura 98,70 %, igual; ruff 0 en 72, igual; mypy 0 en 67,
igual; 4 kept, igual. Ruff y mypy por archivo no aplican: la fase solo toca un `.md`. Tests de la fase: no aplica (plan,
fase A). AGENTS.md: sin código nuevo que revisar.

**Criterio de aceptación de la fase A:** el archivo existe ✔; `grep -c "<FECHA"` → `0` ✔; compuerta en verde con
`806 passed` ✔. No es la última fase: la Verificación final corre tras la fase E.

## Auditoría Fase B — 2026-11-27
**Veredicto Fase B: PASS (0 bloqueantes, 0 opcionales).**
Sin hallazgos.

### Evidencia

**Árbol y commits.** `git status --short` → vacío (antes y después de la compuerta). `git log --oneline -3`:
`4369590 docs(progress): record BE-64 Fase_B completion`, `f22ce02 feat(users): add the verification_sent_at column,
empty in every row`, `c84f12e docs(item-be64): log phase A and the alembic check before phase B`.

**Requisito previo (E1.3, momento 1).** `docs/bitacora/2026-11-27.md:62-77` (commit `c84f12e`, padre de la fase):
`alembic current` → `e50a7c3d9b12 (head)`; `alembic check` → `No new upgrade operations detected.`. Corrido por David;
el auditor no corrió Alembic contra ninguna base.

**Commit de la fase (`f22ce02`).** Hash real (`git cat-file -t` → `commit`), padre `c84f12e`. `git show --stat` → 4
archivos, 136 inserciones, los cuatro de la fase B: `alembic/versions/a64d0c2e7f15_users_verification_sent_at.py`
(nuevo), `app/models/user.py`, `tests/test_migration_verification_sent_at.py` (nuevo), `tests/test_models_schema.py`.
Mensaje: `diff` entre plan.md (bloque **Commit** de la fase B, sin la sangría de dos espacios) y `git log -1
--format=%B f22ce02` (sin la línea vacía final) → idéntico, `Co-Authored-By` incluido.

**Cambios exactos (Anexo B).** Blobs de `f22ce02` (`git rev-parse --short f22ce02:<archivo>`) = lado derecho de las
líneas `index` del Anexo B: migración `2aba32d`, modelo `48cd9d8`, test de migración `33d83c4`, test de esquema
`f26f634`; y blobs de `c84f12e` = lado izquierdo: modelo `de1fbdd`, test de esquema `aae976e`. Contenido idéntico byte a
byte al Anexo; la migración conserva comillas simples y el import de `alembic` antes que `sqlalchemy` (excepción
`(backlog AF-18)` que declara el Anexo).

**Segundo commit (`4369590`).** Toca solo `docs/deuda/BE-64/handoff-Fase_B.md` y `docs/deuda/BE-64/progress.json`
(`git diff --name-only f22ce02 HEAD`). Ningún archivo de otra fase.

**progress.json.** JSON válido. `Fase_B`: `pending` → `completed`, `commit: null` → `"f22ce02"`. `current_target`:
`Fase_B` → `Fase_C` (E1.3 permite C antes del momento 2; D queda condicionada). `last_handoff` presente. `edit_rules`
y `allowed_statuses` sin cambios (`git diff f22ce02 4369590 -- docs/deuda/BE-64/progress.json`).

**RED reproducido por el auditor.** Copia `git archive c84f12e` + los dos tests de `f22ce02`, sin `app/` ni `alembic/`
de la fase (`import app` → la copia): `1 failed, 805 passed, 25 warnings, 2 errors in 34.00s`; FAILED
`test_table_columns_match_the_frozen_schema[users]`, ERROR los dos de `test_migration_verification_sent_at.py`. Igual
al plan y al handoff.

**Compuerta re-ejecutada por el auditor** (`./venv/Scripts/python.exe scripts/check.py`, sin `--soft`). Código de salida
`0`. Windows no bloqueó `_rustgrimp`: E0.3 no aplica.

Paso import-linter (literal, extracto):
```
Capas: api | cli -> services -> repositories -> models KEPT
Los servicios no conocen el transporte HTTP KEPT
Los repositorios solo conocen SQLAlchemy y los modelos KEPT
Los modelos y los schemas no dependen de capas superiores KEPT
Contracts: 4 kept, 0 broken.
--- import-linter: OK en 0.3s
```

RESUMEN (literal):
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

Otras líneas: `73 files already formatted` · `All checks passed!` · `Success: no issues found in 68 source files` ·
`Documentación coherente (...)` · `TOTAL 1072 10 156 6 98.70%` · `Required test coverage of 92.0% reached. Total
coverage: 98.70%` · `808 passed, 25 warnings in 30.93s`.

**Ratchet frente a la línea base** (verificacion.md: 806 passed · 98,70 % · ruff 0 · mypy 0 en 67 · 4 kept): pytest 808,
0 failed (= criterio de la fase, `808 passed`); cobertura 98,70 %, igual; ruff 0 en 73; mypy 0 en 68 (= criterio de la
fase); 4 kept, igual.

**Ruff y mypy por archivo.** `ruff check --force-exclude <los cuatro>` → `All checks passed!`; `ruff format --check
--force-exclude <los cuatro>` → `3 files already formatted` (la migración queda fuera por `extend-exclude`,
`pyproject.toml:61`); `mypy <los cuatro>` → `Success: no issues found in 4 source files`. Sin `--force-exclude`, la
migración nueva y `e50a7c3d9b12_users_email_verified_at.py` dan 5 errores cada una (`Found 10 errors.` juntas): es el
texto que fija el Anexo B, igual que la migración de BE-50 `(backlog AF-18)`; no cuenta en la compuerta.

**SQL fuera de línea (criterio de aceptación), repetido en una copia `git archive f22ce02` sin `.env`.**
`DATABASE_URL=postgresql+asyncpg://u:p@localhost:5432/db ./venv/Scripts/python.exe -m alembic upgrade
e50a7c3d9b12:a64d0c2e7f15 --sql` → exit 0; contiene `ALTER TABLE users ADD COLUMN verification_sent_at TIMESTAMP WITH
TIME ZONE;`; `grep -c "UPDATE users"` → `0`. Downgrade fuera de línea (`a64d0c2e7f15:e50a7c3d9b12 --sql`) → solo
`ALTER TABLE users DROP COLUMN verification_sent_at;`. `alembic heads` → `a64d0c2e7f15 (head)`; una sola migración
desciende de `e50a7c3d9b12`.

**Mutantes MB1–MB5, re-medidos por el auditor** (una copia `git archive f22ce02` por mutante, reemplazo con ancla
única, `import app` → la copia; ejecutados `tests/test_models_schema.py` y `tests/test_migration_verification_sent_at.py`):
MB1 → `1 failed` (`…_adds_the_column_empty_in_every_row`); MB2 → `2 failed` (los dos de migración); MB3 → `1 failed, 2
errors` (`…frozen_schema[users]` y los dos de migración, `IntegrityError: NOT NULL`); MB4 → `1 failed`
(`…frozen_schema[users]`); MB5 → `1 failed` (`…downgrade_drops_only_its_column_and_keeps_the_rows`). 5 muertos, 0 vivos;
los asesinos coinciden con la tabla del Análisis. Los totales de suite completa del handoff (MB3: 258) no se repitieron.

**AGENTS.md.** Modelo en estilo 2.0 (§3, S1): `Mapped[datetime | None]` da la nulabilidad, sin `nullable=`; tipo SQL
explícito `DateTime(timezone=True)`; sin default; `User` ya está en `app/models/__init__.py`. Cambio de esquema por
Alembic, con `down_revision` correcto y downgrade que borra solo su columna. Tests (§5): sin mocks; cuentas con
`make_user`; identificadores y docstrings en inglés; ninguna aserción sobre texto en español; afirman estructura
(nulabilidad, columnas) y estado (filas, valores NULL, marca de verificado). Sin excepciones de dominio, rutas ni
variables nuevas en esta fase.

**Criterio de aceptación de la fase B:** compuerta en 0 con `808 passed` ✔; cobertura 98,70 % ≥ 98,70 % ✔; mypy en 68
archivos ✔; SQL fuera de línea con el `ALTER TABLE` y sin `UPDATE users` ✔ (copiado en el handoff ✔); MB1–MB5 muertos ✔.
No es la última fase: la Verificación final corre tras la fase E. Siguiente, de David: momento 2 de E1.3 (cuatro
comandos de `alembic` y dos consultas) antes de `/implementar BE-64 D`.

## Auditoría Fase C — 2026-11-27
**Veredicto Fase C: PASS (0 bloqueantes, 0 opcionales).**
Sin hallazgos.

### Evidencia

**Árbol y commits.** `git status --short` al empezar → vacío. `git log --oneline -3`: `f3a2ff2 docs(progress): record
BE-64 Fase_C completion`, `a218a65 feat(config): add the minimum wait between two verification links`, `a3c0e90
docs(item-be64): log David's PostgreSQL steps after phase B`. Durante la auditoría (10:53:07) aparecieron sin commitear
los archivos de la enmienda E2 de la sesión Mentor (`docs/adr/0013-…`, `docs/bitacora/2026-11-27.md`,
`docs/deuda/BE-64/plan.md`, `docs/commit-msg.txt`); David los commiteó en `458fc01` (10:56:05, `docs(adr): add an
addendum to ADR-0013 on patching the cached Settings`, 3 archivos, ninguno de código) y el árbol volvió a quedar vacío.
No son de la fase C ni cambian sus cifras: la compuerta se repitió en una copia limpia de `f3a2ff2` (abajo) y
`scripts/check.py --no-tests` sobre `458fc01` → `Compuerta superada.` (docs coherentes).

**Requisito de la fase D (E1.3, momento 2), ya presente.** `docs/bitacora/2026-11-27.md:110-146` en `f3a2ff2` (commit
`a3c0e90`, padre de la fase): `Running upgrade e50a7c3d9b12 -> a64d0c2e7f15`, `No new upgrade operations detected.`,
`verification_sent_at | timestamp with time zone | YES`. Lo corrió David; el auditor no corrió Alembic contra ninguna base.

**Commit de la fase (`a218a65`).** Hash real (`git cat-file -t` → `commit`), padre `a3c0e90`. `git show --stat` → 4
archivos, 33 inserciones y 1 borrado: `.env.example`, `app/core/config.py`, `conftest.py`, `tests/test_config.py`, los
cuatro de la fase C. Mensaje: `diff` entre el bloque **Commit** de la fase C de `plan.md` en `f3a2ff2` (líneas 284-299,
sin la sangría de dos espacios) y `git log -1 --format=%B a218a65` (sin la línea vacía final) → idéntico,
`Co-Authored-By` incluido.

**Cambios exactos (Anexo C).** Blobs de `a3c0e90` / `a218a65` (`git rev-parse --short`) = lados izquierdo / derecho de
las líneas `index` del Anexo C: `.env.example` `8579089`→`4000dc2`, `app/core/config.py` `38173b7`→`35cd82a`,
`conftest.py` `ff2cd6d`→`7a65482`, `tests/test_config.py` `131e0db`→`de1c8ab`. Además, `git diff -U2 a3c0e90 a218a65`
sin las líneas `index`, comparado con `diff` contra el Anexo C de `plan.md` → idéntico. Ninguno de los cuatro archivos
cambió después (`git diff --name-only a218a65 HEAD -- <los cuatro>` → vacío). E2 no cambia la fase C (E2.2, E2.5).

**Segundo commit (`f3a2ff2`).** Toca solo `docs/deuda/BE-64/handoff-Fase_C.md` y `docs/deuda/BE-64/progress.json`
(`git diff --name-only a218a65 f3a2ff2`). Ningún archivo de otra fase.

**progress.json.** JSON válido. `Fase_C`: `pending` → `completed`, `commit: null` → `"a218a65"`. `current_target`:
`Fase_C` → `Fase_D`. `last_handoff` presente. `edit_rules` y `allowed_statuses` sin cambios (`git diff a3c0e90 f3a2ff2
-- docs/deuda/BE-64/progress.json`: solo cambian esas cuatro claves).

**RED reproducido por el auditor.** Copia `git archive a3c0e90` + `tests/test_config.py` y `conftest.py` de `a218a65`,
sin `app/` ni `.env.example` de la fase, sin `.env` (`import app` → la copia): `4 failed, 806 passed, 25 warnings in
34.66s`; FAILED `test_optional_variables_keep_their_current_defaults`,
`test_verification_resend_interval_is_read_in_seconds`, `test_verification_resend_interval_rejects_a_non_integer`,
`test_env_example_is_a_valid_configuration`. Igual al plan y al handoff.

**Compuerta re-ejecutada por el auditor** (`./venv/Scripts/python.exe scripts/check.py`, sin `--soft`), dos veces: en el
árbol de trabajo y en una copia limpia `git archive f3a2ff2` (`Raíz del repo: …\audC-head · Python 3.14.3`). Código de
salida `0` en las dos, con las mismas cifras. Windows no bloqueó `_rustgrimp`: E0.3 no aplica.

Paso import-linter (literal, extracto):
```
Analyzed 56 files, 148 dependencies.
------------------------------------

Capas: api | cli -> services -> repositories -> models KEPT
Los servicios no conocen el transporte HTTP KEPT
Los repositorios solo conocen SQLAlchemy y los modelos KEPT
Los modelos y los schemas no dependen de capas superiores KEPT

Contracts: 4 kept, 0 broken.
--- import-linter: OK en 0.2s
```

RESUMEN (literal):
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

Otras líneas: `73 files already formatted` · `All checks passed!` · `Success: no issues found in 68 source files` ·
`Documentación coherente (...)` · `TOTAL 1073 10 156 6 98.70%` · `Required test coverage of 92.0% reached. Total
coverage: 98.70%` · `810 passed, 25 warnings in 32.63s` (copia limpia: `33.15s`).

**Ratchet frente a la línea base** (verificacion.md: 806 passed · 98,70 % · ruff 0 · mypy 0 en 67 · 4 kept): pytest 810,
0 failed (= criterio de la fase, `810 passed`); cobertura 98,70 %, igual; ruff 0 en 73; mypy 0 en 68; 4 kept, igual.
Avisos 25, los mismos de la base.

**Ruff y mypy por archivo.** `ruff check app/core/config.py conftest.py tests/test_config.py` → `All checks passed!`;
`ruff format --check <los tres>` → `3 files already formatted`; `mypy <los tres>` → `Success: no issues found in 3
source files`. `.env.example` no es Python; lo cubren `test_env_example_documents_every_setting` y
`test_env_example_is_a_valid_configuration`.

**Mutantes MC1–MC4, re-medidos por el auditor** (una copia `git archive f3a2ff2` por mutante, reemplazo con ancla única,
`import app` → la copia, suite completa): MC1 (`= 30` en `config.py`) → `1 failed, 809 passed`
(`test_optional_variables_keep_their_current_defaults`); MC2 (`=61` en `.env.example`) → `1 failed, 809 passed`
(`test_env_example_is_a_valid_configuration`); MC3 (sin la línea en `.env.example`) → `1 failed, 809 passed`
(`test_env_example_documents_every_setting`); MC4 (sin la entrada del `conftest.py` raíz) → `1 failed, 809 passed`
(`test_test_environment_fixes_every_setting`). 4 muertos, 0 vivos; los asesinos coinciden con el plan y el handoff.

**AGENTS.md.** §3 / ADR-0013: la variable es un campo de `Settings` con tipo y default (`app/core/config.py:53`), con su
línea en `.env.example:24` y su valor de prueba en `conftest.py:16`; `grep -rn "os.getenv\|load_dotenv" app alembic
tests conftest.py` → 0. Nadie la lee aún (lo hace la fase D). Comentario y nombres en inglés. §5: sin mocks; el entorno
se prepara con `_set_required` y `monkeypatch`; el test de fallo afirma `(type, loc)` de pydantic (`int_parsing`), sin
texto humano; ninguna aserción sobre texto en español. Sin excepciones de dominio, rutas, modelos ni migraciones en esta
fase. R5 (sin validación de rango) sigue fuera de alcance, como dice el plan.

**Criterio de aceptación de la fase C:** compuerta en 0 con `810 passed` ✔; cobertura 98,70 % ≥ 98,70 % ✔; MC1–MC4
muertos ✔. No es la última fase: la Verificación final corre tras la fase E. Siguiente: `/implementar BE-64 D` (el
momento 2 de David está en la bitácora y E2 ya está commiteada en `458fc01`).

## Auditoría Fase D — 2026-11-27
**Veredicto Fase D: PASS (0 bloqueantes, 0 opcionales).**
Sin hallazgos.

### Evidencia

**Árbol y commits.** `git status --short` al empezar → vacío. `git log --oneline -3`: `c641d47 docs(progress): record
BE-64 Fase_D completion`, `62c5c74 feat(auth): decide who may get a new verification link, and when`, `fa74b16
docs(item-be64): phase C audit PASS (0 blocking, 0 optional)`. `git cat-file -p 62c5c74` → `parent fa74b16…`.
`git show --stat 62c5c74` → los 4 archivos del plan (`app/repositories/user_repository.py` 28,
`app/services/user_service.py` 50, `tests/test_user_repository.py` 70, `tests/test_user_service.py` 89; `234
insertions(+), 3 deletions(-)`); `c641d47` toca solo `handoff-Fase_D.md` y `progress.json`.

**Igualdad con el Anexo D.** `git diff --raw fa74b16 62c5c74` → `b1b6e34 c31fa77`, `6e7d6ee 990c6e1`, `9ce3827
5a9220a`, `40f20eb 8587f9c`: preimágenes y postimágenes iguales a las líneas `index` del Anexo D (`plan.md:861-1157`);
`git ls-tree HEAD` da los mismos cuatro blobs (nada los cambió después). Mismo hash = mismo contenido byte a byte: cada
punto de "Cambios exactos" está en el diff (consulta tras `get_non_deleted_user_by_email`, solo `select`; `timedelta`
en el import; `VerificationResend` tras `RegistrationResult`; dos líneas en el docstring y
`verification_sent_at=datetime.now(UTC)` en el `User(...)` de `register_tourist`; `resend_verification_link` antes de
`authenticate_user`). Código y tests del Anexo sin cambios, como exige E2 punto 2.

**Mensaje de commit.** `plan.md:324-344` sin la sangría, contra `git log -1 --format=%B 62c5c74` sin la línea vacía
final, con `diff` → idénticos (incluido `Co-Authored-By`).

**progress.json.** JSON válido. `Fase_D`: `completed`, `commit` `62c5c74` (hash real); `current_target` `Fase_E`;
`last_handoff` presente; `edit_rules` y `allowed_statuses` sin cambios (`git show c641d47 -- …progress.json`: solo
cambian `current_target`, `status`/`commit` de D y `last_handoff`).

**Requisito previo.** Momento 2 de E1 en `docs/bitacora/2026-11-27.md` (`a3c0e90`): `:118` `Running upgrade
e50a7c3d9b12 -> a64d0c2e7f15`, `:124` `No new upgrade operations detected.`.

**Compuerta re-ejecutada por el auditor** (`./venv/Scripts/python.exe scripts/check.py`, árbol de trabajo en
`c641d47`, sin `--soft`; Windows no bloqueó `_rustgrimp`, E0 punto 3 no aplica). Exit 0. RESUMEN literal:
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
Otras líneas: `73 files already formatted` · `All checks passed!` · `Success: no issues found in 68 source files` ·
`Analyzed 56 files, 148 dependencies.` · `Contracts: 4 kept, 0 broken.` · `TOTAL 1087 10 158 6 98.71%` · `825 passed,
25 warnings in 35.40s`. Coinciden con lo que pegó el ejecutor.

**Ratchet frente a la línea base** (`verificacion.md`: 806 passed · 98,70 % · ruff 0 · mypy 0 en 67 · 4 kept): pytest
825, 0 failed (= criterio de la fase); cobertura 98,71 % ≥ 98,70 % (= lo medido por el plan); ruff 0 en 73; mypy 0 en
68; 4 kept, igual. Avisos 25, los de la base.

**Ruff y mypy por archivo.** `ruff check <los cuatro>` → `All checks passed!`; `ruff format --check <los cuatro>` →
`4 files already formatted`; `mypy <los cuatro>` → `Success: no issues found in 4 source files`.

**RED re-medido por el auditor** (copia `git archive fa74b16` con los dos archivos de test de `62c5c74`, sin `app/`,
`pytest -q -p no:cacheprovider`): `15 failed, 810 passed, 25 warnings`: los 10 de `test_user_repository.py` y los 5
de `test_user_service.py` que nombra el plan, ni uno más. Los 15 tests exigidos por "Tests (RED primero)" existen y
pasan en el GREEN.

**Criterios del plan, por grep.** `grep -c "commit()" app/repositories/user_repository.py` → `3` (A3: la consulta solo
lee); `grep -c "log_transaction" app/services/user_service.py` → `6` (el reenvío no audita, ADR-0023);
`grep -rn "create_verification_token(" app --include=*.py | wc -l` → `3`; escritores de `email_verified_at` → solo
`app/services/user_service.py:181`, dentro de `verify_email_account` (`:128`, ADR-0022); escritores de
`verification_sent_at` → `:109` (registro) y `:222` (reenvío). **E2 punto 4:**
`grep -rn "monkeypatch.setattr(get_settings()" tests` → `tests/test_user_service.py:477` y nada más (1).

**Mutantes, muestra re-medida por el auditor** (7 de 15; una copia `git archive 62c5c74` por mutante, reemplazo con
ancla única, `import app` → la copia, suite completa): MD1 (registro sin sello) → `1 failed, 824 passed`
(`test_register_tourist_counts_as_the_first_link_sent`); MD2 (sin filtro de rol) → `2 failed, 823 passed` (`[admin]`,
`[superadmin]`); MD6 (`<=` → `<`) → `1 failed, 824 passed` (`[sent-at-the-cutoff]`); MD8 (sin sello en el reenvío) →
`1 failed, 824 passed` (`test_resend_issues_a_link_to_the_account_due_one`); MD10 (`timedelta(seconds=60)` fijo) →
`1 failed, 824 passed` (`test_resend_interval_comes_from_the_settings`); MD12 (`log_transaction` con la firma real tras
`save_user`) → `1 failed, 824 passed` (`test_resend_issues_a_link…`, `Expected log_transaction to not have been
awaited`); MD15 (`save_user` en `try/except Exception: pass`) → `1 failed, 824 passed`
(`test_resend_save_failure_…`, `DID NOT RAISE OperationalError`). 7 muertos, 0 vivos; asesinos y conteos iguales a la
tabla del handoff.

**AGENTS.md y ADR.** §3: la consulta vive en el repositorio y no hace `commit()`; el servicio no importa FastAPI ni
Starlette (`grep "fastapi\|starlette"` → 0) y no tiene `role ==` (el filtro de turista es de la consulta, data
scoping); no hay excepciones de dominio nuevas; el intervalo se lee con `get_settings()` (consumidor sin petición,
ADR-0013); sin fila de auditoría por el sello (ADR-0021/ADR-0023, probado con `assert_not_awaited` y MD12).
Addendum de ADR-0013 (`458fc01`): `UserService` llama a `get_settings()` por dentro (`user_service.py:215`) y no recibe
`Settings` por `Depends` ni por argumento, así que (a), (b) y (c) no aplican; el test usa `monkeypatch`, no asignación
directa, y es el único caso. §4: identificadores, docstrings y comentarios en inglés; Google Style con Args/Returns en
los dos métodos y en `VerificationResend`; anotaciones completas. §5: `user_repo` y `audit_service` son
`create_autospec(…, instance=True)`; preparación con `persist_user` y `make_user`; aserciones sobre identidad, `None`,
claims del JWT, horas y llamadas con argumentos (`assert_awaited_once_with`); ninguna sobre texto en español
(líneas `+` de tests en el diff con `[áéíóúñ]|enviar|enlace|cuenta` → 0). Servicio: 1 feliz, 2 de fallo (sin cuenta,
fallo de BD), 2 de borde (intervalo de la configuración, sello del registro); repositorio: 4 felices, 5 de fallo, 1 de
borde (otro correo) más los dos cortes exactos. ADR-0011: los tests de repositorio usan `persist_user` (commit antes)
y la misma sesión, sin cliente HTTP, así que no hay instancia vieja que releer.

**Criterio de aceptación de la fase D:** compuerta en 0 con `825 passed` ✔; cobertura 98,71 % ≥ 98,70 % ✔; `commit()`
= 3 ✔; MD1–MD15 muertos (7 re-medidos aquí, los 15 en el handoff) ✔. No es la última fase: la Verificación final
corre tras la fase E. Siguiente: `/implementar BE-64 E`.

## Auditoría Fase E — 2026-11-27
**Veredicto Fase E: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Bloqueantes de auditorías anteriores: ninguno pendiente (A, B, C y D en PASS sin hallazgos). Fase E es
la última del plan: se corrió la Verificación final completa (comandos 1–16).

**Git.** `git status --short` → vacío (árbol limpio). `git log --oneline -15`: `05dc105 docs(progress): record BE-64
Fase_E completion` sobre `2b6db40 feat(auth): add the public route that resends the verification link`, padre
`a6d1b8a` (auditoría PASS de D). `git show --stat 2b6db40` → los 5 archivos del plan (`app/api/routers/user.py` 56,
`app/schemas/message.py` 16, `app/schemas/user.py` 9, `tests/test_route_guards.py` 2,
`tests/test_verification_resend.py` 260; `342 insertions(+), 1 deletion(-)`); `05dc105` toca solo
`handoff-Fase_E.md` y `progress.json`. Nada fuera de alcance (`app/main.py`, `docs/` fuera de la carpeta del ítem):
`git diff --name-only a6d1b8a 05dc105` → esos 7.

**Igualdad con el Anexo E.** `git diff --full-index a6d1b8a 2b6db40 | grep ^index` → `ed616f8..d630362`,
`0000000..4c114a9`, `d254dfd..3ba2f30`, `ecaf4b1..039299b`, `0000000..018a151`: las líneas `index` del Anexo E
(`plan.md:1163-1560`). Comprobación independiente: `git archive a6d1b8a` en una copia, `git apply` de
`plan.md:1163-1560` (`--check` limpio) y `git hash-object` de los cinco → `d630362`, `4c114a9`, `3ba2f30`, `039299b`,
`018a151`. Byte a byte. Cada punto de "Cambios exactos" está: `MessageResponse` en su módulo;
`VerificationResendRequest` tras `UserLogin`; import de `MessageResponse` y de `app.schemas.user` en varias líneas;
`RESEND_VERIFICATION_MESSAGE` tras `public_router`; `resend_verification_email` con `response_model=MessageResponse` y
`HTTP_200_OK` antes de `login`; dos entradas en `PUBLIC_ROUTES` y `_ANONYMOUS_ON_PUBLIC_ROUTE` (422).

**Mensaje de commit.** `plan.md:374-398` sin la sangría, contra `git log -1 --format=%B 2b6db40` sin la línea vacía
final, con `diff` → idénticos (incluido `Co-Authored-By`).

**progress.json.** JSON válido. `Fase_E`: `completed`, `commit` `2b6db40` (hash real, `git show --stat` lo confirma);
`current_target` `null` (última fase); `last_handoff` presente; `edit_rules` y `allowed_statuses` sin cambios
(`git show 05dc105 -- …progress.json`: solo cambian `current_target`, `status`/`commit` de E y `last_handoff`).

**Compuerta re-ejecutada por el auditor** (`./venv/Scripts/python.exe scripts/check.py`, árbol en `05dc105`, sin
`--soft`; Windows no bloqueó `_rustgrimp`, E0 punto 3 no aplica). Exit 0. RESUMEN literal:
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
Otras líneas: `75 files already formatted` · `All checks passed!` · `Success: no issues found in 70 source files` ·
`Analyzed 57 files, 150 dependencies.` · `Contracts: 4 kept, 0 broken.` · `TOTAL 1098 10 160 6 98.73%` · `845 passed,
29 warnings in 38.74s`. Coinciden con lo que pegó el ejecutor y con la fila "E GREEN" del plan.

**Ratchet frente a la línea base** (`verificacion.md:139`: 806 passed · 98,70 % · ruff 0 · mypy 0 en 67 · 4 kept):
pytest 845, 0 failed (= criterio de la fase); cobertura 98,73 % ≥ 98,70 % (= lo medido por el plan); ruff 0 en 75;
mypy 0 en 70; 4 kept, igual.

**Avisos 25 → 29, origen medido.** Con el aviso de `HTTP_422_UNPROCESSABLE_ENTITY` convertido en error (`-W error:…`)
sobre `tests/test_verification_resend.py tests/test_route_guards.py` caen exactamente 7: los 3
`test_invalid_body_is_422_and_sends_nothing[malformed|null|missing]` y 4 `test_public_route_answers_without_token[…]`
(`registro`, `verificar-email`, `login` y la nueva `reenviar-verificacion`). Los nuevos son 3 + 1 = 4, todos el
`StarletteDeprecationWarning` del handler de 422 (`app/main.py:94`, fuera de alcance): residual R4 (S5), como dice el
plan.

**Ruff y mypy por archivo.** `ruff check <los cinco>` → `All checks passed!`; `ruff format --check <los cinco>` →
`5 files already formatted`; `mypy <los cinco>` → `Success: no issues found in 5 source files`.

**RED re-medido por el auditor** (copia `git archive a6d1b8a` + `git apply --include='tests/*'` del Anexo E, sin
`app/`; `import app` → la copia; `pytest -q -p no:cacheprovider`): `21 failed, 824 passed, 25 warnings`, los 21
nombres del handoff (19 de `test_verification_resend.py`, `test_every_route_is_listed_as_protected_or_public` y
`test_public_route_answers_without_token[POST /usuarios/reenviar-verificacion]`). Causa de
`test_the_new_link_verifies_the_account`, medida aislada: `AttributeError: 'NoneType' object has no attribute
'kwargs'`. Valoración del matiz que anota el ejecutor: la fila "E RED" (`plan.md:27`) atribuye 17 de los 19 a un 405
en la aserción de estado; son 16, y ese caso cae un paso después porque no comprueba el estado del `POST` y lee
`call_args` de un correo que no salió. Es la descripción de la causa en la tabla de medición, no el criterio: la fase
exige `21 failed, 824 passed` (`plan.md:364-365`) y se cumple; el test cae por la razón correcta (sin ruta no hay
enlace) y en GREEN comprueba el `200` del enlace. Ni desajuste del código ni hallazgo. Los 19 tests exigidos por
"Tests (RED primero)" existen y pasan en el GREEN (`83 passed` en los dos archivos).

**Mutantes, muestra re-medida por el auditor** (6 de 9; una copia `git archive 2b6db40` por mutante, reemplazo con
ancla única, `import app` → la copia, suite completa): ME1 (otro `message` si `resend is None`) → `8 failed, 837
passed` (los 6 `…_same_answer_and_no_email[…]`, `test_unknown_…`,
`test_second_request_within_the_interval_sends_nothing`); ME3 (`email: EmailStr`) → `1 failed, 844 passed`
(`test_email_is_matched_in_lowercase`); ME4 (sin `rstrip`) → `1 failed, 844 passed`
(`test_link_is_built_from_frontend_url`); ME6 (sin `response_model`) → `1 failed, 844 passed`
(`test_route_declares_its_response_schema`); ME7 (`detail: str | None = None` en `MessageResponse`) → `2 failed, 843
passed` (`test_pending_tourist_gets_a_new_link`, `test_route_declares_its_response_schema`); ME9 (sin `response_model`
y `"email": body.email` en el `dict`) → `9 failed, 836 passed` (`test_pending_…`, los 6 `…_same_answer…`,
`test_unknown_…`, `test_route_declares_its_response_schema`). 6 muertos, 0 vivos; asesinos y conteos iguales a la
tabla del plan (`plan.md:167-175`) y a la del handoff.

**AGENTS.md y ADR.** §3: el router solo orquesta (llama a `resend_verification_link`, programa
`send_verification_email` como tarea de fondo si hay enlace, devuelve el cuerpo); declara
`response_model=MessageResponse` y nunca devuelve el ORM (`resend.user` solo alimenta los kwargs del correo).
`MessageResponse` hereda de `BaseModel`, sin validadores ni herencia de un DTO de entrada (A9).
`VerificationResendRequest.email` es `LowercaseEmail` (ADR-0016; ME3 lo prueba). Inventario ADR-0012 punto 4: la
ruta en `PUBLIC_ROUTES` (`tests/test_route_guards.py:82`) y en `_ANONYMOUS_ON_PUBLIC_ROUTE` con 422 (`:98`).
ADR-0023 decisión 1: 200 con el mismo cuerpo en cada caso que no envía (6 estados de cuenta, correo desconocido,
dentro del intervalo), comparado contra el cuerpo de un turista pendiente; 422 solo por cuerpo inválido; decisión 5:
sin fila de auditoría (`test_pending_tourist_gets_a_new_link` afirma `AuditLog` vacío). El servicio devuelve `None`
sin lanzar para toda cuenta no elegible (`user_service.py:220`): no hay excepción de dominio nueva que registrar. §4:
la ruta en español es la excepción declarada por E0 punto 1 y ADR-0023; manejador, identificadores, docstrings y
comentarios en inglés; el único texto en español es el `message` al usuario final (excepción c); Google Style con
Args/Returns; anotaciones completas (mypy 0). §5: el único doble es `mock_send_email` (`patch(…, autospec=True)`,
`tests/conftest.py:156`); preparación con `persist_user`; aserciones sobre código HTTP, claves del JSON, estado
releído y `assert_called_once_with` con argumentos, y claims del token decodificados con la clave de la app; ninguna
sobre texto en español (comando 10 → 0); el 422 sobre `detalle[*].raw_field`. 2 felices (pendiente, enlace que
verifica), fallos (6 no elegibles, correo desconocido, 3 cuerpos inválidos) y bordes (activado por admin, registro
como primer envío, segunda petición, intervalo vencido, minúsculas, `frontend_url`, esquema OpenAPI). ADR-0011:
`persist_user` confirma antes de cada petición y cada objeto ya cargado se relee con `db_session.refresh` después; el
override de `get_settings` lo limpia el `app.dependency_overrides.clear()` del fixture `client` (`conftest.py:98`).

**Verificación final (comandos 1–16), corrida por el auditor desde la raíz en Git Bash:**
```
1  create_verification_token(           → 3
2  send_verification_email,             → 2
3  resend|reenv en app                  → 26 (routers/user.py 14, user_service.py 7, config.py 1, models/user.py 1,
                                              user_repository.py 1, schemas/user.py 1, user_access_policy.py 1)
4  @public_router.                      → 4 ; reenviar-verificacion en test_route_guards.py → 2
5  solicite uno nuevo                   → 1
6  email_verified_at                    → 11 ; escritores → 1
7  verification_sent_at                 → 10 ; escritores → 2 ; en app/schemas → 0
8  slowapi|limiter|rate.limit|throttl   → 0
9  down_revision 'e50a7c3d9b12'         → 1
10 le acabamos de enviar un nuevo (app) → 1 ; acabamos de enviar|espere un minuto (tests) → 0
11 commit() en user_repository.py       → 3 ; log_transaction en user_service.py → 6
12 .env.example → 1 ; conftest.py → 1
13 BE-64 → 10 líneas en 10 archivos ; ADR-0023 → 13 (2 en routers/user.py y user_service.py, 1 en los otros nueve;
   schemas/message.py no la cita)
14 response_model=MessageResponse → 1 ; MessageResponse en app → 4 ; en tests → 3
15 git diff --name-only 22328ce HEAD -- app alembic tests conftest.py .env.example docs/adr → 19 archivos: los 18 del
   plan (plan.md:458-462) más docs/adr/0013-configuracion-centralizada-con-pydantic-settings.md (E2 punto 3)
16 compuerta → exit 0 ; 845 passed ; 98,73 % ; ruff 0 en 75 ; mypy 0 en 70 ; 4 kept (bloque de arriba)
```
Todos los valores son los del plan con E2. La deuda no asoma: la API ya tiene dónde pedir el enlace nuevo, el texto
del enlace caducado no cambia y no entra ninguna librería de limitación.

**Criterio de aceptación de la fase E:** compuerta en 0 con `845 passed` ✔; cobertura 98,73 % ≥ 98,70 % ✔; mypy en
70 ✔; `4 kept` ✔; Verificación final 1–16 ✔; ME1–ME9 muertos (6 re-medidos aquí, los 9 en el handoff) ✔; comando 10
→ 0 ✔. **Pendiente antes de `/pr`, fuera de esta auditoría:** el momento 3 de E1 punto 3 (David, API de la rama sobre
su PostgreSQL, nueve pasos, salida a la bitácora). Si algún paso da otra cosa, no hay `/pr`.
