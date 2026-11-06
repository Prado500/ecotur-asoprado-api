# Verificación — A2: tres estrategias de autorización incompatibles

**Veredicto:** parcial
**Fuente del ítem:** docs/backlog.md (§A2, fila `A2`, l.86) + informe `docs/archive/auditorias/Auditoría Ecotur-ASOPRADO.html` (tarjeta `A2`, l.452-470; plan de remediación, fase 2, l.1094)
**Fecha:** 2026-11-06

## Qué describe el ítem

El informe (21 sep, HEAD `f0de961`) dice que no hay una frontera de autorización definida: conviven "guard admin +
re-chequeo en servicio" (13 endpoints), "guard user + RBAC completo en servicio" (3) y "sin guard" (6). Recomienda
una sola frontera: guard IoC para la autorización gruesa por rol y, en el servicio, solo las reglas que dependen del
dato. El backlog lo deja como decisión: "Decidir en `B-TESTS` (revisar guard + política por endpoint)".

## Evidencia en el código

### Lo corregido desde el informe

- La estrategia "guard user + RBAC completo" ya no existe como la describe el informe: `GET /usuarios/` cuelga de
  `admin_router` (`app/api/routers/user.py:37,178`) y `/auditoria` tiene guard admin de router
  (`app/api/routers/audit.py:8`).
- Los re-chequeos de rol en `/servicios` desaparecieron: `app/services/tourist_services_service.py` usa
  `current_user` solo para `performed_by` (l.74, 136, 173, 215, 343) y `_verify_admin` tiene 0 ocurrencias en `app`,
  `tests` y `alembic`.
- Ningún servicio compara roles fuera de la política: todas las comparaciones `role ==`/`!=`/`in`/`not in` de `app/`
  están en `app/services/user_access_policy.py`, salvo el guard (`app/api/dependencies.py:132`).

### Lo que persiste

1. **Re-chequeo redundante en `GET /auditoria/`, y declarado.** Mismo predicado en dos capas:
   - `app/api/routers/audit.py:8` — `router = APIRouter(dependencies=[Depends(get_current_admin_user)])`
   - `app/services/audit_service.py:65` — `self.user_access_policy.assert_is_admin_plus(current_user)`
   - `app/api/routers/audit.py:28-32` lo justifica: "Defense in depth... the service layer re-asserts the same
     administrative rule".
