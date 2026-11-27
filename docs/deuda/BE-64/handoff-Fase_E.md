# Handoff — BE-64 · Fase E (la ruta pública de reenvío)

- **Commit de la fase:** `2b6db40` — `feat(auth): add the public route that resends the verification link` (mensaje
  exacto del plan, fase E, `plan.md:374-398`, extraído con `sed` sin reescribirlo; el cuerpo crudo del commit,
  `git cat-file commit HEAD`, sale idéntico con `diff`).
- **Rama:** `item/be-64`. HEAD al arrancar: `a6d1b8a` (árbol limpio). **Base develop:** `b6a80ba` (`git fetch origin`
  correcto; `git rev-parse --short origin/develop` y `git rev-parse --short $(git merge-base HEAD origin/develop)` =
  `b6a80ba`, igual a `verificacion.md`).
- **Enmiendas aplicadas:** E0 (punto 2: `MessageResponse` como `response_model`; punto 1: la ruta en español,
  AGENTS §4 (b), manejador en inglés), E1 y E2 (comando 15 = 19 archivos). No se tocó `plan.md` ni ningún ADR.
- **Compuerta:** `./venv/Scripts/python.exe scripts/check.py`, sin `--soft`. Windows no bloqueó `_rustgrimp`: E0,
  punto 3, no aplicó.

## Archivos tocados (5, los del plan)
- `app/schemas/message.py` (nuevo): `MessageResponse` con `success: bool` y `message: str`, sobre `BaseModel`, sin
  validadores.
- `app/schemas/user.py`: `VerificationResendRequest` (`email: LowercaseEmail`) tras `UserLogin`.
- `app/api/routers/user.py`: import de `MessageResponse`; import de `app.schemas.user` en varias líneas;
  `RESEND_VERIFICATION_MESSAGE` tras `public_router`; `resend_verification_email` con
  `response_model=MessageResponse` y `status.HTTP_200_OK` antes de `login`.
- `tests/test_route_guards.py`: la ruta en `PUBLIC_ROUTES` y en `_ANONYMOUS_ON_PUBLIC_ROUTE` (422) (ADR-0012, punto 4).
- `tests/test_verification_resend.py` (nuevo): los 19 casos del Anexo E.

Igualdad con el Anexo E: el diff se aplicó con `git apply` desde `plan.md:1163-1560` (primero
`--include='tests/*'` para el RED, luego `--include='app/*'`). Preimágenes comprobadas antes de aplicar
(`ed616f8`, `d254dfd`, `ecaf4b1`). Los cinco blobs del commit son `d630362`, `4c114a9`, `3ba2f30`, `039299b` y
`018a151`, los de las líneas `index` del Anexo E; `git diff --cached -U2` comparado con `diff` contra el Anexo sale
idéntico, con y sin las líneas `index`. `git apply` no pasa por el hook de formato (AF-18);
`ruff format --check` sobre los cinco: `5 files already formatted`.

## Diff (`git show --stat 2b6db40`)
```
 app/api/routers/user.py           |  56 +++++++-
 app/schemas/message.py            |  16 +++
 app/schemas/user.py               |   9 ++
 tests/test_route_guards.py        |   2 +
 tests/test_verification_resend.py | 260 ++++++++++++++++++++++++++++++++++++++
 5 files changed, 342 insertions(+), 1 deletion(-)
```

## Compuerta de arranque (antes de tocar nada)
Exit 0. `73 files already formatted` · `All checks passed!` · `Success: no issues found in 68 source files` ·
`Contracts: 4 kept, 0 broken.` · `825 passed, 25 warnings in 32.12s` · `TOTAL 1087 10 158 6 98.71%` ·
`Compuerta superada.` Igual al estado de salida de la fase D.

