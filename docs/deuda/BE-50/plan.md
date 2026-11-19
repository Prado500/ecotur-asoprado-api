# PLAN — BE-50: Hacer que el enlace de verificación cambie una cuenta una sola vez

> Fuente: `docs/deuda/BE-50/verificacion.md` (confirmada; adenda de David del 19 nov, decisiones 1–13, que este plan
> toma como dadas). Base: HEAD `4f9e29e` de `item/be-50`; `git diff --stat c478e38 HEAD -- app tests alembic conftest.py
> pyproject.toml docs/adr AGENTS.md` sale vacío, así que vale la línea base de la verificación (797 passed · 98,69 % ·
> ruff 0 · mypy 0 en 66 · 4 kept). **Estado: aprobado por David con E0 (19 nov 2026, 12:17); ninguna fase ejecutada.** `Aprobado: 19 nov 2026` (esa es la
> `<FECHA DE APROBACIÓN>` de ADR-0022). Enmiendas al final.
> **Qué midió el redactor:** nada se ejecutó (instrucción de la sesión: solo lectura). Las cifras de tests (RED, GREEN,
> 806) y los conteos de la Verificación final están **calculados leyendo** el código y el texto que este plan dicta. Si
> una cifra no cuadra, el ejecutor se detiene y lo anota en el handoff; no "arregla" código para que cuadre.

## Resumen para aprobación

Tres fases. (A) ADR-0022: la decisión de David por escrito antes del código. (B) Una columna nueva,
`users.email_verified_at` (instante con zona, admite vacío), con su migración Alembic; nace vacía en todas las filas,
también en las activas, y nadie la escribe todavía. (C) La regla del enlace: con la marca vacía, el enlace la llena y
activa la cuenta si está inactiva (200, mensaje de hoy); con la marca llena no cambia nada, no deja fila de auditoría y
responde 200 "Su correo ya fue verificado."; los siete docstrings "single-use" pasan a decir lo que el código hace y los
tres tests que congelaban el defecto se reescriben. Cierra V4: después del enlace, `is_active` es solo del
administrador. **Riesgo principal:** es un cambio de esquema; la suite corre en SQLite, así que David corre `alembic
check` contra su PostgreSQL antes de B y después de B, antes de empezar C. **No se toca:** los DTO de entrada y salida,
la firma de la ruta, los claims del token, el token en la query string, el texto del login (BE-56), el reenvío (BE-64),
la activación manual por un admin (BE-63), el modelo de dos hechos (BE-62) ni el `commit()` de los repositorios (A3).

## Objetivo y decisiones bloqueadas

Que el enlace de verificación tenga un solo efecto por cuenta, decidido por un dato propio que solo el enlace escribe, y
que deje de reactivar una cuenta que un administrador desactivó después de la verificación.

1. **Columna `users.email_verified_at`**: `Mapped[datetime | None] = mapped_column(DateTime(timezone=True))`, sin
   `default` ni `server_default` (decisión 1; ADR-0010). Solo la escribe `UserService.verify_email_account`.
2. **Regla del enlace** con token válido (decisión 2): borrada → 404 sin cambios; marca vacía → se llena con
   `datetime.now(UTC)` y, si `is_active` es falso, pasa a verdadero; 200 "Cuenta verificada exitosamente. Ya puede
   iniciar sesión."; marca llena → nada cambia, sin `save_user`, sin fila; 200 `{"success": true, "message": "Su correo
   ya fue verificado."}`.
3. **El token no cambia:** sin `jti`, no se guarda, 15 min (decisión 2).
4. **P3 y el caso "activado y desactivado a mano sin verificar" son comportamiento deseado** (decisión 3).
5. **Auditoría:** ADR-0021 punto 5 intacto; la marca no se audita; fila solo si el enlace cambia `is_active`
   (decisión 7).
6. **Migración sin relleno:** la columna nace NULL en todas las filas (decisión 6).
7. **ADR-0022** es la fase A (decisión 9). La viñeta de AGENTS §3 la commitea David después de la última auditoría
   (decisión 13): el plan no toca `AGENTS.md`.
8. **Pasos de David en sintaxis `cmd`** (decisión 10).

## Análisis del redactor

**Qué se cambia y por qué.** El defecto es de datos: `is_active=False` significa "pendiente", "desactivada" o
"recuperada sin aprobar", y `verify_email_account` (`app/services/user_service.py:145-165`) decide solo con ese valor
(`:150`). La marca separa "el enlace ya se usó" de "la cuenta está activa". La regla nueva lee la marca antes que
`is_active`; `changed_fields(user, {"is_active": True})` se conserva (la fila de auditoría sigue siendo la de ADR-0021,
punto 5). Cambio de comportamiento que exige la decisión 7 y la verificación no menciona: con la marca vacía y la cuenta
ya activa (un admin la activó), hoy no se llama a `save_user`; desde C sí, para guardar la marca, y sigue sin fila.

**Orden y dependencias.** A primero porque B y C citan ADR-0022 en comentarios y docstrings, y porque es la fase más
pequeña. B antes que C: C lee y escribe la columna. Entre B y C, David corre los pasos de PostgreSQL (abajo); C no
empieza sin su salida en la bitácora.

**Qué tests congelan qué.**
- `tests/test_models_schema.py:67-80` congela las columnas de `users` con literales: B le añade la fila de la columna
  nueva (es su RED).
- `tests/test_email_case.py:81-94` (`pre_migration_db` de BE-51) hace `create_all` con los modelos actuales y luego el
  `downgrade` de `b51f3c9e2a64` en batch: tras B la tabla tiene una columna más y el batch la copia. No cambia.
- Congelan el defecto y se reescriben en C (decisión 8): `tests/test_auth.py:112` (cuenta activa + enlace → sin marca),
  `tests/test_auth.py:147` (su docstring dice "is BE-50"; su secuencia ya es el caso 4 de la decisión 3, que se
  mantiene) y `tests/test_user_service.py:286` (`save_user.assert_not_awaited()` deja de valer: ahora se guarda la marca).
- `tests/test_auth.py:92` y `tests/test_user_service.py:263` (camino feliz) ganan la aserción de la marca.
- Siguen sin cambios: 404 de borrada (`test_auth.py:128`), token inválido, caducado, de otro `scope` o de otra grafía
  (`test_auth.py:174`, `test_user_service.py:304-364`, `test_token_failure_paths.py:308-327`,
  `test_email_case.py:198-210`), la ruta en `PUBLIC_ROUTES` (`test_route_guards.py:81`, `:96`) y las claves de
  `UserResponse` (`tests/test_user_response.py:20-30`, que ya prueba que la marca no se expone).
- `make_user` reenvía `**overrides` a `User(...)` (`tests/conftest.py:177-203`): `email_verified_at=` funciona sin tocar
  `conftest.py`. El bootstrap (`app/services/superadmin_bootstrap.py:53-63`) y el alta administrativa
  (`user_service.py:435-445`) no pasan la columna: su marca queda vacía (decisión 6), sin tocarlos.

