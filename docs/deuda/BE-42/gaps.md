# Gaps — BE-42

## Auditoría Fase A — 2026-11-12
**Veredicto Fase A: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia de la auditoría (contexto fresco, `handoff-auditor`, HEAD `69c032d`, rama `item/be-42`):

- Árbol: `git status --short` vacío antes y después de la auditoría (salvo este `gaps.md`).
- Plan y aprobación: `plan.md` entra en un solo commit (`758a2fa`) y no cambia después (`git log -- docs/deuda/BE-42/plan.md`
  → solo `758a2fa`); `fed1f7c` solo toca `docs/bitacora/2026-11-12.md`. E0 aprueba A → C "como están escritas" y dice
  "sin correcciones de dictado" (`plan.md:611-616`): el texto de la fase A es el del cuerpo del plan.
- `progress.json`: `Fase_A` `completed` con `commit: "db6bc51"` (`git show --stat db6bc51` lo confirma);
  `current_target: "Fase_B"`; `last_handoff` presente; `edit_rules` igual que en `758a2fa` (`git show 69c032d --
  docs/deuda/BE-42/progress.json` solo cambia `current_target`, `status`, `commit` y `last_handoff`).
- Commit `db6bc51`: mensaje idéntico al de `plan.md:200-215`, con `<MODELO EJECUTOR>` → `Claude Opus 5.5`.
  `git show --numstat --format= db6bc51` → `5	1	app/core/security.py` y `2	1	app/services/user_service.py`
  (criterio de aceptación, `plan.md:195`). `git diff --name-only fed1f7c HEAD -- app tests conftest.py alembic` → solo
  esos dos archivos; `69c032d` solo toca `handoff-Fase_A.md` y `progress.json`.
- Cambios exactos: `app/core/security.py:46-55` (`"""` de cierre, línea en blanco, las dos líneas de comentario y
  `EMAIL_VERIFICATION_SCOPE = "email_verification"`, dos líneas en blanco, `def create_access_token`) y `:103`
  (`to_encode` con la constante); `app/services/user_service.py:14` (primer nombre del import partido) y `:138`
  (`if email is None or scope != EMAIL_VERIFICATION_SCOPE:`). Ningún otro cambio en el método.
- Fuera de alcance respetado: `git grep -n "ACCESS_TOKEN_SCOPE" -- app tests | wc -l` → `0`; las únicas apariciones de
  `create_access_token`, `activate_user` y `single-use` en `git diff fed1f7c db6bc51` son líneas de contexto, no `+`/`-`;
  `tests/conftest.py`, `app/api/dependencies.py` y los tests no aparecen en el diff.