## RED (solo los dos archivos de test, sin `app/`)
`./venv/Scripts/python.exe -m pytest -q -p no:cacheprovider`, literal (bloque de resumen y conteo):
```
FAILED tests/test_route_guards.py::test_every_route_is_listed_as_protected_or_public
FAILED tests/test_route_guards.py::test_public_route_answers_without_token[POST /usuarios/reenviar-verificacion]
FAILED tests/test_verification_resend.py::test_pending_tourist_gets_a_new_link
FAILED tests/test_verification_resend.py::test_the_new_link_verifies_the_account
FAILED tests/test_verification_resend.py::test_account_not_due_a_link_gets_the_same_answer_and_no_email[admin]
FAILED tests/test_verification_resend.py::test_account_not_due_a_link_gets_the_same_answer_and_no_email[superadmin]
FAILED tests/test_verification_resend.py::test_account_not_due_a_link_gets_the_same_answer_and_no_email[soft-deleted-tourist]
FAILED tests/test_verification_resend.py::test_account_not_due_a_link_gets_the_same_answer_and_no_email[verified-tourist]
FAILED tests/test_verification_resend.py::test_account_not_due_a_link_gets_the_same_answer_and_no_email[verified-tourist-deactivated]
FAILED tests/test_verification_resend.py::test_account_not_due_a_link_gets_the_same_answer_and_no_email[link-sent-59-seconds-ago]
FAILED tests/test_verification_resend.py::test_unknown_email_gets_the_same_answer_and_no_email
FAILED tests/test_verification_resend.py::test_tourist_an_admin_activated_without_verifying_gets_a_link
FAILED tests/test_verification_resend.py::test_registration_counts_as_the_first_link
FAILED tests/test_verification_resend.py::test_second_request_within_the_interval_sends_nothing
FAILED tests/test_verification_resend.py::test_link_is_sent_again_once_the_interval_passed
FAILED tests/test_verification_resend.py::test_email_is_matched_in_lowercase
FAILED tests/test_verification_resend.py::test_invalid_body_is_422_and_sends_nothing[malformed]
FAILED tests/test_verification_resend.py::test_invalid_body_is_422_and_sends_nothing[null]
FAILED tests/test_verification_resend.py::test_invalid_body_is_422_and_sends_nothing[missing]
FAILED tests/test_verification_resend.py::test_link_is_built_from_frontend_url
FAILED tests/test_verification_resend.py::test_route_declares_its_response_schema
21 failed, 824 passed, 25 warnings in 33.47s
```
Causas (primera línea `E` de cada fallo, literal; conteo de líneas iguales con `uniq -c`):
```
     17 E        +  where 405 = <Response [405 Method Not Allowed]>.status_code
     13 E       assert 405 == 200
      3 E       assert 405 == 422
      1 E       assert (201, 405) == (201, 200)
      1 E       KeyError: '/usuarios/reenviar-verificacion'
      1 E       AttributeError: 'NoneType' object has no attribute 'kwargs'
      1 E       AssertionError: assert {('DELETE', '...direct'), ...} == {('DELETE', '...direct'), ...}
      1 E       AssertionError: assert 405 == 422
```
Es el esperado del plan: `21 failed, 824 passed`. Matiz frente a la fila "E RED" (que dice "17 con `405 Method Not
Allowed` en la aserción de estado"): las 17 líneas `where 405 = <Response [405 …]>` son 16 de
`test_verification_resend.py` y 1 de `test_route_guards.py` (`assert 405 == 422`);
`test_the_new_link_verifies_the_account` no comprueba el estado del `POST` y cae en
`mock_send_email.call_args.kwargs` con `AttributeError: 'NoneType' object has no attribute 'kwargs'` (el correo no
salió). La cifra y los 21 nombres coinciden; solo cambia la causa literal de ese caso.

## Compuerta de salida (literal; comando 16 de la Verificación final, corrida tras el commit)
Exit 0. Líneas por paso:
```
75 files already formatted
--- ruff format --check: OK en 0.2s
All checks passed!
--- ruff check: OK en 0.2s
Success: no issues found in 70 source files
--- mypy: OK en 1.3s
Analyzed 57 files, 150 dependencies.
Capas: api | cli -> services -> repositories -> models KEPT
Los servicios no conocen el transporte HTTP KEPT
Los repositorios solo conocen SQLAlchemy y los modelos KEPT
Los modelos y los schemas no dependen de capas superiores KEPT
Contracts: 4 kept, 0 broken.
--- import-linter: OK en 0.6s
--- docs (coherencia): OK en 0.1s
TOTAL                                       1098     10    160      6  98.73%
845 passed, 29 warnings in 34.83s
--- pytest + cobertura: OK en 38.3s
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
(La misma compuerta, corrida antes del commit sobre el árbol de trabajo, dio las mismas cifras: `845 passed, 29
warnings in 31.89s`, `98.73%`.)
- pytest: `845 passed, 29 warnings` (0 failed). Plan: `845 passed`. ✔
- Cobertura: `98.73%` (línea base 98,71 % tras D; 98,70 % en la verificación; plan: medido 98,73 %). ✔
- mypy: 0 errores en 70 archivos. ✔
- ruff: 0 errores; `75 files` formateados. ✔
- import-linter: `4 kept, 0 broken` (línea base 4). ✔
- Avisos 25 → 29: los 4 nuevos son el `StarletteDeprecationWarning` de `HTTP_422_UNPROCESSABLE_ENTITY`
  (`tests/test_verification_resend.py: 3 warnings`, `tests/test_route_guards.py: 4 warnings`, antes 3), el residual
  R4 del plan (S5).

## Ruff y mypy sobre lo tocado
`python -m ruff check <los cinco>` → `All checks passed!`; `python -m ruff format --check <los cinco>` →
`5 files already formatted`; `python -m mypy <los cinco>` → `Success: no issues found in 5 source files`.

## Mutantes ME1–ME9 (cada uno en su copia, suite completa)
Copias `git archive HEAD` (HEAD `a6d1b8a`) + los cinco archivos de la fase en `be64E-mut/base`; cada mutante en
`be64E-mut/be64E-MEn` (carpetas nuevas) del scratchpad; intérprete del venv por ruta, cwd = la copia; `import app;
app.__file__` → `…\scratchpad\be64E-mut\be64E-MEn\app\__init__.py` en los nueve. Mutante aplicado por reemplazo
exacto (el script exige que cada ancla aparezca una sola vez). Las copias no tienen `.env`.

| # | Mutante | Resultado literal | Lo matan |
|---|---|---|---|
| ME1 | `if resend is None: return {"success": True, "message": "otro"}` antes del `return` | `8 failed, 837 passed` | los 6 `…_same_answer_and_no_email[…]`, `test_unknown_…`, `test_second_request_within_the_interval_sends_nothing` |
| ME2 | `add_task` sin el `if`, `email_to=body.email` | `9 failed, 836 passed` | los 6 `…_same_answer_and_no_email[…]`, `test_unknown_…`, `test_registration_counts_as_the_first_link`, `test_second_request_…` |
| ME3 | `VerificationResendRequest.email: EmailStr` | `1 failed, 844 passed` | `test_email_is_matched_in_lowercase` |
| ME4 | `base_url=settings.frontend_url` sin `rstrip` | `1 failed, 844 passed` | `test_link_is_built_from_frontend_url` |
| ME5 | `status.HTTP_202_ACCEPTED` | `15 failed, 830 passed` | 15 de `test_verification_resend.py`, `test_route_declares_its_response_schema` incluido |
| ME6 | sin `response_model=MessageResponse` | `1 failed, 844 passed` | `test_route_declares_its_response_schema` |
| ME7 | `MessageResponse` gana `detail: str \| None = None` | `2 failed, 843 passed` | `test_pending_tourist_gets_a_new_link`, `test_route_declares_its_response_schema` |
| ME8 | `message: str \| None = None` | `1 failed, 844 passed` | `test_route_declares_its_response_schema` |
| ME9 | sin `response_model` y `"email": body.email` de más en el `dict` | `9 failed, 836 passed` | `test_pending_tourist_gets_a_new_link`, los 6 `…_same_answer_and_no_email[…]`, `test_unknown_…`, `test_route_declares_its_response_schema` |

9 muertos, 0 vivos; los nombres coinciden con la columna "Lo matan" del plan, uno por uno.

## Verificación final (desde la raíz, Git Bash, tras el commit `2b6db40`)
Salida literal de cada comando:
```
$ grep -rn "create_verification_token(" app --include=*.py | wc -l
3
$ grep -rn "send_verification_email," app --include=*.py | wc -l
2
$ grep -rn -i "resend\|reenv" app --include=*.py | wc -l
26
$ grep -n "@public_router\." app/api/routers/user.py | wc -l
4
$ grep -c "reenviar-verificacion" tests/test_route_guards.py
2
$ grep -rn "solicite uno nuevo" app --include=*.py | wc -l
1
$ grep -rn "email_verified_at" app alembic --include=*.py | wc -l
11
$ grep -rn "email_verified_at = " app --include=*.py | wc -l
1
$ grep -rn "verification_sent_at" app alembic --include=*.py | wc -l
10
$ grep -rn "verification_sent_at=\|verification_sent_at = " app --include=*.py | wc -l
2
$ grep -rn "verification_sent_at" app/schemas --include=*.py | wc -l
0
$ grep -rn -i "slowapi\|limiter\|rate.limit\|throttl" app pyproject.toml constraints.txt | wc -l
0
$ grep -rln "down_revision.*'e50a7c3d9b12'" alembic/versions --include=*.py | wc -l
1
$ grep -rn "le acabamos de enviar un nuevo" app --include=*.py | wc -l
1
$ grep -rn -E "acabamos de enviar|espere un minuto" tests --include=*.py | wc -l
0
$ grep -c "commit()" app/repositories/user_repository.py
3
$ grep -c "log_transaction" app/services/user_service.py
6
$ grep -c "^VERIFICATION_RESEND_INTERVAL_SECONDS=60$" .env.example
1
$ grep -c '"VERIFICATION_RESEND_INTERVAL_SECONDS": "60"' conftest.py
1
$ grep -rn "BE-64" app tests alembic --include=*.py | wc -l
10
$ grep -rn "ADR-0023" app tests alembic --include=*.py | wc -l
13
$ grep -c "response_model=MessageResponse" app/api/routers/user.py
1
$ grep -rn "MessageResponse" app --include=*.py | wc -l
4
$ grep -rn "MessageResponse" tests --include=*.py | wc -l
3
$ git diff --name-only 22328ce HEAD -- app alembic tests conftest.py .env.example docs/adr
.env.example
alembic/versions/a64d0c2e7f15_users_verification_sent_at.py
app/api/routers/user.py
app/core/config.py
app/models/user.py
app/repositories/user_repository.py
app/schemas/message.py
app/schemas/user.py
app/services/user_service.py
conftest.py
docs/adr/0013-configuracion-centralizada-con-pydantic-settings.md
docs/adr/0023-el-enlace-de-verificacion-se-puede-pedir-de-nuevo.md
tests/test_config.py
tests/test_migration_verification_sent_at.py
tests/test_models_schema.py
tests/test_route_guards.py
tests/test_user_repository.py
tests/test_user_service.py
tests/test_verification_resend.py
```
(`| wc -l` del 15 → `19`.) Todos los valores son los del plan; el 15 da 19 archivos, los 18 del plan más
`docs/adr/0013-…`, como manda E2, punto 3. El 16 es la compuerta de salida de arriba.

Desglose del 13 por archivo (`grep -rc`, sin los ceros): BE-64, una línea en cada uno de los 10 archivos del plan;
ADR-0023, dos en `routers/user.py` y en `user_service.py`, una en los otros nueve; `schemas/message.py` no la cita.

## Skill `test-sanitizer` (solo checklist, "Ecotur Enterprise Test Standards")
Sobre `tests/test_verification_resend.py` y `tests/test_route_guards.py`: (1) mocks: el único doble es el
`mock_send_email` autouse de `tests/conftest.py` (ya existente); no se crea ningún mock nuevo; (2) preparación con
las fábricas centralizadas `persist_user` (y `make_user` por debajo), sin usuarios ni tokens a mano; el token se
decodifica con la clave de `get_settings()`; (3) nombres, docstrings y variables en inglés (los correos y la cédula
del registro son datos); (4) contratos de datos: el 422 se afirma sobre `detalle[*].raw_field`, la clave que emite
hoy el handler de validación (`app/main.py:95`, mismo contrato que `test_services.py`, `test_user_response.py` y
`test_user_update_null.py`); ninguna aserción sobre texto humano (comando 10 → 0): los casos sin envío comparan el
cuerpo con el de un turista pendiente; (5) ABAC: el filtro por rol del dato lo cubren `[admin]` y `[superadmin]`,
además de borrado, verificado, verificado desactivado y dentro del intervalo. No se reescribió nada: los tests son
los dictados por el Anexo E.

## Incidencias y desviaciones
- Ninguna desviación del plan ni de E0/E1/E2. No se tocó `plan.md`, `verificacion.md`, ningún ADR ni ningún archivo
  fuera de los cinco de la fase.
- Matiz de la RED (arriba): la causa literal de `test_the_new_link_verifies_the_account` es `AttributeError`, no un
  405 en la aserción de estado; el conteo `21 failed, 824 passed` es el del plan.
- No leí `.env`. La suite no lo lee (el `conftest.py` raíz fija todas las variables).
- `rm -rf` está denegado por permisos: las copias de mutantes quedan en `be64E-mut/` del scratchpad.

## Residuales
Ninguno nuevo. Siguen vigentes los del plan (R1–R8; R4 medido aquí: avisos 25 → 29). La comparación `timestamptz`
en PostgreSQL sigue sin medirse en la suite (SQLite).

## Siguiente paso
- `/auditar BE-64 E`.
- **Momento 3 de E1, punto 3 (David, obligatorio antes de `/pr`):** con la API de la rama levantada en local sobre
  el PostgreSQL ya migrado y un buzón propio, los nueve pasos de E1 (registro → reenvío sin correo → T1 → reenvío
  pasado el minuto con segundo correo y T2 > T1 → reenvío inmediato sin correo → enlace del segundo correo → reenvío
  a cuenta verificada sin correo → correo sin cuenta sin correo → auditoría con solo `CREATE` y el `UPDATE` de
  `is_active`). Salida literal a la bitácora del día. No lo ejecuté: Alembic y la API leen `.env`.
- Al cerrar (David): la viñeta R6 en AGENTS §3, las filas del backlog y `docs/CONTEXT.md`.
