# ADR-0015 — Primer superadmin: comando manual `python -m app.cli.bootstrap_superadmin`, credenciales fuera de `Settings`

- **Estado:** aceptado (David, 13 nov 2026, al aprobar el plan de BE-34)
- **Propuesta:** Claude, `plan-redactor` (13 nov 2026), sobre la adenda de David a la verificación (13 nov, 16:28)
- **Ubicación en el repo:** `docs/adr/0015-bootstrap-del-primer-superadmin.md`
- **Origen:** backlog BE-34; `docs/deuda/BE-34/verificacion.md` (veredicto y adenda de ocho puntos);
  `docs/deuda/BE-34/plan.md`. Relación: ADR-0013 (añade una clase hermana de `Settings`), ADR-0012 (el comando no pasa
  por guards ni política), ADR-0003 (reutiliza `AlreadyExistsError`).

## Contexto

Las dos vías de producto para tener un superadmin exigen ya uno: `POST /usuarios/admin` (guard
`get_current_superadmin_user`) y el cambio de rol por `PATCH` (`UserAccessPolicy`). Ni `app/`, ni `alembic/`, ni `scripts/`
crean uno. Tras `alembic upgrade head`, lo único que corre el CD, la tabla `users` está vacía, y si se pierde el último
superadmin solo se recupera con SQL directo. La aplicación no tiene cambio de contraseña: la contraseña con que nazca el
superadmin es la definitiva. El CD solo pasa `DATABASE_URL` al contenedor de migraciones, y el motor de la app escribe
cada sentencia con sus parámetros (`echo=True`, backlog A5).

## Decisión

1. **Lógica en `app/`, en dos piezas.** El núcleo, `bootstrap_superadmin` (`app/services/superadmin_bootstrap.py`),
   recibe credenciales ya validadas y los repositorios. El punto de entrada, `app/cli/bootstrap_superadmin.py` (paquete
   nuevo `app.cli`), lee la configuración, valida, abre su motor y traduce el resultado a código de salida. Nada en
   `scripts/`. `app.cli` entra en el contrato de capas como hermano independiente de `app.api` (`"app.api | app.cli"`).
2. **Invocación manual, una vez por entorno**, con la imagen que despliega el CD:
   `docker run --rm -e DATABASE_URL=… -e SUPERADMIN_CEDULA=… -e SUPERADMIN_EMAIL=… -e SUPERADMIN_FIRST_NAME=…
   -e SUPERADMIN_LAST_NAME=… -e SUPERADMIN_PASSWORD=… <imagen> python -m app.cli.bootstrap_superadmin`. No es ruta HTTP,
   no corre en `lifespan` ni al arrancar y no es paso del CD.
3. **Credenciales en `SuperadminBootstrapSettings(DatabaseSettings)`** (`app/core/config.py`), hermana de `Settings` y
   construida solo por el comando. Tiene cinco campos obligatorios; la contraseña es `SecretStr`. `Settings` sigue con 15
   campos. `.env.example` las documenta con una contraseña de ejemplo que no pasa la validación.
4. **"Ya existe" = al menos un superadmin activo y no borrado** (`UserRepository.count_active_superadmins`). Si existe, no
   se escribe nada y el comando sale con 0. Si la cédula o el correo están en cualquier fila (cualquier rol o estado):
   `AlreadyExistsError`, no se escribe nada y sale con 1. El comando no promueve, no reactiva ni recupera cuentas.
5. **Validación con `UserCreateByAdmin`**, sin repetir reglas. El núcleo fija `role=superadmin`, `is_active=True` y
   `data_consent=True` aunque las credenciales digan otra cosa.
6. **Auditoría:** `CREATE` sobre `User`, con `entity_id` y `performed_by` = la cédula del nuevo superadmin (no hay actor,
   como en `register_tourist`) y `changes={"role": "superadmin", "source": "bootstrap"}`.
7. **Nada secreto en la salida.** Los errores se imprimen como `VARIABLE: tipo` con `errors(include_input=False)`, y el
   comando usa un motor propio con `echo` apagado.

## Consecuencias

- Hay que correr el comando una vez por entorno. El modo de uso vive en el docstring del módulo; el manual técnico lo
  recoge en su bloque `(PLAN §2b)`.
- La contraseña viaja solo en el entorno de ese `docker run`, no en los grupos de variables ni en la Web App. Es la
  definitiva hasta que exista el cambio de contraseña.
- Alta y auditoría son dos `commit()` (A3). Si falla la auditoría, el superadmin queda sin su entrada. Se acepta.
- Dos ejecuciones simultáneas sobre una base vacía: el índice único rechaza la segunda con `IntegrityError`. Se acepta
  porque es un comando manual.
- El comando crea su propio motor, como `alembic/env.py`. `app/db/database.py` no cambia.
- Hay un segundo adaptador, `app.cli`, junto al HTTP; AGENTS §3 describe hoy solo el flujo Router → Servicio.

## Alternativas consideradas

1. **Paso en `cd-pipeline.yml`.** Guardaría una contraseña que no se puede cambiar en los tres grupos de variables, al
   alcance del log del pipeline. Descartada por David.
2. **`lifespan` de la app.** Correría en cada arranque y obligaría a la Web App a guardar la contraseña.
3. **Ruta HTTP de "setup".** Una ruta pública que crea un superadmin es una puerta de escalada para quien llegue primero.
4. **Campos en `Settings`.** La Web App pediría una contraseña que no usa, y el comando exigiría los secretos de JWT,
   correo y Azure (el caso de Alembic, ADR-0013, punto 5).
5. **Migración de datos.** Los secretos no van en `alembic/`, y una migración corre una vez en la historia del esquema,
   no "si no hay superadmin".
6. **Script en `scripts/`.** Quedaría fuera de mypy, de la cobertura (`source = ["app"]`) y de import-linter
   (`root_package = "app"`).

## Evidencia

- Sonda del plan (13 nov, pydantic 2.12.5): `str(ValidationError)` de `UserCreateByAdmin` contiene la contraseña.
  `errors(include_input=False, include_url=False)` da `[(('password',), 'value_error')]`. `SecretStr` sale como
  `'**********'`.
- Copia de `4f10660` con el texto del plan: de 638 a 675 tests y de 96,82 % a 97,37 %. Con `"app.api | app.cli"`, un
  import de `app.cli` desde `app.services` da `3 kept, 1 broken`. El mutante `echo=True` en el motor del comando lo
  tumba un test.
- Documentación: pydantic-settings, SQLAlchemy asyncio e import-linter (layers), enlaces en
  `docs/deuda/BE-34/plan.md`, sección Referencias.
