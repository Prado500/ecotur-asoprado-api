# PLAN — BE-33: Saldar los residuales de ruff y mypy de `app/` que no dependen de A4

> Fuente: `docs/deuda/BE-33/verificacion.md` (parcial, con adenda de once puntos del 6 nov). Base develop: `bab25c2`.
> Estado: **pendiente de aprobación de David.**

## Resumen para aprobación

En cuatro fases, el plan retira de `app/` los 44 errores de ruff y los 5 de mypy que BE-33 tiene a su nombre, en 10
archivos: ruff baja de 53 a 9 y mypy de 10 a 5. La compuerta sigue en rojo por lo que es de A4. Casi todo es forma
(docstrings, líneas largas, anotaciones), pero hay dos cambios reales: `save_service` pasa a `scalar_one()` y los cuatro
`raise` de las ramas JWT pasan a `from err`. Añade 22 casos de test en 3 archivos nuevos (416 → 438), que cubren las
zonas sin red: ramas de token en `dependencies.py` y el correo real de `email.py`. Una comparación por AST demuestra que
ningún texto de usuario cambia y que el cuerpo del correo solo difiere en espacios en blanco.
**Riesgo principal:** el HTML del correo cambia de bytes y ningún test lo pinta en un cliente de correo real. El plan lo
acota partiendo solo donde ya había un espacio, pero no lo elimina (decisión 8).
**No se toca:** I001 ni el orden de imports, los 5 `str | None` de A4, `pyproject.toml`, `--soft` del CI, los `commit()`
de A3, `alembic/versions`, los residuales de `tests/` (BE-32) ni `docs/backlog.md`. Sin ADR.

## Objetivo y decisiones bloqueadas

Objetivo: ruff 53 → 9 y mypy 10 → 5, sin mover la frontera con A4 y sin más cambio de comportamiento que los dos
declarados en las decisiones 4 y 6.

1. **Conteos (adenda 1).** 44 de ruff (E501 19, D205 12, D415 6, B904 4, W293 3) y 5 de mypy. La fila del backlog (45) se
   corrige en el cierre del día, no aquí.
2. **Excepción a ADR-0005 (adenda 2; forma de BE-02, decisión 2).** ADR-0005 y los rituales de `fase-ejecutor` y
   `handoff-auditor` piden cero errores en archivos tocados. Para este plan, **prevaleciendo sobre esos rituales**, cada
   archivo debe quedar con el conjunto exacto de esta tabla; igual conteo con otro error es BLOQUEANTE. Los números de
   l.1, l.11 y l.124 no se mueven; `dependencies.py:92` pasa a `:95` porque su docstring crece tres líneas.

   | Archivo | Fase | Ruff antes → después | Mypy antes → después |
   |---|---|---|---|
   | `app/repositories/audit_repository.py` | A | D205 l.27 → **0** | 0 → 0 |
   | `app/repositories/user_repository.py` | A | I001 l.1, D205 l.46 → **I001 l.1** | 0 → 0 |
   | `app/schemas/audit.py` | A | I001 l.1, D205 l.18 y 26 → **I001 l.1** | 0 → 0 |
   | `app/repositories/service_repository.py` | B | D415 l.15, 28, 38, 48, 75; D205 l.60; E501 l.18, 60 → **0** | l.83 → **0** |
   | `app/api/dependencies.py` | C | I001 l.1, D205 l.80, E501 l.80, 83, 120, B904 l.99, 105 → **I001 l.1** | l.92, 93, 108 → **l.95** (`str \| None`) |
   | `app/schemas/token.py` | C | D205 y D415 l.5 → **0** | 0 → 0 |
   | `app/services/user_service.py` | C | I001 l.1, E501 l.46, 217, 337, B904 l.126, 130 → **I001 l.1** | l.124, 132, 133 → **l.124** |
   | `app/services/user_access_policy.py` | C | D205 l.21, 78, 95, 110, 129; E501 l.37, 74, 106 → **0** | 0 → 0 |
   | `app/core/email.py` | D | I001 l.1, E501 ×8, W293 ×2 → **I001 l.1** | 0 → 0 |
   | `app/db/database.py` | D | I001 l.1, W293 l.16 → **I001 l.1** | l.11 → **l.11** |
   | Tests nuevos (3) | B, C, D | **0** | **0** líneas `^tests` con `mypy <archivo>` (BE-32 los medirá) |

   Totales de ruff por fase: 53 → A 49 → B 41 → C 20 → D 9. De mypy: 10 → A 10 → B 9 → C 5 → D 5. El hook sale con código 2
   en los archivos con errores pendientes; en los seis con I001 lo seguirá haciendo al terminar: es lo esperado y **no
   se corrige ni se reordena a mano** (`unfixable`, bitácora 2 nov).
3. **Textos de usuario (adenda 5): concatenación implícita de literales, partiendo tras un espacio que ya existe.** Nunca
   `\n` ni cambio de letra. `ast` une los literales al parsear: el comando V9 compara los valores, no el diff. Sin red en
   los tests por AGENTS §5. Trade-off: dos fragmentos se leen peor al buscar con grep el mensaje completo; a cambio, valor
   idéntico en ejecución sin `# noqa`.