- `git grep -n '"email_verification"' -- app | wc -l` → `1` (`app/core/security.py:51`).
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`): exit 0, `Compuerta superada.`,
  `61 files already formatted`, `All checks passed!`, `Success: no issues found in 56 source files`,
  `Contracts: 4 kept, 0 broken.`, `618 passed, 8 warnings`, `TOTAL 962 19 136 16 96.81%`. Igual a la línea base de
  `verificacion.md:179-184` (618 passed, 96,81 %, 961 stmts) salvo el `+1` stmt de la constante, y a la fila A del plan.
- Mutantes re-medidos en copias desechables del scratchpad (`git archive` + edición de una línea comprobada con `sed -n`;
  el árbol de trabajo no se tocó):
  - MV sobre `fed1f7c` (forma literal): `1 failed, 328 passed`
    (`test_verify_email_wrong_scope_raises_invalid_verification_token`).
  - MV sobre `db6bc51`: `1 failed, 328 passed` (el mismo test).
  - MEV sobre `db6bc51`: `1 failed, 328 passed` (`test_register_tourist_returns_registration_result`).
  - Control sobre `db6bc51`: `329 passed`.
  Coinciden con `plan.md:189-192`, la fila A de `plan.md:164` y el handoff.
- AGENTS: comentario y nombre en inglés; constante de módulo en `app/core/`, importada por el servicio (capa permitida,
  4 contratos KEPT); sin tests nuevos ni excepciones de dominio nuevas.

## Auditoría Fase B — 2026-11-12
**Veredicto Fase B: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia de la auditoría (contexto fresco, `handoff-auditor`, HEAD `a2bd095`, rama `item/be-42`):

- Árbol: `git status --short` vacío antes de la auditoría (después, solo este `gaps.md`).
- `progress.json`: `Fase_B` `completed` con `commit: "20429bf"` (`git show --stat 20429bf` lo confirma);
  `current_target: "Fase_C"`; `last_handoff` presente; `edit_rules` igual que en `758a2fa`. `git diff 69c032d a2bd095 --
  docs/deuda/BE-42/progress.json` solo cambia `current_target`, `status`, `commit` y `last_handoff` de B. `a2bd095` solo
  toca `handoff-Fase_B.md` y `progress.json`.
- Commit `20429bf`: mensaje idéntico a `plan.md:335-355` con `<MODELO EJECUTOR>` → `Claude Opus 5.5` (`diff` vacío).
  `git show --numstat --format= 20429bf` → `6	2	app/core/security.py`, `30	11	tests/conftest.py`,
  `1	0	tests/test_auth.py`, `29	11	tests/test_user_service.py` (criterio, `plan.md:327-328`).
  `git diff --name-only 53268ba 20429bf` → solo esos cuatro: no se tocan `app/api/dependencies.py`,
  `tests/test_route_guards.py` ni `tests/test_token_failure_paths.py` (fase C); `single-use` y `activate_user` no
  aparecen en ninguna línea `+`/`-` (0).
- Cambios exactos (E0: P2, P3, P4), todos en el diff:
  - `app/core/security.py:51` `ACCESS_TOKEN_SCOPE = "access"` entre el comentario y `EMAIL_VERIFICATION_SCOPE`;
    `:63-64` párrafo del docstring; línea de Args `… A scope in it is replaced.`; `:82`
    `to_encode.update({"scope": ACCESS_TOKEN_SCOPE, "exp": expire})`, después de `to_encode = data.copy()`: el `scope`
    del llamador queda sustituido (lo demuestra MD, abajo).
  - `tests/conftest.py`: imports dictados; `make_token` sin `extra_claims` (P2; `git grep -n "extra_claims" -- app tests
    | wc -l` → `0`) con el docstring dictado; `sign_claims` (`:228-248`) entre `make_token` y `make_auth_headers` (P3):
    fábrica centralizada (AGENTS §5), única que firma con `jwt.encode` en `tests/`, usada por `tests/test_user_service.py:290`.
  - `tests/test_auth.py:136` y `tests/test_user_service.py:221`: `assert claims["scope"] == "access"`.
  - `tests/test_user_service.py`: import partido `:19-24`; test de caducidad con `sign_claims` y
    `assert type(exc_info.value.__cause__) is jwt.ExpiredSignatureError` (el servicio encadena `from err` en
    `app/services/user_service.py:126-129`, así que el rechazo viene de la caducidad y no de la firma ni del `scope`);
    test de `scope` equivocado con `make_token(make_user(email="turista@example.com"))`; test nuevo
    `test_verify_email_rejects_access_token_whose_data_names_the_verification_scope` (P4) antes de
    `test_verify_email_missing_user_raises_not_found`.
- Regla "constante para construir, literal para afirmar" (`plan.md:38-41`): construyen con `EMAIL_VERIFICATION_SCOPE`
  `tests/test_user_service.py:291` y `:319`; afirman con literal `tests/test_auth.py:136`, `tests/test_user_service.py:116`
  y `:221` (`git grep -n -E '"access"|"email_verification"' -- tests`: solo esas tres líneas, todas `assert`).
- RED re-medido en copia desechable (`git archive 53268ba` + `git apply` del diff de `tests/` de `20429bf`; `diff
  --strip-trailing-cr` confirma tests = `20429bf` y `security.py` = `53268ba`, sin `ACCESS_TOKEN_SCOPE`):
  `3 failed, 37 passed` — `KeyError: 'scope'` en `test_login_active_user_returns_bearer_token` y
  `test_authenticate_active_user_returns_bearer_token`; `DID NOT RAISE` en `…_data_names_the_verification_scope`.
  Los dos tests reescritos (caducado y `scope` equivocado) están entre los 37 verdes. Coincide con `plan.md:316-319`.
- Mutantes re-medidos sobre `git archive 20429bf` en directorios nuevos del scratchpad (`auditB_*`; edición de una
  línea comprobada con `diff -r` contra la copia de control; el árbol de trabajo no se tocó):
  - MA: `3 failed, 327 passed` (los tres del RED).
  - MD: `1 failed, 329 passed` (`…_data_names_the_verification_scope`).
  - MV: `2 failed, 328 passed` (`test_verify_email_wrong_scope_…` y `…_data_names_the_verification_scope`).
  - Control: `330 passed`.
  Coinciden con `plan.md:321-324`, la fila B de `plan.md:165` y el handoff.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`): exit 0, `Compuerta superada.`,
  `61 files already formatted`, `All checks passed!`, `Success: no issues found in 56 source files`,
  `Contracts: 4 kept, 0 broken.`, `619 passed, 8 warnings`, `TOTAL 963 19 136 16 96.82%`. Línea base
  (`verificacion.md:179-184`): 618 passed, 96,81 %, 4 kept; la cobertura sube. Sobre los cuatro archivos tocados:
  `ruff check` → `All checks passed!`, `ruff format --check` → `4 files already formatted`, `mypy` → `Success: no issues
  found in 4 source files`.