**Riesgos.**
1. *SQLite frente a PostgreSQL* (BE-31): SQLite guarda la fecha sin zona y la devuelve sin `tzinfo` (SQLAlchemy 2.0,
   `sqlite.DATETIME`), así que los tests de integración solo afirman `is not None` e igualdad entre lecturas; el tipo
   real lo prueban el test de esquema (compilado para PostgreSQL), el SQL fuera de línea de B y el `alembic check` de
   David.
2. *Carrera de dos clics simultáneos:* los dos leen la marca vacía y los dos escriben fila. Sin bloqueo de fila; no
   entra (A3, BE-31). Declarado en Residuales.
3. *Ventana del despliegue:* un enlace emitido en los 15 min previos encuentra la marca vacía y activa la cuenta aunque
   un admin la haya desactivado en ese plazo (decisión 6, aceptado).
4. *Admin desactiva justo después de la verificación:* el turista vio "éxito" y el login le dice "Debe verificar su
   cuenta" (decisión 4, aceptado; BE-56).

**Mutantes (decisión 8; E1 de BE-38):** el ejecutor de B y C, después de su commit con la compuerta en verde, aplica
cada mutante en una copia `git archive <commit de la fase>` en el scratchpad, una por mutante, y corre la suite completa
con `./venv/Scripts/python.exe` del repo por ruta. Nunca sobre el árbol de trabajo. Si uno que el plan da por muerto
vive, lo declara en el handoff y se detiene.

**Qué NO se toca:** `app/schemas/` (la marca no entra en ningún DTO; `UserUpdate` ignora la clave, test C12),
`app/services/user_access_policy.py`, `app/core/email.py`, `app/core/config.py`, `authenticate_user` (texto y
docstring, BE-56), `recover_user_account` salvo su docstring, `app/repositories/`, `tests/conftest.py`, el cliente
Flutter.

## Regla de alcance

**Sí:** ADR-0022; el modelo `User` y una migración; `verify_email_account`; los siete docstrings "single-use"; el
docstring de `recover_user_account` (decisión 3); los tests de esos tres puntos.
**No:** todo lo de la decisión 11 (DTO, contrato, firma de la ruta, claims, query string, login, reenvío, A3); BE-62,
BE-63, BE-64; `docs/backlog.md`, `docs/CONTEXT.md`, `AGENTS.md` y la ficha de estudio (los actualiza David al cerrar).
Un hallazgo nuevo va a Residuales del handoff, nunca al código.

## Fases

### Fase A — ADR-0022: la marca de correo verificado decide el enlace (la más pequeña)
- **Archivos (1):** `docs/adr/0022-la-marca-de-correo-verificado-decide-el-enlace.md` (nuevo).
- **Cambios exactos:** el texto del Anexo A, literal, sustituyendo `<FECHA DE APROBACIÓN>` por la fecha que David anote
  en la línea "Aprobado:" de este plan.
- **Tests (RED primero):** no aplica (documento; `docs/adr` está fuera de `check_docs`). Comprobación mecánica antes:
  `ls docs/adr/0022-*` → sin resultados; después → 1 archivo.
- **Criterio de aceptación:** el archivo existe; `grep -c "<FECHA" docs/adr/0022-*.md` → `0`; compuerta en verde
  (797 passed, sin cambios en código).
- **Fuera de alcance:** AGENTS §3, backlog, CONTEXT, la ficha.
- **Commit:**
  ```
  docs(adr): add ADR-0022, a verified-email mark decides the link

  The verification link reactivated an account an admin had deactivated
  and answered "verified" on every click for 15 minutes, because
  is_active=False meant pending, deactivated or recovered (BE-50,
  probes P1 to P3).

  ADR-0022 records David's decision before any code: a users column,
  email_verified_at, that only the link fills; with it empty the link
  fills it and activates, with it filled the link changes nothing. It
  declares the trade-off against the two-fact model (BE-62), keeps
  ADR-0021 point 5, and lists what stays out (BE-56, BE-63, BE-64).

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase B — Columna `users.email_verified_at` y su migración
- **Archivos (4):** `app/models/user.py`, `alembic/versions/e50a7c3d9b12_users_email_verified_at.py` (nuevo),
  `tests/test_models_schema.py`, `tests/test_migration_email_verified_at.py` (nuevo).
- **Cambios exactos:** Anexo B (modelo: 3 líneas tras `deleted_at`; migración escrita a mano con el id y la fecha del
  plan, estilo de `script.py.mako`, como `b51f3c9e2a64`; una fila en `EXPECTED["users"]`; el archivo de test completo).
- **Antes de empezar (David, `cmd`, ADR-0010 punto 7):** desde `C:\projects\ecotur-asoprado`,
  `venv\Scripts\python.exe -m alembic current` → `b51f3c9e2a64 (head)` y `venv\Scripts\python.exe -m alembic check` →
  `No new upgrade operations detected.`; salida literal en la bitácora.
- **Tests (RED primero):** primero los dos tests sin tocar `app/` ni `alembic/`:
  - `test_table_columns_match_the_frozen_schema[users]` con la fila nueva → falla (columna ausente).
  - `test_migration_adds_the_column_empty_in_every_row` y `test_migration_downgrade_drops_the_column_and_keeps_the_rows`
    → error de preparación (`FileNotFoundError` en `runpy`: la migración no existe).
  - Esperado: `1 failed, 796 passed, 2 errors`.
- **Criterio de aceptación:** compuerta completa en 0 con `799 passed`; cobertura ≥ 98,69 %. SQL fuera de línea (sin
  base, desde Git Bash): `DATABASE_URL=postgresql+asyncpg://u:p@localhost:5432/db ./venv/Scripts/python.exe -m alembic
  upgrade b51f3c9e2a64:e50a7c3d9b12 --sql` contiene `ALTER TABLE users ADD COLUMN email_verified_at TIMESTAMP WITH TIME
  ZONE` y ningún `UPDATE users`; el handoff copia la salida. Mutantes muertos (copias de B): MB1 la migración añade
  `op.execute("UPDATE users SET email_verified_at = CURRENT_TIMESTAMP WHERE is_active")` tras el batch → muere
  `..._empty_in_every_row`; MB2 `downgrade()` reducido a `pass` → mueren los dos de migración; MB3 modelo
  `Mapped[datetime]` y MB4 modelo `DateTime()` sin zona → muere `[users]` del test de esquema.
- **Después del commit (David, `cmd`, antes de la fase C):** `venv\Scripts\python.exe -m alembic upgrade head` →
  `Running upgrade b51f3c9e2a64 -> e50a7c3d9b12`; `venv\Scripts\python.exe -m alembic check` → `No new upgrade
  operations detected.`; `venv\Scripts\python.exe -m alembic downgrade -1` → `Running downgrade e50a7c3d9b12 ->
  b51f3c9e2a64`; `venv\Scripts\python.exe -m alembic upgrade head`. En su cliente SQL: `SELECT column_name, data_type,
  is_nullable FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'email_verified_at';` → una
  fila `email_verified_at | timestamp with time zone | YES`, y `SELECT count(*) FROM users WHERE email_verified_at IS
  NOT NULL;` → `0`. Salida literal en la bitácora. Si `check` lista operaciones, se detiene y va a la sesión Mentor.
- **Fuera de alcance:** cualquier lector o escritor de la columna (es C); `app/schemas/`; `conftest.py`.
- **Commit:**
  ```
  feat(users): add the email_verified_at column, empty in every row

  The verification link needs a fact of its own: is_active cannot tell
  an account waiting for its link from one an admin deactivated
  (BE-50, ADR-0022). This commit adds that fact and nothing reads it
  yet; the next one gives the link its rule.

  - app/models/user.py: email_verified_at, a timestamp with time zone
    that admits NULL, with no default.
  - alembic e50a7c3d9b12: adds the column in batch (a plain ALTER TABLE
    on PostgreSQL) and fills no row, the active ones included: an
    account active today may have been activated by an admin, so a
    verification nobody saw is not invented. Downgrade drops it.
  - tests: the frozen users schema gains the column; the migration runs
    on a SQLite of its own with an active, an inactive and a deleted
    account, and leaves the three empty.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase C — Regla del enlace, docstrings y tests
