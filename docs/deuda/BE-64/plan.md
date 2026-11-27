# PLAN — BE-64: Permitir que un turista pida otro enlace de verificación

> Fuente: `docs/deuda/BE-64/verificacion.md` (confirmada; adenda de David del 19 nov, decisiones 1–10, que este plan
> toma como dadas). Base: HEAD `22328ce` de `item/be-64`; encima de `b6a80ba` solo hay commits de docs, así que vale la
> línea base de la verificación, y además se volvió a medir (abajo). **Estado: aprobado por David con E0 (19 nov 2026, 19:10) y E1 (19:37); E2 (27 nov 2026, 10:51) añade un
> addendum a ADR-0013. Fases ejecutadas: `progress.json`.** `Aprobado: 19 nov 2026`. ADR propuesto: ADR-0023 (Anexo A), con `<FECHA DE APROBACIÓN>` por rellenar.

## Qué se midió y qué no

Todo en copias `git archive HEAD` (`22328ce`) en el scratchpad de la sesión, una carpeta por corrida y una por
mutante, nunca sobre el árbol de trabajo. Intérprete: `C:/projects/ecotur-asoprado/venv/Scripts/python.exe` por ruta
(CPython 3.14.3, Windows), con cwd = la copia; comprobado: `import app; app.__file__` →
`…\scratchpad\be64-base\app\__init__.py`. `scripts/check.py` hace `chdir` a su propia raíz, que es la de la copia
(`Raíz del repo: …\scratchpad\be64-faseE-green`). El código y los tests de los Anexos B–E se aplicaron con scripts de
reemplazo exacto (cada ancla debía aparecer una vez); los Anexos son el `git diff --no-index` entre copias consecutivas.

| Corrida | Comando | Resultado literal |
|---|---|---|
| Línea base (copia limpia de HEAD) | `scripts/check.py` | exit 0 · `72 files already formatted` · `All checks passed!` · `Success: no issues found in 67 source files` · `Contracts: 4 kept, 0 broken.` · `806 passed, 25 warnings` · `TOTAL … 98.70%` · `Compuerta superada.` |
| B RED (solo tests de B) | `pytest -q` | `1 failed, 805 passed, 2 errors`: `test_table_columns_match_the_frozen_schema[users]` (AssertionError) y los dos de `test_migration_verification_sent_at.py` en preparación (`FileNotFoundError` en `runpy`: la migración no existe) |
| B GREEN | `scripts/check.py` | exit 0 · `73 files` · mypy `68 source files` · `4 kept` · `808 passed` · `98.70%` |
| B, SQL fuera de línea | `DATABASE_URL=postgresql+asyncpg://u:p@localhost:5432/db python -m alembic upgrade e50a7c3d9b12:a64d0c2e7f15 --sql` | `ALTER TABLE users ADD COLUMN verification_sent_at TIMESTAMP WITH TIME ZONE;` y ningún `UPDATE users`; `alembic heads` → `a64d0c2e7f15 (head)`. La copia no tiene `.env` |
| C RED (tests de C + `conftest.py` raíz) | `pytest -q` | `4 failed, 806 passed`: `test_optional_variables_keep_their_current_defaults` (conjunto de campos), `test_verification_resend_interval_is_read_in_seconds` y `test_env_example_is_a_valid_configuration` (`AttributeError`), `test_verification_resend_interval_rejects_a_non_integer` (`DID NOT RAISE`) |
| C GREEN | `scripts/check.py` | exit 0 · `810 passed` · `98.70%` · mypy 68 · `4 kept` |
| D RED (solo tests de D) | `pytest -q` | `15 failed, 810 passed`: 10 de `test_user_repository.py` (`'UserRepository' object has no attribute 'get_tourist_due_a_verification_link'`), 4 de reenvío en `test_user_service.py` (`Mock object has no attribute …`) y `test_register_tourist_counts_as_the_first_link_sent` (`assert None is not None`) |
| D GREEN | `scripts/check.py` | exit 0 · `825 passed` · `98.71%` · mypy 68 · `4 kept` |
| E RED, re-medido tras E0 (solo tests de E) | `pytest -q` | `21 failed, 824 passed`: los 19 de `test_verification_resend.py` (17 con `405 Method Not Allowed` en la aserción de estado, 1 con `(201, 405) != (201, 200)`, y `test_route_declares_its_response_schema` con `KeyError: '/usuarios/reenviar-verificacion'`), `test_every_route_is_listed_as_protected_or_public` (conjunto de rutas) y `test_public_route_answers_without_token[POST /usuarios/reenviar-verificacion]` (`assert 405 == 422`) |
| **E GREEN = estado final, re-medido tras E0** | `scripts/check.py` | exit 0 · `75 files already formatted` · `All checks passed!` · `Success: no issues found in 70 source files` · `Contracts: 4 kept, 0 broken.` · `845 passed, 29 warnings` · `TOTAL 1098 10 160 6 98.73%` · `Compuerta superada.` |
| Mutantes | `pytest -q` completo por copia | 33 mutantes, cada uno en la copia del estado de su fase: **33 muertos, 0 vivos** (tabla en el Análisis). MB, MC y MD de la primera medición; ME1–ME9 re-medidos tras E0. Seis de D, repetidos sobre el estado final de la primera medición: también los matan tests HTTP de E |
| Verificación final | comandos 1–14 sobre la copia final re-medida | los valores que se dan abajo; el 15 con `diff -rq` entre copias (17 archivos; el ADR no se escribió en la copia) |

Cobertura: 98,70 % en la base → 98,73 % al final (no baja). Avisos: 25 → 29; los 4 nuevos son el
`StarletteDeprecationWarning` de `HTTP_422_UNPROCESSABLE_ENTITY` del handler de `app/main.py` (backlog S5), que emiten
los tres 422 de `test_invalid_body_is_422_and_sends_nothing` y el 422 nuevo de `test_route_guards.py`.

### Re-medición tras E0, punto 2 (19 nov 2026)

Qué se volvió a medir, y solo eso: la fase E con su DTO de salida. Copias nuevas `git archive be9d385` (HEAD de
`item/be-64`; entre `22328ce` y `be9d385` solo cambian `docs/`) en carpetas `be64r-…` del scratchpad, sin reutilizar
ninguna de la primera medición; encima, los mismos parches de B, C y D, sin cambios. Mismo intérprete por ruta, cwd =
la copia; comprobado `app.__file__` → `…\scratchpad\be64r-faseE-red\app\__init__.py`.

- Línea base de `be9d385` (copia limpia): exit 0 · `72 files` · mypy 67 · `4 kept` · `806 passed, 25 warnings` ·
  `98.70%` · `Compuerta superada.` (igual que en `22328ce`).
- E RED y E GREEN: las dos filas marcadas "re-medido tras E0" de la tabla de arriba.
- Paso import-linter del GREEN, literal: `Analyzed 57 files, 150 dependencies.` · `Capas: api | cli -> services ->
  repositories -> models KEPT` · `Los servicios no conocen el transporte HTTP KEPT` · `Los repositorios solo conocen
  SQLAlchemy y los modelos KEPT` · `Los modelos y los schemas no dependen de capas superiores KEPT` · `Contracts: 4 kept,
  0 broken.` · `--- import-linter: OK en 0.5s`. Windows no bloqueó `_rustgrimp`: E0 punto 3 no aplicó.
- Mutantes ME1–ME9, cada uno en su copia del estado final nuevo (tabla del Análisis).
- Verificación final 1–14 sobre la copia final nueva; el 15, `diff -rq` contra la copia de `22328ce`.

**No re-medido:** las fases B, C y D (sus parches no cambian: siguen valiendo sus cifras y sus mutantes MB, MC y MD de
la primera medición) y todo lo de la lista siguiente.

**No medido, y por qué:** (1) nada en PostgreSQL: los pasos de `alembic` de David y la comparación `timestamptz <=`
con un parámetro con zona; la suite corre en SQLite, que guarda la fecha como texto sin zona (Referencias). (2) El hook
de formato: en las copias no se ejecutó `ruff format` (los Anexos ya salen formateados: `ruff format --check` en verde
sin tocar nada); el hook reescribe la migración (`(backlog AF-18)`), que está fuera de ruff en la compuerta. (3) La
fase A: el ADR no se escribió en las copias (`docs/adr` está fuera de `check_docs`, que solo lee CONTEXT, PLAN, backlog
y sesiones). (4) Los comandos con `git` de la Verificación final (las copias no tienen `.git`); el alcance se midió con
`diff -rq`. (5) La skill `test-sanitizer`. (6) La diferencia de tiempo de respuesta (decisión 7) y la carrera de dos
peticiones (decisión 8): declaradas, no medidas. (7) El correo real (SMTP) y el cliente Flutter (FE-18). (8) El bloqueo
de `_rustgrimp` `(backlog AF-17)`: hoy no se dio, import-linter evaluó `4 kept` en todas las corridas.

## Resumen para aprobación

Cinco fases. (A) ADR-0023 por escrito antes del código. (B) Columna nueva `users.verification_sent_at` (instante con
zona, admite vacío) y su migración `a64d0c2e7f15`; nace vacía en todas las filas. (C) Variable
`VERIFICATION_RESEND_INTERVAL_SECONDS`, 60 por defecto. (D) La regla: una consulta del repositorio encuentra al turista
no borrado, con la marca de correo vacía (activo o no) y cuyo último enlace salió hace al menos el intervalo; el servicio
sella la hora y firma el token de siempre; el registro sella la misma hora (cuenta como primer envío); sin fila de
auditoría. (E) La ruta pública `POST /usuarios/reenviar-verificacion` con `{"email"}` y `MessageResponse` como
`response_model` (E0, punto 2): responde siempre 200 y el mismo texto de David, envíe o no; 422 si el cuerpo no es un correo; el correo sale en segundo plano como en el registro.
**Riesgo principal:** cambio de esquema medido solo en SQLite; David corre los pasos de PostgreSQL antes y después de B,
y D no empieza sin su salida. **Riesgos aceptados por David, declarados:** el turista anterior a BE-50 que un admin
desactivó puede reactivarse; la respuesta puede tardar distinto; dos peticiones simultáneas pueden enviar dos correos.
**No se toca:** la regla del enlace (ADR-0022), el texto del enlace caducado, el login (BE-56), la activación a mano
(BE-63), BE-62, el `commit()` de los repositorios (A3), el cliente Flutter (FE-18). **Decidido por David en E0:** la ruta
queda en español (punto 1) y nace con schema de salida (punto 2); las demás rutas sin schema son BE-65.

## Objetivo y decisiones bloqueadas

Que un turista cuyo enlace caducó pueda pedir otro sin depender de un administrador, sin que la API revele qué correos
tienen cuenta y sin que nadie pueda inundar un buzón.

1. **A quién** (adenda 1): turista, no borrado, `email_verified_at` vacía, activo o inactivo. Nunca una cuenta
   administrativa (ADR-0019). El filtro va en la consulta `UserRepository.get_tourist_due_a_verification_link`: el
   servicio no escribe `if role ==` (AGENTS §3).
2. **Cuándo** (adenda 3 y 4): `users.verification_sent_at`, `Mapped[datetime | None] = mapped_column(DateTime(timezone=
   True))`, sin `default` (ADR-0010). La escriben `register_tourist` y `resend_verification_link`, con `datetime.now(UTC)`.
   Hay enlace si la columna está vacía o es `<= ahora − intervalo`; la comparación va en SQL. Sin tope total.
3. **Intervalo** (adenda 3): `Settings.verification_resend_interval_seconds: int = 60`, línea en `.env.example`, valor
   `"60"` en el `conftest.py` raíz (ADR-0013).
4. **Respuesta** (adenda 5): 200 `{"success": true, "message": RESEND_VERIFICATION_MESSAGE}` en todos los casos, con
   el texto literal de David; 422 si el cuerpo no es un correo; `LowercaseEmail` (ADR-0016). El texto de
   `user_service.py:141` no cambia.
5. **Sin auditoría** (adenda 6): ni el sello del registro ni el del reenvío dejan fila.
6. **El token no cambia:** `create_verification_token` tal cual (ADR-0022, punto 3).
7. **Alcance solo backend** (adenda 9): FE-18 es del cliente.
8. **Ruta y forma** (E0, puntos 1 y 2): `POST /usuarios/reenviar-verificacion` en `public_router`; manejador en
   inglés `resend_verification_email` (AGENTS §4); `response_model=MessageResponse`, un DTO de salida nuevo en
   `app/schemas/message.py` con exactamente `success: bool` y `message: str`, sobre `BaseModel` y sin validadores
   (AGENTS §3, A9). Módulo propio porque la forma no es de usuarios y BE-65 la reutiliza en `/servicios`. El
   manejador sigue construyendo un `dict` y lo anota `-> dict[str, bool | str]`: FastAPI da prioridad a
   `response_model` sobre la anotación (Referencias), y así quitar el `response_model` cambia el OpenAPI y lo ve un
   test. El cuerpo de la respuesta no cambia.
9. **ADR-0023** es la fase A. La viñeta de AGENTS §3 la propone el plan (Residual R6) y la commitea David.

## Análisis del redactor

