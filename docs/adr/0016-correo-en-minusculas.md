# ADR-0016 — Un correo, una sola forma: se guarda en minúsculas y la base lo exige

- **Estado:** aceptado (David, 14 nov 2026, al aprobar las fases F y G del plan de BE-34)
- **Propuesta:** Claude, `plan-redactor` (14 nov 2026), sobre las enmiendas E1 (13 nov, 17:29) y E2 (14 nov, 09:08) de
  David al plan de BE-34
- **Ubicación en el repo:** `docs/adr/0016-correo-en-minusculas.md`
- **Origen:** backlog BE-51 (residual R2 del plan de BE-34); `docs/deuda/BE-34/plan.md`, fases F y G. Relación: ADR-0002
  (la invariante vive también en la base), ADR-0010 (punto 7: `alembic check`), ADR-0009 (no es un addendum de ADR-0015:
  alcanza el registro y el login de todos los usuarios), backlog A9 (lo guardado se devuelve tal cual) y D5 (validadores
  repetidos).

## Contexto

`EmailStr` solo pasa a minúsculas el dominio: `Root@Test.COM` llega como `Root@test.com` a `UserCreate`, `UserLogin` y
`UserUpdate`. Las tres consultas por correo de `UserRepository` comparan exacto, y el índice único `ix_users_email`
también. Medido el 13 nov sobre una copia con las fases A–E de BE-34: un segundo registro con `root@test.com` junto a
`Root@test.com` da 201 y deja dos cuentas; la provisión y el bootstrap también crean la segunda; el login con
`root@test.com` da 401; un `PATCH` a `ROOT@test.com` da 200; un enlace de verificación con `root@test.com` da 404.

Datos reales: 0 correos con alguna mayúscula y 0 colisiones en `develop`, `staging` y `main` (David, 13 nov, 17:40). David
declaró la API apagada el 14 nov: es la ventana de mantenimiento en la que entra este cambio.

## Decisión

1. **Un correo es una sola cuenta y se guarda en una sola forma: minúsculas, parte local y dominio.** Vale para el
   registro, la provisión, el bootstrap, el login, la verificación de correo y el cambio de correo por `PATCH`.
2. **Se normaliza al entrar, en un solo punto:** el tipo `LowercaseEmail` (`Annotated[EmailStr, AfterValidator(str.lower)]`,
   en `app/schemas/user.py`), que usan `UserBase`, `UserLogin` y `UserUpdate`. El servicio recibe el correo ya en
   minúsculas, y las consultas de `UserRepository` siguen comparando exacto.
3. **La base lo exige:** `CHECK (email = lower(email))`, con nombre `ck_users_email_lowercase`, declarada en el modelo
   `User` y creada por la migración `b51f3c9e2a64`. Un correo con mayúsculas escrito por una vía que no pase por un schema
   lo rechaza la base (ADR-0002).
4. **La unicidad la sigue dando `ix_users_email`.** No hay índice nuevo.
5. **Sin migración de datos.** Precondición de cada despliegue que lleve `b51f3c9e2a64`: 0 correos con mayúsculas en esa
   base (`SELECT count(*) FROM users WHERE email <> lower(email);`). Si una fila tiene mayúsculas, PostgreSQL se niega a
   crear la restricción, la migración se detiene sin cambiar nada y el CD no despliega la imagen.
6. **Los tokens comparan exacto.** La app firma el correo guardado, que ya está en minúsculas; un token con otra grafía
   no encuentra cuenta. Los tokens emitidos antes del cambio siguen valiendo, porque ningún correo guardado tenía
   mayúsculas.

## Consecuencias

- `UserResponse` devuelve la forma en minúsculas, y el correo de verificación va a esa forma, no a la que escribió el
  usuario. La guía de OWASP sobre correos dice que la parte local es "technically case-sensitive under SMTP, though many
  providers do not enforce this in practice": un buzón que dependiera de las mayúsculas no recibiría ese correo. Se acepta.