- **Archivos (5):** `app/services/user_service.py`, `app/core/security.py`, `app/api/routers/user.py`,
  `tests/test_user_service.py`, `tests/test_auth.py`.
- **Requisito previo:** la salida de los pasos de David tras B está en la bitácora y `check` dio `No new upgrade
  operations detected.`.
- **Cambios exactos:** Anexo C. En `user_service.py`: import de `UTC, datetime`; `verify_email_account` (guarda de la
  marca antes de `changed_fields`, marca y `is_active` antes de `save_user`, auditoría solo si `changes`, docstring);
  cinco "single-use" (`:32`, `:38`, `:70`, `:104`, `:117`); docstring de `recover_user_account` (excepción de la
  decisión 3). En `security.py` y `routers/user.py`, solo docstrings.
- **Tests (RED primero):** se escriben los del Anexo C sin tocar `app/`. Unitarios en `tests/test_user_service.py`:
  C1 `test_verify_email_activates_account` (+ marca en el intervalo), C2
  `test_verify_email_on_active_account_fills_the_mark_without_audit` (reescribe `:286`), C3
  `test_verify_email_with_the_mark_filled_changes_nothing` (nuevo), C4
  `test_verify_email_second_use_answers_another_message` (nuevo). Integración en `tests/test_auth.py`: C5
  `test_verify_email_endpoint_activates_account` (+ marca), C6
  `test_verify_email_on_account_an_admin_activated_fills_the_mark_without_audit_row` (reescribe `:112`), C7
  `test_verify_email_after_admin_deactivation_of_an_unverified_account_activates_it` (reescribe `:147`, caso 4), C8
  `test_link_used_again_after_admin_deactivation_keeps_the_account_inactive` (P2/V4), C9
  `test_second_click_on_the_link_changes_nothing_and_answers_another_message` (P1), C10
  `test_link_finishes_the_registration_of_a_recovered_account` (P3), C11
  `test_link_does_not_activate_a_recovered_account_that_was_verified`, C12
  `test_admin_patch_cannot_fill_the_verification_mark` (guarda de la decisión 1: pasa antes y después; se declara).
  Esperado en RED: `11 failed, 795 passed` (fallan C1–C11; C12 pasa).
- **Criterio de aceptación:** compuerta completa en 0 con `806 passed`; cobertura ≥ 98,69 %; skill `test-sanitizer`
  aplicada a los dos archivos de test. Mutantes muertos (copias de C): MC1 sin la guarda de la marca → C3, C4, C8, C9,
  C11; MC2 sin `user.email_verified_at = datetime.now(UTC)` → C1, C2, C5–C10; MC3 la guarda devuelve el mensaje de
  éxito → C4, C8, C9; MC4 la guarda lee `user.is_active` en vez de la marca → C2, C3, C6, C11; MC5 `save_user` dentro
  de `if changes:` → C2, C6; MC6 `log_transaction` fuera de `if changes:` → C2, C6.
- **Fuera de alcance:** texto y docstring del login (`:178`, `:185-186`, BE-56); el mensaje de `recover_user_account`
  (`:401`); `app/schemas/`; la política de acceso; reenvío; `tests/test_email*.py`, `tests/test_token_failure_paths.py`.
- **Commit:**
  ```
  fix(auth): let the verification link change an account only once

  For 15 minutes the same link answered "verified" on every click and
  reactivated an account an admin had deactivated (BE-50, probes P1 and
  P2), because the only state it read was is_active.

  The link now reads email_verified_at first (ADR-0022). Empty: it
  fills the mark and activates the account if it is inactive, so a
  registration finishes whatever happened in between, a recovery
  included. Filled: nothing changes, no audit row, and the answer is
  still 200 with another message. After the link, is_active belongs to
  the admin. The token is unchanged: no identifier, never stored.

  - app/services/user_service.py: the rule; the activation keeps the
    UPDATE row of ADR-0021 point 5 and the mark is not audited, so an
    account an admin already activated gets its mark and no row; the
    recovery docstring declares the exception.
  - app/core/security.py, app/api/routers/user.py: seven "single-use"
    docstrings in all now say what the code does.
  - tests: the three tests that froze the old behavior are rewritten,
    and P1, P2, P3, a verified recovered account and an admin PATCH
    carrying the mark get their own case.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

## Verificación final

Desde la raíz, en Git Bash, tras la fase C. Cada número cuenta también el texto que dictan los Anexos.

```bash
# 1. "single-use" en código y tests → 0 líneas (hoy 7)
grep -rn -i "single-use" app tests --include=*.py | wc -l

# 2. La guarda de la marca existe y va antes de changed_fields → 1 línea cada uno; la de la guarda con número menor
grep -n "if user.email_verified_at is not None:" app/services/user_service.py
grep -n 'changed_fields(user, {"is_active": True})' app/services/user_service.py

# 3. Mensajes del enlace → 1 y 1 en app; 0 en tests (no se afirma sobre texto en español)
grep -rn "Cuenta verificada exitosamente" app --include=*.py | wc -l
grep -rn "Su correo ya fue verificado." app --include=*.py | wc -l
grep -rn -E "verificada exitosamente|ya fue verificado" tests --include=*.py | wc -l

# 4. Dato nuevo (patrón 4 de la verificación, con --include) → 8: models/user.py 1, la migración 6, security.py 1
grep -rn -i -E "verified|email_verified|verification_sent|jti" app/models alembic/versions app/core/security.py --include=*.py | wc -l

# 5. Tests que congelaban el defecto, por su nombre viejo → 0
grep -n -E "def test_be38_verify_email_on_active_account|def test_be38_verify_email_after_admin_deactivation|def test_verify_email_on_active_account_writes_nothing" tests/test_auth.py tests/test_user_service.py | wc -l

# 6. Menciones de BE-50 en .py → 3: app/models/user.py, alembic/versions/e50a7c3d9b12_…, tests/test_migration_email_verified_at.py
grep -rn "BE-50" app tests alembic --include=*.py