**Qué se cambia y por qué.** Hoy `create_verification_token` tiene un solo llamador, `register_tourist`
(`app/services/user_service.py:106`), y una sola ruta programa el correo (`app/api/routers/user.py:70-76`). El reenvío
reutiliza los dos: el servicio devuelve `VerificationResend(user, verification_token)` o `None`, y la ruta programa
`send_verification_email` solo si no es `None` y responde lo mismo siempre. La elegibilidad es un filtro de consulta y
no un `if` en el servicio por dos razones medidas en el diseño: (a) AGENTS §3 prohíbe `if role ==` sueltos en
servicios, y el filtro por rol del dato sin actor es *data scoping*, como `count_active_superadmins`
(`user_repository.py:23-41`); (b) SQLite devuelve `DateTime(timezone=True)` sin zona y Python no compara un instante
sin zona con `datetime.now(UTC)`: en SQL la comparación es de texto con el mismo formato UTC en SQLite y de
`timestamptz` en PostgreSQL. El método nuevo solo lee (`select`), así que nace sin `commit()` (A3); la escritura usa
`save_user`, que ya existe.

**Orden y dependencias.** A primero (lo citan B–E y es la más pequeña). B y C son independientes; D lee la columna y la
variable, así que va después de las dos. Entre B y D, David corre los pasos de PostgreSQL. E consume el método de D.

**Qué tests congelan qué.**
- `tests/test_models_schema.py:66-80` congela `users` con literales: la fila nueva es el RED de B.
- `tests/test_migration_email_verified_at.py` y `tests/test_email_case.py` hacen `create_all` con el modelo actual y
  bajan su propia migración en batch: con la columna nueva siguen en verde (medido en B GREEN).
- `tests/test_config.py:35-46` (`OPTIONAL_DEFAULTS`) obliga a declarar la variable; `:236-245` exigen su línea en
  `.env.example` y en el `conftest.py` raíz.
- `tests/test_route_guards.py:78-104` obliga a inscribir la ruta en `PUBLIC_ROUTES` y `_ANONYMOUS_ON_PUBLIC_ROUTE`.
- `tests/conftest.py:144-157` parchea `app.api.routers.user.send_verification_email`: la ruta nueva está en ese módulo,
  así que el doble la cubre sin tocar `tests/conftest.py`. `make_user` reenvía `**overrides` a `User(...)`
  (`:183-203`): `verification_sent_at=` funciona sin tocarlo.
- Siguen sin cambios y en verde: registro (`tests/test_auth.py:29-89`), enlace (`:92-312`), `UserResponse`
  (`tests/test_user_response.py`, que fija las claves y por tanto que la columna no se expone).

**Mutantes (todos medidos; cada uno en su copia, suite completa).**

| # | Mutante (archivo de producción) | Lo matan |
|---|---|---|
| MB1 | migración: `op.execute("UPDATE users SET verification_sent_at = CURRENT_TIMESTAMP")` tras el batch | `test_migration_adds_the_column_empty_in_every_row` |
| MB2 | `downgrade()` → `pass` | los dos de `test_migration_verification_sent_at.py` |
| MB3 | modelo `Mapped[datetime]` (NOT NULL) | `test_table_columns_match_the_frozen_schema[users]`, los 2 de migración y 255 más (258 en total) |
| MB4 | modelo `DateTime()` sin zona | `test_table_columns_match_the_frozen_schema[users]` |
| MB5 | `downgrade()` borra también `email_verified_at` | `test_migration_downgrade_drops_only_its_column_and_keeps_the_rows` |
| MC1 | `verification_resend_interval_seconds: int = 30` | `test_optional_variables_keep_their_current_defaults` |
| MC2 | `.env.example` con `=61` | `test_env_example_is_a_valid_configuration` |
| MC3 | `.env.example` sin la línea | `test_env_example_documents_every_setting` |
| MC4 | `conftest.py` raíz sin la entrada | `test_test_environment_fixes_every_setting` |
| MD1 | `register_tourist` sin `verification_sent_at=` | `test_register_tourist_counts_as_the_first_link_sent`; en el estado final también `test_registration_counts_as_the_first_link` |
| MD2 | consulta sin `User.role == UserRole.tourist` | `…_is_not_found[admin]`, `[superadmin]`; final: + `…_same_answer_and_no_email[admin]`, `[superadmin]` |
| MD3 | consulta sin `deleted_at.is_(None)` | `…_is_not_found[soft-deleted]` |
| MD4 | consulta sin `email_verified_at.is_(None)` | `…_is_not_found[verified]`; final: + `[verified-tourist]`, `[verified-tourist-deactivated]` |
| MD5 | `or_(…)` → solo `verification_sent_at <= sent_before` | `…_is_found[inactive-never-sent]`, `[active-unverified]` |
| MD6 | `<=` → `<` | `…_is_found[sent-at-the-cutoff]` |
| MD7 | sin la condición de hora | `…_is_not_found[sent-after-the-cutoff]` |
| MD8 | el servicio no sella la hora | `test_resend_issues_a_link_to_the_account_due_one`; final: + `test_pending_tourist_gets_a_new_link`, `test_second_request_within_the_interval_sends_nothing`, `test_link_is_sent_again_once_the_interval_passed` |
| MD9 | el servicio no llama a `save_user` | `test_resend_issues_a_link…`, `test_resend_save_failure_propagates_without_a_link`; final: + los tres HTTP de MD8 |
| MD10 | intervalo fijo `timedelta(seconds=60)` | `test_resend_interval_comes_from_the_settings` |
| MD11 | `now + interval` | `test_resend_issues_a_link…`, `test_resend_interval_comes_from_the_settings` |
| MD12 | el reenvío escribe una fila de auditoría | `test_resend_issues_a_link_to_the_account_due_one` |
| MD13 | consulta exige `is_active` falso | `…_is_found[active-unverified]`; final: + `test_tourist_an_admin_activated_without_verifying_gets_a_link` |
| MD14 | consulta sin `User.email == email` | `test_due_verification_link_lookup_matches_only_its_email` |
| MD15 | `save_user` en `try/except: pass` | `test_resend_save_failure_propagates_without_a_link` |
| ME1 | otro `message` cuando no se envía | los 6 `…_same_answer_and_no_email[…]`, `test_unknown_…`, `test_second_request_within_the_interval_sends_nothing` (8) |
| ME2 | programa el correo aunque el servicio dé `None` | los 6 `…_same_answer_and_no_email[…]`, `test_unknown_…`, `test_registration_counts_as_the_first_link`, `test_second_request_…` (9) |
| ME3 | `VerificationResendRequest.email: EmailStr` (sin minúsculas) | `test_email_is_matched_in_lowercase` |
| ME4 | `base_url=settings.frontend_url` sin `rstrip` | `test_link_is_built_from_frontend_url` |
| ME5 | `status.HTTP_202_ACCEPTED` | 15 de `test_verification_resend.py`, `test_route_declares_its_response_schema` incluido |
| ME6 | sin `response_model=MessageResponse` | `test_route_declares_its_response_schema` |
| ME7 | `MessageResponse` gana `detail: str \| None = None` | `test_pending_tourist_gets_a_new_link` (claves del cuerpo), `test_route_declares_its_response_schema` |
| ME8 | `message: str \| None = None` (opcional) | `test_route_declares_its_response_schema` |
| ME9 | sin `response_model` y el `dict` con una clave de más (`"email": body.email`) | `test_pending_tourist_gets_a_new_link`, los 6 `…_same_answer_and_no_email[…]`, `test_unknown_…`, `test_route_declares_its_response_schema` (9) |

ME1–ME9 son de la re-medición tras E0, sobre el estado final nuevo. Con el `response_model` puesto, una clave de más
en el `dict` no sale de la API (el schema la filtra): por eso ME9 la combina con quitarlo.

**Riesgos.** (1) SQLite frente a PostgreSQL `(backlog BE-31)`: lo cubren el test de esquema compilado para PostgreSQL,
el SQL fuera de línea y los pasos de David. (2) Carrera de dos peticiones: dos lecturas antes de la escritura, dos
correos (adenda 8, aceptado). (3) Tiempo de respuesta distinto si la cuenta es elegible (adenda 7, aceptado; R1). (4)
El texto dice "espere un minuto": si alguien cambia la variable, el texto miente (ADR-0023, consecuencias). (5) El hook
reescribe la migración `(backlog AF-18)`: el ejecutor de B la restaura al texto del Anexo B y lo declara.

**Qué NO se toca:** `verify_email_account` y sus textos, `authenticate_user`, `create_verification_token`,
`app/core/email.py`, `app/main.py`, `UserAccessPolicy`, `app/api/dependencies.py`, `tests/conftest.py`, `UserResponse`
y los demás DTO, `save_user`/`create_user` (A3), el cliente Flutter.

## Regla de alcance

**Sí:** ADR-0023; la columna y su migración; la variable; la consulta, el método del servicio y el sello del registro;
el DTO de entrada, el de salida (`MessageResponse`), la ruta y su inventario; los tests de todo eso.
**No:** BE-56, BE-62, BE-63, BE-65 (las otras siete rutas sin schema), SEC3, S5, A3, FE-18; `docs/backlog.md`, `docs/CONTEXT.md`, `AGENTS.md` (los actualiza
David al cerrar). Un hallazgo nuevo va a Residuales del handoff, nunca al código.

## Fases

### Fase A — ADR-0023: el enlace de verificación se puede pedir de nuevo (la más pequeña)
- **Archivos (1):** `docs/adr/0023-el-enlace-de-verificacion-se-puede-pedir-de-nuevo.md` (nuevo).
- **Cambios exactos:** el texto del Anexo A, literal, con `<FECHA DE APROBACIÓN>` sustituido por la fecha de la línea
  "Aprobado:" que David anote en este plan.
- **Tests (RED primero):** no aplica (documento fuera de `check_docs`). Antes: `ls docs/adr/0023-*` → sin resultados.
- **Criterio de aceptación:** el archivo existe; `grep -c "<FECHA" docs/adr/0023-*.md` → `0`; compuerta en verde con
  `806 passed` (sin cambios de código).
- **Fuera de alcance:** AGENTS §3, backlog, CONTEXT.
- **Commit:**
  ```
  docs(adr): add ADR-0023, a verification link can be asked for again

  A tourist whose 15-minute link expired had no way to get another one:
  registering again is a 400 and only an admin could activate the
  account by hand (BE-64).

  ADR-0023 records David's decisions before any code: a public route
  that always answers the same, a new link only for a non-deleted
  tourist with the verified mark empty, at least 60 seconds between
  two links with no cap, registration counting as the first one, and
  no audit row. It declares the accepted risks (a pre-BE-50 tourist an
  admin deactivated can reactivate, response timing, two concurrent
  requests) and leaves the client to FE-18.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase B — Columna `users.verification_sent_at` y su migración
- **Archivos (4):** `app/models/user.py`, `alembic/versions/a64d0c2e7f15_users_verification_sent_at.py` (nuevo),
  `tests/test_models_schema.py`, `tests/test_migration_verification_sent_at.py` (nuevo).
- **Cambios exactos:** Anexo B (modelo: 3 líneas tras `email_verified_at`, `:58`; migración escrita a mano con el id y
  la fecha del Anexo; una fila en `EXPECTED["users"]`, `:80`; el test completo).
- **Antes de empezar (David, `cmd`, ADR-0010 punto 7):** desde `C:\projects\ecotur-asoprado`,
  `venv\Scripts\python.exe -m alembic current` → `e50a7c3d9b12 (head)`; `venv\Scripts\python.exe -m alembic check` →
  `No new upgrade operations detected.`; salida literal en la bitácora.
- **Tests (RED primero):** los dos archivos de test sin tocar `app/` ni `alembic/`: falla
  `test_table_columns_match_the_frozen_schema[users]`; los dos de migración dan error de preparación
  (`FileNotFoundError`). Esperado: `1 failed, 805 passed, 2 errors`.
- **Criterio de aceptación:** compuerta completa en 0 con `808 passed`, cobertura ≥ 98,70 %, mypy en 68 archivos.
  SQL fuera de línea (Git Bash, sin base): `DATABASE_URL=postgresql+asyncpg://u:p@localhost:5432/db
  ./venv/Scripts/python.exe -m alembic upgrade e50a7c3d9b12:a64d0c2e7f15 --sql` contiene `ALTER TABLE users ADD COLUMN
  verification_sent_at TIMESTAMP WITH TIME ZONE;` y ningún `UPDATE users`; el handoff copia la salida. Mutantes MB1–MB5
  muertos (tabla del Análisis).
- **Después del commit (David, `cmd`, antes de la fase D):** `venv\Scripts\python.exe -m alembic upgrade head` →
  `Running upgrade e50a7c3d9b12 -> a64d0c2e7f15`; `… -m alembic check` → `No new upgrade operations detected.`;
  `… -m alembic downgrade -1` → `Running downgrade a64d0c2e7f15 -> e50a7c3d9b12`; `… -m alembic upgrade head`. En su
  cliente SQL: `SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'users'
  AND column_name = 'verification_sent_at';` → `verification_sent_at | timestamp with time zone | YES`, y `SELECT
  count(*) FROM users WHERE verification_sent_at IS NOT NULL;` → `0`. Si `check` lista operaciones, se detiene.
- **Fuera de alcance:** quien lee o escribe la columna (D); `app/schemas/`; `tests/conftest.py`.
- **Commit:**
  ```
  feat(users): add the verification_sent_at column, empty in every row

  A new verification link has to wait a minimum interval after the
  last one (BE-64, ADR-0023), and nothing kept when a link was sent.
  This commit adds that fact; nothing reads or writes it yet.

  - app/models/user.py: verification_sent_at, a timestamp with time
    zone that admits NULL, with no default.
  - alembic a64d0c2e7f15: adds the column in batch (a plain ALTER TABLE
    on PostgreSQL) and fills no row: the time of an earlier link was
    never kept, and an empty value lets that account ask at once.
    Downgrade drops only this column.
  - tests: the frozen users schema gains the column; the migration runs
    on a SQLite of its own and leaves a pending tourist, a verified one
    and an admin empty, and its downgrade keeps the verified mark.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase C — Variable `VERIFICATION_RESEND_INTERVAL_SECONDS`