- La misma guía desaconseja plegar la parte local por defecto y lo admite solo cuando el sistema controla ese
  comportamiento y no crea riesgo de colisión ni de cuenta equivocada. Aquí se pliega siempre: segunda desviación, aceptada.
- `lower()` de SQLite solo pliega ASCII; el de PostgreSQL y `str.lower()` de Python pliegan también el resto de Unicode.
  `EmailStr` admite una parte local no ASCII, y `LowercaseEmail` la pliega en Python, así que por un schema no llega
  ninguna mayúscula. Lo que la suite no ve: en SQLite, la restricción acepta `Ángel@x.com` escrito sin schema; PostgreSQL
  lo rechaza.
- `alembic check` no compara restricciones `CHECK` (Alembic las lista entre lo que autogenerate aún no detecta; medido:
  `compare_metadata` da `[]` con la restricción ausente de la base). Su presencia en PostgreSQL se comprueba en
  `pg_constraint`.
- La migración usa `batch_alter_table`: en PostgreSQL emite un `ALTER TABLE … ADD CONSTRAINT`; en SQLite, que no puede
  añadir una restricción a una tabla existente, reconstruye la tabla. Así la suite la ejecuta.
- Toda vía nueva que escriba un correo usa `LowercaseEmail`; si no, la base la rechaza.

## Alternativas consideradas

1. **Comparar `lower(email)` en las consultas, con un índice único sobre `lower(email)`, sin normalizar lo guardado**
   (propuesta del 13 nov, no aprobada en E2). Guarda grafías distintas del mismo correo y deja la forma del dato sin
   fijar: cada consulta nueva tendría que recordar comparar sin mayúsculas. David prefiere una sola forma en la base.
2. **Normalizar en los schemas, sin restricción en la base.** La regla dependería solo del código: una escritura que no
   pase por un schema guardaría mayúsculas sin que nada lo impida.
3. **Guardar el correo como se escribió y, aparte, su forma canónica** (lo que recomienda la guía de OWASP: "Store both:
   Original input (for display and communication); Canonical form (for comparison according to your policy)"). Una
   columna más, sincronizada en cada escritura, para una forma original que hoy nada usa. Se aparta de la guía a
   sabiendas; si un día hace falta, es un cambio de esquema aparte.
4. **Tipo `citext` de PostgreSQL.** Exige la extensión en las tres bases de Azure y no existe en SQLite, así que la suite
   dejaría de probar la invariante.
5. **Migración de datos que pase a minúsculas lo guardado.** No hace falta: ningún correo guardado tiene mayúsculas.
6. **No hacer nada.** Una persona podría tener dos cuentas, y escribir su correo con otras mayúsculas le impediría entrar.

## Evidencia

- Sondas del plan (14 nov; pydantic 2.12.5, email-validator 2.3.0, SQLAlchemy 2.0.48, Alembic 1.18.4): `LowercaseEmail`
  da `root@test.com` para `rOOT@Test.com` y `ángel@test.com` para `ÁNGEL@Test.com`; en SQLite, `lower('ÁNGEL@x.com')` da
  `Ángel@x.com`; la migración sube, baja y se detiene con una fila en mayúsculas.
- SQL fuera de línea para PostgreSQL: `ALTER TABLE users ADD CONSTRAINT ck_users_email_lowercase CHECK (email =
  lower(email));` entre `BEGIN;` y `COMMIT;`.
- Sesión Mentor (14 nov), sobre una réplica mínima de `users` en PostgreSQL 16.15: un correo con mayúsculas da
  `CheckViolation`; un segundo correo igual, `UniqueViolation`; crear la restricción con una fila en mayúsculas ya
  guardada da `CheckViolation` y deja 0 restricciones.
- Copia con las fases A–G: de 675 a 691 tests y de 97,37 % a 97,63 %. Ocho mutantes, los ocho muertos.
- Documentación: OWASP (Email Validation and Verification Cheat Sheet), pydantic (`AfterValidator`), SQLAlchemy
  (`CheckConstraint`) y Alembic (modo batch, autogenerate), enlaces en `docs/deuda/BE-34/plan.md`, sección Referencias.