4. **`save_service`: `scalar_one()` (adenda 7).** Trade-off: la firma no se ensancha, así que el error no se muda a
   `update_package_details` (l.347). A cambio, si la fila ha desaparecido lanza `NoResultFound`. Es un cambio real en un
   caso imposible hoy; el punto 2 del análisis precisa su efecto por llamador.
5. **`TokenData.email: str`, sin valor por defecto (adenda 8).** `dependencies.py:10` lo importa y `:97` es su único uso,
   con un `email` ya estrechado. Trade-off: construir `TokenData()` sin email pasa a fallar; no lo hace nadie. Las tres
   anotaciones de `payload.get` pasan a `str | None`.
6. **B904: `raise … from err` en los cuatro sitios (adenda 6).** Precedente: `app/core/storage.py:138,210`. `from None`
   haría igual de contento a ruff pero borraría la causa que necesitará el logging (A6). Trade-off: las trazas se alargan
   con la causa. `credentials_exception` se crea por llamada, así que fijarle `__cause__` no se filtra entre peticiones.
7. **Ramas `except` (adenda 3): tests antes de tocar las líneas.** Un test HTTP de 401 pasa antes y después: es de
   caracterización y no puede estar en RED. El RED real lo dan cuatro tests de `__cause__`, que es exactamente lo que
   `from err` añade. La no vacuidad de los HTTP se demuestra con una mutación controlada y con la cobertura.
8. **`email.py` (adenda 4): prueba de estructura, no de bytes, y sin `# noqa`.** Cada salto sustituye un espacio
   existente por salto + sangría; nunca se inserta espacio donde no lo había. Por eso V9 exige `strings=whitespace-only`:
   mismo cuerpo con espacios colapsados. HTML y CSS colapsan esos espacios, también dentro de `style="…"`. Descartados: `#
   noqa: E501` (silencia, no resuelve) y plantilla en archivo aparte (módulo nuevo sin necesidad).
9. **Colaterales en líneas tocadas (adenda 9).** `is_active` → `is_available` en `service_repository.py:28,38`. `usuario`
   → `user` en `dependencies.py:108`, y también en **l.110 y l.113**, sin las que no compila. Nada más.
10. **Herramientas.** Siempre `./venv/Scripts/python.exe` (prevalece sobre el `python …` de los rituales, AF-07). Nunca
    `scripts/check.py --fix`. Único autofix inseguro permitido: el comando W293 de la fase D, acotado a dos archivos.

## Análisis del redactor

**1. Qué y por qué.** Contrastado archivo por archivo con `ruff` y `mypy` sobre `HEAD`: los 44 y los 5 están donde dice la
verificación. Todo el trabajo cabe en ediciones locales, sin imports nuevos en `app/`.

**2. Efecto real de `scalar_one()`.** La ficha de BE-33 dice que el comportamiento observable no cambia, y eso solo es
cierto en un llamador. En `tourist_services_service.py:347` (`update_package_details`) hoy un `None` acaba en 500 al
validar la respuesta, y seguirá en 500. En l.129, 168 y 209 el retorno se ignora: hoy, sin fila, se escribiría auditoría y
se respondería éxito; con `scalar_one()`, 500 antes de auditar. Es mejor, pero es distinto. Además `app/main.py` no tiene
handler genérico (solo `RequestValidationError`, `IntegrityError` y `DomainError`): el 500 lo pone el `ServerErrorMiddleware`
de Starlette. El caso sigue siendo inalcanzable: no hay borrado físico en repositorios ni servicios.

**3. Un docstring de Pydantic es contrato publicado.** Medido en la sonda: `/openapi.json` cambia en dos líneas y solo en
esas: `description` de `AuditLogResponse` (fase A) y de `TokenResponse` (fase C). D205 obliga a reescribirlos y no hay forma
de dejarlos idénticos. Campos y tipos no cambian. `TokenData` no aparece en el esquema.

**4. Orden y dependencias.** Cada archivo pertenece a una sola fase y ninguna fase usa lo que otra cambia: el orden es por
riesgo creciente y por tamaño. Si David reordena, cambian los totales intermedios, no los conjuntos por archivo.

**5. Por qué cuatro fases y no las tres que sugiere la adenda 11 (no vinculante).** La A sugerida son cinco archivos de
`app/` más el test de `save_service`: seis, sobre el tope de cinco. Mover `token.py` a la fase de `dependencies.py`, donde
vive su único uso, deja cinco, pero la fase de `email.py` queda como la más pequeña y mezcla un commit `docs` con un `fix`.
Separar docstrings puros (A) de `save_service` (B) hace atómicos ambos commits y deja A como la menor (4 errores). Coste:
un ritual más, pequeño: la A no ejecuta nada nuevo.

**6. Por qué el test de tokens evita `conftest.py`.** `make_token(user)` no admite claims ni caducidad. Tocar `conftest.py`
daría seis archivos en C. El test llama directamente a `create_access_token`, la misma factoría que usa `make_token`,
sin `jwt.encode` a mano ni importar `SECRET_KEY` (A4 la moverá). Trampa medida en la sonda: no importes `TestingSessionLocal`
de `tests.conftest`, porque carga un segundo módulo con otro motor en memoria y sin tablas.