- **Archivos (4):** `app/core/config.py`, `.env.example`, `conftest.py` (raíz), `tests/test_config.py`.
- **Cambios exactos:** Anexo C (un campo con comentario tras `verification_token_expire_minutes`, `:51`; dos líneas en
  `.env.example` tras `VERIFICATION_TOKEN_EXPIRE_MINUTES=15`; una entrada en `TEST_ENVIRONMENT`; en `test_config.py`
  una entrada en `OPTIONAL_DEFAULTS`, un cuarto valor en `test_env_example_is_a_valid_configuration` y dos tests).
- **Tests (RED primero):** `tests/test_config.py` y el `conftest.py` raíz sin tocar `app/` ni `.env.example` (la
  entrada del `conftest.py` no rompe nada: `extra="ignore"`). Esperado: `4 failed, 806 passed`
  (`test_optional_variables_keep_their_current_defaults`, `test_verification_resend_interval_is_read_in_seconds`,
  `test_verification_resend_interval_rejects_a_non_integer`, `test_env_example_is_a_valid_configuration`).
- **Criterio de aceptación:** compuerta en 0 con `810 passed`, cobertura ≥ 98,70 %. Mutantes MC1–MC4 muertos.
- **Fuera de alcance:** quien lee la variable (D); validar rangos (cero o negativo dejan reenviar sin espera: no lo pide
  la adenda; Residual R5).
- **Commit:**
  ```
  feat(config): add the minimum wait between two verification links

  The resend of the verification link waits a minimum interval between
  two links to one account (BE-64, ADR-0023). David fixed 60 seconds
  and wanted it configurable, so it is a Settings field like every
  other value (ADR-0013).

  - app/core/config.py: verification_resend_interval_seconds, 60 by
    default.
  - .env.example and the root conftest.py: its line and its test value,
    which tests/test_config.py requires.
  - tests/test_config.py: the default, the value read from the
    environment, a non-integer rejected naming the field, and the
    example file loading 60.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase D — Quién recibe un enlace nuevo y cuándo
- **Requisito previo:** la salida de los pasos de David tras B está en la bitácora y `check` dio `No new upgrade
  operations detected.`.
- **Archivos (4):** `app/repositories/user_repository.py`, `app/services/user_service.py`,
  `tests/test_user_repository.py`, `tests/test_user_service.py`.
- **Cambios exactos:** Anexo D. Repositorio: `get_tourist_due_a_verification_link(email, sent_before)` tras
  `get_non_deleted_user_by_email` (`:43-46`), solo `select`. Servicio: `timedelta` en el import; `VerificationResend`
  tras `RegistrationResult`; dos líneas en el docstring de `register_tourist` y `verification_sent_at=datetime.now(UTC)`
  en su `User(...)` (`:82-92`); `resend_verification_link` antes de `authenticate_user` (`:180`).
- **Tests (RED primero):** los del Anexo D sin tocar `app/`. Repositorio: `test_tourist_due_a_verification_link_is_found`
  ×4 (`inactive-never-sent`, `active-unverified`, `sent-before-the-cutoff`, `sent-at-the-cutoff`),
  `test_account_not_due_a_verification_link_is_not_found` ×5 (`admin`, `superadmin`, `soft-deleted`, `verified`,
  `sent-after-the-cutoff`), `test_due_verification_link_lookup_matches_only_its_email`. Servicio:
  `test_register_tourist_counts_as_the_first_link_sent`, `test_resend_issues_a_link_to_the_account_due_one`,
  `test_resend_with_no_account_due_writes_nothing`, `test_resend_interval_comes_from_the_settings`,
  `test_resend_save_failure_propagates_without_a_link`. Esperado: `15 failed, 810 passed`.
- **Criterio de aceptación:** compuerta en 0 con `825 passed`, cobertura ≥ 98,70 % (medido 98,71 %);
  `grep -c "commit()" app/repositories/user_repository.py` → `3` (el método nuevo no hace commit). Mutantes MD1–MD15
  muertos. Skill `test-sanitizer` sobre los dos archivos de test.
- **Fuera de alcance:** la ruta y el DTO (E); `save_user`/`create_user`; la regla del enlace; `authenticate_user`.
- **Commit:**
  ```
  feat(auth): decide who may get a new verification link, and when

  A tourist whose link expired needs another one, but the empty
  verified mark alone also matches admin accounts and every row older
  than BE-50, so it cannot decide on its own (BE-64, verification
  corner 1; ADR-0023).

  - app/repositories/user_repository.py: one read-only query finds the
    account due a link: a tourist, not deleted, with the mark empty,
    active or not, whose last link is at or before now minus the
    interval, or not on record. The comparison runs in SQL, so it
    holds on PostgreSQL timestamptz and on the suite's SQLite text.
  - app/services/user_service.py: resend_verification_link stamps the
    send time, saves it and signs the usual token, or returns None;
    registration stamps the same time, so it counts as the first link.
    Neither writes an audit row: the time is operational data.
  - tests: the query on each kind of account and on the exact cutoff;
    the service on its cutoff, its interval, its stamp and a failed
    save.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

### Fase E — La ruta pública de reenvío
- **Archivos (5):** `app/schemas/message.py` (nuevo), `app/schemas/user.py`, `app/api/routers/user.py`,
  `tests/test_route_guards.py`, `tests/test_verification_resend.py` (nuevo).
- **Cambios exactos:** Anexo E. `MessageResponse` en su módulo; DTO `VerificationResendRequest` tras `UserLogin`
  (`:135-137`); en el router, el import de `MessageResponse`, el de `app.schemas.user` en varias líneas,
  `RESEND_VERIFICATION_MESSAGE` tras `public_router` (`:32`) y `resend_verification_email` con
  `response_model=MessageResponse` antes de `login` (`:98`); dos entradas en las tablas de rutas públicas (`:81`,
  `:96`).
- **Tests (RED primero):** `tests/test_route_guards.py` y el archivo nuevo sin tocar `app/`. Casos:
  `test_pending_tourist_gets_a_new_link`, `test_the_new_link_verifies_the_account`,
  `test_account_not_due_a_link_gets_the_same_answer_and_no_email` ×6 (`admin`, `superadmin`, `soft-deleted-tourist`,
  `verified-tourist`, `verified-tourist-deactivated`, `link-sent-59-seconds-ago`),
  `test_unknown_email_gets_the_same_answer_and_no_email`, `test_tourist_an_admin_activated_without_verifying_gets_a_link`,
  `test_registration_counts_as_the_first_link`, `test_second_request_within_the_interval_sends_nothing`,
  `test_link_is_sent_again_once_the_interval_passed`, `test_email_is_matched_in_lowercase`,
  `test_invalid_body_is_422_and_sends_nothing` ×3 (`malformed`, `null`, `missing`),
  `test_link_is_built_from_frontend_url`, `test_route_declares_its_response_schema` (el 200 del OpenAPI es
  `$ref` a `MessageResponse`, con `success` booleano y `message` texto, los dos obligatorios). Esperado: `21 failed,
  824 passed`.
- **Criterio de aceptación:** compuerta completa en 0 con `845 passed`, cobertura ≥ 98,70 % (medido 98,73 %), mypy en
  70 archivos, `4 kept` (o E0 punto 3 si Windows bloquea `_rustgrimp`); Verificación final 1–16 con los valores
  dados. Mutantes ME1–ME9 muertos. Skill
  `test-sanitizer` sobre los dos archivos de test. Ningún test afirma sobre el texto en español (comando 10).
- **Fuera de alcance:** `app/main.py` (S5), `verificar-email` y las otras seis rutas sin schema (BE-65), el cliente
  (FE-18), `docs/`.
- **Commit:**
  ```
  feat(auth): add the public route that resends the verification link

  The API told a tourist with an expired link to ask for a new one and
  had nowhere to ask (BE-64). POST /usuarios/reenviar-verificacion
  takes an email and answers 200 with the same body whether or not a
  link leaves, so it does not tell which addresses have an account
  (ADR-0023).

  - app/schemas/message.py: MessageResponse, success and message and
    nothing else, on BaseModel with no validators (backlog A9). Its own
    module: the shape is not about users and BE-65 reuses it.
  - app/schemas/user.py: VerificationResendRequest, a LowercaseEmail
    only (ADR-0016); anything else is a 422.
  - app/api/routers/user.py: the route declares MessageResponse as its
    response_model, asks the service for a link and, when there is one,
    schedules the usual email as a background task, as registration
    does; the message is David's text.
  - tests: the route in the public inventory (ADR-0012); its 200 schema
    in the OpenAPI; a pending and an admin-activated tourist get a
    working link; admins, deleted or verified accounts, an unknown
    address and a request inside the interval get the same body and
    no email; registration counts as the first link; the email is
    matched in lower case.

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  ```

## Verificación final

Desde la raíz, en Git Bash, tras la fase E. Valores medidos en la copia final re-medida tras E0 (el 15, con `diff -rq`
más el ADR). Los
números cuentan el texto que dictan los Anexos (docstrings, comentarios, nombres de tests).

```bash
# 1. Emisores del token → 3: security.py:91 (la def), register_tourist, resend_verification_link (hoy 2)
grep -rn "create_verification_token(" app --include=*.py | wc -l
# 2. Sitios que programan el correo → 2, los dos en app/api/routers/user.py (hoy 1)
grep -rn "send_verification_email," app --include=*.py | wc -l
# 3. Reenvío → 26 líneas: routers/user.py 14, user_service.py 7, config.py 1, models/user.py 1,
#    user_repository.py 1, schemas/user.py 1, user_access_policy.py 1 (este último ya estaba: "resending the current role")
grep -rn -i "resend\|reenv" app --include=*.py | wc -l
# 4. Rutas públicas de usuarios → 4; la nueva inscrita dos veces en el inventario → 2
grep -n "@public_router\." app/api/routers/user.py | wc -l
grep -c "reenviar-verificacion" tests/test_route_guards.py
# 5. El texto del enlace caducado no cambia → 1
grep -rn "solicite uno nuevo" app --include=*.py | wc -l
# 6. La marca de BE-50: 11 líneas (hoy 10; +1 el filtro de la consulta) y un solo escritor → 1
grep -rn "email_verified_at" app alembic --include=*.py | wc -l
grep -rn "email_verified_at = " app --include=*.py | wc -l
# 7. La columna nueva → 10 (migración 5, modelo 1, repositorio 1, servicio 3); escritores → 2 (user_service.py);
#    en los schemas → 0
grep -rn "verification_sent_at" app alembic --include=*.py | wc -l
grep -rn "verification_sent_at=\|verification_sent_at = " app --include=*.py | wc -l
grep -rn "verification_sent_at" app/schemas --include=*.py | wc -l
# 8. Limitador de peticiones → 0 (no se añade librería)
grep -rn -i "slowapi\|limiter\|rate.limit\|throttl" app pyproject.toml constraints.txt | wc -l
# 9. Una sola cabeza: solo la migración nueva desciende de e50a7c3d9b12 → 1
grep -rln "down_revision.*'e50a7c3d9b12'" alembic/versions --include=*.py | wc -l
# 10. El texto de David → 1 en app; 0 en tests (no se afirma sobre texto en español)
grep -rn "le acabamos de enviar un nuevo" app --include=*.py | wc -l
grep -rn -E "acabamos de enviar|espere un minuto" tests --include=*.py | wc -l
# 11. A3: el repositorio no gana commit() → 3, como hoy; el servicio no gana log_transaction → 6, como hoy
grep -c "commit()" app/repositories/user_repository.py
grep -c "log_transaction" app/services/user_service.py
# 12. Variable documentada y fijada en la suite → 1 y 1
grep -c "^VERIFICATION_RESEND_INTERVAL_SECONDS=60$" .env.example
grep -c '"VERIFICATION_RESEND_INTERVAL_SECONDS": "60"' conftest.py
# 13. Menciones en .py → BE-64: 10 líneas en 10 archivos; ADR-0023: 13 líneas
grep -rn "BE-64" app tests alembic --include=*.py | wc -l
grep -rn "ADR-0023" app tests alembic --include=*.py | wc -l
# 14. Schema de salida (E0, punto 2): declarado en la ruta → 1; líneas en app → 4 (el import y la ruta en el
#     router, una línea del docstring del manejador, la clase); en tests → 3
grep -c "response_model=MessageResponse" app/api/routers/user.py
grep -rn "MessageResponse" app --include=*.py | wc -l
grep -rn "MessageResponse" tests --include=*.py | wc -l
# 15. Alcance del diff → exactamente los 18 archivos de abajo
git diff --name-only 22328ce HEAD -- app alembic tests conftest.py .env.example docs/adr
# 16. Compuerta → exit 0; 845 passed; cobertura ≥ 98,70 % (medido 98,73 %); ruff 0 en 75; mypy 0 en 70; 4 kept
./venv/Scripts/python.exe scripts/check.py
```