- AGENTS: identificadores, docstrings y comentarios en inglés; `user_repo` sigue siendo `create_autospec(UserRepository,
  instance=True)` (`tests/test_user_service.py:71-73`); ninguna aserción sobre texto en español; sin excepciones de
  dominio nuevas; la constante vive en `app/core/` (4 contratos KEPT).
- Nota, no es hallazgo de B: el commit de la auditoría de A, `53268ba`, lleva el scope `docs(item-be40)` en lugar de
  `docs(item-be42)`; su contenido (`docs/deuda/BE-42/gaps.md`) es correcto. Error del humano, sin efecto en el estado.

## Auditoría Fase C — 2026-11-12
**Veredicto Fase C: PASS (0 bloqueantes, 0 opcionales).**

Sin hallazgos. Evidencia de la auditoría (contexto fresco, `handoff-auditor`, HEAD `8c38f47`, rama `item/be-42`). C es la
última fase: se ejecutó también la "Verificación final" del plan (`plan.md:510-558`).

- Árbol: `git status --short` vacío antes de la auditoría (después, solo este `gaps.md`).
- `progress.json`: `Fase_C` `completed` con `commit: "717fc73"` (`git show --stat 717fc73` lo confirma); las tres fases
  `completed`; `current_target: null`; `last_handoff` presente; `edit_rules` igual que en `758a2fa` (línea de contexto en
  `git diff 758a2fa 8c38f47 -- docs/deuda/BE-42/progress.json`). `8c38f47` solo toca `handoff-Fase_C.md` y
  `progress.json`. `current_target: null` es coherente con `check_docs`: el paso `docs (coherencia)` de la compuerta pasa y
  `scripts/check_docs.py --estado` da `BE-42: verificado → planeado → ejecutado (todas las fases); pendiente de PR o
  mezclado → handoffs: Fase_A, Fase_B, Fase_C`.
- Commit `717fc73`: mensaje idéntico a `plan.md:484-507` con `<MODELO EJECUTOR>` → `Claude Opus 5.5` (`diff` vacío),
  incluidos `fix(auth)!` y el footer `BREAKING CHANGE` (E0, P1). `git show --numstat --format= 717fc73` →
  `8	2	app/api/dependencies.py`, `24	0	tests/test_route_guards.py`, `34	0	tests/test_token_failure_paths.py`
  (criterio, `plan.md:473-474`): ningún test existente cambia. `git diff --name-only 48e782e 717fc73` → solo esos tres; no
  se tocan `security.py`, `conftest.py` ni los tests de B.
- Cambios exactos, todos en el diff: `app/api/dependencies.py:9` (import), `:102-104` (párrafo del docstring), `:116`
  (`Raises:`), `:127-128` (`scope` y `if email is None or scope != ACCESS_TOKEN_SCOPE:`). El `raise` va dentro del `try`
  pero `HTTPException` no es `jwt.InvalidTokenError`, así que sale la misma `credentials_exception` (`:118-122`): 401,
  `WWW-Authenticate: Bearer` y el mismo `detail` que un token corrupto (lo fija
  `tests/test_token_failure_paths.py:188`, P4). `credentials_exception`, los dos `except`, la búsqueda del usuario y todo
  desde `get_current_admin_user` sin cambios (Verificación final, punto 2: `0`).
  `tests/test_route_guards.py:14` y `:154-174`; `tests/test_token_failure_paths.py:40`, `:170-185` y `:188-200`: texto
  dictado, en el sitio dictado.