**7. Tests que congelan comportamiento relacionado; ninguno cambia.** `tests/test_user_service.py:254,264` (B904 de
`verify_email_account`, sin mirar la causa), `tests/test_fixtures_contract.py:54,64` (el router usa el doble de correo; el
real sigue importable), `tests/test_services.py` (los cuatro llamadores de `save_service`), `tests/test_audit.py:141` (401
sin token), `tests/test_domain_error_handler.py:55`.

**8. Frontera con A4 (esta tarde).** BE-33 no toca imports, `conf` (`email.py:11-22`), `database.py:7-12` ni los `jwt.decode`
(`dependencies.py:92`, `user_service.py:124`). A su verificación le afectan: `dependencies.py:92` → `:95`; las líneas de
`email.py` posteriores a la 37; y `tests/test_email.py`, que parchea `app.core.email.fast_mail.send_message`: si A4 renombra
ese objeto, actualiza el test.

**9. ¿ADR? No.** No hay patrón, módulo ni contrato nuevo. `scalar_one()` ya está en `create_service` y `from e` en
`storage.py`. La excepción a ADR-0005 sigue la decisión de BE-02: sin addendum, porque el ADR caduca al quedar verde.

**10. Sonda de este plan** (copia desechable de `HEAD` fuera del repo, con variables ficticias; dos tests de
`test_check_docs.py` fallan allí solo porque la copia no lleva `docs/`). Se aplicaron los textos de este plan fase a fase.
Totales por fase, formato, AST, conteos de grep, `numstat`, RED y mutaciones citados aquí salen de esa medición: 438 casos
(436 en verde + los 2 deseleccionados), 96.11 %, 4 KEPT. La compuerta real la mide cada fase.

## Regla de alcance

**Sí:** los 44 + 5 del mapa, los tres archivos de tests y los colaterales de la decisión 9. **No:** I001, los 5 `str | None`,
`unfixable`, `--soft`, `commit()` de A3, `alembic/versions`, `tests/` existentes, `conftest.py`, reescribir docstrings sin error,
`email.py:28`, `database.py:12`, renombrar handlers, `docs/backlog.md`.

## Fases

**Precondición:** `plan.md` y `progress.json` commiteados por David; el arranque de `fase-ejecutor` se detiene con el árbol
sucio. Criterio común de cada fase: compuerta en **exit 1** solo por `ruff check` y `mypy`; import-linter 4 KEPT;
cobertura ≥ 94.82 %; decisión 2 cumplida en los archivos de la fase. Salida literal en el handoff.
En cada commit, el ejecutor sustituye `<MODELO EJECUTOR>` por su modelo real y deja el resto letra a letra.

### Fase A — Docstrings de auditoría y usuarios (la más pequeña: 3 archivos, 4 errores)

- **Archivos (3):** `app/repositories/audit_repository.py`, `app/repositories/user_repository.py`, `app/schemas/audit.py`.
- **Cambios exactos:** con Edit normal.
  ```text
  # audit_repository.py, l.27-29
  """Retrieves the audit logs using explicit pagination and optional filters.

  Pagination (limit/offset) and the dynamic equality filters prevent over-fetching.
  """
  # user_repository.py, l.46-48
  """Applies logical deletion by stamping the current UTC time on deleted_at.

  It also deactivates the user defensively, which revokes access instantly.
  """
  # schemas/audit.py, l.18-20
  """DTO the Service Layer uses internally to dispatch records to the Audit Repository."""
  # schemas/audit.py, l.26-28
  """DTO that serializes backend audit data for the frontend administrative dashboards."""
  ```
- **Tests (RED primero):** sin pytest nuevo, porque no cambia código ejecutable. El RED es la herramienta: antes,
  `ruff check <los 3> --select D205` da 4; después, 0. La prueba de ausencia de cambio es V9 (`code=same strings=exact`).