El 13 por archivo: BE-64 en la migración, `routers/user.py`, `config.py`, `models/user.py`, `schemas/message.py`,
`schemas/user.py`, `user_service.py`, `test_migration_verification_sent_at.py`, `test_user_service.py`, `test_verification_resend.py`;
ADR-0023 dos veces en `routers/user.py` y en `user_service.py`, una en los otros nueve (`schemas/message.py` no la cita). El 15 lista: `.env.example`,
`alembic/versions/a64d0c2e7f15_users_verification_sent_at.py`, `app/api/routers/user.py`, `app/core/config.py`,
`app/models/user.py`, `app/repositories/user_repository.py`, `app/schemas/message.py`, `app/schemas/user.py`,
`app/services/user_service.py`, `conftest.py`, `docs/adr/0023-el-enlace-de-verificacion-se-puede-pedir-de-nuevo.md`, `tests/test_config.py`,
`tests/test_migration_verification_sent_at.py`, `tests/test_models_schema.py`, `tests/test_route_guards.py`,
`tests/test_user_repository.py`, `tests/test_user_service.py`, `tests/test_verification_resend.py`.
**Paso humano antes de `/pr`:** los pasos de PostgreSQL de la fase B están en la bitácora con su salida literal.
Recomendado, no exigido: con la API local sobre PostgreSQL, dos `POST /usuarios/reenviar-verificacion` seguidos a un
turista pendiente envían un solo correo (prueba la comparación `timestamptz`, que la suite no ve).

## Residuales

| # | Hallazgo (evidencia) | Destino sugerido |
|---|---|---|
| R1 | La ruta tarda algo más cuando la cuenta es elegible (firma token, escribe la columna, programa la tarea); OWASP pide tiempo uniforme. Aceptado (adenda 7). | Nota en la fila SEC3. |
| R2 | Dos peticiones simultáneas leen la columna antes de que ninguna la escriba y envían dos correos (adenda 8; razonado, no medido). | Nota en A3/BE-31; sin fila nueva. |
| R3 | Las demás rutas que devuelven un `dict` sin `response_model` (siete, medido por la sesión Mentor). La de este ítem ya nace con `MessageResponse` (E0, punto 2), que BE-65 reutiliza. | Ya es la fila `(backlog BE-65)`; sin fila nueva. |
| R4 | Los 422 nuevos suben los avisos de la suite de 25 a 29 (`HTTP_422_UNPROCESSABLE_ENTITY`, `app/main.py`; medido). | Nota en la fila S5. |
| R5 | `VERIFICATION_RESEND_INTERVAL_SECONDS` acepta 0 o negativos (sin espera) y el texto fijo dice "un minuto". | Nota en BE-64 al cerrar; validar rango solo si David lo pide. |
| R6 | Viñeta para AGENTS §3. Propuesta: "**Reenvío del enlace (ADR-0023):** solo lo recibe un turista no borrado con `email_verified_at` vacía; entre dos enlaces pasan `VERIFICATION_RESEND_INTERVAL_SECONDS` (`users.verification_sent_at`, que escriben el registro y el reenvío); `POST /usuarios/reenviar-verificacion` responde siempre lo mismo." | David, tras la última auditoría. |
| R7 | FE-18 necesita el contrato: `POST /usuarios/reenviar-verificacion`, cuerpo `{"email"}`, 200 `MessageResponse` (`{"success": bool, "message": str}`, documentado en `/openapi.json`) siempre, 422 `{"detalle": [...]}`. | Nota en la fila FE-18 al mezclar. |
| R8 | El mensaje del login de una cuenta inactiva (`user_service.py:199`) podría remitir al reenvío. | Nota en la fila BE-56. |

## Referencias

- SQLAlchemy 2.0.48 · SQLite `DATETIME` guarda texto `YYYY-MM-DD HH:MM:SS.ffffff` sin zona y lee con
  `datetime.fromisoformat()` · https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#sqlalchemy.dialects.sqlite.DATETIME
  (leído en Context7, `/sqlalchemy/sqlalchemy/rel_2_0_49`, texto fuente de `doc/build/dialects/sqlite.rst`).
- Alembic 1.18.4 · `batch_alter_table` y `alembic check` (precedente de BE-50) · https://alembic.sqlalchemy.org/en/latest/batch.html
- FastAPI 0.135.1 / Starlette 1.3.1 · `BackgroundTasks` (patrón ya usado en `/registro`) ·
  https://fastapi.tiangolo.com/tutorial/background-tasks/
- FastAPI 0.135.1 · "`response_model` Priority": si hay anotación de retorno y `response_model`, manda
  `response_model` (validación, documentación y filtrado de la salida) · https://fastapi.tiangolo.com/tutorial/response-model/
  (leído en Context7, `/websites/fastapi_tiangolo`).
- OWASP Cheat Sheet Series · Forgot Password, "Forgot Password Request": mensaje igual para cuentas que existen y que
  no, tiempo de respuesta uniforme, y "rate-limiting on a per-account basis" contra envíos automatizados; no da cifra ·
  https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html (leído en Context7,
  `/owasp/cheatsheetseries`, texto fuente; trata de la recuperación de contraseña: aplica por analogía).
- Supabase · tabla "Auth rate limits": "Signup confirmation request · Limited by: Last request · Defaults to 60 seconds
  window before a new request is allowed. Is customizable." · https://supabase.com/docs/guides/deployment/going-into-prod
  (leído en Context7, `/supabase/supabase`, `apps/docs/content/guides/deployment/going-into-prod.mdx`). La página que
  cita la adenda (`/docs/guides/auth/rate-limits`) solo dice, en el texto leído, que hay límites configurables; la cifra
  de 60 s está en la tabla de la otra página.

---

## Anexo A — texto de ADR-0023

```markdown
# ADR-0023 — El enlace de verificación se puede pedir de nuevo: a un turista sin verificar, con un mínimo entre envíos y la misma respuesta siempre

- **Estado:** aceptado (David, <FECHA DE APROBACIÓN>, al aprobar el plan de BE-64)
- **Propuesta:** Claude, `plan-redactor` (19 nov 2026), sobre la adenda de David a la verificación (19 nov, 17:13 a
  17:44)
- **Ubicación en el repo:** `docs/adr/0023-el-enlace-de-verificacion-se-puede-pedir-de-nuevo.md`
- **Origen:** backlog BE-64; `docs/deuda/BE-64/verificacion.md` (veredicto, rincones 1 a 3 y adenda);
  `docs/deuda/BE-64/plan.md`. Relación: ADR-0022 (la regla del enlace no cambia; esta decisión responde a su
  consecuencia "sin reenvío"), ADR-0019 (las cuentas administrativas las decide un superadmin), ADR-0016 (correo en
  minúsculas), ADR-0013 (variable nueva), ADR-0012 (ruta pública en el inventario), ADR-0010 (estilo de la columna),
  ADR-0021 (qué se audita). BE-65 reutiliza su schema de salida.

## Contexto

El enlace de verificación vive 15 minutos y solo lo emitía el registro. Pasado ese plazo la API respondía que había
caducado y pedía "solicite uno nuevo", sin ruta para pedirlo; registrarse otra vez da 400 porque el correo y la cédula
ya existen, y la cuenta quedaba inactiva hasta que un administrador la activara a mano (BE-63). La marca
`email_verified_at` (ADR-0022) no basta para decidir a quién se le emite: está vacía en las cuentas administrativas, en
el superadmin del bootstrap y en todas las filas anteriores a su migración, y un enlace con la marca vacía activa la
cuenta. La aplicación no tiene limitador de peticiones ni guardaba cuándo salió un enlace.

## Decisión

1. **Ruta pública `POST /usuarios/reenviar-verificacion`**, cuerpo `{"email": …}` (`LowercaseEmail`), con
   `response_model=MessageResponse` (`app/schemas/message.py`: exactamente `success: bool` y `message: str`, sobre
   `BaseModel`, sin validadores ni herencia de un DTO de entrada). Responde siempre 200 `{"success": true,
   "message": …}` con el mismo texto, exista o no la cuenta, sea cual sea su estado y haya pasado o no el intervalo.
   Un cuerpo que no es un correo es 422. La ruta va en español aunque es nueva: AGENTS §4 (b) exceptúa del inglés
   solo las rutas públicas ya existentes, y esta sigue a sus vecinas de `/usuarios` a sabiendas, porque unificar el
   idioma es `(backlog P2)`, en `B-FUTURO`, y una sola ruta en inglés haría la asimetría más visible. El manejador va
   en inglés.
2. **A quién:** a una cuenta de turista, no borrada, con `email_verified_at` vacía, activa o inactiva. Nunca a una
   cuenta administrativa. El filtro es la consulta del repositorio, no un `if` sobre el rol en el servicio.
3. **Cuándo:** columna `users.verification_sent_at` (`TIMESTAMP WITH TIME ZONE`, admite vacío). La escriben el registro
   y cada reenvío. Un enlace nuevo exige que la columna esté vacía o que hayan pasado al menos
   `VERIFICATION_RESEND_INTERVAL_SECONDS` (60 por defecto) desde el último. Sin tope total. La migración `a64d0c2e7f15`
   no rellena ninguna fila: vacía significa "no consta envío" y deja pedir uno ya.
4. **El enlace es el de siempre:** el mismo token (`sub`, `scope`, `exp`, 15 minutos, sin identificador, sin guardar).
   Varios vigentes a la vez no son un riesgo: el primero que se usa llena la marca y los demás no cambian nada.
5. **Sin auditoría:** ni el registro ni el reenvío dejan fila por el envío; la hora es un dato operativo y ningún DTO
   la lleva.
6. **El correo sale en segundo plano**, como tras el registro. El texto del enlace caducado no cambia.

## Consecuencias

- Un turista cuyo enlace caducó lo pide de nuevo sin depender de un administrador. Hasta FE-18, solo desde la API.
- Un turista que un administrador activó sin verificar (BE-63) puede pedir el enlace; al usarlo solo se llena la marca.
- **Riesgo aceptado:** un turista anterior a la migración de ADR-0022 que verificó su correo y que un administrador
  desactivó después tiene la marca vacía, es indistinguible de uno pendiente y puede reactivarse con un enlace nuevo.
  Ningún entorno tiene usuarios reales (palabra de David); lo cierra el modelo de dos hechos (BE-62).
- **Declarado:** la respuesta puede tardar algo más cuando la cuenta es elegible (SEC3); el registro sigue revelando si
  un correo o una cédula existen.
- **Declarado:** dos peticiones simultáneas pueden enviar dos correos; no hay bloqueo de fila (como los dos clics de
  ADR-0022).
- El texto de la respuesta dice "espere un minuto": cambiar la variable exige cambiar el texto.
- La comparación con el intervalo va en SQL: SQLite, donde corre la suite, guarda la columna como texto sin zona.

## Alternativas consideradas

1. **"Marca vacía y no borrada", sin mirar el rol.** Rechazada: un admin desactivado por un superadmin, o creado
   inactivo, se activaría solo (ADR-0019).
2. **Exigir además `is_active` falso.** Propuesta y retirada (17:36): dejaría sin enlace al turista que un
   administrador activó sin verificar, que es la única vía para que llegue a tener su correo probado.
3. **Reenviar solo a cuentas con la hora llena.** Rechazada: deja sin reenvío a todo turista pendiente anterior al
   despliegue, que es a quien el ítem quiere ayudar.
4. **Tope total de enlaces.** Rechazado: vuelve a dejar la cuenta sin salida.
5. **Una fila de auditoría por reenvío.** Rechazada: llenaría el historial con cada clic sin valor para el negocio.
6. **Respuestas distintas (404 sin cuenta, 429 dentro del intervalo).** Rechazadas: dirían qué correos tienen cuenta.
7. **Un limitador de peticiones por librería.** Fuera: no está en las dependencias, y el límite pedido es por cuenta.
8. **Devolver un `dict` sin `response_model`, como `verificar-email`.** Rechazada por David (AGENTS §3: un router
   devuelve schemas): sin schema nada limita qué claves salen ni las documenta. Las rutas que ya lo hacen son BE-65.

## Evidencia

- Verificación (19 nov): un solo emisor del token y una sola ruta que programa el correo (grep global); rincón 1 leído
  en el código; adenda con las decisiones 1 a 10.
- Plan: RED y GREEN de cada fase, compuerta completa y 33 mutantes medidos en copias del repositorio
  (`docs/deuda/BE-64/plan.md`).
- OWASP, Forgot Password Cheat Sheet, "Forgot Password Request": mensaje igual exista o no la cuenta, tiempo de
  respuesta uniforme y límite por cuenta contra envíos automatizados, sin cifra. Trata de la recuperación de
  contraseña: aplica por analogía.
- Supabase, tabla "Auth rate limits" de "Going into production": la petición de confirmación de registro se limita por
  la última petición, 60 segundos por defecto, configurable. Es el valor por defecto de un producto, no una norma;
  ninguna fuente leída fija 60 s como estándar.
- Fuentes leídas el 19 nov en el texto fuente que sirve Context7, no en la página publicada.
```

