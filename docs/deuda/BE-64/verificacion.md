# Verificación — BE-64: no hay forma de pedir otro enlace de verificación

**Veredicto:** confirmada
**Fuente del ítem:** docs/backlog.md (fila BE-64, l.119; origen: rincón 7 de `docs/deuda/BE-50/verificacion.md`, l.107-110, y
dato C6 de `docs/deuda/BE-38/verificacion.md`, l.466). No referencia tag del informe de auditoría.
**Fecha:** 2026-11-19

## Qué describe el ítem
El enlace de verificación caduca a los 15 min y no existe ninguna ruta (ni comando) que emita otro. El mensaje de
token expirado pide "solicite uno nuevo" sin que haya dónde, y repetir el registro da 400 porque el correo y la cédula
ya existen. La cuenta queda inactiva hasta que un administrador la active a mano (BE-63).

## Evidencia en el código
- `app/core/config.py:51` — `verification_token_expire_minutes: int = 15`.
- `app/core/security.py:91-109` — `create_verification_token(email)`: `exp = now + verification_token_expire_minutes`,
  claims `{"sub", "scope": EMAIL_VERIFICATION_SCOPE, "exp"}`; sin `jti`, no se guarda.
- `app/services/user_service.py:106` — **única** llamada a `create_verification_token` en `app/`, dentro de
  `register_tourist`.
- `app/api/routers/user.py:43-78` — `POST /usuarios/registro`: **único** sitio que programa `send_verification_email`
  (`background_tasks.add_task(send_verification_email, ...)`, l.70-76).
- `app/services/user_service.py:138-142` — `except jwt.ExpiredSignatureError` →
  `InvalidVerificationTokenError("El enlace de verificación ha expirado. Por favor solicite uno nuevo.")` (400,
  `app/main.py:127`). La fila cita `:132`; hoy está en `:141`.
- `app/services/user_service.py:76-80` — `register_tourist` rechaza con `AlreadyExistsError("Este usuario ya se
  encuentra registrado.")` (400, `app/main.py:124`) si existe correo **o** cédula. La fila cita `:75`; hoy `:80`.
- `app/repositories/user_repository.py:17-21` — `get_user_by_email_or_cedula` no filtra `deleted_at`: también una
  cuenta borrada bloquea el re-registro.
- `app/services/user_service.py:198-199` — login de cuenta inactiva: `AccountNotActiveError("Debe verificar su cuenta.
  Revise su correo electrónico.")` (403): remite al correo, cuyo enlace ya caducó.
- `app/api/routers/user.py:43, 81, 98` — las tres rutas públicas de usuarios: `/registro`, `/verificar-email`,
  `/login`. Ninguna emite un enlace nuevo. Rutas de usuarios protegidas: l.117, 130, 151, 182, 201, 220, 247; ninguna
  emite enlace.
- `tests/test_route_guards.py:78-89` — `PUBLIC_ROUTES` confirma el inventario: no hay ruta de reenvío.
- `app/cli/` — sin comando que emita enlace (el grep de `create_verification_token` no lo encuentra).
- Sin limitador de peticiones: `grep -rn -i "slowapi\|limiter\|rate.limit\|throttl" app pyproject.toml
  constraints.txt` → 0 resultados (dato para el punto (c) de la fila).
- `app/models/user.py:40-58` — `users` no tiene columna de "último envío"; la única marca es `email_verified_at`
  (l.58).

## Ficheros afectados (mapa completo)
- `app/api/routers/user.py` — no hay ruta de reenvío; la ruta nueva iría en `public_router` (l.32) y reutilizaría el
  patrón de `BackgroundTasks` de `/registro` (l.70-76).
- `app/services/user_service.py` — `register_tourist` es el único emisor del token (l.106); el texto de l.141 promete
  un reenvío que no existe; la regla de "a quién se le emite" viviría aquí.
- `app/core/security.py` — `create_verification_token` (l.91), reutilizable tal cual.
- `app/core/config.py` — `verification_token_expire_minutes` (l.51); una variable nueva (p. ej. intervalo mínimo
  entre envíos) exige campo, línea en `.env.example` y valor en `conftest.py` raíz (ADR-0013).
- `app/repositories/user_repository.py` — `get_non_deleted_user_by_email` (l.43) ya existe para la búsqueda.
- `app/models/user.py` + `alembic/versions/` — solo si se guarda la hora del último envío (punto (c)).
- `tests/test_route_guards.py` — toda ruta nueva entra en `PUBLIC_ROUTES` (l.78) y `_ANONYMOUS_ON_PUBLIC_ROUTE`
  (l.94), o la suite falla (ADR-0012).
- `tests/conftest.py:156` — el doble de `send_verification_email` parchea `app.api.routers.user.send_verification_email`;
  la ruta nueva en el mismo router lo reutiliza.

