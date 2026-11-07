# PLAN — BE-32: Saldar los residuales de la suite (aserciones, copias HTTP, mypy en `tests/` y opcionales de BE-33)

> Fuente: `docs/deuda/BE-32/verificacion.md` (confirmada, con adenda de ocho puntos del 7 nov, 10:24). Base develop:
> `fd144ad`. Estado: **aprobado por David (7 nov 2026, 11:14) con la enmienda E0** (sección "Enmiendas aprobadas",
> al final): 8 fases; P1 = 548; P2–P5 como propone el plan; P6 = D8 inmatable, fase H sin espía del constructor.

## Resumen para aprobación

En ocho fases, solo sobre `tests/`, `pyproject.toml` y un docstring de `app/`, el plan salda todos los subpuntos de
BE-32 y los rincones 1–5 y 8 de la verificación. `tests/` entra en `mypy.files`, y sus 7 errores de BE-32 quedan en 0
antes del commit que lo activa. Las 11 aserciones de mock sin argumentos pasan a `_with(...)`. Se borran las tres copias
HTTP de `test_user_access_policy.py`. Además, ocho tests existentes y cuatro nuevos matan 15 mutantes que hoy
sobreviven (G1, D2, U6, U7, D17, D11, M5, M10, L4, L5, L14, L15, L17, C10 y D8), con su `failed/passed` esperado.
Al cerrar, la compuerta queda con el rojo de A4 y nada más: ruff 8 · mypy 9 · 4 kept. Hay una diferencia con la adenda:
**548 tests, no 544.** La adenda resta las 3 copias (547 → 544), pero no suma el test D2 que ella misma pide ni los otros
tres nuevos (orden de guardas, U6/U7 y D17). Ver P1 al final del análisis.
**Riesgo principal:** la línea de los 4 errores de A4 en `tests/test_user_service.py` se mueve (103/197/274/292 →
105/203/280/298) porque las fases B y D añaden importaciones y líneas encima. El plan fija el conjunto por identidad y
por línea nueva. Un error de más o de menos es BLOQUEANTE.
**No se toca:** comportamiento de `app/`, los 8 I001 y los 5 `str | None` de `app/`, los 4 `str | None` de tests (A4),
`sqlalchemy.future` de `app/` (S2), tests de firma con otra clave (A4), `docs/backlog.md`. Sin ADR.

## Objetivo y decisiones bloqueadas

Objetivo: dejar la suite a la altura de AGENTS §4/§5 en todo lo que BE-32 tiene a su nombre y hacer que la compuerta
mida `tests/` con mypy, sin cambiar el comportamiento de `app/` y sin mover la frontera con A4.

1. **Alcance completo (adenda 1):** los nueve puntos de la fila, la nota del 5 nov, la lista (a)–(d) y los rincones 1–5 y 8.
2. **Test D2 (adenda 2):** nuevo, en `tests/test_token_failure_paths.py`, junto al de `:93-98`, con `==` entre las
   respuestas a un token corrupto y a `create_access_token(data={"sub": "ghost@test.com"})`. El de `:93-98` se queda.
3. **Rincones 1–5 (adenda 3)** como ediciones de tests existentes. En cada par redundante se borra
   `assert_not_awaited()` y queda `assert_not_called()`, que es más fuerte: una llamada sin `await` la detecta.
4. **Copias HTTP (adenda 4):** se borran `test_user_access_policy.py:314`, `:384` y `:412`, y quedan las de
   `test_auth.py`. Antes se copia `:407-409` a `test_auth.py:388-389`.
5. **Excepción a ADR-0005, conjunto exacto de A4 (adenda 5; forma de BE-02).** Prevalece sobre los rituales de
   `fase-ejecutor` y `handoff-auditor`, que piden cero errores en archivos tocados. `tests/test_user_service.py` se toca
   (fases B y D) y conserva exactamente sus 4 `[arg-type]` `str | None`, todos en `SECRET_KEY`. Se identifican por
   contenido y la línea se mueve:

   | Error de A4 (contenido de la línea) | Base | Tras B | Tras D (y al cerrar) |
   |---|---|---|---|
   | `jwt.decode(result.verification_token, SECRET_KEY, ...)` en `test_register_tourist_returns_registration_result` | 103 | 104 | **105** |
   | `jwt.decode(result.access_token, SECRET_KEY, ...)` en `test_authenticate_active_user_returns_bearer_token` | 197 | 198 | **203** |
   | `SECRET_KEY,` de `jwt.encode` en `test_verify_email_expired_token_raises_invalid_verification_token` | 274 | 275 | **280** |
   | `SECRET_KEY,` de `jwt.encode` en `test_verify_email_wrong_scope_raises_invalid_verification_token` | 292 | 293 | **298** |

   En `app/` no cambia nada: mypy `app/db/database.py:11`, `app/core/security.py:71`, `:87`,
   `app/services/user_service.py:124`, `app/api/dependencies.py:95`. Ruff: los 8 I001 `:1:1` de la línea base.
6. **Mutantes (adenda 6):** cada uno se define abajo, en su fase, con el test que lo mata y el `failed/passed` esperado.
   Se mide sobre una **copia desechable fuera del árbol de trabajo**, como en BE-02 y BE-33. El árbol nunca lleva un
   mutante. El ejecutor pega la salida en el handoff y el auditor la reproduce. Los mensajes se comparan con `==`/`!=`
   entre respuestas o excepciones, nunca leyendo el texto.
7. **`app/` (adenda 7):** solo el docstring `Raises:` de `app/repositories/service_repository.py:86-88` (fase F).
8. **Fuera (adenda 8):** S2 y A4. La nota de AF-08 es del cierre, no de este plan.
9. **Compuerta:** siempre `./venv/Scripts/python.exe scripts/check.py`. Sale con exit 1 en todas las fases
   (`Compuerta NO superada: ruff check, mypy`) por el rojo de A4. Ese rojo no bloquea (ADR-0005). Lo que bloquea es
   apartarse de la tabla de cada fase.

## Análisis del redactor

**Qué cambia y por qué.** Son unos 30 hallazgos en 12 archivos de `tests/`, más `pyproject.toml` y un docstring de
`app/`. Ninguno cambia lo que la API hace. Cambian cuatro cosas: lo que la suite afirma (argumentos de los dobles,
mensajes comparados entre sí, filas vecinas), lo que la compuerta mide (mypy sobre `tests/`), lo que no está duplicado
(3 tests HTTP) y lo que los docstrings prometen.

**Orden y dependencias.**
- A → B es obligatorio. La adenda 5 pide que `tests/` entre en mypy con los 7 errores de BE-32 ya en 0, pero arreglar
  los 7 y tocar `pyproject.toml` suman 6 archivos (límite: 5). La fase A arregla los 2 de
  `test_fixtures_contract.py`, y la B activa mypy y arregla los otros 5 en el mismo commit. Ningún commit tiene
  `tests/` en mypy con errores de BE-32 (P4).
- B va antes que C–H. Así todo test nuevo o editado después nace revisado por mypy.
- B arregla también el I001 de `test_user_service.py:3`: toca ese bloque de imports (añade `typing.Any`), y ADR-0005
  pide cero errores de BE-32 en los archivos tocados (P3).
- D va después de B porque edita `test_user_service.py` otra vez. Las líneas de A4 se calculan sobre ese orden
  (decisión 5).
- C, E, F, G y H no dependen entre sí en contenido. Sí comparten archivo: C y E tocan `test_user_access_policy.py`, y
  C y G tocan `conftest.py`. La línea 86 de `override_get_db` en la verificación final suma las dos de `conftest.py`.

