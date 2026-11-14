# Verificación — BE-34: no hay bootstrap de superadmin

**Veredicto:** confirmada
**Fuente del ítem:** docs/backlog.md (fila BE-34, l.82; origen: rincón 1 de `docs/deuda/BE-02/verificacion.md`, l.80-82).
Fila hija medida aquí: BE-47 (backlog l.96), que entra como fase de BE-34 si esta verificación la mide (la mide: ver abajo).
**Fecha:** 2026-11-13

## Qué describe el ítem
Ni `app/`, ni `alembic/`, ni `scripts/` crean un superadmin. Las dos únicas vías de producto para obtener uno (provisión
por `POST /usuarios/admin` y cambio de rol por `PATCH`) exigen ya un superadmin, así que una base sin él (instalación
nueva o tras perder el último) solo se recupera con SQL directo. La fila pide un comando o script idempotente que cree el
primer superadmin si no existe, con credenciales por configuración (`Settings`, ADR-0013) y con test.

## Evidencia en el código
Ausencia (grep global, 0 coincidencias):
- `git grep -i -E 'seed|create_superuser|create_superadmin' -- app alembic scripts` → exit 1. En `tests/` solo aparece
  "seed" como verbo de fixtures (`tests/test_services.py:45,585,601`, `tests/test_user_response.py:7`), sin relación.
- `git grep -i -E 'bootstrap|first_superadmin|initial_admin|superadmin_(email|password|cedula|first_name|last_name)'`
  sobre `app alembic scripts tests conftest.py .env.example Dockerfile docker-compose.yml .azure-pipelines` → exit 1.
- `app/core/config.py:40-64` — `Settings` no tiene ningún campo de credenciales de superadmin (15 campos: BD, JWT,
  correo, Azure, `frontend_url`, `cors_origins`).
- `alembic/versions/*` — ninguna migración inserta filas en `users`: el único `op.execute` de datos es
  `22d7d68f4844_...py:24` (`UPDATE users SET cedula = ...`); `4b3a83d69833_...py:28` solo añade el valor `'superadmin'` al
  ENUM `user_role`.
- `app/main.py` — sin `lifespan` ni `on_event("startup")`: nada se ejecuta al arrancar.
- `Dockerfile:20` — `CMD ["uvicorn", ...]` sin paso previo; `.azure-pipelines/cd-pipeline.yml:62,91,120` — solo
  `alembic upgrade head` por entorno. Ningún punto de despliegue crea un superadmin.
- `scripts/` contiene solo `check.py`, `check_docs.py`, `context_generator.py`.

Las únicas dos construcciones de `User` en `app/` (todo alta pasa por aquí):
- `app/services/user_service.py:88` — `register_tourist`: `role=UserRole.tourist` fijo (ruta pública de registro).
- `app/services/user_service.py:412` — `create_administrative_account`: `role=user_data.role`; solo se alcanza por
  `POST /usuarios/admin`, bajo `superadmin_router` (`app/api/routers/user.py:35,243`), guard
  `get_current_superadmin_user` (`app/api/dependencies.py:170-186`: `if current_user.role != UserRole.superadmin` → 403).

Única mutación de rol de una cuenta existente:
- `app/services/user_service.py:285` — `setattr(target_user, key, value)`, tras `assert_can_update`.
- `app/services/user_access_policy.py:67` — `if "role" in update_dict and actor.role != UserRole.superadmin` → 403.
- `app/services/user_access_policy.py:72` — `if is_self_update and "role" in update_dict` → 403 (BE-02).