El Anexo A dice "33 mutantes" (cifra re-medida tras E0); si una enmienda cambia esa cifra, se cambia aquí antes de
la fase A.

## Anexos B a E — cambios exactos de cada fase

Son la salida literal de `git diff --no-index -U2` entre las copias de una fase y la siguiente (las que dieron los
GREEN de arriba; el Anexo E, de las copias re-medidas tras E0). El ejecutor aplica ese contenido; el auditor compara el diff de la fase con su anexo. Los saltos de
línea los decide el `ruff format` del hook; el contenido no cambia. La migración nueva es la excepción `(backlog
AF-18)`: queda como en el Anexo B, con comillas simples y el import de `alembic` antes que el de `sqlalchemy`.

### Anexo B — fase B

```diff
diff --git a/alembic/versions/a64d0c2e7f15_users_verification_sent_at.py b/alembic/versions/a64d0c2e7f15_users_verification_sent_at.py
new file mode 100644
index 0000000..2aba32d
--- /dev/null
+++ b/alembic/versions/a64d0c2e7f15_users_verification_sent_at.py
@@ -0,0 +1,38 @@
+"""users: verification_sent_at, when the last verification link was issued (BE-64)
+
+Revision ID: a64d0c2e7f15
+Revises: e50a7c3d9b12
+Create Date: 2026-11-19 18:00:00.000000
+
+"""
+from typing import Sequence, Union
+
+from alembic import op
+import sqlalchemy as sa
+
+
+# revision identifiers, used by Alembic.
+revision: str = 'a64d0c2e7f15'
+down_revision: Union[str, Sequence[str], None] = 'e50a7c3d9b12'
+branch_labels: Union[str, Sequence[str], None] = None
+depends_on: Union[str, Sequence[str], None] = None
+
+
+def upgrade() -> None:
+    """Adds users.verification_sent_at, NULL in every row (ADR-0023).
+
+    No row is filled: the time of a link sent before this column existed was never kept, and an
+    empty value lets that account ask for a new link at once, which is what a tourist whose link
+    expired needs. batch_alter_table emits a plain ALTER TABLE on PostgreSQL; on SQLite, where
+    the suite runs this function, adding a column needs no rebuild.
+    """
+    with op.batch_alter_table('users') as batch_op:
+        batch_op.add_column(
+            sa.Column('verification_sent_at', sa.DateTime(timezone=True), nullable=True)
+        )
+
+
+def downgrade() -> None:
+    """Drops users.verification_sent_at; SQLite rebuilds the table and keeps its rows."""
+    with op.batch_alter_table('users') as batch_op:
+        batch_op.drop_column('verification_sent_at')
diff --git a/app/models/user.py b/app/models/user.py
index de1fbdd..48cd9d8 100644
--- a/app/models/user.py
+++ b/app/models/user.py
@@ -57,2 +57,5 @@ class User(Base):
     # (BE-50, ADR-0022). Empty means the link was never used, not that the account is inactive.
     email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
+    # When the last verification link was issued: registration and every resend write it, so
+    # a new link waits the configured interval (BE-64, ADR-0023). Empty: no link on record.
+    verification_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
diff --git a/tests/test_migration_verification_sent_at.py b/tests/test_migration_verification_sent_at.py
new file mode 100644
index 0000000..33d83c4
--- /dev/null
+++ b/tests/test_migration_verification_sent_at.py
@@ -0,0 +1,94 @@
+"""Tests for the BE-64 migration: users.verification_sent_at is born empty (ADR-0023).
+
+The migration runs on a SQLite database of its own, as the one of ADR-0022 does in
+test_migration_email_verified_at.py: the accounts are written with the full schema, the downgrade
+removes the column and the upgrade adds it back, so the test reads what the upgrade leaves in
+existing rows. Empty means that no link is on record: the account may ask for one at once.
+"""
+
+import runpy
+from collections.abc import Iterator
+from datetime import UTC, datetime
+from pathlib import Path
+
+import pytest
+from alembic.migration import MigrationContext
+from alembic.operations import Operations
+from sqlalchemy import Connection, create_engine, inspect, text
+from sqlalchemy.orm import Session
+
+from app.db.database import Base
+from app.models.user import UserRole
+
+COLUMN = "verification_sent_at"
+MIGRATION = (
+    Path(__file__).resolve().parents[1]
+    / "alembic"
+    / "versions"
+    / "a64d0c2e7f15_users_verification_sent_at.py"
+)
+
+
+def _migrate(connection: Connection, step: str) -> None:
+    """Runs upgrade() or downgrade() of the migration under test, with its own op."""
+    migration = runpy.run_path(str(MIGRATION))
+    with Operations.context(MigrationContext.configure(connection)):
+        migration[step]()
+
+
+def _columns(connection: Connection) -> dict[str, bool]:
+    """Maps each column of users to whether it admits NULL."""
+    columns = inspect(connection).get_columns("users")
+    return {column["name"]: column["nullable"] for column in columns}
+
+
+@pytest.fixture
+def pre_migration_db(make_user) -> Iterator[Connection]:
+    """A SQLite database of its own with three accounts, on the schema before the migration.
+
+    A pending tourist, a verified tourist and an admin: the upgrade invents a send for none.
+    """
+    engine = create_engine("sqlite://")
+    with engine.connect() as connection:
+        Base.metadata.create_all(connection)
+        connection.commit()
+        with Session(connection) as session:
+            session.add_all(
+                [
+                    make_user(is_active=False),
+                    make_user(is_active=True, email_verified_at=datetime.now(UTC)),
+                    make_user(role=UserRole.admin, is_active=True),
+                ]
+            )
+            session.commit()
+        _migrate(connection, "downgrade")
+        connection.commit()
+        yield connection
+    engine.dispose()
+
+
+def test_migration_adds_the_column_empty_in_every_row(pre_migration_db: Connection) -> None:
+    """Happy path: the column comes back nullable and NULL in every row."""
+    assert COLUMN not in _columns(pre_migration_db)
+
+    _migrate(pre_migration_db, "upgrade")
+
+    assert _columns(pre_migration_db)[COLUMN] is True
+    rows = pre_migration_db.execute(text("SELECT verification_sent_at FROM users")).all()
+    assert [sent_at for (sent_at,) in rows] == [None, None, None]
+
+
+def test_migration_downgrade_drops_only_its_column_and_keeps_the_rows(
+    pre_migration_db: Connection,
+) -> None:
+    """Edge case: a filled send time goes away with its column; rows and verified mark stay."""
+    _migrate(pre_migration_db, "upgrade")
+    pre_migration_db.execute(text("UPDATE users SET verification_sent_at = CURRENT_TIMESTAMP"))
+
+    _migrate(pre_migration_db, "downgrade")
+
+    assert COLUMN not in _columns(pre_migration_db)
+    assert "email_verified_at" in _columns(pre_migration_db)
+    verified = "SELECT count(*) FROM users WHERE email_verified_at IS NOT NULL"
+    assert pre_migration_db.execute(text(verified)).scalar_one() == 1
+    assert pre_migration_db.execute(text("SELECT count(*) FROM users")).scalar_one() == 3
diff --git a/tests/test_models_schema.py b/tests/test_models_schema.py
index aae976e..f26f634 100644
--- a/tests/test_models_schema.py
+++ b/tests/test_models_schema.py
@@ -79,4 +79,5 @@ EXPECTED: dict[str, dict[str, FrozenColumn]] = {
         "deleted_at": FrozenColumn(TZ, nullable=True),
         "email_verified_at": FrozenColumn(TZ, nullable=True),
+        "verification_sent_at": FrozenColumn(TZ, nullable=True),
     },
     "tourist_services": {
```

### Anexo C — fase C

```diff
diff --git a/.env.example b/.env.example
index 8579089..4000dc2 100644
--- a/.env.example
+++ b/.env.example
@@ -21,4 +21,6 @@ ALGORITHM=HS256
 ACCESS_TOKEN_EXPIRE_MINUTES=30
 VERIFICATION_TOKEN_EXPIRE_MINUTES=15
+# Minimum seconds between two verification links to the same account.
+VERIFICATION_RESEND_INTERVAL_SECONDS=60
 
 # ==========================================
diff --git a/app/core/config.py b/app/core/config.py
index 38173b7..35cd82a 100644
--- a/app/core/config.py
+++ b/app/core/config.py
@@ -50,4 +50,6 @@ class Settings(DatabaseSettings):
     access_token_expire_minutes: int = 30
     verification_token_expire_minutes: int = 15
+    # Minimum wait between two verification links to one account (BE-64, ADR-0023).
+    verification_resend_interval_seconds: int = 60
 
     mail_username: str = Field(min_length=1)
diff --git a/conftest.py b/conftest.py
index ff2cd6d..7a65482 100644
--- a/conftest.py
+++ b/conftest.py
@@ -14,4 +14,5 @@ TEST_ENVIRONMENT = {
     "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
     "VERIFICATION_TOKEN_EXPIRE_MINUTES": "15",
+    "VERIFICATION_RESEND_INTERVAL_SECONDS": "60",
     "MAIL_USERNAME": "smtp-account@test.com",
     "MAIL_PASSWORD": "test-mail-password",
diff --git a/tests/test_config.py b/tests/test_config.py
index 131e0db..de1c8ab 100644
--- a/tests/test_config.py
+++ b/tests/test_config.py
@@ -37,4 +37,5 @@ OPTIONAL_DEFAULTS = {
     "access_token_expire_minutes": 30,
     "verification_token_expire_minutes": 15,
+    "verification_resend_interval_seconds": 60,
     "mail_from": None,
     "mail_port": 465,
@@ -126,4 +127,29 @@ def test_optional_variables_keep_their_current_defaults(monkeypatch: pytest.Monk
 
 
+def test_verification_resend_interval_is_read_in_seconds(
+    monkeypatch: pytest.MonkeyPatch,
+) -> None:
+    """Edge case: the minimum wait between two verification links comes from the environment."""
+    _set_required(monkeypatch)
+    monkeypatch.setenv("VERIFICATION_RESEND_INTERVAL_SECONDS", "90")
+
+    assert Settings(_env_file=None).verification_resend_interval_seconds == 90
+
+
+def test_verification_resend_interval_rejects_a_non_integer(
+    monkeypatch: pytest.MonkeyPatch,
+) -> None:
+    """Unhappy path: a wait that is not a whole number of seconds stops the app, naming it."""
+    _set_required(monkeypatch)
+    monkeypatch.setenv("VERIFICATION_RESEND_INTERVAL_SECONDS", "1m")
+
+    with pytest.raises(ValidationError) as exc_info:
+        Settings(_env_file=None)
+
+    assert [(e["type"], e["loc"]) for e in exc_info.value.errors()] == [
+        ("int_parsing", ("verification_resend_interval_seconds",))
+    ]
+
+
 def test_mail_sender_defaults_to_mail_username(monkeypatch: pytest.MonkeyPatch) -> None:
     """Edge case: with no mail_from, the sender is the SMTP account."""
@@ -231,5 +257,6 @@ def test_env_example_is_a_valid_configuration(monkeypatch: pytest.MonkeyPatch) -
         settings.access_token_expire_minutes,
         settings.verification_token_expire_minutes,
-    ) == ("HS256", 30, 15)
+        settings.verification_resend_interval_seconds,
+    ) == ("HS256", 30, 15, 60)
 
 
```

### Anexo D — fase D