**Qué congela comportamiento relacionado (y por eso no se rompe).**
- `tests/test_fixtures_contract.py` congela los dobles globales de `conftest.py`. La fase G cambia `make_token` sin
  tocar la llamada `make_token(user)` de `make_auth_headers`, así que todo test que firma con `make_auth_headers` recibe
  el mismo token que hoy.
- `tests/test_auth.py:262,361,242` ya cubren lo que cubren las copias que se borran. Las líneas de `app/` que
  ejercitan son las mismas, así que la cobertura no puede bajar. El ejecutor la mide antes y después.
- `tests/test_user_service.py:261,281` (`assert_not_awaited` en token corrupto y caducado) siguen detectando U8 cuando
  la fase G borra la línea redundante `test_token_failure_paths.py:166`. Medición de BE-33: U8 da `1 failed` en la
  suite sin esa línea (`docs/deuda/BE-33/gaps.md:146`).

**Riesgos.**
1. *mypy con `tests/`:* si la compuerta da algo distinto de 14 en el RED de B o de 9 al cerrar B, el ejecutor se detiene
   y no "arregla" errores que no estén en la tabla.
2. *Desplazamiento de líneas de A4:* resuelto por la tabla de la decisión 5. El auditor compara por contenido y línea.
3. *Espía de `MessageSchema` (fase H):* matar D8 exige saber qué mensaje se *construyó*, y no se puede leer el asunto
   (está en español). Se dobla el constructor con `spec=MessageSchema` y un `side_effect` que llama a la clase real.
   Valida igual y no cambia lo que se envía. El coste es atar el test al nombre `MessageSchema` del módulo (P6).
4. *`ContentSettings` por igualdad (fase D):* depende de `DictMixin.__eq__` (compara `__dict__`), leído en la versión
   instalada (12.30.0).
5. *Mutantes:* D1 y U1 (intercambiar los textos) siguen vivos. No se pueden matar sin leer el texto o sin un código de
   error nuevo, que cambiaría el contrato. Van a Residuales.

**Discrepancias menores con la verificación (leídas en el código).** `test_storage.py:96` ya comprueba
`content_settings.content_type`, aunque la verificación dice que no. No cambia el plan: la fase D sustituye `:92-96`
entero. Los `jwt.encode` de `test_user_service.py:268,286` no se migran a una factoría (P5).

**Puntos que piden decisión de David (P1–P6).**
- **P1. 548, no 544.** La adenda 4 da 547 → 544 al borrar las copias, pero la adenda 2 añade un test nuevo (D2), y el
  plan añade tres más: orden de guardas (G1), U6/U7 y D17. Ninguno cabe con honestidad en un test existente, porque
  cada uno es un caso de borde con su propia razón de fallar. Opciones: (a) aceptar **548**, lo que dice este plan;
  (b) fundir U6/U7 y D17 en tests existentes, para 546, a costa de tests con dos razones de fallo. El mínimo posible
  con la adenda 2 es 545.
- **P2. Líneas de A4.** La adenda 5 fija `tests/test_user_service.py:103,197,274,292`. El plan las mueve a
  105/203/280/298 sin cambiar el conjunto. Hay que confirmar que el auditor compara por contenido y línea nueva.
- **P3. El I001 de `test_user_service.py:3` va en la fase B**, no en la de higiene, porque B toca ese bloque de imports.
- **P4. "En el mismo commit".** Los 2 errores de `test_fixtures_contract.py` se arreglan un commit antes (fase A), por
  el límite de 5 archivos. Ningún commit tiene `tests/` en mypy con errores de BE-32.
- **P5. (c) `make_token`.** Solo gana `expires_delta`, que tiene un consumidor. Las claims libres no tienen ninguno
  (YAGNI). Los `jwt.encode` de `test_user_service.py` se quedan: son tokens de verificación sin `User`, y sus líneas
  `SECRET_KEY` son el conjunto de A4. Migrarlos borraría 2 errores de ese conjunto.
- **P6. D8 exige espiar el constructor `MessageSchema`**, con `spec=` y llamando a la clase real. La alternativa es
  declarar D8 imposible de matar, como D1, y quedarse con `assert_awaited_once_with(message)` contra el objeto
  capturado.

## Regla de alcance

- **Sí:** los 12 archivos de `tests/` del mapa de la verificación, más `pyproject.toml:94` y el docstring `Raises:` de
  `app/repositories/service_repository.py:86-88`.
- **No:** ninguna otra línea de `app/`. Tampoco: los 8 I001 de `app/` ni el `unfixable` de ruff; los 9 `str | None` de A4;
  `sqlalchemy.future` de `app/repositories/*` (S2); tests de firma con otra clave (A4); `test_user_response.py`;
  `alembic/`; `docs/backlog.md`, `docs/CONTEXT.md` y la bitácora (cierre); renombrar o reordenar tests que el plan no
  cita; el texto de los `detail`.

## Fases

Tabla de compuerta esperada (exit 1 siempre; `ruff format --check`: `57 files already formatted`; docs ✔; 4 kept):

| Fin de | ruff check | mypy | pytest | Cobertura |
|---|---|---|---|---|
| Base | 9 (8 I001 `app/` + `tests\test_user_service.py:3`) | `Found 5 errors in 4 files (checked 35 source files)` | 547 passed | 96.11 % |
| A | 9 (igual) | igual que la base | 547 passed | ≥ 96.11 % |
| B | **8** (solo `app/`) | `Found 9 errors in 5 files (checked 53 source files)`; tests en 104/198/275/293 | 547 passed | ≥ 96.11 % |
| C | 8 | 9 (igual que B) | 547 passed | ≥ 96.11 % |
| D | 8 | 9; tests en **105/203/280/298** | 547 passed | ≥ 96.11 % |
| E | 8 | 9 (igual que D) | **545 passed** | ≥ 96.11 % |
| F | 8 | 9 | 545 passed | ≥ 96.11 % |
| G | 8 | 9 | **548 passed** | ≥ 96.11 % |
| H | 8 | 9 | 548 passed | ≥ 96.11 % |

En cada commit, el ejecutor sustituye `<MODELO EJECUTOR>` por su modelo real y deja el resto letra a letra. Los
bloques de código dictan el contenido exacto; el corte de línea es el que deje `ruff format` (100 columnas).

### Fase A — Que mypy no estreche el doble del correo (la más pequeña)
- **Archivos:** `tests/test_fixtures_contract.py`.
- **Cambios exactos:** en `test_email_dispatch_double_is_autouse_and_autospecced` (`:54-61`), el cuerpo pasa a ser:
  ```python
      double: Any = user_router.send_verification_email
      assert double is mock_send_email

      with pytest.raises(TypeError):
          await double(recipient="x")

      double.assert_not_called()
  ```
  Docstring y firma sin cambios.
- **Tests (RED primero):** el RED es de herramienta.
  `./venv/Scripts/python.exe -m mypy tests --cache-dir "$TMPDIR/mypycache" 2>&1 | grep -cE "^tests.test_fixtures_contract"`
  da `2` antes (`:59 [call-arg]`, `:61 [attr-defined]`) y `0` después. El mismo `mypy tests` pasa de
  `Found 16 errors in 9 files` a `Found 14 errors in 8 files (checked 18 source files)`.
  `pytest tests/test_fixtures_contract.py -q` da `9 passed` antes y después.