## Rincones no mencionados por la fuente
1. **"Marca vacía y no borrada" (punto (b) de la fila) no basta como criterio: alcanza cuentas que no son turistas
   pendientes.** La migración `e50a7c3d9b12` deja `email_verified_at` NULL en **todas** las filas previas
   (`alembic/versions/e50a7c3d9b12_users_email_verified_at.py:22,30`; ADR-0022 punto 7), y solo
   `verify_email_account` la llena (`user_service.py:163`). Por tanto tienen la marca vacía, para siempre:
   - toda cuenta administrativa creada por `create_administrative_account` (`user_service.py:448-460`, con
     `is_active=user_data.is_active`, por defecto `False` en `app/schemas/user.py:132`) y el superadmin del bootstrap
     (`app/services/superadmin_bootstrap.py:62`);
   - todo turista anterior a la migración, incluidos los que verificaron y luego un admin desactivó.
   Como el enlace con marca vacía pone `is_active = True` (`user_service.py:162-164`), una ruta de reenvío con solo ese
   criterio permitiría que (i) un admin desactivado por un superadmin se reactive solo (choca con ADR-0017: "la baja de
   un admin la decide un superadmin"), (ii) una cuenta administrativa creada inactiva se active sin el superadmin, y
   (iii) un turista anterior a BE-50 desactivado por un admin se reactive cuando quiera (lo que ADR-0022 punto 5
   cierra). Hoy no es alcanzable solo porque el token original caducó; el reenvío lo vuelve alcanzable sin límite de
   tiempo. El punto (d) de la fila solo contempla el caso de la decisión 3 de BE-50. Leído, no probado con sonda.
2. **El registro ya revela si un correo o cédula existe** (`user_service.py:79-80`, 400 con texto distinto al 201).
   La exigencia (a) de que la ruta nueva no revele la existencia del correo es correcta pero no cierra la enumeración
   por sí sola; tampoco lo cubre SEC3 (l.156 del backlog, que habla de `str(e)` y del tiempo del login). Además, la
   ruta nueva puede filtrar por tiempo si solo las cuentas existentes generan token y programan correo (mismo patrón que
   SEC3 en el login).
3. **El login de una cuenta pendiente remite al correo** (`user_service.py:199`) cuyo enlace pudo caducar: el punto
   de entrada natural del reenvío en el cliente. Relacionado con BE-56 (texto del login), no con esta fila.

## Patrones de detección (copiables)
```bash
# 1. Emisores del token de verificación (hoy: 1 en app/, user_service.py:106; tras el arreglo: 2 o un helper común)
grep -rn "create_verification_token(" app --include=*.py
# 2. Sitios que programan el correo de verificación (hoy: 1, routers/user.py:71)
grep -rn "send_verification_email," app --include=*.py
# 3. Rutas de reenvío (hoy: 0 en app/; tras el arreglo: la ruta nueva)
grep -rn -i "resend\|reenv" app --include=*.py
# 4. Inventario de rutas públicas (hoy: registro, verificar-email, login en /usuarios)
grep -n "@public_router\." app/api/routers/user.py
grep -n -A 14 "^PUBLIC_ROUTES" tests/test_route_guards.py
# 5. Mensaje que promete el reenvío
grep -rn "solicite uno nuevo" app --include=*.py
# 6. Escritores de email_verified_at (hoy: solo user_service.py:163) y filas que nacen con la marca vacía
grep -rn "email_verified_at" app alembic --include=*.py
grep -rn "is_active=" app/services --include=*.py
# 7. Limitador de peticiones (hoy: 0)
grep -rn -i "slowapi\|limiter\|rate.limit\|throttl" app pyproject.toml constraints.txt
```

## Línea base (`scripts/check.py` con el Python del venv por ruta, AGENTS §6)
- Base develop: `b6a80ba` (`git fetch origin` correcto; `git merge-base HEAD origin/develop` = `git rev-parse
  origin/develop`; la rama `item/be-64` lleva encima solo commits de docs: `8600df0`, `cc043c9`).
- Comando: `./venv/Scripts/python.exe scripts/check.py` (sin `--soft`; salida 0).

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
- pytest: `806 passed, 25 warnings in 35.22s` (0 failed).
- Cobertura total: `98.70%` (umbral 92,0 %).
- ruff format: `72 files already formatted`; ruff check: `All checks passed!` (0 errores).
- mypy: `Success: no issues found in 67 source files` (0 errores).
- import-linter: `Contracts: 4 kept, 0 broken.` (Capas api | cli -> services -> repositories -> models KEPT; Los
  servicios no conocen el transporte HTTP KEPT; Los repositorios solo conocen SQLAlchemy y los modelos KEPT; Los
  modelos y los schemas no dependen de capas superiores KEPT).
- La compuerta pasa antes de tocar nada.

## Conclusión para el planificador
Hay que añadir una ruta pública de reenvío en `public_router` que reutilice `create_verification_token` y el patrón de
`BackgroundTasks` de `/registro`, con respuesta idéntica exista o no la cuenta, y registrarla en `PUBLIC_ROUTES` y
`_ANONYMOUS_ON_PUBLIC_ROUTE`. El criterio de emisión no puede ser solo "marca vacía y no borrada": como mínimo
`role == tourist`, y el plan debe decidir (con David, por adenda) qué hacer con los turistas anteriores a la migración
que un admin desactivó, porque tienen la marca vacía y el reenvío los dejaría reactivarse (ADR-0022 punto 5; para
cuentas administrativas, ADR-0017). El tiempo mínimo entre envíos (punto (c)) exige columna nueva y migración Alembic, o
dejarlo fuera explícitamente; no hay limitador en la app. No tocar: la regla del enlace de ADR-0022 (`verify_email_account`),
el texto del login (BE-56), la activación manual (BE-63), la enumeración del registro y del login (SEC3), ni el cliente
Flutter si se cierra solo con backend (fila `FE-nn` ese día). Cambiar el texto de `user_service.py:141` es contrato visible:
solo si la decisión lo pide.