- **Criterio de aceptación:** `416 passed`; ruff **49**; mypy **10**; `git diff --numstat` da `3 2`, `3 2` y `2 6`.
- **Fuera de alcance:** I001 de `user_repository.py` y `schemas/audit.py`; `pass` de `AuditLogCreate`; `commit()` de A3.
- **Commit:**
  ```text
  docs(app): put audit and user data-layer docstrings in summary form

  Ruff D205 needs a one-line summary and a blank line; these four docstrings ran
  the summary across two lines. No executable code changes.

  - audit_repository.py, user_repository.py: summary plus description.
  - schemas/audit.py: one line each. AuditLogResponse is a Pydantic model, so its
    docstring is also its description in /openapi.json: that text changes, its
    fields do not.

  Ruff drops from 53 to 49 (BE-33). I001 stays in user_repository.py and
  schemas/audit.py: it belongs to A4.

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

### Fase B — `save_service` falla donde se rompe la invariante

- **Archivos (2):** `tests/test_service_repository.py` (nuevo), `app/repositories/service_repository.py`.
- **Cambios exactos:**
  1. l.83: `return result.scalar_one()`. l.72 conserva `scalars().first()`: `get_service_by_id` sí puede no encontrar.
  2. l.15: `"""Creates a new TouristService entity."""`
  3. l.18, en dos líneas:
     ```python
     # The freshest db registry, in which all the tourist service's images are properly
     # linked to their corresponding service, is retrieved.
     ```
  4. l.28: `"""Returns a list of active TouristService entities (is_available = True)."""`
  5. l.38: `"""Returns a list of inactive TouristService entities (is_available = False)."""`
  6. l.48: `"""Returns a list of deleted TouristService entities."""`
  7. l.60-62:
     ```text
     """Returns a TouristService based on its id.

     If no 2nd-positional argument is given, it will bring only non-deleted tourist services.
     Otherwise, it will retrieve a package even if it was soft-deleted.
     """
     ```
  8. l.75, porque el contrato de la función cambia:
     ```text
     """Commits changes to an existing service and refreshes relationships.

     Args:
         service (TouristService): The tracked entity whose changes are committed.

     Returns:
         TouristService: The committed row, with its images loaded.

     Raises:
         NoResultFound: The row is gone. It was just committed and nothing deletes rows
             physically, so this is a broken invariant, not a business case.
     """
     ```
- **Tests (RED primero).** Docstring breve en inglés por test; `ServiceRepository(db_session)` real; fixture `repo`; helper
  local `_package(**overrides)` con los valores de `_persist_package` de `test_services.py`.

  | Test | Entrada | Esperado | Antes |
  |---|---|---|---|
  | `test_save_service_commits_pending_changes_and_returns_the_row` | fila + `is_available=False`; tras guardar, `rollback` y `refresh` | mismo `id`; el cambio sobrevive | verde |
  | `test_save_service_raises_when_the_row_never_existed` | transitorio con `id=999_999` | `NoResultFound` | **rojo** |
  | `test_save_service_raises_when_the_row_was_physically_deleted` | `delete()` SQL y `commit` | `NoResultFound` | **rojo** |
  | `test_save_service_returns_a_soft_deleted_row` | `deleted_at` con valor | la devuelve con `deleted_at` | verde |
  | `test_save_service_returns_the_row_with_its_images_loaded` | una `ServiceImage` | `image_url` leída sin `MissingGreenlet` | verde |

  RED en el handoff: `2 failed, 3 passed` con `pytest tests/test_service_repository.py`.
- **Criterio de aceptación:** `5 passed`; `421 passed`; ruff **41**; mypy **9**; el archivo con 0 de ruff y mypy; `numstat`
  `23 9`; V6 cumplido; `is_active` en 0 en ese archivo.
- **Fuera de alcance:** `commit()` de l.17 y l.76 (A3), `== True` (E712 tolerado), `sqlalchemy.future`, llamadores de
  `tourist_services_service.py`.
- **Commit:**
  ```text
  fix(service-repository): raise when save_service finds no row

  save_service promised a TouristService but returned first(), which may be None.
  Widening the signature would only move the mypy error to update_package_details,
  so it now uses scalar_one(), like create_service in the same file.

  A missing row raises NoResultFound instead of returning None. Three callers ignore
  the result and would have audited and answered success for a row that is gone; the
  fourth would have failed later validating the response. The case stays unreachable:
  nothing deletes these rows physically.

  - service_repository.py: scalar_one() and contract in the docstring; D415, D205 and
    E501 in the same file; docstrings said is_active where the filter uses is_available.
  - test_service_repository.py: 5 cases, 2 of them red before the change.

  Ruff drops from 49 to 41 and mypy from 10 to 9 (BE-33).

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

### Fase C — Autenticación y cuentas: causa de errores JWT, tipado y textos

- **Archivos (5):** `tests/test_token_failure_paths.py` (nuevo), `app/api/dependencies.py`, `app/schemas/token.py`,
  `app/services/user_service.py`, `app/services/user_access_policy.py`.
- **Cambios exactos:**
  1. `dependencies.py`, l.80-84:
     ```text
     """Decodes the given JWT token and resolves the active user it identifies.

     Verifies payload consistency, lifespan status (unexpired or expired) and user enabling
     (only active users are allowed).

     It's injected with a UserRepository instance for user-state consulting against the
     persistence layer.
     """
     ```
  2. `dependencies.py`, cuerpo: l.93 `email: str | None = payload.get("sub")`; l.98 `except jwt.ExpiredSignatureError as err:`;
     l.103 `) from err`; l.104 `except jwt.InvalidTokenError as err:`; l.105 `raise credentials_exception from err`;
     `usuario` → `user` en l.108, 110 y 113.
  3. `dependencies.py`, l.120, en dos líneas:
     ```text
     to prevent unauthorized access to resources that should only be available for admin or
     superadmin users.
     ```
  4. `token.py`, l.5-7:
     ```text
     """Schema responsible for the standard server response after a successful login operation.

     Complies with the OAuth2 standard.
     """
     ```
     y l.21: `email: str`.
  5. `user_service.py`, l.46: `"""Encapsulates the business rules, validations and operational logic of the User entity."""`
  6. `user_service.py`, l.125-133 (el texto de `:130` pasa de línea porque ya no cabe con `from err`):
     ```python
     except jwt.ExpiredSignatureError as err:
         raise InvalidVerificationTokenError(
             "El enlace de verificación ha expirado. Por favor solicite uno nuevo."
         ) from err
     except jwt.InvalidTokenError as err:
         raise InvalidVerificationTokenError(
             "Token de verificación inválido o corrupto."
         ) from err

     email: str | None = payload.get("sub")
     scope: str | None = payload.get("scope")
     ```
  7. `user_service.py`, l.217:
     ```python
     "message": (
         f"La cuenta vinculada a {soft_deleted_user.email}, con C.C. {target_cedula} "
         "ha sido eliminada exitosamente."
     ),
     ```
  8. `user_service.py`, l.337:
     ```text
     AuthorizationError: 403 Forbidden if a standard admin attempts to recover a
         higher-tier account.
     ```
  9. `user_access_policy.py`, textos, con el mismo valor:
     ```python
     # l.37
     "Privilegios insuficientes o violación de jerarquía. "
     "No tiene autorización para eliminar esta cuenta."
     # l.74
     "Privilegios insuficientes. "
     "No tiene permisos para modificar el estado de la cuenta."
     # l.106
     "Violación de jerarquía: "
     "Solo un Superusuario puede aprovisionar cuentas administrativas."
     ```
  10. `user_access_policy.py`, resúmenes:
      ```text
      # l.21-22
      """Enforces the deletion invariant on a user account.

      The actor must delete their own account or strictly outrank the target.
      # l.78-79
      """Enforces recovery precedence over soft-deleted accounts.

      Standard admins cannot restore accounts of equal or higher tier.
      # l.95-96
      """Enforces provisioning governance over administrative accounts.

      Only superadmins may create them.
      # l.110-111
      """Enforces the administrative-tier rule on a guarded operation.

      Only admins and superadmins may proceed (e.g. reading the audit trail).
      # l.129-130
      """Determines whether a viewer role may see a subject role in directory listings.
      ```