- **Criterio de aceptación:** lo anterior, más la compuerta de la fila A de la tabla.
- **Fuera de alcance de esta fase:** `pyproject.toml` y los otros 5 errores (fase B).
- **Commit:**
  ```text
  test(fixtures): stop mypy narrowing the email double to the real function

  The identity assert between the router's name and the fixture let mypy
  narrow the Any-typed double to send_verification_email itself, so the
  keyword call and assert_not_called were reported as errors (call-arg,
  attr-defined). Binding the router's name to an Any-typed local keeps
  the same identity check and leaves the double untyped.

  These are two of the seven BE-32 mypy errors in tests/; the other five
  go in the commit that adds tests/ to mypy.files, which would otherwise
  touch six files.

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

### Fase B — `tests/` entra en mypy, con los otros 5 errores de BE-32 en 0
- **Archivos:** `pyproject.toml`, `tests/conftest.py`, `tests/test_services.py`, `tests/test_audit.py`,
  `tests/test_user_service.py`.
- **Cambios exactos:**
  - `pyproject.toml:94` → `files = ["app", "scripts/check_docs.py", "scripts/check.py", "tests"]`.
  - `conftest.py:235` → `user: User = make_user(**overrides)` (`:239`, `no-any-return`).
  - `test_services.py`: `from typing import Any` entre `from decimal import Decimal` y `from unittest.mock ...`, y
    `:138` → `update_payload: dict[str, Any] = {` (`:157`, `[index]`; misma forma que `test_auth.py:16`).
  - `test_audit.py`: `from typing import Any` antes de `from unittest.mock ...`, y `:70` → `def audit_repo(self) -> Any:`
    (`:72`; misma forma que `test_token_failure_paths.py:58`).
  - `test_user_service.py`: `:3` → `from datetime import UTC, datetime, timedelta` (I001); nueva línea 4,
    `from typing import Any`; `:63` → `def user_repo() -> Any:` y `:69` → `def audit_service() -> Any:` (`:65`, `:71`).
- **Tests (RED primero):** primero, solo `pyproject.toml`. La compuerta da en rojo
  `Found 14 errors in 8 files (checked 53 source files)`: 5 de `app/`, los 4 de A4 en `:103,197,274,292` y los 5 de
  BE-32. Después, el resto de cambios.
- **Criterio de aceptación:** fila B de la tabla. mypy lista exactamente los 5 de `app/` y
  `tests\test_user_service.py:104`, `:198`, `:275`, `:293`, y ninguno más. Ruff no tiene ninguna línea `tests\`, y
  `./venv/Scripts/python.exe -m ruff check tests/` da `All checks passed!`.
- **Fuera de alcance de esta fase:** los 4 `str | None` de A4; aserciones y demás contenido de estos archivos (fases C y D).
- **Commit:**
  ```text
  chore(mypy): check tests/ in the gate and clear the suite's own errors

  tests/ was outside mypy.files, so the gate never saw type errors in the
  suite. It now does. The five BE-32 errors left after the previous
  commit (two of them missing from the backlog row) are fixed here, so
  no commit has tests/ checked with BE-32 errors in it.

  - pyproject.toml: add "tests" to [tool.mypy] files.
  - conftest.py: type the persisted user so persist_user stops returning Any.
  - test_services.py: type the update payload as dict[str, Any].
  - test_audit.py, test_user_service.py: autospec fixtures return Any, the
    form test_token_failure_paths.py already uses; sort the datetime import
    (the only I001 in tests/).

  mypy goes from 5 to 9: the four new errors are str | None on SECRET_KEY
  in test_user_service.py and belong to A4, declared as its exact set in
  the BE-32 plan (exception to the ADR-0005 ratchet).

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

### Fase C — Higiene de la suite: `select`, comentario, `Yields:` e ids
- **Archivos:** `tests/test_services.py`, `tests/test_user_access_policy.py`, `tests/test_audit.py`,
  `tests/test_check_docs.py`, `tests/conftest.py`.
- **Cambios exactos:**
  - `test_services.py` y `test_user_access_policy.py`: `from sqlalchemy.future import select` → `from sqlalchemy import select`.
  - `test_audit.py`, el comentario en español (`:21` en la base) →
    `# 1. Create a package with a plain JSON payload that satisfies ServiceCreate`.
  - `test_check_docs.py:1039`: `"year-by-monotony"` → `"year-nearest-to-version"` y `"year-resets-per-table"` →
    `"year-nearest-in-each-table"`. `:1089-1090`: `"year-jump-marked"` → `"new-year-rows-marked"` y
    `"year-jump-future-row"` → `"new-year-row-in-future"`. Describen `_date_near` (`scripts/check_docs.py:757`).
  - `conftest.py`: una sección `Yields:` al final del docstring de cada fixture generador, precedida de una línea en
    blanco:
    - `setup_database`: `None: control passes to the test while the tables exist.`
    - `db_session`: `AsyncSession: the test's own session; it closes when the test ends.`
    - `client`: `AsyncClient: the client bound to the app; the overrides are cleared on exit.`
    - `override_azure_storage_client`: `None: the double stays installed until the test ends.`

    Cada uno ocupa 3 líneas: la línea en blanco, `Yields:` y el elemento, sangrado 4 espacios más.
- **Tests (RED primero):** sin comportamiento nuevo, así que el RED son los patrones de la verificación, que bajan a 0:
  `grep -rn "sqlalchemy.future" tests/` 2 → 0; el comentario, 1 → 0;
  `grep -cE "year-by-monotony|year-resets-per-table|year-jump" tests/test_check_docs.py` 2 → 0 (2 líneas, 4 ids).
- **Criterio de aceptación:** fila C de la tabla. El comando AST del patrón 7 de la verificación ya no lista
  `conftest.py` 34, 51, 62 ni 89. `test_check_docs.py` da el mismo número de passed que antes.
- **Fuera de alcance de esta fase:** el `Yields:` de `test_email.py:43` (fase H); `override_get_db` (función anidada);
  cualquier otra línea de estos archivos.
- **Commit:**
  ```text
  test(suite): import select from sqlalchemy, add Yields, rename stale ids

  Hygiene the suite owed to AGENTS 4 and to S2's direction:

  - test_services.py, test_user_access_policy.py: select comes from
    sqlalchemy, not the legacy sqlalchemy.future alias (same object in 2.0).
  - test_audit.py: translate the one Spanish comment left in tests/.
  - conftest.py: Yields sections on the four generator fixtures
    (setup_database, db_session, client, override_azure_storage_client).
  - test_check_docs.py: four R7 ids named the retired year-by-monotony
    rule; they now name what _date_near does (nearest year to the
    version line).

  No assertion changes; app/ keeps its own sqlalchemy.future (S2).

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

### Fase D — Aserciones de dobles con argumentos
- **Archivos:** `tests/test_user_service.py`, `tests/test_services.py`, `tests/test_storage.py`, `tests/test_audit.py`.
- **Cambios exactos** (líneas de la base):
  - `test_user_service.py`: `from app.models.audit import AuditAction` entre `app.core.security` y `app.models.user`.
    `:110` → `user_repo.create_user.assert_awaited_once_with(result.user)`. `:111` →
    ```python
        audit_service.log_transaction.assert_awaited_once_with(
            entity_name="User",
            entity_id="1005911792",
            action=AuditAction.CREATE,
            performed_by="1005911792",
        )
    ```
    Borrar `:122` (`assert_not_awaited`). `:328` → `user_repo.create_user.assert_awaited_once_with(created_user)`.
    `:329` → la misma forma con `entity_id="5555555555"`, `performed_by=actor.cedula` y `changes={"role": "admin"}`,
    con coma final en cada argumento.
  - `test_services.py:219` →
    `failing_client.upload_image.assert_awaited_once_with(StagedImage("test_image.jpg", "image/jpeg", b"fake_binary_payload"))`.
    Se quedan `:220-221` (`isinstance`, porque una `NamedTuple` es igual a una tupla plana) y se borran `:222-224`,
    que ya cubre la igualdad. `:486` → lo mismo con `StagedImage("notes.bin", "application/octet-stream", b"binary")`;
    se quedan `:487-488` y se borra `:489`.
  - `test_storage.py`: `from azure.storage.blob import ContentSettings` entre `azure.core.exceptions` y
    `azure.storage.blob.aio`. `:92-96` →
    ```python
        doubles.source_blob.upload_blob.assert_awaited_once_with(
            b"bytes", overwrite=True, content_settings=ContentSettings(content_type="image/jpeg")
        )
    ```
    `:159`, `:189` y `:198` → `.assert_awaited_once_with()`.
  - `test_audit.py`: borrar `audit_repo.get_all_audit_logs.assert_not_awaited()` (`:87` en la base).
- **Tests (RED primero, mutantes en copia desechable):**

  | Mutante | Cambio | Antes | Después |
  |---|---|---|---|
  | MU1 | `user_service.py:101` `performed_by=saved_user.email` | `test_user_service.py`: 19 passed | `1 failed, 18 passed` (`test_register_tourist_returns_registration_result`) |
  | MU2 | `user_service.py:425` borra `changes=...` | 19 passed | `1 failed, 18 passed` (`test_create_administrative_account_provisions_admin`) |
  | MS1 | `storage.py:202` `delete_blob(delete_snapshots="include")` | `test_storage.py`: 18 passed | `1 failed, 17 passed` (`promote_happy_path`) |
  | MS2 | `storage.py:154` `delete_blob(delete_snapshots="include")` | 18 passed | `2 failed, 16 passed` (los dos de `delete_image`) |
  | MR1 | `routers/service.py:76` `filename=""` | `test_services.py`: `1 failed` (503) | `2 failed` (503 y 415) |
- **Criterio de aceptación:** fila D de la tabla, con A4 en `105/203/280/298`. Además,
  `grep -rnE "\.assert_(called|awaited)(_once)?\(\)" tests/` da 0, y el patrón 1b (`not_called` seguido de
  `not_awaited`) también da 0.
- **Fuera de alcance de esta fase:** `test_email.py:99` (fase H); `test_token_failure_paths.py:166` (fase G); los
  `jwt.encode` de A4.
- **Commit:**
  ```text
  test(doubles): assert mock calls with their arguments

  Ten assertions only checked that a double was awaited once, so a wrong
  audit actor, a dropped changes dict or an extra delete_blob option went
  unnoticed (AGENTS 5 asks for assert_called_once_with).

  - test_user_service.py: create_user with the user it was given, and
    log_transaction with entity, action, actor and changes; drop an
    assert_not_awaited that assert_not_called already implies.
  - test_services.py: upload_image with the exact StagedImage; isinstance
    stays because a NamedTuple equals a plain tuple.
  - test_storage.py: upload_blob with data, overwrite and ContentSettings,
    delete_blob with no arguments.
  - test_audit.py: drop the same redundant assert_not_awaited.

  The A4 mypy lines in test_user_service.py move to 105, 203, 280 and
  298; the set is unchanged.

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

### Fase E — Copias HTTP fuera y orden de las guardas de `assert_can_update` congelado
- **Archivos:** `tests/test_auth.py`, `tests/test_user_access_policy.py`.
- **Cambios exactos:**
  - `test_auth.py:388-389` (conteo) → las tres líneas de `test_user_access_policy.py:407-409`:
    `users = (await db_session.execute(select(User))).scalars().all()`, `assert len(users) == 1`,
    `assert users[0].cedula == admin.cedula`. `func` se queda porque lo usa `:67`.
  - `test_user_access_policy.py`: borrar `test_patch_hierarchy_violation_returns_403_detail`,
    `test_admin_cannot_provision_admin_account_403_and_no_db_mutation` y `test_admin_update_tourist_persists_mutation`.
    `from app.models.user import User, UserRole` → `from app.models.user import UserRole` (`User` queda sin uso).
  - Al final de `TestAssertCanUpdate`:
    ```python
        def test_role_guard_for_non_superadmins_runs_before_the_self_role_guard(self, policy, make_user):
            """Freezes the guard order without reading the text.

            An admin sending its own role gets the non-superadmin answer, the same one it gets
            for someone else's role, and not the self-update answer a superadmin gets.
            """
            admin = make_user(role=UserRole.admin)
            tourist = make_user(role=UserRole.tourist)
            superadmin = make_user(role=UserRole.superadmin)

            with pytest.raises(AuthorizationError) as admin_self:
                policy.assert_can_update(admin, admin, {"role": "admin"})
            with pytest.raises(AuthorizationError) as admin_other:
                policy.assert_can_update(admin, tourist, {"role": "admin"})
            with pytest.raises(AuthorizationError) as superadmin_self:
                policy.assert_can_update(superadmin, superadmin, {"role": "superadmin"})

            assert admin_self.value.detail == admin_other.value.detail
            assert admin_self.value.detail != superadmin_self.value.detail
    ```
- **Tests (RED primero):** mutante **G1**, en copia desechable, que intercambia los bloques
  `user_access_policy.py:66-69` y `:71-72`. Sin el test nuevo, el archivo y la suite pasan enteros. Con él, `1 failed`
  (el test nuevo) y el resto passed. La aserción que se copia a `test_auth.py` no es RED: replica una que ya pasa.
- **Criterio de aceptación:** fila E de la tabla (547 − 3 + 1 = **545**), con la cobertura medida antes y después, sin
  bajar.
  `grep -cE "def test_(patch_hierarchy_violation|admin_cannot_provision_admin_account|admin_update_tourist_persists)" tests/test_user_access_policy.py`
  da 0. El mismo `grep -cE` sobre `tests/test_auth.py`, con
  `admin_patching_superadmin|admin_provisioning_admin|admin_updates_tourist_email`, da 3.
- **Fuera de alcance de esta fase:** otros tests HTTP de `test_user_access_policy.py`; el texto de los `detail`.
- **Commit:**
  ```text
  test(access-policy): drop three HTTP copies and freeze the role guard order

  Three tests in test_user_access_policy.py repeated test_auth.py ones
  (admin patches a superadmin, admin provisions an admin, admin fixes a
  tourist's email) with weaker body checks. test_auth.py keeps them and
  inherits the one assertion only the copy had: the single row left is
  the admin's own.

  Nothing pinned the order of the role guards in assert_can_update:
  swapping the non-superadmin guard and the self-role guard kept every
  test green. A unit test now compares the details of three rejections,
  never their text.

  Suite: 547 - 3 + 1 = 545 tests; app/ lines exercised are the same.

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

### Fase F — `save_service`: su fila entre dos, su `deleted_at` y su `Raises:`
- **Archivos:** `tests/test_service_repository.py`, `app/repositories/service_repository.py` (solo docstring).
- **Cambios exactos:**
  - `test_save_service_commits_pending_changes_and_returns_the_row`: tras persistir `package`, persistir una vecina con
    `await _persist(db_session, _package(name="Paquete Vecino De Prueba"))`. Docstring →
    `"""The pending change survives a later rollback, and the row returned is this id's of two."""`.
  - `test_save_service_raises_when_the_row_was_physically_deleted`, docstring →
    `"""A row deleted from the table before the call raises instead of returning None."""`.
  - `test_save_service_returns_a_soft_deleted_row`: la misma vecina, después de `package`. `:93` →
    `assert saved.deleted_at == deleted_at.replace(tzinfo=None)`, precedido de
    `# SQLite returns the column without its time zone.`. Docstring →
    `"""A soft-deleted row still exists, so saving it returns it with its own deletion date."""`.
  - `service_repository.py`, tras el `NoResultFound` de `Raises:`:
    ```text
                StaleDataError: The commit flushed a pending change to a row that another session had
                    already deleted (the UPDATE matched no row): the same broken invariant, caught earlier.
    ```
- **Tests (RED primero, copia desechable):**

  | Mutante | Cambio | Antes (archivo) | Después (archivo) |
  |---|---|---|---|
  | M5 | `service_repository.py:94` sin `.where(...)` | 5 passed | `2 failed, 3 passed` (commits y soft-deleted: `MultipleResultsFound`) |
  | M10 | antes del `commit()`: `service.deleted_at = datetime(2000, 1, 1, tzinfo=UTC)` | 5 passed | `1 failed, 4 passed` (soft-deleted) |
- **Criterio de aceptación:** fila F de la tabla. `grep -c "StaleDataError" app/repositories/service_repository.py` = 1,
  y el `git diff` de `app/` se limita a esas 2 líneas de docstring.
- **Fuera de alcance de esta fase:** un test que provoque `StaleDataError` con otra sesión (Residuales); el código de
  `save_service`.
- **Commit:**
  ```text
  test(service-repo): pin save_service to its own row and deletion date

  The five save_service tests ran with zero or one row, so dropping the
  WHERE on the id went unnoticed, and the soft-deleted case only checked
  that deleted_at was not None, so rewriting it inside save_service
  survived too.

  - test_service_repository.py: a neighbour row in the two tests that
    return a row; deleted_at compared exactly (SQLite drops the zone); the
    physical-delete docstring no longer claims another session did it.
  - service_repository.py: Raises documents StaleDataError, which commit()
    raises before the select when another session deleted the row under a
    pending change. Docstring only.

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

### Fase G — Fallos de token: respuestas iguales y distintas, usuario borrado y `make_token` con caducidad
- **Archivos:** `tests/test_token_failure_paths.py`, `tests/conftest.py`.
- **Cambios exactos:**
  - `conftest.py`: `from datetime import timedelta` tras `import itertools`. `_make_token` pasa a
    `def _make_token(user: User, *, expires_delta: timedelta | None = None) -> str:` y llama a
    `create_access_token(data={"sub": user.email, "role": user.role.value}, expires_delta=expires_delta)`. El elemento
    de `Returns:` pasa a `Callable[..., str]: Factory producing a signed bearer token with the user's email and role as
    claims; expires_delta overrides the default lifespan, and a negative one yields an already expired token.` No se
    añaden claims libres (P5).
  - `test_token_failure_paths.py`:
    - Importaciones: `from datetime import UTC, datetime, timedelta`, y el alias `MakeToken = Callable[..., str]`.
    - `_expired_token()` sin parámetro, porque ya nadie pasa `email`. Docstring:
      `"""Signs an access token for an email with no account that expired a minute ago."""`.
    - Helper `_user_service(user_repo: Any) -> UserService` con el `UserService(...)` de `:156-160`. Lo usan el test
      de causa y el nuevo U6/U7.
    - `test_valid_token_...`: `await persist_user()` (vecina) **antes** de `user = await persist_user()` (D11).
    - `test_expired_token_on_protected_route_returns_401`: recibe `make_token: MakeToken` y usa
      `_bearer(make_token(user, expires_delta=timedelta(minutes=-1)))`.
    - Nuevo, tras `:93-98`:
      ```python
      async def test_corrupt_token_gets_the_same_detail_as_an_unknown_user(client: AsyncClient) -> None:
          """Edge case: a corrupt token is answered like a valid token for nobody, text unread."""
          corrupt = await client.get(PROTECTED_ROUTE, headers=_bearer(_corrupt_token()))
          unknown = await client.get(
              PROTECTED_ROUTE, headers=_bearer(create_access_token(data={"sub": "ghost@test.com"}))
          )

          _assert_bearer_401(corrupt)
          _assert_bearer_401(unknown)
          assert corrupt.json()["detail"] == unknown.json()["detail"]
      ```
    - `test_token_for_unknown_user_returns_401`: recibe `persist_user: PersistUser` y crea una vecina con
      `await persist_user()` antes de la petición (D11).
    - Nuevo, tras el de usuario inactivo: `test_token_for_soft_deleted_active_user_returns_401(client, persist_user,
      make_auth_headers)`, con docstring
      `"""Edge case: a soft-deleted account is rejected even while is_active is still True."""`. Persiste con
      `persist_user(deleted_at=datetime(2026, 1, 15, 12, 0, tzinfo=UTC))`, hace un GET con `make_auth_headers(user)` y
      llama a `_assert_bearer_401`.
    - `test_verify_email_chains_the_jwt_error_as_cause`: usa `_user_service`; se borra `:166`. Docstring:
      `"""The domain error keeps the JWT error as its cause."""`.
    - Nuevo, al final:
      ```python
      async def test_verify_email_expired_and_corrupt_tokens_get_distinct_errors(user_repo: Any) -> None:
          """Edge case: each verification failure keeps its own detail, compared without reading it."""
          service = _user_service(user_repo)

          with pytest.raises(InvalidVerificationTokenError) as expired:
              await service.verify_email_account(_expired_token())
          with pytest.raises(InvalidVerificationTokenError) as corrupt:
              await service.verify_email_account(_corrupt_token())

          assert expired.value.detail != corrupt.value.detail
      ```
- **Tests (RED primero, copia desechable; el archivo tiene 11 casos antes y 14 después):**

  | Mutante | Cambio | Antes | Después |
  |---|---|---|---|
  | D2 | `dependencies.py`: la rama `ExpiredSignatureError` (`:101`) lanza `credentials_exception from err`, y la `InvalidTokenError` (`:107`), el `HTTPException` de sesión expirada `from err` | 11 passed | `1 failed, 13 passed` (`corrupt_token_gets_the_same_detail...`) |
  | U6 | `user_service.py:126-128` con el mensaje de `:130-132` | 11 passed | `1 failed, 13 passed` (`verify_email_expired_and_corrupt...`) |
  | U7 | `user_service.py`: `except jwt.InvalidTokenError` antes de `except jwt.ExpiredSignatureError` | 11 passed | `1 failed, 13 passed` (el mismo) |
  | D17 | `user_repository.py:22` sin `User.deleted_at.is_(None)` | 11 passed | `1 failed, 13 passed` (`soft_deleted_active_user`); suite: `1 failed` |
  | D11 | `user_repository.py:22` sin `User.email == email` | 11 passed | `2 failed, 12 passed` (`valid_token` y `unknown_user`) |
  | D1, U1 | intercambiar los dos textos | 11 passed | 14 passed (vivos: Residuales) |
  | U8 | activar antes de lanzar | lo detecta `:166` | archivo, 14 passed; la suite lo sigue detectando en `test_user_service.py` (medición de BE-33: `1 failed`) |
- **Criterio de aceptación:** fila G de la tabla (545 + 3 = **548**). Además,
  `grep -c "expired\.value\.detail != corrupt\.value\.detail" tests/test_token_failure_paths.py` da 1, y
  `grep -c "expires_delta" tests/conftest.py` da 3.
- **Fuera de alcance de esta fase:** tests de firma con otra clave (A4); `jwt.encode` de `test_user_service.py` (A4);
  claims libres en `make_token`; los tres `create_access_token` de este archivo que no tienen `User` detrás.
- **Commit:**
  ```text
  test(tokens): pin token error details and soft-deleted user rejection

  Several JWT failure branches had answers no test told apart:

  - test_token_failure_paths.py: a corrupt token must get the same detail
    as a valid token for nobody (swapping the except branches of
    get_current_user survived); expired and corrupt verification tokens
    must get different details (answering both with one message
    survived); a soft-deleted user with is_active still True must get
    401 (a lookup that ignored deleted_at survived). The valid and
    unknown-user tests get a neighbour account, so "the user it names" is
    tested, not "the only user". The redundant activate_user assertion
    goes: test_user_service.py already pins it.
  - conftest.py: make_token takes an optional expires_delta, which the
    expired-token test now uses instead of a hand-built token.

  Details are compared with each other, never read. Swapping the two
  texts stays undetected by design (AGENTS 5).

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

### Fase H — Correo: enlace visible, regla del botón y el mensaje que de verdad se envía
- **Archivos:** `tests/test_email.py`.
- **Cambios exactos:**
  - Importar `re`. `_AnchorCollector` → `_BodyCollector`, con `anchors` (igual que hoy) y
    `texts: list[tuple[str, dict[str, str | None], str]]`. `handle_starttag` guarda `(tag, dict(attrs))` como etiqueta
    abierta (y el ancla en `anchors`); `handle_endtag` la pone a `None`; `handle_data` añade `(tag, attrs, data.strip())`
    si hay etiqueta abierta y el texto no está en blanco. Ni los comentarios ni los atributos son texto. Cada método
    lleva un docstring de una línea.
  - `send_message`: docstring con `Yields:` (`The autospecced stand-in for FastMail.send_message.`).
  - Fixture nuevo `built_messages(send_message: Any) -> Iterator[list[MessageSchema]]`. Depende de `send_message`, así
    que nunca hay SMTP real. Aplica
    `patch.object(email_module, "MessageSchema", spec=MessageSchema, side_effect=_build)`, donde
    `_build(**kwargs: Any) -> MessageSchema` construye con la clase real, guarda el mensaje y lo devuelve. Su docstring
    dice qué registra y por qué, con `Yields:` (`The messages in build order.`).
  - `_send_and_capture(built_messages, first_name=FIRST_NAME)`: llama a la función real, comprueba
    `len(built_messages) == 1` y devuelve `built_messages[0]`. Ya no lee `await_args.args[0]` (D4).
  - `test_dispatches_...`: recibe `send_message` y `built_messages`. `send_message.assert_awaited_once_with(message)`
    compara con el mensaje **construido**. Se borra `assert isinstance(message.subject, str)`. Docstring:
    `"""Happy path: the HTML message it built for the recipient alone is the one sent."""`.
  - `test_body_carries_...`: tras las aserciones actuales del ancla, añade
    `assert len([t for tag, _, t in parser.texts if tag == "a"]) == 1` (L14). Después,
    `link_texts = [(tag, attrs) for tag, attrs, text in parser.texts if text == VERIFICATION_LINK]` y
    `assert [tag for tag, _ in link_texts] == ["p"]` (L2–L5). Por último, el `style` de ese `<p>` no es `None` y,
    normalizado con `" ".join(...split())`, vale `"font-size: 12px; color: #006875; word-break: break-all;"` (L17).
    Docstring:
    `"""The link is the button's href and, once, visible text in a styled <p>; the button has text."""`.
  - `test_smtp_failure_propagates`: recibe `built_messages`. `:99` → `assert len(built_messages) == 1` y
    `send_message.assert_awaited_once_with(built_messages[0])`.
  - `test_body_renders_...` y `test_css_braces_...`: reciben `built_messages` en lugar de `send_message`.
    `test_css_braces_...` añade `assert re.search(r"\{\s*\}", body) is None` (C10) y
    `assert re.search(r"\.btn\s*\{", body) is not None` (L15). Docstring:
    `"""Edge: doubled braces come out single, 9 rules, none empty, and the .btn rule exists."""`.
- **Tests (RED primero, copia desechable de `app/core/email.py`; el archivo tiene 6 tests):**

  | Mutante | Cambio | Antes | Después |
  |---|---|---|---|
  | L4 | el `{verification_link}` del `<p>` (l.95) dentro de `<!-- -->` | 6 passed | `1 failed, 5 passed` (body) |
  | L5 | ese `<p>` vacío, con `data-link="{verification_link}"` | 6 passed | `1 failed, 5 passed` (body) |
  | L14 | `<a ...></a>` sin texto (l.90) | 6 passed | `1 failed, 5 passed` (body) |
  | L15 | `.btn {{` → `.button {{` (l.57) | 6 passed | `1 failed, 5 passed` (css) |
  | L17 | sin `style` en el `<p>` (l.94-95) | 6 passed | `1 failed, 5 passed` (body) |
  | C10 | cuerpo de `.btn` (l.58-64) vaciado: `.btn {{ }}` | 6 passed | `1 failed, 5 passed` (css) |
  | D8 | `await fast_mail.send_message(message.model_copy(update={"subject": "x"}))` | 6 passed | `2 failed, 4 passed` (dispatches y smtp) |
  | D4 | `send_message(message=message)` | `4 failed, 2 passed` (IndexError) | 6 passed (falsa alarma retirada) |
  | L2, L3 | quitar o cambiar el segundo enlace | `1 failed` | `1 failed` (siguen muertos) |
- **Criterio de aceptación:** fila H de la tabla (548). Además,
  `grep -cE "isinstance\(message\.subject, str\)|await_args\.args\[0\]" tests/test_email.py` da 0; los avisos siguen
  siendo los 5 `StarletteDeprecationWarning`; y el comando AST del patrón 7 lista una sola línea,
  `tests\conftest.py:86 override_get_db`.
- **Fuera de alcance de esta fase:** `app/core/email.py`, incluido su docstring en español (P2 del backlog); ocultar el
  `<p>` con una regla CSS de clase (Residuales); la revisión visual del correo.
- **Commit:**
  ```text
  test(email): pin visible link, button rule and the message actually sent

  The characterization tests let through several broken emails: the
  plain-text link moved into a comment or an attribute, a button with no
  text, a renamed .btn rule, an emptied rule, the <p> without its style,
  and a copy of the message sent instead of the one built.

  - A body collector now records text nodes with their tag: the link
    must be visible text exactly once, in a <p> with its style, and the
    anchor must carry text.
  - The stylesheet has no empty rule and still defines .btn.
  - A built_messages fixture records each MessageSchema through the real
    class, so dispatch is compared with what was built, not with itself,
    and the capture no longer depends on positional arguments.
  - The isinstance check on the subject was vacuous (the schema already
    enforces str) and goes; send_message gets its Yields section.

  Only SMTP and the message constructor are doubled; no assertion reads
  Spanish text.

  Co-Authored-By: <MODELO EJECUTOR> <noreply@anthropic.com>
  ```

## Verificación final

Tras la fase H, desde `C:\projects\ecotur-asoprado`. Los números cuentan también el texto que dicta este plan: ningún
nombre, docstring ni comentario dictado coincide con estos patrones, salvo donde se indica.

```bash
# 1. Aserciones de mock sin argumentos: 0 (base 11)
grep -rnE "\.assert_(called|awaited)(_once)?\(\)" tests/ --include=*.py | wc -l
# 1b. Pares not_called + not_awaited: 0 (base 2; la fase G borra además test_token_failure_paths.py:166)
grep -rnE -A1 "\.assert_not_called\(\)" tests/ --include=*.py | grep -cE "assert_not_awaited"
# 2. Copias HTTP: 0 en la política y 3 en test_auth; la cédula heredada: 1 y 0
grep -cE "def test_(patch_hierarchy_violation|admin_cannot_provision_admin_account|admin_update_tourist_persists)" tests/test_user_access_policy.py
grep -cE "def test_(admin_patching_superadmin|admin_provisioning_admin|admin_updates_tourist_email)" tests/test_auth.py
grep -c "assert users\[0\].cedula == admin.cedula" tests/test_auth.py tests/test_user_access_policy.py   # 1 y 0
# 3. Ruff: tests/ limpio; en el repo, 8 líneas, todas app\...:1:1: I001
./venv/Scripts/python.exe -m ruff check tests/                                      # All checks passed!
./venv/Scripts/python.exe -m ruff check . --output-format=concise | grep -c "I001"  # 8
# 4. sqlalchemy.future en tests: 0 (base 2)
grep -rn "sqlalchemy.future" tests/ --include=*.py | wc -l
# 5. Comentario en español: 0 (base 1)
grep -rnE "^\s*#.*\b(Sustituimos|Creamos|Verificamos|Comprobamos|Probamos|Usamos|Simulamos|Validamos)\b" tests/ --include=*.py | wc -l
# 6. mypy: tests/ dentro; 9 errores, el conjunto de A4 y ninguno más
grep -n "^files = " pyproject.toml   # 94:files = ["app", "scripts/check_docs.py", "scripts/check.py", "tests"]
./venv/Scripts/python.exe -m mypy    # Found 9 errors in 5 files (checked 53 source files)
#   líneas: app\db\database.py:11, app\core\security.py:71 y :87, app\services\user_service.py:124,
#   app\api\dependencies.py:95, tests\test_user_service.py:105, :203, :280 y :298
# 7. Generadores sin Yields: una línea, la función anidada que queda fuera de alcance
./venv/Scripts/python.exe -I -c "import ast,pathlib;[print(f'{p}:{n.lineno} {n.name}') for p in sorted(pathlib.Path('tests').glob('*.py')) for n in ast.walk(ast.parse(p.read_text(encoding='utf-8'))) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and any(isinstance(x,ast.Yield) for x in ast.walk(n)) and 'Yields:' not in (ast.get_docstring(n) or '')]"
#   -> tests\conftest.py:86 override_get_db
# 8. Orden de guardas congelado: 1
grep -c "def test_role_guard_for_non_superadmins_runs_before_the_self_role_guard" tests/test_user_access_policy.py
# 9b-B. Raises con StaleDataError: 1 (base 0)
grep -c "StaleDataError" app/repositories/service_repository.py
# 9b-C. Mensajes distinguidos sin leerlos: 1; D2: 1; usuario borrado y activo: 3 (base 2: test_auth.py:306 y test_user_response.py:116)
grep -c "expired\.value\.detail != corrupt\.value\.detail" tests/test_token_failure_paths.py
grep -c 'assert corrupt.json()\["detail"\] == unknown.json()\["detail"\]' tests/test_token_failure_paths.py
grep -rnE "persist_user\([^)]*deleted_at" tests/ --include=*.py | wc -l
# 9b-D. Aserción vacua y captura por posición: 0
grep -cE "isinstance\(message\.subject, str\)|await_args\.args\[0\]" tests/test_email.py
# 9c. make_token con caducidad: 3 líneas en conftest y 1 uso; jwt.encode: 2 (de A4, test_user_service.py:274 y :292)
grep -c "expires_delta" tests/conftest.py
grep -c "make_token(user, expires_delta=" tests/test_token_failure_paths.py
grep -rn "jwt.encode" tests/ --include=*.py | wc -l
# 9d. Ids de la regla vieja: 0 (base 2 líneas)
grep -cE "year-by-monotony|year-resets-per-table|year-jump" tests/test_check_docs.py
# 10. app/ en todo el ítem: solo el docstring de service_repository.py
git diff --stat fd144ad -- app/    # 1 file changed, 2 insertions(+)
# 11. Compuerta: exit 1 por ruff check y mypy; 4 kept; 548 passed; cobertura >= 96.11 %
./venv/Scripts/python.exe scripts/check.py
```

## Residuales

| Hallazgo | Evidencia | Destino sugerido |
|---|---|---|
| D1 y U1 (intercambiar los textos de los dos `detail`) siguen vivos. Solo se matan leyendo el texto o con un código de error estable en el cuerpo, y eso cambia el contrato HTTP | `app/api/dependencies.py:101-108`; `app/services/user_service.py:125-132`; tabla de la fase G | Fila P3 opcional, "códigos de error estables en `detail`", con ADR si entra. Hoy es un límite aceptado |
| Ningún test provoca el `StaleDataError` que documenta la fase F. Haría falta una segunda sesión, y la trampa de importar `TestingSessionLocal` ya está medida en BE-33 | `docs/deuda/BE-33/plan.md:98-101`; `service_repository.py:86-88` | Nota en BE-31 (aislamiento real con Postgres) |
| Los `jwt.encode` con `SECRET_KEY` de `test_user_service.py` (en 274 y 292 al cerrar) construyen tokens a mano. Migrarlos borraría 2 errores del conjunto de A4 | decisión 5; P5 | Nota en la fila A4: migrarlos cuando `SECRET_KEY` salga de `security.py`, con las líneas nuevas 105/203/280/298 |
| Ocultar el enlace con una regla CSS de clase (no en el `style` del `<p>`) sobrevive. El `style` exacto del `<p>` sí mata un `display: none` inline | fase H | Revisión visual del correo (ya pendiente de BE-33) |
| `upload_image` se sigue leyendo con `call_args.args[0]` en `test_services.py:220,487`, por posición, como D4 | fase D | Sin fila: es solo el `isinstance`, y la igualdad con `_with` ya liga el argumento |
| Para el cierre (adenda 8): un opcional "→ BE-xx" que nadie llevó a su fila (el D2) | `docs/deuda/BE-33/gaps.md:141` | Nota en la fila AF-08 |

## Referencias

Context7 no estaba disponible en esta sesión. Lo no trivial se comprobó contra el código instalado. Los enlaces son la
documentación oficial de cada API y no se consultaron hoy.

- `unittest.mock` · Python 3.14.3 · el `assert_*_with` de un doble con autospec liga la llamada a la firma
  (`_call_matcher`, `C:\Python314\Lib\unittest\mock.py:911-936`), así que posición y palabra clave son equivalentes ·
  https://docs.python.org/3/library/unittest.mock.html#autospeccing
- `html.parser.HTMLParser` · Python 3.14.3 · `handle_data` no recibe comentarios ni atributos ·
  https://docs.python.org/3/library/html.parser.html
- `sqlalchemy.select` y `sqlalchemy.future` · SQLAlchemy 2.0.48 · https://docs.sqlalchemy.org/en/20/core/future.html
- `StaleDataError` · SQLAlchemy 2.0.48 ·
  https://docs.sqlalchemy.org/en/20/orm/exceptions.html#sqlalchemy.orm.exc.StaleDataError
- `ContentSettings` · azure-storage-blob 12.30.0 · igualdad por `__dict__` (`DictMixin.__eq__`,
  `azure/storage/blob/_shared/models.py:226`) ·
  https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.contentsettings
- `FastMail.send_message(message, template_name=None)` · fastapi-mail 1.6.5 (`fastmail.py:118-121`) ·
  https://sabuhish.github.io/fastapi-mail/
- `[tool.mypy] files` · mypy 2.4.0 · https://mypy.readthedocs.io/en/stable/config_file.html

## Enmiendas aprobadas

### E0 — 7 nov 2026, 11:14 (David, sesión Mentor; regla del retoque, README de sesiones)

Texto literal de David: «1.) 8 fases, 2.) p1 p5 si como recomiendas, p6 inamatble si estar 100% seguro (es decision por
flip de moneda, no por anazlizis y entendimiento, pero no me detendré hoy a decidirlo) ve y escribe lo que tengas que
escribir en el plan y voy a implementar.»