**Líneas desplazadas respecto de la fila del backlog** (no cambian el veredicto): la fila cita
`user_access_policy.py:97` (provisión) y `l.60` (rol). BE-40 (PR #94) sacó `assert_can_provision_admin` de la política:
la provisión la decide hoy el guard `dependencies.py:186`; la regla de rol está en `user_access_policy.py:67` y `:72`.

Piezas que una solución reutilizaría o debe respetar (lectura, no deuda de BE-34):
- `app/repositories/user_repository.py:16` — `get_user_by_email_or_cedula`; no existe consulta por rol ni conteo de
  superadmins (métodos en l.16, 22, 27, 33, 46, 68, 82, 91).
- `app/repositories/user_repository.py:27-31` — `create_user` hace `commit()` (deuda A3, AGENTS §3).
- `app/models/user.py:38-39` — `cedula` y `email` únicos; `:44-46` `role` con `default=UserRole.tourist`;
  `:47-48` `data_consent` e `is_active` con `default=False` (un bootstrap debe fijar `is_active=True` explícito).
- `app/models/audit.py:47` — `performed_by: Mapped[str]` (NOT NULL): un alta auditada necesita un autor; no hay actor
  autenticado en un bootstrap.

### BE-47 (fila hija), medida
- `conftest.py:10-26` — `TEST_ENVIRONMENT` tiene hoy las 15 claves de `Settings`: no hay violación actual.
- `git grep -n 'TEST_ENVIRONMENT' -- tests` → exit 1: ningún test lo compara con `Settings.model_fields`. Confirmada.
- `tests/test_config.py:219` exige la clave en `.env.example` (`<= set(dotenv_values(ENV_EXAMPLE))`), no en
  `TEST_ENVIRONMENT`.
- `tests/test_config.py:188-189` (`get_settings() == Settings(_env_file=None)`) solo detecta el hueco si el `.env` de quien
  corre la suite trae esa clave; en CI (sin `.env`) pasa siempre. Protección dependiente del entorno, no determinista.
- `tests/test_config.py:24-45,105` — `REQUIRED`/`OPTIONAL_DEFAULTS` inventarían los campos y l.105 exige igualdad con
  `Settings.model_fields`: todo campo nuevo de BE-34 obliga a tocar este inventario.

## Ficheros afectados (mapa completo)
- `app/core/config.py` — `Settings` sin campos de credenciales de superadmin (l.40-64).
- `app/services/user_service.py` — únicas altas de `User` (l.88 turista fijo, l.412 solo bajo guard de superadmin);
  única mutación de rol (l.285).
- `app/api/routers/user.py` — `POST /usuarios/admin` bajo `superadmin_router` (l.35, 243).
- `app/api/dependencies.py` — guard `get_current_superadmin_user` (l.170-186).
- `app/services/user_access_policy.py` — cambio de rol solo por superadmin (l.67) y nunca sobre sí mismo (l.72).
- `alembic/versions/` — ninguna migración de datos crea un superadmin (sin cambio esperado: ADR-0013 y AGENTS §3 dejan
  las credenciales en `Settings`, no en una migración).
- `scripts/` — sin script de bootstrap.
- `Dockerfile`, `.azure-pipelines/cd-pipeline.yml` — arranque y despliegue sin paso de bootstrap (l.20; l.62, 91, 120).
- `.env.example`, `conftest.py` (`TEST_ENVIRONMENT`), `tests/test_config.py` (`REQUIRED`/`OPTIONAL_DEFAULTS`, l.105,
  l.219) — tocados obligatoriamente por cualquier campo nuevo de `Settings` (ADR-0013, punto 6).
- `tests/test_config.py` — falta la aserción de BE-47 (`Settings.model_fields` ⊆ `TEST_ENVIRONMENT`).
- `tests/` — ningún test de bootstrap.

## Rincones no mencionados por la fuente
1. **Arranque en blanco, no solo pérdida del último superadmin.** La fila enfoca "si la base queda sin superadmin"; el
   mismo hueco existe desde la primera instalación: tras `alembic upgrade head` (lo único que corre el CD) la tabla `users`
   está vacía y no hay forma de producto de crear el primer administrador.
2. **Autor de auditoría sin actor.** `audit_logs.performed_by` es NOT NULL (`app/models/audit.py:47`); el registro de turista
   usa su propia cédula (`user_service.py:101`). Si el bootstrap audita el alta, el plan debe fijar qué autor registra.
3. **Herramientas de la compuerta no cubren `scripts/` nuevos.** `pyproject.toml:90` lista en `mypy` solo
   `scripts/check_docs.py` y `scripts/check.py`; `pyproject.toml:135` mide cobertura solo de `app`; `import-linter` usa
   `root_package = "app"`. Un script nuevo en `scripts/` quedaría fuera de mypy, de la cobertura y de los contratos salvo
   que el plan lo prevea (o ponga la lógica en `app/`).
4. **`create_user` hace `commit()`** (`user_repository.py:29`, deuda A3): reutilizarlo en el bootstrap hereda la deuda; no es
   alcance de BE-34 corregirlo.

## Patrones de detección (copiables)
```bash
# 1. Bootstrap/seed de superadmin (hoy 0 coincidencias, exit 1)
git grep -n -i -E 'seed|create_superuser|create_superadmin' -- app alembic scripts

# 2. Credenciales/bootstrap en código, config y despliegue (hoy 0 coincidencias, exit 1)
git grep -n -i -E 'bootstrap|first_superadmin|initial_admin|superadmin_(email|password|cedula|first_name|last_name)' -- app alembic scripts tests conftest.py .env.example Dockerfile docker-compose.yml .azure-pipelines

# 3. Puntos de alta de User con rol (hoy: user_service.py:88 turista fijo, :412 bajo guard de superadmin)
git grep -n -E 'role=(UserRole\.|user_data\.role)' -- app

# 4. Guardas que exigen un superadmin previo (hoy: dependencies.py:199, routers/user.py:35, user_access_policy.py:67, :72)
git grep -n -E '"role" in update_dict|get_current_superadmin_user\)' -- app

# 5. BE-47: ningún test compara TEST_ENVIRONMENT con Settings (hoy 0 coincidencias, exit 1)
git grep -n 'TEST_ENVIRONMENT' -- tests
```

## Línea base (`scripts/check.py` con el Python del venv por ruta, AGENTS §6)
- Base develop: `4f10660` (`git fetch origin` correcto; `git merge-base HEAD origin/develop` = `git rev-parse
  origin/develop` = `HEAD`: precondición cumplida, la rama `item/be-34` está en `develop` sin commits propios)
- Comando: `./venv/Scripts/python.exe scripts/check.py` (exit 0), Python 3.14.3

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
- pytest: `638 passed, 8 warnings in 18.02s` (0 failed)
- Cobertura total: `96.82%` (`TOTAL 965 19 136 16 96.82%`; mínimo exigido 92.0 %)
- ruff format: `61 files already formatted` · ruff check: `All checks passed!` (0)
- mypy: `Success: no issues found in 56 source files` (0)
- import-linter: `Contracts: 4 kept, 0 broken.`
- docs: `Documentación coherente (reglas: R1 comandos, R2 fechas de cronograma, R3 bloques, R4 decisiones, R5 deadline).`

La compuerta pasa antes de tocar nada.

## Conclusión para el planificador
- Resolver: un mecanismo idempotente que cree el primer superadmin solo si no hay ninguno (activo y no borrado: decidir y
  fijar en test qué cuenta como "existe"), con credenciales en campos nuevos de `Settings` (ADR-0013), su línea en
  `.env.example`, su valor en `TEST_ENVIRONMENT` y su entrada en `REQUIRED`/`OPTIONAL_DEFAULTS` de `tests/test_config.py`.
  Decidir dónde vive (lógica en `app/` para que mypy, cobertura e import-linter la midan; envoltorio en `scripts/` o
  similar) y cómo se invoca en el despliegue (hoy el CD solo corre `alembic upgrade head`). Probablemente es decisión no
  trivial (módulo nuevo y punto de entrada): valorar ADR.
- BE-47 queda medida (sin violación hoy, sin test): entra como fase del plan, idealmente antes de añadir los campos, con su
  mutante (quitar una clave de `TEST_ENVIRONMENT`).
- No tocar: reglas de la política (BE-35..BE-38), guards y rutas existentes, `create_user` con `commit()` (A3), ni una
  migración de datos con credenciales (los secretos no van en `alembic/`).
- Riesgos: credenciales por defecto o débiles en `.env.example`/producción (el valor de ejemplo no debe servir de clave
  real; validar la contraseña con las mismas reglas que `UserCreate`); idempotencia ante choque de `email`/`cedula` con una
  cuenta existente no superadmin (¿falla, promueve o ignora? decidirlo explícito); `performed_by` NOT NULL si se audita;
  el bootstrap no debe convertirse en puerta de escalada (que no promueva cuentas existentes en silencio).

## Adenda — decisiones de David antes de planear (13 nov 2026, 16:28, sesión Mentor)

Resuelve lo que la conclusión deja abierto. El planificador las toma como dadas; lo demás (fases, tests, commits, nombres)
es suyo. Regla del verificador: no reescribir, añadir. **Veredicto aceptado: confirmada. Línea base aceptada:** `4f10660`,
compuerta completa en verde (638 passed · 96,82 % · ruff 0 · mypy 0 en 56 archivos · 4 kept). Severidad: Alta, la de la
fila. Contraste de la sesión Mentor contra el código, sin correcciones de hecho: `user_service.py:84-104,283-286,388-425`,
`user_access_policy.py:64-73`, `routers/user.py:33-36,241-246`, `dependencies.py:168-200`, `user_repository.py:14-32`,
`models/user.py:34-52`, `models/audit.py:44-48`, `core/config.py:30-66`, `pyproject.toml:88-91,132-136`, `Dockerfile`,
`cd-pipeline.yml:50-66` y sus líneas 91 y 120, `tests/test_config.py:20-48,100-107,184-190,212-220` y el `conftest.py` de
la raíz. Única precisión: el patrón 4 rotula `dependencies.py:199` como guarda y es el alias `SuperadminDep`; la guarda es
la l.186, que el cuerpo de la verificación cita bien. David aprobó los ocho puntos a las 16:28 ("sí a las 7"; el punto 8
es la consecuencia del 3 sobre BE-47, explicada antes de aprobar).

Tres hechos que la verificación no trae y que condicionan las decisiones (medidos por la sesión Mentor):
- **No existe cambio de contraseña en la aplicación.** `UserUpdate` (`app/schemas/user.py:152`) no tiene el campo y
  `git grep -i password -- app/api app/services` solo da login y altas. La contraseña con que nazca el superadmin es la
  definitiva hasta que exista esa función.
- **El CD solo pasa `DATABASE_URL` al contenedor de migraciones** (`cd-pipeline.yml:62,91,120`). Un proceso que construya
  `Settings` completo no arranca ahí sin los otros cuatro secretos (el caso de Alembic en A4; ADR-0013, punto 5).
- **El motor se crea con `echo=True`** (`app/db/database.py:7`): el `INSERT` del alta saldría por la salida estándar con
  sus parámetros (correo, cédula, hash bcrypt). No ejecutado hoy; la fila A5 lo recoge como medido el 10 nov en el log de
  uvicorn `(backlog A5)`, que es la dueña de `echo`; BE-34 no toca `app/db/database.py`.

1. **Dónde vive: en `app/`.** La lógica es una función núcleo que recibe la sesión y las credenciales ya validadas, más un
   punto de entrada delgado ejecutable con `python -m`. Nada nuevo en `scripts/`: quedaría fuera de mypy
   (`pyproject.toml:90`), de la cobertura (`:135`) y de los contratos de import-linter (rincón 3). Módulo, nombres y capa
   los elige el planificador; el núcleo no importa FastAPI ni Starlette y respeta los cuatro contratos. Como
   `source = ["app"]`, el punto de entrada también cuenta para la cobertura: se prueba o el plan declara cuánto baja y
   por qué.
2. **Cómo se invoca: comando manual del operador**, de la misma forma que el CD corre las migraciones
   (`docker run --rm -e ... <imagen> python -m ...`). **No** es una ruta HTTP (una ruta de "setup" sería pública; las
   tablas de `tests/test_route_guards.py` no cambian), **no** corre en `lifespan` ni al arrancar la app, y **no** se añade
   paso a `cd-pipeline.yml`; el `CMD` del `Dockerfile` no se toca. Razón: un paso de CD obliga a guardar una contraseña
   que no se puede cambiar en los tres grupos de variables y la deja al alcance del log del pipeline (`echo=True`).
   Coste aceptado por David: hay que correrlo una vez por entorno y documentarlo; el modo de uso queda en el docstring
   del punto de entrada y el manual técnico lo recoge en su bloque `(PLAN §2b)`.
3. **Dónde se leen las credenciales: una clase propia en `app/core/config.py` que hereda de `DatabaseSettings`**, hermana
   de `Settings`, construida solo por el comando. `Settings` **no gana campos** (sigue en 15): la Web App ni pide ni
   guarda la contraseña del superadmin, y el comando no exige `JWT_SECRET_KEY`, las de correo ni la de Azure Storage.
   Cumple AGENTS §3 (toda variable de entorno se lee en ese módulo). Campos obligatorios, sin valor por defecto; los
   nombres los fija el planificador. Lo que el plan resuelve y justifica:
   - cómo se documentan en `.env.example` sin que el valor de ejemplo sirva de credencial real: **el ejemplo de
     contraseña no debe pasar la validación del punto 6**;
   - cómo se prueba la clase sin leer el `.env` de quien corre la suite (ADR-0013, consecuencias (a) y (c): la clase con
     `_env_file=None` y `monkeypatch`; el núcleo recibe las credenciales como argumento), y si `TEST_ENVIRONMENT`
     necesita claves para ella.
4. **Qué cuenta como "ya existe" y qué pasa si choca.** Si hay al menos un superadmin **activo y no borrado**
   (`role == superadmin`, `is_active`, `deleted_at IS NULL`), el comando no escribe nada y termina con código 0 (es la
   idempotencia: la segunda corrida no hace nada). Si no hay ninguno y la cédula o el correo configurados ya existen en
   **cualquier** fila (cualquier rol, activa, inactiva o borrada; `models/user.py:38-39` los hace únicos), el comando
   falla con código distinto de 0 y no escribe nada: **no promueve, no reactiva y no recupera** cuentas existentes (no es
   puerta de escalada). Si los superadmins que hay están todos inactivos o borrados y las credenciales no chocan, crea
   uno nuevo. La consulta "¿hay superadmin activo?" es nueva en `user_repository.py`; BE-35 necesitará contar lo mismo:
   el planificador la deja reutilizable sin implementar nada de BE-35. Tests mínimos: base vacía → crea; ya existe →
   no escribe; segunda corrida → no escribe; choque → falla sin mutar; solo superadmins inactivos o borrados → crea.
5. **Auditoría: el alta se registra.** `CREATE` sobre `User`, `entity_id` la cédula nueva, `performed_by` **la cédula del
   propio superadmin** (precedente: `register_tourist`, `user_service.py:97-102`; `performed_by` es NOT NULL,
   `models/audit.py:47`) y `changes` con el rol, como `create_administrative_account` (`user_service.py:417-423`). Si
   conviene una marca que distinga el bootstrap de un alta normal, el planificador la propone.
6. **Validación: las credenciales pasan por `UserCreateByAdmin`** (`app/schemas/user.py:122`), sin duplicar las reglas de
   cédula, nombres y contraseña (`:19-119`); `role=superadmin`, `is_active=True` y `data_consent=True` explícitos; hash
   con `get_password_hash`. **La contraseña no se imprime nunca**: ni en el mensaje de éxito, ni en el de "ya existe", ni
   en un error. Riesgo que el plan mide con sonda antes de dictar: el `ValidationError` de un modelo Pydantic incluye
   `input_value` en su texto (el `hide_input_in_errors` de `config.py:34` cubre la clase de configuración, no a
   `UserCreateByAdmin`); el comando no puede volcar esa excepción tal cual. `create_user` hace `commit()`
   (`user_repository.py:29`, A3): reutilizarlo se acepta; no se corrige aquí.
7. **ADR: sí, ADR-0015**, redactado por el planificador en su paso 6: módulo y punto de entrada nuevos, y dónde viven
   (y dónde no) las credenciales de arranque (AGENTS §7). Alternativas que debe recoger: paso de CD, `lifespan`, ruta
   HTTP, campos en `Settings`, migración de datos.
8. **BE-47 entra como fase, la primera.** Con el punto 3, BE-34 ya no añade campos a `Settings`, que era la razón de la
   fila para venir aquí `(backlog BE-47)`; entra igual por la decisión de David del 11 nov, porque esta verificación la
   midió y confirmó: un test en `tests/test_config.py`
   (`{n.upper() for n in Settings.model_fields} <= set(TEST_ENVIRONMENT)`) con su mutante (quitar una clave). El
   plan dice si la clase nueva del punto 3 necesita una vigilancia equivalente.

**No se toca** (de la conclusión, sin cambios): reglas de la política (BE-35..BE-38), guards, routers y rutas existentes,
`Settings`, `app/db/database.py`, `alembic/`, `cd-pipeline.yml`, `Dockerfile`, `docker-compose.yml`. **Fuera de alcance,
declarado:** cambio de contraseña (no existe; si se quiere, es feature con fila), `echo=True` (A5).