```diff
diff --git a/app/repositories/user_repository.py b/app/repositories/user_repository.py
index b1b6e34..c31fa77 100644
--- a/app/repositories/user_repository.py
+++ b/app/repositories/user_repository.py
@@ -46,4 +46,32 @@ class UserRepository:
         return result.scalars().first()
 
+    async def get_tourist_due_a_verification_link(
+        self, email: str, sent_before: datetime
+    ) -> User | None:
+        """Finds the account that may receive a new email-verification link (ADR-0023).
+
+        A tourist, not soft-deleted, whose email is not verified yet, active or not, and whose
+        last link was issued at or before sent_before, or is not on record. Administrative
+        accounts never match: their sign-up and their retirement belong to a superadmin
+        (ADR-0019).
+
+        Args:
+            email (str): Lowercased address of the account.
+            sent_before (datetime): Latest issue time of the previous link that still allows a
+                new one: now minus the resend interval.
+
+        Returns:
+            User | None: The matching account, or None.
+        """
+        stmt = select(User).where(
+            User.email == email,
+            User.role == UserRole.tourist,
+            User.deleted_at.is_(None),
+            User.email_verified_at.is_(None),
+            or_(User.verification_sent_at.is_(None), User.verification_sent_at <= sent_before),
+        )
+        result = await self.db.execute(stmt)
+        return result.scalars().first()
+
     async def create_user(self, user: User) -> User:
         self.db.add(user)
diff --git a/app/services/user_service.py b/app/services/user_service.py
index 6e7d6ee..990c6e1 100644
--- a/app/services/user_service.py
+++ b/app/services/user_service.py
@@ -1,3 +1,3 @@
-from datetime import UTC, datetime
+from datetime import UTC, datetime, timedelta
 from typing import NamedTuple
 
@@ -44,4 +44,19 @@ class RegistrationResult(NamedTuple):
 
 
+class VerificationResend(NamedTuple):
+    """A new email-verification link for an account that still waits for one (BE-64).
+
+    The service picks the account and signs the token; the transport layer schedules the
+    email, as it does after a registration.
+
+    Attributes:
+        user (User): The tourist the link is for.
+        verification_token (str): The signed email-verification JWT.
+    """
+
+    user: User
+    verification_token: str
+
+
 class UserService:
     """Encapsulates the business rules, validations and operational logic of the User entity."""
@@ -63,4 +78,6 @@ class UserService:
         to the transport layer (the router's BackgroundTasks), while the
         service decides what to send (the token) and persists the account.
+        Registration counts as the first link sent: it stamps verification_sent_at, so a
+        resend waits the configured interval (ADR-0023).
 
         Args:
@@ -90,4 +107,5 @@ class UserService:
             data_consent=user_data.data_consent,
             is_active=False,
+            verification_sent_at=datetime.now(UTC),
         )
 
@@ -178,4 +196,34 @@ class UserService:
         }
 
+    async def resend_verification_link(self, email: str) -> VerificationResend | None:
+        """Issues a new email-verification link when the account may receive one now.
+
+        Only a non-deleted tourist whose email is not verified yet receives it, active or
+        inactive, and only once the resend interval has passed since its last link,
+        registration included. Any other address gets None, and the caller answers the same
+        either way, so the answer does not tell whether an account exists (ADR-0023). The
+        send time is operational data: stamping it writes no audit row.
+
+        Args:
+            email (str): Lowercased address the link is asked for.
+
+        Returns:
+            VerificationResend | None: The account and its new token, or None when no link
+                is due.
+        """
+        now = datetime.now(UTC)
+        interval = timedelta(seconds=get_settings().verification_resend_interval_seconds)
+        user = await self.user_repo.get_tourist_due_a_verification_link(
+            email, sent_before=now - interval
+        )
+        if user is None:
+            return None
+
+        user.verification_sent_at = now
+        await self.user_repo.save_user(user)
+        return VerificationResend(
+            user=user, verification_token=create_verification_token(user.email)
+        )
+
     async def authenticate_user(self, credentials: UserLogin) -> TokenResponse:
         """Authenticates credentials and issues an access token.
diff --git a/tests/test_user_repository.py b/tests/test_user_repository.py
index 9ce3827..5a9220a 100644
--- a/tests/test_user_repository.py
+++ b/tests/test_user_repository.py
@@ -1,5 +1,6 @@
-"""Tests for UserRepository.count_active_superadmins: which superadmins can sign in."""
+"""Tests for the UserRepository queries that decide who counts: which superadmins can sign in
+and which account may receive a new verification link (ADR-0023)."""
 
-from datetime import UTC, datetime
+from datetime import UTC, datetime, timedelta
 
 import pytest
@@ -40,2 +41,67 @@ async def test_count_active_superadmins_skips_those_who_cannot_sign_in(
 
     assert await UserRepository(db_session).count_active_superadmins() == 0
+
+
+# The cutoff a resend passes: now minus the interval, fixed here so the boundary is exact.
+SENT_BEFORE = datetime(2026, 11, 19, 12, 0, tzinfo=UTC)
+
+
+@pytest.mark.parametrize(
+    "overrides",
+    [
+        {"is_active": False},
+        {"is_active": True},
+        {"is_active": False, "verification_sent_at": SENT_BEFORE - timedelta(minutes=5)},
+        {"is_active": False, "verification_sent_at": SENT_BEFORE},
+    ],
+    ids=[
+        "inactive-never-sent",
+        "active-unverified",
+        "sent-before-the-cutoff",
+        "sent-at-the-cutoff",
+    ],
+)
+async def test_tourist_due_a_verification_link_is_found(db_session, persist_user, overrides):
+    """Happy path: a non-deleted, unverified tourist, active or not, past the interval."""
+    tourist = await persist_user(role=UserRole.tourist, **overrides)
+
+    found = await UserRepository(db_session).get_tourist_due_a_verification_link(
+        tourist.email, sent_before=SENT_BEFORE
+    )
+
+    assert found is tourist
+
+
+@pytest.mark.parametrize(
+    "overrides",
+    [
+        {"role": UserRole.admin, "is_active": False},
+        {"role": UserRole.superadmin, "is_active": False},
+        {"is_active": False, "deleted_at": SENT_BEFORE},
+        {"is_active": False, "email_verified_at": SENT_BEFORE},
+        {"is_active": False, "verification_sent_at": SENT_BEFORE + timedelta(microseconds=1)},
+    ],
+    ids=["admin", "superadmin", "soft-deleted", "verified", "sent-after-the-cutoff"],
+)
+async def test_account_not_due_a_verification_link_is_not_found(
+    db_session, persist_user, overrides
+):
+    """Unhappy path: administrative, deleted or verified accounts, or a link still too recent."""
+    account = await persist_user(**overrides)
+
+    found = await UserRepository(db_session).get_tourist_due_a_verification_link(
+        account.email, sent_before=SENT_BEFORE
+    )
+
+    assert found is None
+
+
+async def test_due_verification_link_lookup_matches_only_its_email(db_session, persist_user):
+    """Edge case: a tourist due a link is not returned for another address."""
+    await persist_user(role=UserRole.tourist, is_active=False)
+
+    found = await UserRepository(db_session).get_tourist_due_a_verification_link(
+        "otra@test.com", sent_before=SENT_BEFORE
+    )
+
+    assert found is None
diff --git a/tests/test_user_service.py b/tests/test_user_service.py
index 40f20eb..8587f9c 100644
--- a/tests/test_user_service.py
+++ b/tests/test_user_service.py
@@ -141,4 +141,17 @@ async def test_register_tourist_duplicate_raises_already_exists(user_repo, user_
 
 
+async def test_register_tourist_counts_as_the_first_link_sent(user_repo, user_service):
+    """Edge case: registration stamps the send time, so a resend waits (ADR-0023)."""
+    user_repo.get_user_by_email_or_cedula.return_value = None
+    user_repo.create_user.side_effect = lambda user: user
+    before = datetime.now(UTC)
+
+    result = await user_service.register_tourist(_tourist_payload())
+
+    sent_at = result.user.verification_sent_at
+    assert sent_at is not None
+    assert before <= sent_at <= datetime.now(UTC)
+
+
 # ==========================================
 # ORDER INVARIANT: 404 EXISTENCE BEFORE 403 HIERARCHY
@@ -410,4 +423,80 @@ async def test_verify_email_missing_user_raises_not_found(user_repo, audit_servi
 
 
+# ==========================================
+# VERIFICATION LINK RESEND (BE-64)
+# ==========================================
+
+RESEND_INTERVAL = timedelta(seconds=60)  # root conftest.py
+
+
+async def test_resend_issues_a_link_to_the_account_due_one(
+    user_repo, audit_service, user_service, make_user
+):
+    """Happy path: the account the query finds gets a new token and its send is stamped."""
+    user = make_user(email="turista@example.com", is_active=False)
+    user_repo.get_tourist_due_a_verification_link.return_value = user
+    before = datetime.now(UTC)
+
+    result = await user_service.resend_verification_link("turista@example.com")
+
+    assert result is not None
+    assert result.user is user
+    settings = get_settings()
+    claims = jwt.decode(
+        result.verification_token, settings.jwt_secret_key, algorithms=[settings.algorithm]
+    )
+    assert (claims["sub"], claims["scope"]) == ("turista@example.com", EMAIL_VERIFICATION_SCOPE)
+    sent_at = user.verification_sent_at
+    assert sent_at is not None
+    assert before <= sent_at <= datetime.now(UTC)
+    assert user.is_active is False
+    user_repo.get_tourist_due_a_verification_link.assert_awaited_once_with(
+        "turista@example.com", sent_before=sent_at - RESEND_INTERVAL
+    )
+    user_repo.save_user.assert_awaited_once_with(user)
+    audit_service.log_transaction.assert_not_awaited()
+
+
+async def test_resend_with_no_account_due_writes_nothing(user_repo, audit_service, user_service):
+    """Unhappy path: no account due a link, so no token, no write and no audit row."""
+    user_repo.get_tourist_due_a_verification_link.return_value = None
+
+    result = await user_service.resend_verification_link("nadie@example.com")
+
+    assert result is None
+    user_repo.get_tourist_due_a_verification_link.assert_awaited_once()
+    assert user_repo.get_tourist_due_a_verification_link.call_args.args == ("nadie@example.com",)
+    user_repo.save_user.assert_not_awaited()
+    audit_service.log_transaction.assert_not_awaited()
+
+
+async def test_resend_interval_comes_from_the_settings(
+    user_repo, user_service, monkeypatch: pytest.MonkeyPatch
+):
+    """Edge case: the cutoff is now minus the configured interval, not a fixed minute."""
+    monkeypatch.setattr(get_settings(), "verification_resend_interval_seconds", 300)
+    user_repo.get_tourist_due_a_verification_link.return_value = None
+    before = datetime.now(UTC)
+
+    await user_service.resend_verification_link("turista@example.com")
+
+    sent_before = user_repo.get_tourist_due_a_verification_link.call_args.kwargs["sent_before"]
+    interval = timedelta(seconds=300)
+    assert before - interval <= sent_before <= datetime.now(UTC) - interval
+
+
+async def test_resend_save_failure_propagates_without_a_link(
+    user_repo, audit_service, user_service, make_user
+):
+    """Unhappy path: if the send time cannot be saved, the error surfaces and no link leaves."""
+    user_repo.get_tourist_due_a_verification_link.return_value = make_user(is_active=False)
+    user_repo.save_user.side_effect = OperationalError("UPDATE users", {}, Exception("db down"))
+
+    with pytest.raises(OperationalError):
+        await user_service.resend_verification_link("turista@example.com")
+
+    audit_service.log_transaction.assert_not_awaited()
+
+
 # ==========================================
 # ADMINISTRATIVE PROVISIONING
```

### Anexo E — fase E (re-medido tras E0)

