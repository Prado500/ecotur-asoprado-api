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