- **Tests (RED primero).** 9 funciones, 11 casos. `PROTECTED_ROUTE = "/usuarios/mi-perfil"`. `_assert_bearer_401`: 401,
  `WWW-Authenticate == "Bearer"`, `set(body) == {"detail"}`, `detail` es `str`. Tokens construidos **dentro del test** con
  `create_access_token(data=…, expires_delta=timedelta(minutes=-1))` o `make_auth_headers`; ningún test importa
  `SECRET_KEY`. Doble: `create_autospec(UserRepository, instance=True)`.

  | Test | Cubre | Esperado | Antes |
  |---|---|---|---|
  | `test_valid_token_on_protected_route_returns_the_user` | camino feliz; `user` | 200; `cedula` | verde |
  | `test_expired_token_on_protected_route_returns_401` | l.98-103 | Bearer 401 | verde |
  | `test_corrupt_token_on_protected_route_returns_401` | l.104-105 | Bearer 401 | verde |
  | `test_expired_and_corrupt_tokens_get_distinct_details` | ramas no intercambiadas, sin leer el texto | `detail` distintos | verde |
  | `test_token_without_subject_returns_401` | l.95, de la anotación de l.93 | Bearer 401 | verde |
  | `test_token_for_unknown_user_returns_401` | l.111, renombrado | Bearer 401 | verde |
  | `test_token_for_inactive_user_returns_401` | l.111, renombrado | Bearer 401 | verde |
  | `test_get_current_user_chains_the_jwt_error_as_cause` (`expired`, `corrupt`) | `from err` | 401; `__cause__` es `ExpiredSignatureError` / `DecodeError`; repo sin llamadas | **2 rojos** |
  | `test_verify_email_chains_the_jwt_error_as_cause` (`expired`, `corrupt`) | `from err` | `InvalidVerificationTokenError` con esa causa; `activate_user` sin llamadas | **2 rojos** |

  RED en el handoff: `4 failed, 7 passed`. Tras el verde, mutación controlada de `dependencies.py`, en este orden: copia del
  archivo al temporal; `sed -i 's/HTTP_401_UNAUTHORIZED/HTTP_403_FORBIDDEN/' app/api/dependencies.py`; el test da
  `7 failed, 4 passed`; se restaura desde la copia (no invertir el `sed`: l.130 ya usa 403). Salida literal en el handoff.
- **Criterio de aceptación:** `11 passed`; `432 passed`; ruff **20**; mypy **5**; `dependencies.py` con Missing `63` (hoy
  `63, 95, 98-105, 111`); `numstat` `16 12`, `3 2`, `15 9` y `19 13`; V5, V7 y V8 cumplidos; `code=same` en
  `user_access_policy.py` y `strings=exact` en los cuatro.
- **Fuera de alcance:** I001; `dependencies.py:92` y `user_service.py:124` (A4); formato `Args:` de `get_current_admin_user`;
  `TokenData.role`; handlers en español; `tests/test_user_service.py` y `conftest.py`.