```diff
diff --git a/app/api/routers/user.py b/app/api/routers/user.py
index ed616f8..d630362 100644
--- a/app/api/routers/user.py
+++ b/app/api/routers/user.py
@@ -12,6 +12,14 @@ from app.api.dependencies import (
 from app.core.config import Settings, get_settings
 from app.core.email import send_verification_email
+from app.schemas.message import MessageResponse
 from app.schemas.token import TokenResponse
-from app.schemas.user import UserCreate, UserCreateByAdmin, UserLogin, UserResponse, UserUpdate
+from app.schemas.user import (
+    UserCreate,
+    UserCreateByAdmin,
+    UserLogin,
+    UserResponse,
+    UserUpdate,
+    VerificationResendRequest,
+)
 from app.services.user_service import UserService
 
@@ -31,4 +39,12 @@ from app.services.user_service import UserService
 
 public_router = APIRouter()
+
+# The resend answers this whether or not a link left, so it never tells whether an account
+# exists (BE-64, ADR-0023).
+RESEND_VERIFICATION_MESSAGE = (
+    "Si su correo tiene una cuenta pendiente de verificación, le acabamos de enviar un nuevo "
+    "enlace. Revise su bandeja de entrada y la carpeta de correo no deseado. Si ya pidió uno "
+    "hace poco, espere un minuto antes de intentarlo de nuevo."
+)
 self_service_router = APIRouter(dependencies=[Depends(get_current_user)])
 admin_router = APIRouter(dependencies=[Depends(get_current_admin_user)])
@@ -96,4 +112,42 @@ async def verificar_cuenta(token: str, user_service: UserService = Depends(get_u
 
 
+@public_router.post(
+    "/reenviar-verificacion", response_model=MessageResponse, status_code=status.HTTP_200_OK
+)
+async def resend_verification_email(
+    body: VerificationResendRequest,
+    background_tasks: BackgroundTasks,
+    user_service: UserService = Depends(get_user_service),
+    settings: Settings = Depends(get_settings),
+) -> dict[str, bool | str]:
+    """Public endpoint: emails a new verification link to an account still waiting for one.
+
+    The service decides whether a link is due (a non-deleted, unverified tourist past the
+    resend interval) and signs it; the email leaves as a background task, as after a
+    registration. The answer is the same in every case (ADR-0023); MessageResponse, the
+    response_model, documents it and lets no other key out.
+
+    Args:
+        body (VerificationResendRequest): The address the link is asked for.
+        background_tasks (BackgroundTasks): Starlette task queue for email dispatch.
+        user_service (UserService): Injected business-logic service.
+        settings (Settings): Injected configuration; frontend_url is the base of the emailed link.
+
+    Returns:
+        dict: Success flag and the message to show, identical whether or not a link left.
+    """
+    resend = await user_service.resend_verification_link(body.email)
+    if resend is not None:
+        background_tasks.add_task(
+            send_verification_email,
+            email_to=resend.user.email,
+            first_name=resend.user.first_name,
+            token=resend.verification_token,
+            base_url=settings.frontend_url.rstrip("/"),
+        )
+
+    return {"success": True, "message": RESEND_VERIFICATION_MESSAGE}
+
+
 @public_router.post("/login", response_model=TokenResponse)
 async def login(credenciales: UserLogin, user_service: UserService = Depends(get_user_service)):
diff --git a/app/schemas/message.py b/app/schemas/message.py
new file mode 100644
index 0000000..4c114a9
--- /dev/null
+++ b/app/schemas/message.py
@@ -0,0 +1,16 @@
+from pydantic import BaseModel
+
+
+class MessageResponse(BaseModel):
+    """Body of the routes that answer with a success flag and a message to show (BE-64).
+
+    Declared on BaseModel with no validators: an output DTO never re-applies input rules
+    (backlog A9). The shape is not specific to users, so it lives in its own module.
+
+    Attributes:
+        success: Whether the request was handled.
+        message: Text for the end user.
+    """
+
+    success: bool
+    message: str
diff --git a/app/schemas/user.py b/app/schemas/user.py
index d254dfd..3ba2f30 100644
--- a/app/schemas/user.py
+++ b/app/schemas/user.py
@@ -138,4 +138,13 @@ class UserLogin(BaseModel):
 
 
+class VerificationResendRequest(BaseModel):
+    """Body of the request for a new email-verification link (BE-64).
+
+    Only the address: the answer is the same whether or not it names an account (ADR-0023).
+    """
+
+    email: LowercaseEmail
+
+
 class UserResponse(BaseModel):
     """Serialized view of a stored user account.
diff --git a/tests/test_route_guards.py b/tests/test_route_guards.py
index ecaf4b1..039299b 100644
--- a/tests/test_route_guards.py
+++ b/tests/test_route_guards.py
@@ -80,4 +80,5 @@ PUBLIC_ROUTES: frozenset[tuple[str, str]] = frozenset(
         ("POST", "/usuarios/registro"),
         ("GET", "/usuarios/verificar-email"),
+        ("POST", "/usuarios/reenviar-verificacion"),
         ("POST", "/usuarios/login"),
         ("GET", "/servicios/"),
@@ -95,4 +96,5 @@ _ANONYMOUS_ON_PUBLIC_ROUTE: dict[tuple[str, str], int] = {
     ("POST", "/usuarios/registro"): 422,
     ("GET", "/usuarios/verificar-email"): 422,
+    ("POST", "/usuarios/reenviar-verificacion"): 422,
     ("POST", "/usuarios/login"): 422,
     ("GET", "/servicios/"): 200,
diff --git a/tests/test_verification_resend.py b/tests/test_verification_resend.py
new file mode 100644
index 0000000..018a151
--- /dev/null
+++ b/tests/test_verification_resend.py
@@ -0,0 +1,260 @@
+"""HTTP tests for POST /usuarios/reenviar-verificacion (BE-64, ADR-0023).
+
+The route answers 200 with the same body whether or not a link leaves, so each case that sends
+nothing compares its body with the one a pending tourist gets. The email double is the autouse
+mock_send_email of tests/conftest.py: a link left when, and only when, it was called.
+"""
+
+from datetime import UTC, datetime, timedelta
+from typing import Any
+from unittest.mock import ANY
+
+import jwt
+import pytest
+from sqlalchemy import select
+
+from app.core.config import get_settings
+from app.core.security import EMAIL_VERIFICATION_SCOPE
+from app.main import app
+from app.models.audit import AuditLog
+from app.models.user import UserRole
+
+URL = "/usuarios/reenviar-verificacion"
+FRONTEND_URL = "http://localhost:3000"  # root conftest.py
+LONG_AGO = datetime(2026, 11, 1, tzinfo=UTC)
+
+# Accounts that get no link. "sent_seconds_ago" becomes verification_sent_at in the test itself,
+# so the clock it measures from is the request's, not the collection's.
+NOT_DUE: dict[str, dict[str, Any]] = {
+    "admin": {"role": UserRole.admin, "is_active": False},
+    "superadmin": {"role": UserRole.superadmin, "is_active": False},
+    "soft-deleted-tourist": {"is_active": False, "deleted_at": LONG_AGO},
+    "verified-tourist": {"is_active": True, "email_verified_at": LONG_AGO},
+    "verified-tourist-deactivated": {"is_active": False, "email_verified_at": LONG_AGO},
+    "link-sent-59-seconds-ago": {"is_active": False, "sent_seconds_ago": 59},
+}
+
+
+def _claims(token: str) -> dict[str, Any]:
+    """Decodes a token with the app's key, as the verification link does."""
+    settings = get_settings()
+    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.algorithm])
+
+
+def _sent_seconds_ago(overrides: dict[str, Any]) -> dict[str, Any]:
+    """Turns the "sent_seconds_ago" key of a case into a verification_sent_at from now."""
+    overrides = dict(overrides)
+    seconds = overrides.pop("sent_seconds_ago", None)
+    if seconds is not None:
+        overrides["verification_sent_at"] = datetime.now(UTC) - timedelta(seconds=seconds)
+    return overrides
+
+
+async def test_pending_tourist_gets_a_new_link(client, db_session, persist_user, mock_send_email):
+    """Happy path: an inactive, unverified tourist gets a link; nothing else changes."""
+    tourist = await persist_user(is_active=False)
+
+    response = await client.post(URL, json={"email": tourist.email})
+
+    assert response.status_code == 200
+    body = response.json()
+    assert set(body) == {"success", "message"}
+    assert body["success"] is True
+    mock_send_email.assert_called_once_with(
+        email_to=tourist.email, first_name=tourist.first_name, token=ANY, base_url=FRONTEND_URL
+    )
+    claims = _claims(mock_send_email.call_args.kwargs["token"])
+    assert (claims["sub"], claims["scope"]) == (tourist.email, EMAIL_VERIFICATION_SCOPE)
+    await db_session.refresh(tourist)
+    assert tourist.verification_sent_at is not None
+    assert tourist.is_active is False
+    assert tourist.email_verified_at is None
+    assert (await db_session.execute(select(AuditLog))).scalars().all() == []
+
+
+async def test_the_new_link_verifies_the_account(client, db_session, persist_user, mock_send_email):
+    """Happy path: the emailed token is a working verification link."""
+    tourist = await persist_user(is_active=False)
+    await client.post(URL, json={"email": tourist.email})
+    token = mock_send_email.call_args.kwargs["token"]
+
+    response = await client.get(f"/usuarios/verificar-email?token={token}")
+
+    assert response.status_code == 200
+    await db_session.refresh(tourist)
+    assert tourist.is_active is True
+    assert tourist.email_verified_at is not None
+
+
+@pytest.mark.parametrize("overrides", NOT_DUE.values(), ids=NOT_DUE.keys())
+async def test_account_not_due_a_link_gets_the_same_answer_and_no_email(
+    client, db_session, persist_user, mock_send_email, overrides
+):
+    """Unhappy path: no link and no write, and the body is the one a pending tourist gets."""
+    pending = await persist_user(is_active=False)
+    account = await persist_user(**_sent_seconds_ago(overrides))
+    before = (account.is_active, account.email_verified_at, account.verification_sent_at)
+
+    expected = await client.post(URL, json={"email": pending.email})
+    response = await client.post(URL, json={"email": account.email})
+
+    assert expected.status_code == response.status_code == 200
+    assert response.json() == expected.json()
+    mock_send_email.assert_called_once_with(
+        email_to=pending.email, first_name=ANY, token=ANY, base_url=ANY
+    )
+    await db_session.refresh(account)
+    assert (account.is_active, account.email_verified_at, account.verification_sent_at) == before
+
+
+async def test_unknown_email_gets_the_same_answer_and_no_email(
+    client, persist_user, mock_send_email
+):
+    """Unhappy path: an address with no account answers as a pending tourist's does."""
+    pending = await persist_user(is_active=False)
+
+    expected = await client.post(URL, json={"email": pending.email})
+    response = await client.post(URL, json={"email": "nadie@example.com"})
+
+    assert expected.status_code == response.status_code == 200
+    assert response.json() == expected.json()
+    mock_send_email.assert_called_once_with(
+        email_to=pending.email, first_name=ANY, token=ANY, base_url=ANY
+    )
+
+
+async def test_tourist_an_admin_activated_without_verifying_gets_a_link(
+    client, db_session, persist_user, mock_send_email
+):
+    """Edge case: an active tourist whose mark is empty gets a link and stays active."""
+    tourist = await persist_user(is_active=True)
+
+    response = await client.post(URL, json={"email": tourist.email})
+
+    assert response.status_code == 200
+    mock_send_email.assert_called_once_with(
+        email_to=tourist.email, first_name=tourist.first_name, token=ANY, base_url=FRONTEND_URL
+    )
+    await db_session.refresh(tourist)
+    assert tourist.is_active is True
+    assert tourist.email_verified_at is None
+
+
+async def test_registration_counts_as_the_first_link(client, mock_send_email):
+    """Edge case: right after registering, a resend sends nothing more."""
+    payload = {
+        "cedula": "1005911792",
+        "email": "turista@example.com",
+        "first_name": "Juan",
+        "last_name": "Perez",
+        "phone": "3001234567",
+        "password": "passwordSegura123",
+        "data_consent": True,
+    }
+    registered = await client.post("/usuarios/registro", json=payload)
+
+    response = await client.post(URL, json={"email": payload["email"]})
+
+    assert (registered.status_code, response.status_code) == (201, 200)
+    mock_send_email.assert_called_once_with(
+        email_to="turista@example.com", first_name="Juan", token=ANY, base_url=FRONTEND_URL
+    )
+
+
+async def test_second_request_within_the_interval_sends_nothing(
+    client, db_session, persist_user, mock_send_email
+):
+    """Edge case: two requests in a row send one link and keep the first send time."""
+    tourist = await persist_user(is_active=False)
+
+    first = await client.post(URL, json={"email": tourist.email})
+    await db_session.refresh(tourist)
+    sent_at = tourist.verification_sent_at
+    second = await client.post(URL, json={"email": tourist.email})
+
+    assert first.status_code == second.status_code == 200
+    assert first.json() == second.json()
+    mock_send_email.assert_called_once()
+    await db_session.refresh(tourist)
+    assert sent_at is not None
+    assert tourist.verification_sent_at == sent_at
+
+
+async def test_link_is_sent_again_once_the_interval_passed(
+    client, db_session, persist_user, mock_send_email
+):
+    """Edge case: 61 seconds after the last link, a new one leaves and the time moves on."""
+    tourist = await persist_user(
+        is_active=False, verification_sent_at=datetime.now(UTC) - timedelta(seconds=61)
+    )
+    previous = tourist.verification_sent_at
+    assert previous is not None
+
+    response = await client.post(URL, json={"email": tourist.email})
+
+    assert response.status_code == 200
+    mock_send_email.assert_called_once()
+    await db_session.refresh(tourist)
+    assert tourist.verification_sent_at is not None
+    assert tourist.verification_sent_at > previous
+
+
+async def test_email_is_matched_in_lowercase(client, persist_user, mock_send_email):
+    """Edge case: the address is lowered before the lookup, as every email input (ADR-0016)."""
+    tourist = await persist_user(is_active=False, email="turista@example.com")
+
+    response = await client.post(URL, json={"email": "Turista@EXAMPLE.com"})
+
+    assert response.status_code == 200
+    mock_send_email.assert_called_once_with(
+        email_to=tourist.email, first_name=tourist.first_name, token=ANY, base_url=FRONTEND_URL
+    )
+
+
+@pytest.mark.parametrize(
+    "payload",
+    [{"email": "no-es-un-correo"}, {"email": None}, {}],
+    ids=["malformed", "null", "missing"],
+)
+async def test_invalid_body_is_422_and_sends_nothing(
+    client, persist_user, mock_send_email, payload
+):
+    """Unhappy path: a body that is not one address is rejected before any lookup."""
+    await persist_user(is_active=False, email="turista@example.com")
+
+    response = await client.post(URL, json=payload)
+
+    assert response.status_code == 422
+    assert [error["raw_field"] for error in response.json()["detalle"]] == ["email"]
+    mock_send_email.assert_not_called()
+
+
+async def test_link_is_built_from_frontend_url(client, persist_user, mock_send_email):
+    """Edge case: the link base is the injected frontend_url, without its trailing slash."""
+    settings = get_settings().model_copy(update={"frontend_url": "https://front.example/"})
+    app.dependency_overrides[get_settings] = lambda: settings
+    tourist = await persist_user(is_active=False)
+
+    response = await client.post(URL, json={"email": tourist.email})
+
+    assert response.status_code == 200
+    mock_send_email.assert_called_once_with(
+        email_to=tourist.email,
+        first_name=tourist.first_name,
+        token=ANY,
+        base_url="https://front.example",
+    )
+
+
+async def test_route_declares_its_response_schema(client):
+    """Edge case: the 200 answer is MessageResponse in the OpenAPI, two required keys, no more."""
+    spec = (await client.get("/openapi.json")).json()
+
+    answer = spec["paths"][URL]["post"]["responses"]["200"]["content"]["application/json"]
+    assert answer["schema"] == {"$ref": "#/components/schemas/MessageResponse"}
+    schema = spec["components"]["schemas"]["MessageResponse"]
+    assert {name: field.get("type") for name, field in schema["properties"].items()} == {
+        "success": "boolean",
+        "message": "string",
+    }
+    assert sorted(schema["required"]) == ["message", "success"]
```