2. **Regla solo de rol dentro de la política, sin dato.** Ninguna de las dos recibe un `target`:
   - `app/services/user_access_policy.py:115-133` — `assert_is_admin_plus(actor)`; la comprobación está en l.130.
   - `app/services/user_access_policy.py:98-113` — `assert_can_provision_admin(actor)`; la comprobación está en l.109;
     se llama en `app/services/user_service.py:396`. No es redundante (es más estricta que el guard), pero queda en el
     lado contrario al que fija AGENTS §3 ("guard IoC ... para el rol; `UserAccessPolicy` para reglas que dependen del
     dato"). `app/services/user_service.py:379-383` la defiende como "intentional hierarchical business rule, not a
     duplicate of the transport frontier". `app/api/dependencies.py` no tiene guard de superadmin.
   - **Efecto medido:** en `POST /usuarios/admin` con cuerpo `{}`, un turista recibe 403 (guard) y un admin 422; el
     admin solo recibe 403 con un cuerpo válido (`tests/test_auth.py:361`), porque la regla corre después de validar.
3. **El código se contradice en cuál es la regla.**
   - `app/api/routers/user.py:31-32` — "Services ... never duplicate the transport-level authorization frontier."
   - `app/api/routers/audit.py:28-30` — el docstring citado arriba hace justo eso.
   - `app/services/user_access_policy.py:120-121` — "stays reusable for any operation restricted to administrative
     tiers", con el mensaje fijo de auditoría en l.132 ("...visualizar la auditoría del sistema").
4. **El predicado "es administrador" sigue escrito en dos sitios**, más una variante:
   - `app/api/dependencies.py:132` y `app/services/user_access_policy.py:130` — `role not in [UserRole.admin, UserRole.superadmin]`
   - `app/services/user_access_policy.py:93` — `target.role in [UserRole.admin, UserRole.superadmin]`
5. **Tres formas de inyectar la identidad bajo un guard admin**, y la tercera no se lee como lo que es:
   - `app/api/routers/user.py:21` — alias `AdminDep`
   - `app/api/routers/service.py:89,146,170,191,212,234` — `= Depends(get_current_admin_user)`
   - `app/api/routers/audit.py:24` — `= Depends(get_current_user)` en un router con guard admin

### Hallazgo no previsto: el guard de rol no tiene ningún test que dependa de él

Medido con mutantes sobre una copia desechable (`git archive HEAD` en el scratchpad, `app/` del repo intacto; suite sin
`tests/test_check.py` ni `tests/test_check_docs.py`, que no importan `app`; línea base de la copia: 259 passed).

| Mutante | Resultado |
|---|---|
| M7: `get_current_admin_user` no comprueba el rol (`dependencies.py:132` → `if False:`) | **259 passed** |
| M1: sin guard de router en `/servicios` (`service.py:24`) | **259 passed** |
| M2: todo `/servicios` admin pasa a `get_current_user` | **259 passed** |
| M3: M1 + M2 (3 handlers sin identidad quedan anónimos, 6 abiertos a cualquier autenticado) | **259 passed** |
| M6: `AdminDep` y `admin_router` de `/usuarios` a `get_current_user` | **259 passed** |
| M4: sin guard de router en `/auditoria` (`audit.py:8`) | **259 passed** |
| M5: sin re-chequeo en `audit_service.py:65` | 1 failed: `TestAuditServiceAuthorization::test_tourist_raises_authorization_error_and_repo_never_called` |
| M8: sin `assert_can_provision_admin` (`user_service.py:396`) | 3 failed: `test_admin_provisioning_admin_returns_403_without_row`, `test_admin_cannot_provision_admin_account_403_and_no_db_mutation`, `test_create_administrative_account_rejects_non_superadmin` |

Bajo M7, medido por HTTP con token de turista (sin datos sembrados): `GET /usuarios/`, `GET /usuarios/admin/eliminados`,
`GET /servicios/admin/inactivos` y `GET /servicios/admin/eliminados` → 200; `PUT`, `activar`, `desactivar` y `DELETE` de
`/servicios/{id}`, y `PATCH /usuarios/{cedula}/recuperar` → 404, no 403; `POST /servicios/`, `POST /servicios/upload-images/`
y `POST /usuarios/admin` con cuerpo `{}` → 422; `PATCH /servicios/{id}/recuperar` → 400. Solo `/auditoria/` sigue en 403,
por el re-chequeo.

Causas leídas en el código:
- `tests/test_services.py` no contiene ningún `UserRole.tourist` ni ningún `status_code == 401/403`.
- El único test HTTP de turista contra un endpoint de guard admin es `tests/test_audit.py:49`, y no distingue qué capa
  respondió: guard y re-chequeo dan 403 con `{"detail": str}` (ver backlog P2, campo `code`).
- La cobertura no lo revela: `dependencies.py:133` se ejecuta (solo falta l.63), pero ningún test depende de él.
- La política no cierra sola si el guard falta: `assert_can_recover` (`user_access_policy.py:93`) y `can_see` (l.147)
  dejan pasar a un turista. Es coherente con una frontera única, pero hace del guard el único control.

### Inventario por endpoint (22 rutas, medido sobre `app.routes` y el árbol de dependencias)

| Clase | Rutas | N |
|---|---|---|
| Sin guard (público) | `POST /usuarios/registro` (`user.py:45`), `GET /usuarios/verificar-email` (`:81`), `POST /usuarios/login` (`:95`), `GET /servicios/` (`service.py:32`), `GET /` (`main.py:211`) | 5 |
| Guard user, sin regla de servicio | `GET /usuarios/mi-perfil` (`user.py:114`) | 1 |
| Guard user + regla de dato (conforme) | `DELETE /usuarios/{cedula}` (`user.py:127` → `user_service.py:204`), `PATCH /usuarios/{cedula}` (`user.py:147` → `user_service.py:280`) | 2 |
| Guard admin solo (conforme) | `/servicios` admin: `service.py:50,86,110,126,142,166,187,208,230` | 9 |
| Guard admin + regla de dato (conforme) | `GET /usuarios/` (`user.py:178` → `user_service.py:243`), `GET /usuarios/admin/eliminados` (`user.py:197` → `user_service.py:321`), `PATCH /usuarios/{cedula}/recuperar` (`user.py:216` → `user_service.py:351`) | 3 |
| Guard admin + regla solo de rol, más estricta (**no conforme**) | `POST /usuarios/admin` (`user.py:238` → `user_service.py:396`) | 1 |
| Guard admin + la misma regla repetida (**no conforme**) | `GET /auditoria/` (`audit.py:11` → `audit_service.py:65`) | 1 |

Respuestas medidas sin mutar: anónimo 401 y turista 403 en los 14 endpoints de guard admin; anónimo 401 en los 3 de
guard user.

## Ficheros afectados (mapa completo)

- `app/api/dependencies.py` — guard admin (l.119-136, predicado en l.132); sin guard de superadmin; `get_audit_service` inyecta la política solo para el re-chequeo (l.44-48).
- `app/services/user_access_policy.py` — `assert_can_provision_admin` (l.98-113), `assert_is_admin_plus` (l.115-133), variante del predicado (l.93).
- `app/services/audit_service.py` — dependencia de la política (l.6, 12, 14) y re-chequeo (l.65); docstring y `Raises` (l.46-50, 62-63).
- `app/services/user_service.py` — llamada (l.396) y docstring (l.379-383, 392-393).
- `app/api/routers/audit.py` — guard (l.8), identidad con `get_current_user` (l.5, 24), docstring (l.28-32).
- `app/api/routers/user.py` — comentario de la frontera (l.24-33), `POST /admin` (l.238-259, docstring l.246-247).
- `app/api/routers/service.py` — sin deuda de estrategia; es el mayor hueco de tests (l.24, 50-249).
- `tests/test_audit.py` — `TestAuditServiceAuthorization` congela el re-chequeo (l.66-111); único test HTTP de turista (l.49).
- `tests/test_user_access_policy.py` — `TestAssertIsAdminPlus` (desde l.260) y el bloque de provisión (l.239-256, l.384).
- `tests/test_user_service.py` — `test_create_administrative_account_rejects_non_superadmin` (l.346).
- `tests/test_auth.py` — `test_admin_provisioning_admin_returns_403_without_row` (l.361).
- `tests/test_services.py` — sin ningún caso de rechazo por rol o sesión.
- `alembic/` — sin deuda: la única coincidencia es la columna `role` (`a0f621304d75_init_esquema_inicial_limpio.py:44`).

## Rincones no mencionados por la fuente

- El guard de rol no tiene ningún test que dependa de él (sección anterior). No figura en BE-15 ni en BE-32.
- Ningún ADR recoge la frontera de autorización: el grep de `get_current_admin|UserAccessPolicy|autorización` en
  `docs/adr/` da 0 coincidencias. La regla solo está en AGENTS §3.
- `app/api/routers/service.py:115` — el docstring dice "active JWT session with an 'admin' role payload", pero el rol
  sale de la base (`dependencies.py:111`), ningún código lee el claim `role` emitido en `user_service.py:171`, y
  superadmin también pasa.
- Solapamiento con D6/S3 (`Annotated` frente a `= Depends(`) en las tres formas de inyección; D6/S3 sale a `B-FUTURO`.

## Patrones de detección (copiables)

```bash
# Reglas solo de rol en la política y sus usos (13 líneas hoy)
grep -rnE "assert_is_admin_plus|assert_can_provision_admin" app tests --include=*.py
# El predicado "es administrador" (3 líneas hoy)
grep -rn "UserRole.admin, UserRole.superadmin" app --include=*.py
# Comparaciones de rol (7 líneas hoy: 6 en la política, 1 en el guard)
grep -rnE "role (==|!=|in |not in )" app --include=*.py
# Guards e identidad en routers (13 líneas hoy)
grep -rnE "Depends\(get_current_(admin_)?user\)" app/api/routers --include=*.py
# La contradicción de comentarios (2 líneas hoy)
grep -rn "Defense in depth\|never duplicate" app --include=*.py
# Huecos de test: rechazo por rol o sesión en /servicios (0 líneas hoy)
grep -rnE "UserRole\.tourist|status_code == 40[13]" tests/test_services.py
# Regresión de B1 (0 líneas hoy)
grep -rn "_verify_admin" app tests alembic --include=*.py
```

## Línea base (`scripts/check.py` con el Python del venv por ruta, AGENTS §6)

- Base develop: `86256b2` (`git fetch origin` correcto; `git merge-base HEAD origin/develop` = `git rev-parse origin/develop`)
- Comando: `./venv/Scripts/python.exe scripts/check.py` (salida redirigida a un fichero del scratchpad; exit 1)
- **La compuerta ya falla antes de tocar nada** (ruff y mypy); ninguno de los 14 errores es de A2.

```
=== RESUMEN ===
  ✔ ruff format --check
  ✘ ruff check
  ✘ mypy
  ✔ import-linter
  ✔ docs (coherencia)
  ✔ pytest + cobertura

Compuerta NO superada: ruff check, mypy
```

- **ruff format:** 57 files already formatted.
- **ruff check:** 9 errors, todos `I001`: `app/api/dependencies.py:1`, `app/api/routers/audit.py:1`, `app/core/email.py:1`, `app/db/database.py:1`, `app/repositories/user_repository.py:1`, `app/schemas/audit.py:1`, `app/services/audit_service.py:1`, `app/services/user_service.py:1`, `tests/test_user_service.py:3`.
- **mypy:** Found 5 errors in 4 files (checked 35 source files), todos `arg-type`: `app/db/database.py:11`, `app/core/security.py:71`, `app/core/security.py:87`, `app/services/user_service.py:124`, `app/api/dependencies.py:95`.
- **import-linter:** Contracts: 4 kept, 0 broken.
  - Capas: api -> services -> repositories -> models KEPT
  - Los servicios no conocen el transporte HTTP KEPT
  - Los repositorios solo conocen SQLAlchemy y los modelos KEPT
  - Los modelos y los schemas no dependen de capas superiores KEPT
- **docs:** Documentación coherente (R1–R5).
- **pytest:** 438 passed, 0 failed, 5 warnings in 12.39s.
- **cobertura:** Total coverage: 96.11% (piso exigido 92.0%).

Tres de los ficheros en rojo por `I001` (`dependencies.py`, `audit.py`, `audit_service.py`) y dos por mypy
(`dependencies.py:95`, `user_service.py:124`) están en el mapa de A2.

## Conclusión para el planificador

- **Debe resolver:** (1) la decisión pendiente del backlog, por escrito: frontera única con el guard para el rol y la
  política para el dato, y qué pasa con las dos reglas no conformes (`GET /auditoria/`, `POST /usuarios/admin`);
  AGENTS §7 pide ADR y hoy no hay ninguno. (2) Si la frontera es el guard, tests HTTP que dependan de él en los 14
  endpoints de guard admin: es el hallazgo de más riesgo y el backlog no lo registra. Tests RED primero y re-ejecutar
  M1–M7 para comprobar que ahora fallan.
- **No debe tocar:** la regla de dato de `assert_can_update`, `assert_can_delete`, `assert_can_recover` y `can_see`
  (BE-34..BE-38, `B-GHOST-ADMIN`); `Annotated` frente a `Depends` (D6/S3, `B-FUTURO`); los `commit()` (A3); `I001` y los
  errores de mypy (A4); el campo `code` en errores (P2).
- **Riesgos:** quitar el re-chequeo de auditoría cambia `AuditService.__init__`, `get_audit_service` y los tests de
  l.66-111 de `tests/test_audit.py` y `TestAssertIsAdminPlus`, y hace que `tests/test_audit.py:49` pase a depender del
  guard. Llevar la provisión a un guard cambia un contrato observable: admin con cuerpo inválido pasa de 422 a 403, y el
  cliente Flutter debe confirmarlo; los tres tests de M8 siguen siendo la red. Conservar cualquiera de las dos reglas es
  una opción válida si queda justificada y se corrige la contradicción de comentarios (`user.py:31-32` frente a
  `audit.py:28-32`).
- **Esfuerzo:** la estimación S del backlog cubre la decisión y los dos cambios puntuales; la matriz de tests por
  endpoint no estaba contada al estimarla.