- **Commit:**
  ```text
  fix(auth): chain JWT errors as causes and correct token typing

  The four raises in the JWT except branches dropped the cause, and three annotations
  claimed str for values payload.get may return as None. The next line already checks
  for None, so only the annotations were false. HTTP answers do not change.

  - dependencies.py: raise from err; email is str | None until narrowed; usuario
    becomes user; docstring summary and long lines.
  - token.py: TokenData.email is required, which closes the mypy error at the query;
    its only use passes a narrowed email. TokenResponse's docstring is also its
    /openapi.json description: that text changes, its fields do not.
  - user_service.py: raise from err in verify_email_account; annotations; long lines.
  - user_access_policy.py: docstring summaries; user-facing messages split with
    implicit concatenation, same runtime value.
  - test_token_failure_paths.py: 11 cases; the 4 on __cause__ are red before the change
    and the 7 HTTP ones pin branches that had no test.

  Ruff drops from 41 to 20 and mypy from 9 to 5 (BE-33). I001 and the str | None of
  SECRET_KEY stay: they belong to A4.

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

### Fase D — Correo de verificación y cadena de `database.py`

- **Archivos (3):** `tests/test_email.py` (nuevo), `app/core/email.py`, `app/db/database.py`.
- **Cambios exactos:**
  1. Solo W293, primero, con el comando exacto:
     `./venv/Scripts/python.exe -m ruff check --fix --unsafe-fixes --select W293 app/core/email.py app/db/database.py`
     (debe informar `3 fixed`; es lo único que cambia en `database.py`).
  2. `email.py`, sustituciones. CSS, l.37, 38, 44 y 45, una declaración por línea, con 16 de sangría y `}}` en la línea de 12:
     ```text
     body {{
         font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
         background-color: #F7F9FB;
         margin: 0;
         padding: 0;
     }}
     .container {{
         max-width: 600px;
         margin: 40px auto;
         background-color: #ffffff;
         border-radius: 8px;
         overflow: hidden;
         box-shadow: 0 4px 15px rgba(0,0,0,0.05);
         border: 1px solid #E2E8F0;
     }}
     .btn {{
         background-color: #006C49;
         color: #ffffff;
         padding: 14px 32px;
         text-decoration: none;
         border-radius: 6px;
         font-weight: bold;
         display: inline-block;
     }}
     .footer {{
         background-color: #F2F4F6;
         padding: 24px;
         text-align: center;
         font-size: 12px;
         color: #6B7A7D;
     }}
     ```
  3. `email.py`, cuerpo, conservando sangrías originales (16 y 20; continuaciones como aquí):
     ```text
     <p>Gracias por unirte a Ecotur Asoprado. Estás a un solo paso de descubrir las
     mejores experiencias bioculturales que tenemos para ti desde Prado, Tolima.</p>
     <p>Para garantizar la seguridad de tu cuenta y activar tu acceso, por favor
     verifica tu dirección de correo electrónico haciendo clic en el siguiente botón:</p>
     ```
     ```text
         <a href="{verification_link}" class="btn"
             style="color: #ffffff !important;
             text-decoration: none;">Verificar mi Cuenta</a>
     ```
     ```text
     <p style="font-size: 12px; color: #006875;
         word-break: break-all;">{verification_link}</p>
     ```
- **Tests (de caracterización; pasan antes del cambio).** Autospec sobre el objeto real, sin tocar el fixture autouse del
  router: `patch.object(email_module.fast_mail, "send_message", autospec=True)`. Importar
  `send_verification_email` de `app.core.email`. `message.body` se estrecha a `str` con `assert isinstance` en un helper
  (es `str | list | None`; sin esto, mypy da 6 errores en el test).

  | Test | Esperado |
  |---|---|
  | `test_dispatches_one_html_message_to_the_recipient` | `assert_awaited_once_with(message)`; `[r.email for r in recipients] == [destinatario]`; `subject` es `str` no vacío; `subtype is MessageType.html` |
  | `test_body_carries_the_link_in_the_button_and_as_plain_text` | enlace ×2; con `html.parser`, un único `<a>`: `href` exacto, `class == "btn"`, `style` con espacios colapsados igual a `color: #ffffff !important; text-decoration: none;` |
  | `test_smtp_failure_propagates` | `side_effect = ConnectionErrors(...)` → la misma excepción; una llamada |
  | `test_invalid_recipient_is_rejected_before_sending` | `ValidationError`; `send_message` sin llamadas |
  | `test_body_renders_a_compound_first_name_verbatim` | el nombre de entrada aparece tal cual |
  | `test_css_braces_are_rendered_unescaped` | sin `{{` ni `}}`; 9 `{` y 9 `}` |

  Evidencia en el handoff, por este orden: `6 passed` antes de editar; `6 passed` después; y mutación controlada: copia de
  `email.py` al temporal, cambiar `<a href="{verification_link}"` por `<a href="#"`, el test da `1 failed, 5 passed`, restaurar.
- **Criterio de aceptación:** `438 passed`; ruff **9** (8 I001 en `app/` + `tests/test_user_service.py:3`); mypy **5**;
  `email.py` al 100 % (hoy Missing `29-82`); `numstat` `42 10` y `1 1`; V9 con `email.py code=same strings=whitespace-only`.
- **Fuera de alcance:** docstring en español de `email.py:28`; comentario de `database.py:12`; `echo=True` (A5); `conf`,
  `load_dotenv`, `os.getenv` (A4); cualquier cambio de texto del correo.