## Enmiendas aprobadas

### E0 — 19 nov 2026, 19:10 (decisiones de David sobre la revisión de la sesión Mentor; no es la aprobación del plan)

El plan **no queda aprobado con esta enmienda**: el punto 2 cambia la fase E y el texto del Anexo A, así que ninguna
fase se ejecuta hasta que el planificador lo recalcule, lo mida y David lo apruebe (será E1). Donde el plan y esta
enmienda difieran, rige la enmienda.

1. **La ruta queda en español: `POST /usuarios/reenviar-verificacion`** (decisión 8 del plan, confirmada). Razón de
   David: el ítem que unifica el idioma `(backlog P2)` está en `B-FUTURO`; si no se hace nunca, una sola ruta en inglés
   entre todas las demás en español haría la asimetría más evidente. AGENTS §4 (b) exceptúa del inglés "las rutas
   públicas ya existentes" y esta es nueva: se declara aquí y en el ADR que sigue a sus vecinas a sabiendas. El
   manejador sigue en inglés (`resend_verification_email`).
2. **La ruta nace con schema de salida** (decisión 8 del plan, **cambiada por David**; el plan devolvía un `dict` sin
   `response_model`, como `verificar-email`). AGENTS §3: un router devuelve schemas Pydantic. El planificador recalcula
   la fase E:
   - un DTO de salida con exactamente `success: bool` y `message: str`, declarado como `response_model` de la ruta;
     nombre y archivo, del planificador (el residual R3 proponía `MessageResponse`); no hereda de ningún DTO de
     entrada ni lleva validadores (AGENTS §3, A9); el cuerpo de la respuesta no cambia;
   - al menos un test que caiga si se quita el `response_model` (por ejemplo, el esquema de la respuesta 200 en
     `/openapi.json`, o una clave de más que el schema filtra), con su mutante;
   - RED y GREEN de la fase E, compuerta completa y mutantes, medidos otra vez en copias `git archive`; cifras de la
     tabla "Qué se midió", de la fase E y de la Verificación final; lista de archivos del comando 14 si cambia;
   - el Anexo A (ADR-0023): decisión 1 con el schema, la nota de AGENTS §4 (b) del punto 1 y la cifra de mutantes;
   - el residual R3 deja de proponer una fila: las demás rutas sin `response_model` son `(backlog BE-65)`, que entra
     en el mismo bloque por decisión de David; y el contrato del residual R7, si cambia.
   Las fases A a D no cambian por este punto, salvo el texto del ADR que escribe la fase A.
3. **Si Windows bloquea la librería de import-linter** `(backlog AF-17)`. Solo si al correr la compuerta el paso
   import-linter falla con `ImportError: DLL load failed while importing _rustgrimp` (política de Application
   Control), y solo en esta máquina: la compuerta se corre con `--soft imports` y la fase se acepta si se cumplen las
   cuatro condiciones de la E1 de BE-50 (`docs/deuda/BE-50/plan.md`, E1): salida 0; RESUMEN impreso; el único paso en
   rojo es import-linter; y su salida contiene ese `ImportError`. Si el paso llega a evaluar contratos, se exige
   `Contracts: 4 kept, 0 broken.` sin `--soft`. El handoff copia la salida literal. Los contratos del commit de esa
   fase los mide la sesión Mentor en Linux antes de la fase siguiente, y el CI del PR con la compuerta estricta. Si
   el bloqueo no aparece, este punto no aplica y la compuerta se corre como dice AGENTS §6.
4. **La prueba contra PostgreSQL pasa de recomendada a exigida, antes de `/pr`** (paso humano de la Verificación
   final). La corre David con la API local sobre su PostgreSQL, tras los pasos de `alembic` de la fase B: (a) para un
   turista pendiente, dos `POST /usuarios/reenviar-verificacion` seguidos: los dos responden 200 con el mismo cuerpo y
   sale **un** solo correo; (b) pasado el intervalo, un tercero: sale el segundo correo y `verification_sent_at`
   avanza; (c) justo después de un registro nuevo, un reenvío no envía nada. Es lo único que la suite no ve: SQLite
   compara la hora como texto y PostgreSQL como `timestamptz`, y esta vez no hay comprobación en el cliente que lo
   cubra (FE-18). La salida va a la bitácora.
5. **Sin acción, anotado para la auditoría de la fase D:** `test_resend_interval_comes_from_the_settings` cambia el
   intervalo con `monkeypatch.setattr` sobre el `Settings` en caché; funciona y se restaura, pero ADR-0013
   (Consecuencias) no lista esa forma y ningún test la usa hoy (`grep "monkeypatch.setattr(get_settings()" tests`:
   0). No se cambia.
6. **Qué contrastó la sesión Mentor y qué no.** Leído el plan entero contra la adenda y el código de `22328ce`: las
   diez decisiones respetadas; valores "de hoy" de la Verificación final comprobados con `grep` (2 emisores, 3
   `commit()`, 6 `log_transaction`, 10 líneas con `email_verified_at`, 1 con `resend`); `expire_on_commit=False` en
   las dos fábricas de sesiones (`app/db/database.py:17`, `tests/conftest.py:31`), así que leer `resend.user` tras el
   `commit()` no falla. **No se ejecutó nada:** las mediciones son las del planificador, en Windows.

### E1 — 19 nov 2026, 19:37 (David: "listo, apruebo"; contraste de la sesión Mentor sobre la re-medición)

1. **Plan aprobado, cinco fases, con la fase E recalculada tras E0, y ADR-0023 aceptado** con el texto del Anexo A.
   `<FECHA DE APROBACIÓN>` = `19 nov 2026`. La aprobación se da también en la sesión de Claude Code, remitiendo a la
   cabecera, a E0 y a E1.
2. **Contraste de la re-medición.** El planificador aplicó solo E0.2: `MessageResponse` en `app/schemas/message.py`,
   `response_model` en la ruta, `test_route_declares_its_response_schema` y los mutantes ME6 a ME9; estado final
   `845 passed` · 98,73 % · mypy 0 en 70 · 4 kept · 33 mutantes muertos. La sesión Mentor leyó el diff entero contra
   `be9d385` y rehízo a mano los conteos de la Verificación final sobre el texto de los anexos (4 menciones de
   `MessageResponse` en `app` y 3 en `tests`; 18 archivos en el comando 15; 13 menciones de ADR-0023 y 10 de BE-64;
   5 + 4 + 15 + 9 = 33 mutantes). E0, la línea `Estado` y las fases A a D, sin tocar. **No ejecutó nada.**
3. **Pruebas contra el PostgreSQL local: tres momentos, los tres de David y los tres obligatorios.** Ningún agente los
   corre (Alembic y la API leen el `.env`, que un agente no lee) y ninguna fase los sustituye con SQLite. La salida
   literal de cada uno va a la bitácora del día. Los comandos van en la sintaxis de `cmd`, desde
   `C:\projects\ecotur-asoprado`.
   - **Momento 1, antes de `/implementar BE-64 B`:** `venv\Scripts\python.exe -m alembic current` debe dar
     `e50a7c3d9b12 (head)` y `venv\Scripts\python.exe -m alembic check` debe dar `No new upgrade operations
     detected.`. Es la medición de antes (ADR-0010, punto 7). Si no da eso, la fase B no empieza.
   - **Momento 2, después de la auditoría de la fase B y antes de `/implementar BE-64 D`** (la fase C puede correr
     entre medias): los cuatro comandos de `alembic` y las dos consultas de "Después del commit" de la fase B, con los
     resultados que allí se dan (`Running upgrade e50a7c3d9b12 -> a64d0c2e7f15`; `check` sin operaciones;
     `downgrade -1`; `upgrade head`; la columna `timestamp with time zone | YES`; 0 filas con la columna llena). Si
     `check` lista operaciones, el ítem se detiene. La fase D tiene esta salida como requisito previo.
   - **Momento 3, después de la auditoría de la fase E y antes de `/pr`.** Sustituye a la frase "Recomendado, no
     exigido" de la Verificación final, que deja de regir (E0, punto 4). Con la API de la rama levantada en local
     sobre el PostgreSQL local ya migrado, y un buzón que David pueda abrir, en este orden:
     1. `POST /usuarios/registro` con una cuenta nueva: 201 y llega **un** correo.
     2. Enseguida, `POST /usuarios/reenviar-verificacion` con ese correo: 200 con el cuerpo de siempre y **ningún**
        correo nuevo (el registro cuenta como envío).
     3. `SELECT email, is_active, email_verified_at, verification_sent_at FROM users WHERE email = '<ese correo>';`
        y se anota la hora de `verification_sent_at` (T1).
     4. Pasados más de 60 segundos, el mismo `POST`: 200 con el mismo cuerpo y llega el **segundo** correo; la
        consulta del paso 3 da una hora posterior (T2 > T1).
     5. Enseguida, otro `POST`: 200 con el mismo cuerpo, ningún correo y la hora sigue en T2.
     6. Se usa el enlace del **segundo** correo (desde el cliente, o con `GET /usuarios/verificar-email?token=…`): la
        consulta da `is_active` verdadero y `email_verified_at` llena.
     7. Otro `POST` con ese correo, pasado el minuto: 200 con el mismo cuerpo y ningún correo (ya está verificado).
     8. Un `POST` con un correo que no tiene cuenta: 200 con el mismo cuerpo y ningún correo.
     9. En el historial de auditoría, esa cuenta tiene solo su `CREATE` y el `UPDATE` de `is_active` del paso 6:
        ninguna fila por los reenvíos.
     Lo que esto prueba y la suite no puede: la comparación de la hora en PostgreSQL (`timestamptz` contra un
     parámetro con zona); en SQLite, donde corre la suite, es una comparación de texto. Si algún paso da otra cosa,
     no hay `/pr`: se anota en la bitácora con la salida y vuelve al flujo como hallazgo.
4. **Lo demás de E0 sigue vigente:** la ruta en español (punto 1), la cláusula por si Windows bloquea
   `_rustgrimp` (punto 3) y la observación sin acción sobre `monkeypatch.setattr` (punto 5).
5. **`progress.json`:** el planificador cambió la descripción de la fase E; nada más depende de E1.

### E2 — 27 nov 2026, 10:51 (David: addendum a ADR-0013 por el test que cambia el `Settings` en caché)

Sustituye al punto 5 de E0 ("sin acción"). Donde el plan y esta enmienda difieran, rige la enmienda.

1. **ADR-0013 recibe un addendum** (`docs/adr/0013-configuracion-centralizada-con-pydantic-settings.md`, al final;
   regla de ADR-0009). Decisión de David (10:51, sus palabras): "quiero el addendum solo en este caso que no se pueden
   usar las otras 3 alternativas, dejando debidamente declarados aquellos riesgos aceptados". El addendum admite
   `monkeypatch.setattr(get_settings(), "<campo>", <valor>)` solo para un consumidor sin petición que llama a
   `get_settings()` por dentro, y declara tres riesgos aceptados. Lo escribe la sesión Mentor y lo commitea David
   antes de `/implementar BE-64 D`; ningún agente lo toca.
2. **El código y los tests del Anexo D no cambian:** `test_resend_interval_comes_from_the_settings` queda como está
   dictado. Tampoco cambian los conteos de RED y GREEN, los mutantes ni los comandos 1 a 14 y 16 de la Verificación
   final (el 13 cuenta menciones solo en archivos `.py`).
3. **Comando 15 de la Verificación final: 19 archivos, no 18.** Su ruta incluye `docs/adr`, así que la lista gana
   `docs/adr/0013-configuracion-centralizada-con-pydantic-settings.md`. Los otros 18 son los que da el plan.
4. **Para la auditoría de la fase D:** el test nombrado usa `monkeypatch.setattr` sobre `get_settings()`, como admite
   el addendum, y ningún otro test de la fase cambia la configuración por esa vía (`grep -rn
   "monkeypatch.setattr(get_settings()" tests` → 1 tras la fase D).
5. **`progress.json`:** nada en él depende de E2.
6. **Qué midió la sesión Mentor y qué no.** Leído: `app/core/config.py:30-35` (`model_config` sin `frozen` y sin
   `validate_assignment`), `:101-102` (`get_settings` con `lru_cache`), `conftest.py:16` (60 en la suite),
   `constraints.txt` y `pyproject.toml` (sin `pytest-xdist`), y el texto del test en el Anexo D. **No ejecutó nada:**
   que el test pasa y restaura el valor es medición del planificador (fila "D GREEN").