# 7. Archivos de test que golpean el enlace → los mismos 3: test_auth.py, test_email.py, test_email_case.py
grep -rln "verificar-email?token=" tests --include=*.py

# 8. Escritores de is_active → 8 líneas, como hoy
grep -rn "is_active = \|is_active=" app --include=*.py | wc -l

# 9. Quién lee y escribe la marca → 5 líneas en app (user.py 1, user_service.py 3, security.py 1); 1 sola escritura;
#    0 en los schemas (no se expone)
grep -rn "email_verified_at" app --include=*.py | wc -l
grep -rn "email_verified_at = " app --include=*.py
grep -rn "email_verified_at" app/schemas --include=*.py | wc -l

# 10. Una sola cabeza de Alembic: solo la migración nueva desciende de b51f3c9e2a64 → 1
grep -rln "down_revision.*'b51f3c9e2a64'" alembic/versions --include=*.py | wc -l

# 11. ADR → 1 archivo, sin marcador de fecha (0)
ls docs/adr/0022-*.md
grep -c "<FECHA" docs/adr/0022-*.md

# 12. Alcance del diff → exactamente estos 10 archivos
git diff --name-only 4f9e29e HEAD -- app alembic tests docs/adr

# 13. Compuerta → exit 0; 806 passed; cobertura ≥ 98,69 %; ruff 0; mypy 0; 4 kept
./venv/Scripts/python.exe scripts/check.py
```

El 12 lista: `alembic/versions/e50a7c3d9b12_users_email_verified_at.py`, `app/api/routers/user.py`,
`app/core/security.py`, `app/models/user.py`, `app/services/user_service.py`,
`docs/adr/0022-la-marca-de-correo-verificado-decide-el-enlace.md`, `tests/test_auth.py`,
`tests/test_migration_email_verified_at.py`, `tests/test_models_schema.py`, `tests/test_user_service.py`.
Paso humano antes de `/pr`: los pasos de PostgreSQL de la fase B están en la bitácora con su salida literal.

## Residuales

| # | Hallazgo (evidencia) | Destino sugerido |
|---|---|---|
| R1 | El docstring de `authenticate_user` dice `AccountNotActiveError: Account pending email verification.` (`app/services/user_service.py:178`), falso para una cuenta desactivada o recuperada; mismo origen que el texto de `:186`. | Nota en la fila BE-56: corregir texto y docstring juntos. |
| R2 | Dos clics simultáneos leen la marca vacía y escriben dos filas `UPDATE` (no hay bloqueo de fila; razonado, no medido). | Nota en A3/BE-31; sin fila nueva. |
| R3 | Pantalla del cliente tras el botón: si muestra `message` de la respuesta, el texto nuevo llega solo; si muestra un texto fijo de "verificada", el segundo clic seguirá diciendo eso (decisión 12; el cliente no está en este repo). | David lo comprueba en Flutter antes de mezclar; si hace falta, fila `FE-nn`. |
| R4 | OWASP (Forgot Password Cheat Sheet, "URL Tokens") pide `Referrer-Policy: no-referrer` en la página que recibe un token en la URL; aplica a la pantalla del cliente que abre el enlace. | Opcional: fila `FE-nn`, Baja; o nota en la fila del token en query string. |
| R5 | Viñeta de AGENTS §3 (decisión 13). Propuesta: "**Verificación de correo (ADR-0022):** `users.email_verified_at` solo la escribe `verify_email_account`; ningún DTO la lleva. Con la marca llena el enlace no cambia nada; después del enlace, `is_active` es solo del administrador." | David, tras la última auditoría. |
| R6 | La sección "Después" de `docs/aprendizaje/fichas/BE-50.md`. | David / sesión Mentor, al cerrar. |

## Referencias

- SQLAlchemy 2.0.48 · `mapped_column` con `DateTime(timezone=True)`; en SQLite, `DATETIME` se guarda como texto sin zona
  · https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#sqlalchemy.dialects.sqlite.DATETIME
- Alembic 1.18.4 · `batch_alter_table`: en SQLite `add_column` no reconstruye la tabla y `drop_column` sí ("move and
  copy"); en los demás motores emite `ALTER` normales · https://alembic.sqlalchemy.org/en/latest/batch.html
- Alembic 1.18.4 · `alembic check` (ADR-0010 punto 7) · https://alembic.sqlalchemy.org/en/latest/autogenerate.html
- OWASP Cheat Sheet Series · Email Validation and Verification, "Email Ownership Verification" ·
  https://cheatsheetseries.owasp.org/cheatsheets/Email_Validation_and_Verification_Cheat_Sheet.html
- OWASP Cheat Sheet Series · Forgot Password, "Introduction", "URL Tokens", "General Security Practices" ·
  https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html
- Devise (wiki) · "How-To: Add :confirmable to Users" y "How-To: Customize user account status validation when logging
  in" · https://github.com/heartcombo/devise/wiki
- Las tres últimas, leídas el 19 nov en el texto fuente que sirve Context7 (`/owasp/cheatsheetseries`,
  `/heartcombo/devise`), no en la página publicada. OWASP ASVS 4 2.3.1 y la página de rubydoc de Confirmable **no se
  leyeron** y no se citan (regla del 14 nov).

---

## Anexo A — texto de ADR-0022

```markdown
# ADR-0022 — Una marca de correo verificado decide el enlace de verificación

- **Estado:** aceptado (David, <FECHA DE APROBACIÓN>, al aprobar el plan de BE-50)
- **Propuesta:** Claude, `plan-redactor` (19 nov 2026), sobre la adenda de David a la verificación (19 nov, 10:34 a
  11:24)
- **Ubicación en el repo:** `docs/adr/0022-la-marca-de-correo-verificado-decide-el-enlace.md`
- **Origen:** backlog BE-50; `docs/deuda/BE-50/verificacion.md` (veredicto, sondas P1 a P5b y adenda);
  `docs/deuda/BE-50/plan.md`; `docs/aprendizaje/fichas/BE-50.md` (las tres opciones comparadas). Relación: ADR-0021
  (su punto 5 no cambia), ADR-0010 (estilo de la columna), ADR-0002 (el dato vive en la base), ADR-0018 (un admin
  sigue pudiendo activar a un turista).

## Contexto

Una cuenta tenía dos datos de estado, `is_active` y `deleted_at`. `is_active = false` significaba tres cosas: pendiente
de verificar el correo, desactivada por un administrador y recuperada de la papelera a la espera de aprobación. El
enlace de verificación (un JWT con `sub`, `scope` y `exp`, 15 minutos, sin identificador y sin guardar) activaba
cualquiera de las tres. Medido el 19 nov: el segundo clic respondía otra vez 200 "verificada" (P1), el enlace
reactivaba una cuenta que un administrador había desactivado (P2) y activaba una recuperada sin aprobación (P3). Siete
docstrings llamaban "single-use" al token.

## Decisión