- **Commit:**
  ```text
  style(email): wrap the verification HTML at its existing spaces

  Eight lines of the email's f-string exceeded the limit and two blank lines held
  whitespace. Each break replaces a space that was already there, so the body only
  differs in whitespace runs, which HTML and CSS collapse. No text or attribute
  changes; no noqa, so the limit stays enforced.

  - email.py: one CSS declaration per line; long tags and paragraphs wrapped; W293.
  - database.py: W293 inside the stray string of l.13-17, no runtime effect.
  - test_email.py: 6 characterization cases over the real function with the SMTP
    client autospecced; this module had no tests and they passed before the change.

  Ruff drops from 20 to 9 and mypy stays at 5: only A4's I001 and str | None remain,
  plus the I001 that BE-32 owns in tests. BE-33 closes with the gate still red.

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

## Verificación final

Expectativas medidas en la sonda con los textos literales de este plan. Desde la raíz, en Git Bash, tras la fase D.

```bash
# V1. Ruff de BE-33: "All checks passed!" (hoy "Found 44 errors.")
./venv/Scripts/python.exe -m ruff check app --select E501,D205,D415,B904,W293

# V2. Ruff total: "Found 9 errors.", los 9 I001: 8 en app/ (l.1) + tests/test_user_service.py:3
./venv/Scripts/python.exe -m ruff check . --output-format=concise

# V3. Mypy de BE-33: 0 líneas
./venv/Scripts/python.exe -m mypy | grep -E 'Incompatible types in assignment|Incompatible return value type|"get_non_deleted_user_by_email"'

# V4. Frontera con A4: 5 líneas, security.py:71, security.py:87, database.py:11, user_service.py:124, dependencies.py:95;
#     y en total "Found 5 errors in 4 files"
./venv/Scripts/python.exe -m mypy | grep -E 'has incompatible type "str \| None"' | grep -v get_non_deleted_user_by_email

# V5. Anotaciones: 0 líneas la primera; 3 la segunda (1 en dependencies.py, 2 en user_service.py)
git grep -n -E '(email|scope): str = payload\.get' -- app
git grep -n -E 'str \| None = payload\.get' -- app

# V6. save_service: 1 first() (get_service_by_id, legítimo) y 2 scalar_one() (create_service, save_service)
git grep -n -F 'scalars().first()' -- app/repositories/service_repository.py
git grep -n -F 'scalar_one()' -- app/repositories/service_repository.py

# V7. B904: 4 líneas con from err y 4 con as err (2 y 2 en dependencies.py y user_service.py)
git grep -n -E '\bfrom err\b' -- app
git grep -n -E '\bas err:' -- app

# V8. Colaterales y silenciadores: 0, 0, 0, y 4 líneas de noqa, todas UP042 (backlog D2), como hoy
git grep -n -F 'is_active' -- app/repositories/service_repository.py
git grep -n -w 'usuario' -- app/api/dependencies.py
git grep -n -F 'email: str | None' -- app/schemas/token.py
git grep -n -E 'noqa|type: ignore' -- app

# V9. Comparación con la base. Salida esperada exacta en la tabla de abajo.
./venv/Scripts/python.exe - <<'PY'
import ast
import subprocess
from pathlib import Path

BASE = "bab25c2"
FILES = """app/api/dependencies.py app/core/email.py app/db/database.py
app/repositories/audit_repository.py app/repositories/service_repository.py
app/repositories/user_repository.py app/schemas/audit.py app/schemas/token.py
app/services/user_access_policy.py app/services/user_service.py""".split()


def is_str(node):
    return isinstance(node, ast.Constant) and isinstance(node.value, str)