Resolución de los puntos P1–P6, en el orden del plan:

- **Ocho fases, como están.** A4 no empieza hoy; lo que no cierre el sábado recibe decisión nueva en el cierre (PLAN §3).
- **P1 → (a) 548 tests.** La adenda 5 de `verificacion.md` decía 544 por error de la sesión Mentor (restó las tres copias
  y no sumó los cuatro tests nuevos: G1, D2, U6/U7, D17). Prevalece este plan: 547 − 3 + 4 = **548**. La adenda no se
  reescribe (regla del verificador: no reescribir, añadir); esta enmienda la corrige.
- **P2 → sí.** El conjunto de A4 en `tests/test_user_service.py` se identifica por el contenido de la línea (`SECRET_KEY`
  en `jwt.decode` / `jwt.encode`) y por la línea nueva de la tabla de la decisión 5 (105/203/280/298 al cerrar). El
  auditor compara contra esa tabla.
- **P3 → sí.** El I001 de `test_user_service.py:3` se corrige en la fase B.
- **P4 → sí.** Lectura aceptada: ningún commit tiene `tests/` en `mypy.files` con errores de BE-32 vivos; la fase A
  corrige los 2 de `test_fixtures_contract.py` un commit antes por el límite de 5 archivos.
- **P5 → sí.** `make_token` solo gana `expires_delta`; los `jwt.encode` de `test_user_service.py` (274 y 292 en la base)
  se quedan. Nota en la fila A4 en el cierre.