1. **Columna `users.email_verified_at`** (`TIMESTAMP WITH TIME ZONE`, admite vacío): vacía hasta que el enlace se usa
   con éxito y llena desde entonces. Solo la escribe `verify_email_account`; ningún acto de un administrador la llena
   ni la vacía, y ningún DTO de entrada o salida la lleva.
2. **Regla del enlace**, con el token válido: cuenta borrada → 404, sin cambios; marca vacía → se llena y, si la cuenta
   está inactiva, pasa a activa; 200 con "Cuenta verificada exitosamente. Ya puede iniciar sesión."; marca llena → no
   cambia nada, no deja fila de auditoría y responde 200 con "Su correo ya fue verificado.", que no promete el acceso
   porque la cuenta puede estar desactivada.
3. **El enlace es de un solo efecto por el estado de la cuenta, no por consumir el token.** El token sigue sin `jti`,
   no se guarda y caduca a los 15 minutos.
4. **El enlace completa el alta de quien nunca lo usó, pase lo que pase entre medias:** también una cuenta borrada y
   recuperada (excepción declarada a "una cuenta recuperada espera la aprobación de un administrador") y una que un
   administrador activó y desactivó a mano. Para frenar un registro pendiente, el administrador borra la cuenta y no la
   recupera.
5. **Después del enlace, `is_active` es solo del administrador.**
6. **Auditoría:** el punto 5 de ADR-0021 no cambia. La fila es un `UPDATE` de `is_active` con la cuenta como autora y
   existe solo cuando el enlace cambia `is_active`; la marca no se audita, y cuándo se verificó lo dice ella misma.
7. **La migración `e50a7c3d9b12` no inventa verificaciones:** la columna nace vacía en todas las filas, también en las
   activas, porque una cuenta activa pudo activarla un administrador. Las cuentas administrativas y el superadmin del
   bootstrap no reciben enlace: su marca queda vacía.

## Consecuencias

- El segundo clic deja de decir "verificada" y deja de escribir; un administrador que desactiva a un turista ya
  verificado no ve su decisión deshecha por el enlace.
- **Es una simplificación frente al modelo de dos hechos.** El enlace sigue escribiendo a la vez "correo verificado"
  (la marca) y "cuenta activa" (`is_active`), y el login solo mira `is_active`. El modelo de la industria los separa:
  el enlace solo anota la marca y entrar exige las dos cosas. Se eligió esta opción para no cambiar el registro ni lo
  que el cliente muestra como "por activar" dentro del MVP; el modelo separado es la fila BE-62.
- **Riesgo aceptado:** si un administrador desactiva la cuenta justo después de la verificación, el turista vio la
  pantalla de éxito y no puede entrar, y el login le pide verificar el correo (BE-56).
- Un administrador puede activar a quien nunca verificó; esa cuenta queda activa con la marca vacía (BE-63).
- Sin reenvío del enlace (BE-64), un turista cuyo enlace caducó depende de un administrador. Con la marca, varios
  enlaces vigentes a la vez no son un riesgo: el primero que se usa la llena y los demás no cambian nada.
- Los enlaces emitidos en los 15 minutos previos al despliegue encuentran la marca vacía y activan su cuenta aunque un
  administrador la haya desactivado en ese plazo.
- Dos clics simultáneos pueden escribir dos filas: no hay bloqueo de fila (A3).

## Alternativas consideradas

1. **Dos hechos separados** (el enlace solo anota la marca; el turista nace habilitado; entrar exige marca y
   `is_active`). Es el modelo de Devise. Rechazada para el MVP por coste: cambia el registro, el kanban del cliente y
   supersede el punto 5 de ADR-0021. Queda como BE-62.
2. **Un acto del administrador mata el enlace** (una marca de "registro pendiente" que apagan el clic y cualquier
   acción administrativa). Rechazada: la cuenta podría quedar activa sin que nadie haya probado que el correo existe, y
   cada escritor de `is_active` tendría que acordarse de apagarla.
3. **Token de un solo uso con `jti` guardado.** Rechazada: protege el token y no la cuenta, exige una tabla y su
   limpieza, y con reenvío (BE-64) un segundo token vigente volvería a reactivar.
4. **Rechazar el segundo clic con un error.** Rechazada por David: mostraría un error a quien pulsa dos veces sobre una
   cuenta ya verificada, sin forma de pedir otro enlace.
5. **Rellenar la marca de las cuentas activas en la migración.** Rechazada (decisión 7). La wiki de Devise lo
   recomienda al añadir `confirmed_at` porque allí la marca habilita el login; aquí no habilita nada, así que dejarla
   vacía no deja a nadie fuera.

## Evidencia

- Verificación (19 nov): sondas P1, P2 (V4 de BE-38), P3, P4 y P5b; siete docstrings "single-use".
- Plan: tests de cada caso y mutantes en copias del repositorio (`docs/deuda/BE-50/plan.md`).
- OWASP, Email Validation and Verification Cheat Sheet, "Email Ownership Verification": tokens de un solo uso y con
  plazo, y "Do not activate accounts before verification is completed". Esta decisión cumple el plazo y da un solo
  efecto, no invalida el token, y la activación manual por un administrador (BE-63) es la desviación declarada.
- OWASP, Forgot Password Cheat Sheet, "Introduction": "Single use and expire after an appropriate period" (trata de la
  recuperación de contraseña; aplica por analogía).
- Devise, wiki "How-To: Add :confirmable to Users" (`confirmed_at` en columna propia; la migración marca confirmadas
  las cuentas existentes) y "How-To: Customize user account status validation when logging in"
  (`active_for_authentication?` combina con `super &&` la condición base y la propia).
- Fuentes leídas el 19 nov en el texto fuente que sirve Context7, no en la página publicada.
```

## Anexo B — fase B

**`app/models/user.py`**, tras la línea de `deleted_at` (`:55`), tres líneas:

```python
    # Filled once, only by the email-verification link; no admin action writes or clears it
    # (BE-50, ADR-0022). Empty means the link was never used, not that the account is inactive.
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
```

**`alembic/versions/e50a7c3d9b12_users_email_verified_at.py`** (nuevo; `alembic/versions` está fuera de ruff y mypy):

```python
"""users: email_verified_at, filled only by the email-verification link (BE-50)

Revision ID: e50a7c3d9b12
Revises: b51f3c9e2a64
Create Date: 2026-11-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e50a7c3d9b12'
down_revision: Union[str, Sequence[str], None] = 'b51f3c9e2a64'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adds users.email_verified_at, NULL in every row, the active ones too (ADR-0022).

    No row is filled: an account active today may have been activated by an admin, and a
    verification nobody saw is not invented. batch_alter_table emits a plain ALTER TABLE on
    PostgreSQL; on SQLite, where the suite runs this function, adding a column needs no rebuild.
    """
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(
            sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True)
        )


def downgrade() -> None:
    """Drops users.email_verified_at; SQLite rebuilds the table and keeps its rows."""
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('email_verified_at')
```

**`tests/test_models_schema.py`**, en `EXPECTED["users"]`, tras `"deleted_at"` (`:79`):

```python
        "email_verified_at": FrozenColumn(TZ, nullable=True),