def split(source):
    """Returns the code with strings blanked and no-effect strings removed, and its strings."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(getattr(node, "body", None), list):
            node.body = [s for s in node.body if not (isinstance(s, ast.Expr) and is_str(s.value))]
    strings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr):
            strings.append(
                "".join(v.value if is_str(v) else "{" + ast.unparse(v) + "}" for v in node.values)
            )
            for v in node.values:
                if is_str(v):
                    v.value = ""
    for node in ast.walk(tree):
        if is_str(node) and node.value:
            strings.append(node.value)
            node.value = ""
    return ast.dump(tree), sorted(strings)


def squeeze(strings):
    return [" ".join(s.split()) for s in strings]


for path in FILES:
    old = subprocess.run(["git", "show", f"{BASE}:{path}"], capture_output=True, check=True)
    old_code, old_strings = split(old.stdout.decode("utf-8"))
    new_code, new_strings = split(Path(path).read_text(encoding="utf-8"))
    if old_strings == new_strings:
        verdict = "exact"
    else:
        verdict = "whitespace-only" if squeeze(old_strings) == squeeze(new_strings) else "DIFFERENT"
    print(f"{path:44} code={'same' if old_code == new_code else 'changed':8} strings={verdict}")
PY

# V10. Alcance: 13 archivos (los 10 del mapa + 3 tests nuevos); numstat de app/ como en los criterios de cada fase
git diff --name-only bab25c2 HEAD -- app tests alembic pyproject.toml
git diff --numstat bab25c2 HEAD -- app

# V11. Tests nuevos: 5, 9 y 6 funciones; "22 passed"; sin líneas que empiecen por tests en mypy
git grep -c -E 'def test_' -- tests/test_service_repository.py tests/test_token_failure_paths.py tests/test_email.py
./venv/Scripts/python.exe -m pytest tests/test_service_repository.py tests/test_token_failure_paths.py tests/test_email.py -q
./venv/Scripts/python.exe -m mypy tests/test_service_repository.py tests/test_token_failure_paths.py tests/test_email.py | grep '^tests'

# V12. Compuerta: exit 1 solo por ruff check y mypy; 438 passed; cobertura >= 94.82 % (sonda: 96.11 %);
#      56 files already formatted; 4 KEPT; Missing de dependencies.py: 63; email.py al 100 %
./venv/Scripts/python.exe scripts/check.py
```

Salida esperada de V9:

```text
app/api/dependencies.py                      code=changed  strings=exact
app/core/email.py                            code=same     strings=whitespace-only
app/db/database.py                           code=same     strings=exact
app/repositories/audit_repository.py         code=same     strings=exact
app/repositories/service_repository.py       code=changed  strings=exact
app/repositories/user_repository.py          code=same     strings=exact
app/schemas/audit.py                         code=same     strings=exact
app/schemas/token.py                         code=changed  strings=exact
app/services/user_access_policy.py           code=same     strings=exact
app/services/user_service.py                 code=changed  strings=exact
```

`code` ignora docstrings, cadenas sueltas y el contenido de las cadenas. Los cuatro `changed` son los de las decisiones 4, 5, 6
y 9, y se revisan en el diff. `strings=exact` en `user_access_policy.py` y `user_service.py` es la comprobación de la
decisión 3. Con `strings=DIFFERENT` en cualquier archivo, un texto cambió: es BLOQUEANTE.

## Residuales

1. **Ficha `docs/aprendizaje/fichas/BE-33.md`.** "El comportamiento observable no cambia" y "por el handler genérico" no son
   exactos (Análisis, punto 2). La decisión no cambia, pero el argumento se sustenta ante el jurado. Destino: corrección de
   David en el cierre de hoy.
2. **Español en líneas no tocadas (adenda 9):** `email.py:28` y `database.py:12`. Destino: nota en la fila P2 del backlog.
3. **Fila BE-33 del backlog:** 45 → 44 y D205 13 → 12 (adenda 1). Destino: cierre de hoy.
4. **`make_token` no admite claims ni caducidad.** Por eso `test_token_failure_paths.py` llama a `create_access_token` y
   `test_user_service.py:268,286` a `jwt.encode` con `SECRET_KEY`. Destino sugerido: BE-32 (fila o nota), al centralizar
   tokens; esas líneas ya tocan sus errores de mypy.
5. **`TokenData.role` no se usa:** `dependencies.py:97` solo pasa `email`, y `TokenData` no sale de esa función. Destino
   sugerido: fila P3 (`refactor`), sin urgencia. También `token.py:17` dice `weather` por `whether`.
6. **`alembic/versions` (rincón 8):** 16 errores fuera de la compuerta; no se tocan. Sin fila, salvo que David la quiera.

## Referencias

Context7 no estaba disponible en esta sesión: lo no trivial se comprobó contra el código instalado y con la sonda; los
enlaces son de referencia y no se consultaron hoy.

- fastapi-mail · 1.6.5 · `FastMail.send_message`, `MessageSchema`, `ConnectionErrors` leídos en `venv/Lib/site-packages/fastapi_mail/` · https://sabuhish.github.io/fastapi-mail/
- SQLAlchemy · 2.0.48 · `Result.scalar_one()`, `NoResultFound` · https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Result.scalar_one
- PyJWT · 2.12.1 · `ExpiredSignatureError`, `DecodeError` (subclases de `InvalidTokenError`) · https://pyjwt.readthedocs.io/en/stable/api.html
- Ruff · 0.17.2 · el formatter une literales implícitos solo si caben en la línea: medido (`user_access_policy.py:74` unido daría 101) · https://docs.astral.sh/ruff/formatter/
- Internas: ADR-0005, ADR-0011; `docs/deuda/BE-02/plan.md` (decisión 2 y residual 1).

## Enmiendas aprobadas

**E0 — 6 nov 2026, 10:22 (David, sesión Mentor): plan aprobado; las cinco decisiones abiertas, resueltas.** Ninguna fase,
conjunto ni total cambia; `progress.json` queda como está, `current_target: "Fase_A"`.

1. **Cuatro fases**, como recomienda el plan (un commit `docs` no mezcla un `fix`; la A es la menor).
2. **Tests de `__cause__`** se mantienen: son el único RED real de la fase C; los HTTP de 401 son de caracterización y su no
   vacuidad la prueba la mutación controlada 401 → 403.
3. **Revisión visual del correo:** la hace David **una vez antes de `/pr`**, con el HTML de `email.py` tras la fase D
   abierto en un navegador (o un correo real), y se declara en la descripción del PR ("cómo se probó"). Ningún agente la
   hace ni la finge.
4. **`/openapi.json`:** se aceptan los dos cambios de `description` (`AuditLogResponse`, `TokenResponse`); campos y tipos
   no cambian.
5. **Ficha `docs/aprendizaje/fichas/BE-33.md`:** corregida por el Mentor el mismo día con el punto 2 del análisis (efecto
   por llamador; `ServerErrorMiddleware`, no "handler genérico"). Residual 1 resuelto.

Desviaciones de la adenda (3, 4, 9, 11) aceptadas con los motivos de la tabla "Dónde el plan se aparta de tu adenda".
Nota de flujo, no del plan: la sonda (copia de `HEAD` fuera del repo para medir los textos del plan) se registra en la
bitácora como pendiente de flujo; no bloquea.