- **P6 → D8 inmatable**, con D1 y U1 en Residuales. Decisión declarada por David como no analizada ("flip de moneda");
  se revisa cuando se estudie BE-32. **Cambios que esto produce en la fase H** (lo demás de H sigue igual):
  1. No existe el fixture `built_messages` ni el `patch.object(email_module, "MessageSchema", ...)`. Solo SMTP se dobla.
  2. `_send_and_capture(send_message, first_name=FIRST_NAME)` sigue recibiendo `send_message`. Para matar D4 (captura por
     posición), su cuerpo lee el mensaje así:
     ```python
         call = send_message.await_args
         message: MessageSchema = call.args[0] if call.args else call.kwargs["message"]
         return message
     ```
     Mutante D4 (`send_message(message=message)` en `email.py`): antes `4 failed, 2 passed` (`IndexError`); después
     `6 passed`.
  3. `test_dispatches_one_html_message_to_the_recipient`: recibe solo `send_message`; conserva
     `send_message.assert_awaited_once_with(message)` (declarado tautológico frente a D8: compara el enviado consigo
     mismo; se mantiene porque fija que la llamada fue una y con ese objeto) y borra `assert isinstance(message.subject,
     str)`. Docstring sin cambio.
  4. `test_smtp_failure_propagates` (`:99` en la base, `send_message.assert_awaited_once()`): se sustituye por
     ```python
         call = send_message.await_args
         message: MessageSchema = call.args[0] if call.args else call.kwargs["message"]
         assert [recipient.email for recipient in message.recipients] == [RECIPIENT]
     ```
     (afirma con un valor que el propio test suministró, no con texto en español; sigue cumpliendo el patrón 1 de la
     verificación final: 0 aserciones sin argumentos).
  5. `test_body_renders_...` y `test_css_braces_...` siguen recibiendo `send_message` (no `built_messages`).
  6. Tabla de mutantes de H: la fila **D8** pasa a `6 passed` antes y después, marcada «vivo: Residuales (E0)». Las
     filas L4, L5, L14, L15, L17, C10, D4, L2 y L3 no cambian.
  7. Commit de H: en el cuerpo se borra el párrafo que empieza por «A built_messages fixture records each MessageSchema»
     y se sustituye por «The capture reads the message by position or by keyword, so dispatch no longer depends on
     positional arguments.»; la última línea pasa a «Only SMTP is doubled; no assertion reads Spanish text.». El título no
     cambia.
  8. Verificación final: el patrón 9b-D (`isinstance\(message\.subject, str\)|await_args\.args\[0\]`) sigue dando 0
     (el cuerpo nuevo usa `call.args[0]`, no `await_args.args[0]`). Las demás cifras no cambian (548, ruff 8, mypy 9).
  9. Residuales: fila nueva «D8 (enviar una copia del mensaje con otro asunto) sigue vivo: matarlo exige suplantar la
     clase `MessageSchema` dentro de `email.py`; declarado inmatable por E0, como D1 y U1».