```

**`tests/test_migration_email_verified_at.py`** (nuevo):

```python
"""Tests for the BE-50 migration: users.email_verified_at is born empty in every row (ADR-0022).

The migration runs on a SQLite database of its own, as the one of ADR-0016 does in
test_email_case.py: the accounts are written with the full schema, the downgrade removes the
column and the upgrade adds it back, so the test reads what the upgrade leaves in existing rows.
"""

import runpy
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import Connection, create_engine, inspect, text
from sqlalchemy.orm import Session

from app.db.database import Base

COLUMN = "email_verified_at"
MIGRATION = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "e50a7c3d9b12_users_email_verified_at.py"
)


def _migrate(connection: Connection, step: str) -> None:
    """Runs upgrade() or downgrade() of the migration under test, with its own op."""
    migration = runpy.run_path(str(MIGRATION))
    with Operations.context(MigrationContext.configure(connection)):
        migration[step]()


def _columns(connection: Connection) -> dict[str, bool]:
    """Maps each column of users to whether it admits NULL."""
    columns = inspect(connection).get_columns("users")
    return {column["name"]: column["nullable"] for column in columns}


@pytest.fixture
def pre_migration_db(make_user) -> Iterator[Connection]:
    """A SQLite database of its own with three accounts, on the schema before the migration.

    One account is active, one inactive and one soft-deleted: the upgrade must not read a
    verification into any of them.
    """
    engine = create_engine("sqlite://")
    with engine.connect() as connection:
        Base.metadata.create_all(connection)
        connection.commit()
        with Session(connection) as session:
            session.add_all(
                [
                    make_user(is_active=True),
                    make_user(is_active=False),
                    make_user(is_active=False, deleted_at=datetime.now(UTC)),
                ]
            )
            session.commit()
        _migrate(connection, "downgrade")
        connection.commit()
        yield connection
    engine.dispose()


def test_migration_adds_the_column_empty_in_every_row(pre_migration_db: Connection) -> None:
    """Happy path: the column comes back nullable and NULL in every row, the active one too."""
    assert COLUMN not in _columns(pre_migration_db)

    _migrate(pre_migration_db, "upgrade")

    assert _columns(pre_migration_db)[COLUMN] is True
    rows = pre_migration_db.execute(text("SELECT is_active, email_verified_at FROM users")).all()
    assert sorted(is_active for is_active, _ in rows) == [False, False, True]
    assert [verified_at for _, verified_at in rows] == [None, None, None]


def test_migration_downgrade_drops_the_column_and_keeps_the_rows(
    pre_migration_db: Connection,
) -> None:
    """Edge case: a filled mark goes away with its column; the three accounts stay."""
    _migrate(pre_migration_db, "upgrade")
    pre_migration_db.execute(text("UPDATE users SET email_verified_at = CURRENT_TIMESTAMP"))

    _migrate(pre_migration_db, "downgrade")

    assert COLUMN not in _columns(pre_migration_db)
    assert pre_migration_db.execute(text("SELECT count(*) FROM users")).scalar_one() == 3
```

## Anexo C — fase C

### `app/services/user_service.py`

- Línea 1, nueva: `from datetime import UTC, datetime` (antes de `from typing import NamedTuple`).
- `:32` → `    Bundles the persisted account with its email-verification token so`
- `:38` → `        verification_token (str): The signed email-verification JWT.`
- `:69-70` → `            RegistrationResult: The persisted inactive account plus its` /
  `                email-verification token.`
- `:104` → `        # 3. Generate the verification token (the transport decides when it is emailed)`
- `verify_email_account`: docstring (`:110-126`) y cuerpo desde `if user is None:` (`:147-165`) quedan así; el decode
  (`:127-143`) y la búsqueda (`:145`) no cambian:

```python
    async def verify_email_account(self, token: str) -> dict:
        """Decodes the verification token and verifies the account's email, once.

        The link has one effect per account, not per token: the token is never stored and
        the email_verified_at mark decides. With the mark empty, the link fills it and
        activates the account if it is inactive, whatever happened in between: an account
        that never used its link finishes its registration, also after a recovery. With
        the mark filled, the link changes nothing, so it never undoes a deactivation by an
        admin (ADR-0022).
        The activation is audited as the same UPDATE of is_active an admin would write,
        with the account as its own author. The mark is not audited, so filling it on an
        account already active writes no row; a soft-deleted account is never reached
        (ADR-0021).

        Args:
            token (str): Email-verification JWT issued during registration.

        Returns:
            dict: Confirmation payload with a success flag and the message to show,
                which is another one once the email was already verified.

        Raises:
            InvalidVerificationTokenError: Token corrupted, expired or
                carrying an unexpected scope.
            NotFoundError: No non-deleted account matches the token subject.
        """
        # (decode, scope check and lookup unchanged)

        if user is None:
            raise NotFoundError("Usuario no encontrado.")

        if user.email_verified_at is not None:
            return {"success": True, "message": "Su correo ya fue verificado."}

        changes = changed_fields(user, {"is_active": True})
        user.email_verified_at = datetime.now(UTC)
        user.is_active = True
        await self.user_repo.save_user(user)
        if changes:
            await self.audit_service.log_transaction(
                entity_name="User",
                entity_id=user.cedula,
                action=AuditAction.UPDATE,
                performed_by=user.cedula,
                changes=changes,
            )

        return {
            "success": True,
            "message": "Cuenta verificada exitosamente. Ya puede iniciar sesión.",
        }
```

  La línea `# (decode, scope check and lookup unchanged)` es una indicación del plan, no se escribe.
- `recover_user_account`, tras `is_active true (ADR-0018).` (`:361`), dos líneas:

```python
        One exception: an account that never used its email-verification link
        finishes its registration with it while the link is valid (ADR-0022).
```

### `app/core/security.py` — docstring de `create_verification_token` (`:92-96`)

```python
    """Generates the JWT of the email-verification link.

    There is a specific scope within the token's payload to prevent its usage as a
    general authorization token. Its lifespan is the settings'
    verification_token_expire_minutes. It carries no identifier and is never stored,
    so nothing consumes it: the link changes an account once because
    verify_email_account fills the account's email_verified_at mark (ADR-0022).
```

(`Args` y `Returns` no cambian.)

### `app/api/routers/user.py` — docstring de `verificar_cuenta` (`:85-92`)

```python
    """Public endpoint: verifies the account's email with the emailed token.

    The first use fills the account's verification mark and activates the account if it
    is inactive; a later use changes nothing and answers with another message (ADR-0022).

    Args:
        token (str): Email-verification JWT issued during registration.
        user_service (UserService): Injected business-logic service.

    Returns:
        dict: Success flag and the message to show.
    """
```

### `tests/test_user_service.py`

- `:3` → `from datetime import UTC, datetime, timedelta`.
- Tras el encabezado `# EMAIL VERIFICATION` (`:256-258`): `VERIFIED_AT = datetime(2026, 11, 19, 12, 0, tzinfo=UTC)`.
- C1, `test_verify_email_activates_account` (`:263`): docstring → `"""Happy path: a first use fills the mark,
  activates the account and audits only is_active."""`; antes de la llamada, `before = datetime.now(UTC)`; tras
  `assert user.is_active is True`:

```python
    verified_at = user.email_verified_at
    assert verified_at is not None
    assert before <= verified_at <= datetime.now(UTC)
```

  (el resto del test no cambia).
- C2, sustituye a `test_verify_email_on_active_account_writes_nothing` (`:286-301`):

```python
async def test_verify_email_on_active_account_fills_the_mark_without_audit(
    user_repo, audit_service, user_service, make_user
):
    """Edge case: an account an admin activated gets its mark and no audit row (ADR-0022)."""
    user = make_user(email="turista@example.com", is_active=True)
    user_repo.get_non_deleted_user_by_email.return_value = user

    result = await user_service.verify_email_account(
        create_verification_token("turista@example.com")
    )

    assert result["success"] is True
    assert user.is_active is True
    assert user.email_verified_at is not None
    user_repo.get_non_deleted_user_by_email.assert_awaited_once_with("turista@example.com")
    user_repo.save_user.assert_awaited_once_with(user)
    audit_service.log_transaction.assert_not_awaited()


async def test_verify_email_with_the_mark_filled_changes_nothing(
    user_repo, audit_service, user_service, make_user
):
    """Unhappy path: a used link does not undo a deactivation by an admin (ADR-0022)."""
    user = make_user(email="turista@example.com", is_active=False, email_verified_at=VERIFIED_AT)
    user_repo.get_non_deleted_user_by_email.return_value = user

    result = await user_service.verify_email_account(
        create_verification_token("turista@example.com")
    )

    assert result["success"] is True
    assert user.is_active is False
    assert user.email_verified_at == VERIFIED_AT
    user_repo.save_user.assert_not_awaited()
    audit_service.log_transaction.assert_not_awaited()


async def test_verify_email_second_use_answers_another_message(
    user_repo, audit_service, user_service, make_user
):
    """Edge case: a second use succeeds, writes nothing more and does not repeat the message."""
    user = make_user(email="turista@example.com", is_active=False)
    user_repo.get_non_deleted_user_by_email.return_value = user
    token = create_verification_token("turista@example.com")

    first = await user_service.verify_email_account(token)
    second = await user_service.verify_email_account(token)

    assert first["success"] is True
    assert second["success"] is True
    assert set(first) == set(second) == {"success", "message"}
    assert second["message"] != first["message"]
    user_repo.save_user.assert_awaited_once_with(user)
    audit_service.log_transaction.assert_awaited_once()
```

### `tests/test_auth.py`

- C5, `test_verify_email_endpoint_activates_account` (`:92`): tras `assert user.is_active is True` (`:105`), la línea
  `    assert user.email_verified_at is not None`.
- C6, sustituye a `test_be38_verify_email_on_active_account_returns_200_without_audit_row` (`:112-125`); C7 sustituye a
  `test_be38_verify_email_after_admin_deactivation_writes_an_audit_row` (`:147-171`), en su mismo sitio; C8–C12 van
  tras C7, antes de `test_verify_email_invalid_token_returns_400`:

```python
async def test_verify_email_on_account_an_admin_activated_fills_the_mark_without_audit_row(
    client, db_session, persist_user
):
    """Edge case: on an account already active the link fills the mark and writes no row."""
    user = await persist_user(is_active=True)
    token = create_verification_token(user.email)

    response = await client.get(f"/usuarios/verificar-email?token={token}")

    assert response.status_code == 200
    assert response.json()["success"] is True
    await db_session.refresh(user)
    assert user.is_active is True
    assert user.email_verified_at is not None
    assert (await db_session.execute(select(AuditLog))).scalars().all() == []


async def test_verify_email_after_admin_deactivation_of_an_unverified_account_activates_it(
    client, db_session, persist_user, make_auth_headers
):
    """Edge case: an account that never used its link finishes its registration with it.

    An admin activated it by hand and deactivated it; its mark is still empty, so the link
    activates it, and the activation is the account's own row (ADR-0022).
    """
    admin = await persist_user(role=UserRole.admin)
    tourist = await persist_user(is_active=False)
    token = create_verification_token(tourist.email)
    headers = make_auth_headers(admin)

    activated = await client.patch(
        f"/usuarios/{tourist.cedula}", json={"is_active": True}, headers=headers
    )
    deactivated = await client.patch(
        f"/usuarios/{tourist.cedula}", json={"is_active": False}, headers=headers
    )
    verified = await client.get(f"/usuarios/verificar-email?token={token}")

    assert activated.status_code == deactivated.status_code == verified.status_code == 200
    await db_session.refresh(tourist)
    assert tourist.is_active is True
    assert tourist.email_verified_at is not None
    audits = (await db_session.execute(select(AuditLog).order_by(AuditLog.id))).scalars().all()
    assert [(a.entity_id, a.performed_by, a.changes) for a in audits] == [
        (tourist.cedula, admin.cedula, {"is_active": {"old": False, "new": True}}),
        (tourist.cedula, admin.cedula, {"is_active": {"old": True, "new": False}}),
        (tourist.cedula, tourist.cedula, {"is_active": {"old": False, "new": True}}),
    ]


async def test_link_used_again_after_admin_deactivation_keeps_the_account_inactive(
    client, db_session, persist_user, make_auth_headers
):
    """Unhappy path: once the link verified the email, only an admin moves is_active."""
    admin = await persist_user(role=UserRole.admin)
    tourist = await persist_user(is_active=False)
    url = f"/usuarios/verificar-email?token={create_verification_token(tourist.email)}"

    first = await client.get(url)
    deactivated = await client.patch(
        f"/usuarios/{tourist.cedula}", json={"is_active": False}, headers=make_auth_headers(admin)
    )
    second = await client.get(url)

    assert first.status_code == deactivated.status_code == second.status_code == 200
    assert second.json()["success"] is True
    assert second.json()["message"] != first.json()["message"]
    await db_session.refresh(tourist)
    assert tourist.is_active is False
    assert tourist.email_verified_at is not None
    audits = (await db_session.execute(select(AuditLog).order_by(AuditLog.id))).scalars().all()
    assert [(a.entity_id, a.performed_by, a.changes) for a in audits] == [
        (tourist.cedula, tourist.cedula, {"is_active": {"old": False, "new": True}}),
        (tourist.cedula, admin.cedula, {"is_active": {"old": True, "new": False}}),
    ]


async def test_second_click_on_the_link_changes_nothing_and_answers_another_message(
    client, db_session, persist_user
):
    """Edge case: the second click succeeds without writing, and its message is another one."""
    user = await persist_user(is_active=False)
    url = f"/usuarios/verificar-email?token={create_verification_token(user.email)}"

    first = await client.get(url)
    await db_session.refresh(user)
    verified_at = user.email_verified_at
    second = await client.get(url)

    assert first.status_code == second.status_code == 200
    assert set(first.json()) == set(second.json()) == {"success", "message"}
    assert second.json()["success"] is True
    assert second.json()["message"] != first.json()["message"]
    await db_session.refresh(user)
    assert user.is_active is True
    assert verified_at is not None
    assert user.email_verified_at == verified_at
    assert len((await db_session.execute(select(AuditLog))).scalars().all()) == 1


async def test_link_finishes_the_registration_of_a_recovered_account(
    client, db_session, persist_user, make_auth_headers
):
    """Edge case: an account that never used its link, deleted and recovered, ends its sign-up.

    The declared exception to "a recovered account waits for an admin" (ADR-0022).
    """
    admin = await persist_user(role=UserRole.admin)
    tourist = await persist_user(is_active=False, deleted_at=datetime.now(UTC))
    token = create_verification_token(tourist.email)

    recovered = await client.patch(
        f"/usuarios/{tourist.cedula}/recuperar", headers=make_auth_headers(admin)
    )
    verified = await client.get(f"/usuarios/verificar-email?token={token}")

    assert recovered.status_code == verified.status_code == 200
    assert verified.json()["success"] is True
    await db_session.refresh(tourist)
    assert tourist.deleted_at is None
    assert tourist.is_active is True
    assert tourist.email_verified_at is not None
    audits = (await db_session.execute(select(AuditLog).order_by(AuditLog.id))).scalars().all()
    assert [(a.action, a.performed_by) for a in audits] == [
        (AuditAction.RECOVER, admin.cedula),
        (AuditAction.UPDATE, tourist.cedula),
    ]


async def test_link_does_not_activate_a_recovered_account_that_was_verified(
    client, db_session, persist_user, make_auth_headers
):
    """Unhappy path: a verified account, deleted and recovered, still waits for an admin."""
    admin = await persist_user(role=UserRole.admin)
    tourist = await persist_user(
        is_active=False, deleted_at=datetime.now(UTC), email_verified_at=datetime.now(UTC)
    )
    token = create_verification_token(tourist.email)

    recovered = await client.patch(
        f"/usuarios/{tourist.cedula}/recuperar", headers=make_auth_headers(admin)
    )
    verified = await client.get(f"/usuarios/verificar-email?token={token}")

    assert recovered.status_code == verified.status_code == 200
    assert verified.json()["success"] is True
    await db_session.refresh(tourist)
    assert tourist.deleted_at is None
    assert tourist.is_active is False
    audits = (await db_session.execute(select(AuditLog))).scalars().all()
    assert [a.action for a in audits] == [AuditAction.RECOVER]


async def test_admin_patch_cannot_fill_the_verification_mark(
    client, db_session, persist_user, make_auth_headers
):
    """Edge case: no admin action writes the mark, and no response shows it (ADR-0022)."""
    admin = await persist_user(role=UserRole.admin)
    tourist = await persist_user(is_active=False)

    response = await client.patch(
        f"/usuarios/{tourist.cedula}",
        json={"is_active": True, "email_verified_at": "2026-11-19T12:00:00Z"},
        headers=make_auth_headers(admin),
    )

    assert response.status_code == 200
    assert "email_verified_at" not in response.json()
    await db_session.refresh(tourist)
    assert tourist.is_active is True
    assert tourist.email_verified_at is None
```