- AGENTS §5: usuarios con `persist_user`; tokens de la API de producción (`create_verification_token`) o de la fábrica
  `sign_claims`; sin mocks; aserciones sobre código, cabecera `Bearer`, estructura `{"detail"}` y tipo, y la igualdad de
  `detail` entre dos respuestas, nunca sobre texto en español. Sin excepciones de dominio nuevas ni rutas nuevas.
- RED re-medido en copia desechable (`git archive 48e782e` + `git apply` del diff de `tests/` de `717fc73`; `diff
  --strip-trailing-cr` confirma tests = `717fc73` y `dependencies.py` = `48e782e`, sin `ACCESS_TOKEN_SCOPE`):
  `19 failed, 64 passed`. Los 17 `test_protected_route_rejects_verification_token_as_bearer[...]` y los dos tests nuevos de
  `test_token_failure_paths.py`; códigos: 200 × 8 (6 rutas + los 2 tests nuevos), 404 × 7, 422 × 3, 400 × 1. Coincide con
  `plan.md:448-457` y el handoff.
- Mutantes re-medidos, todos, sobre `git archive HEAD` en directorios nuevos del scratchpad (`auditC_*`; cada edición
  comprobada con `diff` contra `HEAD`: una línea, dos en los dobles; el árbol de trabajo no se tocó): control
  `349 passed`; MSC `19 failed, 330 passed` (17 de `test_route_guards.py` + 2 de `test_token_failure_paths.py`); MSUB
  `1 failed, 348 passed` (`test_token_without_subject_returns_401`); MU `3 failed, 346 passed`; MA `102 failed, 247 passed`
  (services 29, user_access_policy 24, route_guards 18, auth 13, user_response 12, audit 3, user_service 2,
  token_failure_paths 1); MA+MSUB y MA+MU `102 failed, 247 passed`, mismo desglose, con los tres tests del rincón 2 en
  verde; MD `1 failed, 348 passed`; MV `2 failed, 347 passed`; MEV `1 failed, 348 passed`; MAV `2 failed, 347 passed`.
  Coinciden con `plan.md:458-470`, `plan.md:556-558` y el handoff.
- Compuerta re-ejecutada (`./venv/Scripts/python.exe scripts/check.py`): exit 0, `Compuerta superada.`,
  `61 files already formatted`, `All checks passed!`, `Success: no issues found in 56 source files`,
  `Contracts: 4 kept, 0 broken.`, `638 passed, 8 warnings`, `TOTAL 965 19 136 16 96.82%`. Línea base
  (`verificacion.md:179-184`): 618 passed, 96,81 %; fila C del plan: 638, 96,82 %, 965 stmts. Sobre los tres archivos
  tocados: `ruff check` → `All checks passed!`, `ruff format --check` → `3 files already formatted`, `mypy` →
  `Success: no issues found in 3 source files`.
- Verificación final (puntos 1-5), salida re-ejecutada: `# 1` las 8 líneas de numstat exactas de `plan.md:519-526`;
  `# 2` `0`, `0`, `0`; `# 3` `app/api/dependencies.py:4`, `2`, `2`, `16`, `4`, `5`, `3`, `3`,
  `tests/test_route_guards.py:17`, `63 tests collected`; `# 4` `1`, `1`, `6`, `7`; `# 5` `0`, `8`, `2`, `83 passed`.
  Punto 6: la compuerta de arriba. Punto 7: los mutantes de arriba. La deuda no asoma: `get_current_user` es el único
  lector de bearer (`Depends(get_current_user)` × 3, los guards de admin y superadmin se apoyan en él) y los dos
  `jwt.decode` de `app/` comprueban el `scope`.
- Estado del ítem: tres fases `completed`, tres auditorías PASS. Listo para PR. Residuales del plan (`plan.md:560-574`),
  sin hallazgo nuevo: R1 (cita de 5 líneas, sin deuda; la Verificación final ya usa 5), R2 (`TokenData.role` sin uso,
  decisión de David), R3 (BE-50 ya tiene fila, `docs/backlog.md:97`), R4 (cierre de documentos tras el merge; el PR
  declara el `BREAKING CHANGE` y los 30 minutos; AGENTS §5 y `sign_claims`, decisión de David antes de `/pr`).
- Nota, no es hallazgo: el commit de la auditoría de A, `53268ba`, lleva el scope `docs(item-be40)` en lugar de
  `docs(item-be42)` (error humano; contenido correcto, sin efecto en el estado).