- `progress.json`: sin cambios (8 fases, `current_target` = `Fase_A`).

### E1 — 7 nov 2026, 11:55 (David, sesión Mentor; tras la auditoría de la fase B)

Texto literal de David: «super claro. ahora si, entonces todo aprobado. ve al plan con e1».

**Orden de edición en las fases C–H.** El hook `PostToolUse` de `.claude/settings.json` corre `ruff check --fix` sobre
cada archivo guardado (`.claude/hooks/ruff_on_edit.py:28`), y F401 borra un import que todavía no tiene uso. Por eso el
ejecutor escribe **primero la línea que usa el nombre nuevo y después su `import`** (o ambas en la misma edición). Afecta
a: D (`AuditAction` en `test_user_service.py`, `ContentSettings` en `test_storage.py`), G (`timedelta` en `conftest.py`;
`UTC`, `datetime`, `timedelta`, `MakeToken` en `test_token_failure_paths.py`) y H (`re` en `test_email.py`). Lo
observaron el ejecutor de B (handoff, "Desviaciones y dudas", punto 2) y el de C de BE-33. No cambia ningún "Cambios
exactos", ninguna cifra ni ningún mensaje de commit. `progress.json`: sin cambios.

### E2 — 7 nov 2026, 14:50 (David, sesión Mentor; tras la auditoría de la fase F)

**Patrón 10 de la Verificación final:** el docstring `Raises:` de `app/repositories/service_repository.py` dictado por la
fase F ocupa **3 líneas**, no 2 (ningún corte en 2 líneas cabe en 100 columnas, medido por el auditor de F). La línea
`git diff --stat fd144ad -- app/    # 1 file changed, 2 insertions(+)` se lee como **`3 insertions(+)`**. Sigue siendo el
único cambio en `app/` y es solo docstring. Ninguna otra cifra cambia. Para el cierre del ítem, no para las fases:
`replace(tzinfo=None)` en `tests/test_service_repository.py:96` solo vale en SQLite → nota en BE-31; el docstring de `:51`
(«this id's of two») → Residuales con la redacción del auditor («and of the two rows, the one returned has this id»).