El diseño de las líneas lo decide el `ruff format` del hook; el auditor compara contenido, no saltos de línea. Ningún
nombre, docstring ni comentario de los Anexos B y C contiene "single-use", "BE-50" (salvo los tres de la Verificación
final, 6) ni texto en español afirmado.

## Enmiendas aprobadas

### E0 — 19 nov 2026, 12:17 (David: "si, apruebo todo."; revisión y medición de la sesión Mentor)

1. **Plan aprobado, tres fases, y ADR-0022 aceptado** con el texto del Anexo A. `<FECHA DE APROBACIÓN>` =
   `19 nov 2026`.
2. **Tres cifras del plan se corrigen con lo medido.** El plan las calculó leyendo; la sesión Mentor las midió (punto
   3). Donde el plan y esta enmienda difieran, rige la enmienda:
   - **Verificación final, comando 4:** el resultado es **7**, no 8: `app/models/user.py` 1, la migración **5** (no 6)
     y `app/core/security.py` 1.
   - **Mutante MC2** (sin `user.email_verified_at = datetime.now(UTC)`): lo matan **nueve** tests, C1, C2, C4 y C5 a
     C10. El plan omite C4 (`test_verify_email_second_use_answers_another_message`). Resultado medido: `9 failed, 797
     passed`.
   - **Mutante MC4** (la guarda lee `user.is_active` en vez de la marca): lo matan **cinco** tests, C2, C3, C6, C8 y
     C11. El plan omite C8 (`test_link_used_again_after_admin_deactivation_keeps_the_account_inactive`). Resultado
     medido: `5 failed, 801 passed`.
   Ninguna es un defecto del código dictado: en los dos mutantes muere un test más de los previstos. Las demás cifras
   del plan coinciden con lo medido y no cambian.
3. **Qué midió la sesión Mentor** (copia `git archive 4f9e29e` fuera del repo, en la VM del dispositivo; CPython
   3.14.10 en Linux; dependencias instaladas con `-c constraints.txt`; Anexos B y C aplicados como están dictados):
   línea base `797 passed`; RED de B `1 failed, 796 passed, 2 errors`; GREEN de B con `scripts/check.py` completo, `799
   passed`, 98,69 %, compuerta superada; SQL fuera de línea de B, `ALTER TABLE users ADD COLUMN email_verified_at
   TIMESTAMP WITH TIME ZONE;` y ningún `UPDATE users`; MB1 a MB4 mueren; RED de C `11 failed, 795 passed` (C1 a C11);
   GREEN de C con `scripts/check.py` completo, `806 passed`, 98,70 %, ruff 0, mypy 0, 4 kept; MC1 a MC6 mueren, con
   las listas del punto 2 para MC2 y MC4 y las del plan para los otros cuatro; comandos 1 a 3 y 5 a 10 de la
   Verificación final con el valor del plan; comando 12, los nueve archivos de código y tests (el ADR no se escribió
   en la copia). **No medido:** nada en PostgreSQL (los pasos de David de la fase B); Windows con 3.14.3; la skill
   `test-sanitizer`; el hook de formato (en la copia se corrió `ruff format` sobre `tests/` a mano); los comandos 11 y
   13 sobre el repo real.
4. **Fuentes del ADR-0022.** La cita de OWASP del Anexo A ("Do not activate accounts before verification is
   completed"; tokens de un solo uso y con plazo) existe en la página referenciada, comprobado por la sesión Mentor con
   una consulta resumida a la página, no leyéndola entera. Las dos páginas de la wiki de Devise no se abrieron: valen
   por la lectura del redactor en Context7, como dicen las Referencias.
5. **Pasos de David, sin cambio:** `alembic current` y `alembic check` antes de la fase B; los cuatro comandos y las
   dos consultas después de B y antes de C, con la salida literal en la bitácora; el residual R3 (qué muestra el
   cliente Flutter tras el segundo clic) antes de mezclar.
6. `progress.json` no cambia: ninguna descripción de fase depende de las tres cifras.
