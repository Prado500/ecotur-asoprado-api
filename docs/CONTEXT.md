# Ecotur-ASOPRADO — Contexto de trabajo (briefing portable)

> **Para qué sirve este archivo.** Es la memoria del proyecto para cualquier sesión de IA
> (Claude Code, OpenCode, el chat de Claude) y para cualquier persona que entre al repo.
> Vive en `docs/CONTEXT.md`. Regla de oro: **el contexto vive en archivos versionados, no en la
> memoria de un chat.** Cada sesión nueva arranca leyendo esto.
>
> **Versión 4.2 — 11 nov 2026.** Bitácora `2026-11-11` (§4: CI estricto sin `--soft`, dependencias fijadas en `constraints.txt`,
> toda ruta protegida con test de rechazo; §5: lo que el flujo enseñó con BE-39; §6: filas de ADR-0014 y de las decisiones del
> día; §8 reescrito: `B-GUARD-TESTS m2` como siguiente paso). Versiones anteriores: `2026-11-10` (4.1, bitácora `2026-11-10` (§4: configuración centralizada en `Settings` y compuerta local en verde
> sin `--soft` desde A4; §5: Context7 alcanzable desde los agentes y ritmo medido de A4; §6: fila de ADR-0013 y fila de las
> decisiones del día; §8 reescrito: merge de A4 y CI duro)); `2026-11-09` (4.0, cambio de premisa: bitácora `2026-11-09` (§2: la capacidad declarada el 7 nov entra en
> vigor —Bogotá hasta nuevo aviso, 2 m/día de lunes a viernes, 1 m el sábado con la tarde como comodín, sin régimen de
> Prado—; §6: fila del 9 nov; §8 reescrito con la ruta de la semana: A4 → CI duro → `B-GUARD-TESTS` → `B-GHOST-ADMIN` →
> puesta en `staging` → `B-RESERVAS`; al cierre del mismo día: §4 la compuerta sin binarios de `venv/Scripts/` (AF-12, AF-13); §5
> desviación del ejecutor y evidencia estructural; §6 segunda fila del 9 nov; §8 con A4 deslizado al martes));
> `2026-11-07` (3.8: bitácora `2026-11-07` (§4: `tests/` dentro
> de mypy desde BE-32; §5: contrato del auditor y `current_target` cumplidos por los agentes en BE-32; §6: cinco filas del
> 7 nov; §8 reescrito tras BE-32 hecho (PR #85) y A4 sin empezar); `2026-11-06` (3.7: bitácora `2026-11-06` (§2: Bogotá un día más, mudanza por
> confirmar —ajuste de un día dentro del mismo régimen; si David lo considera cambio de premisa, 4.0—; §4: compuerta en rojo
> solo por A4 y BE-32, frontera de autorización ADR-0012; §5: `--estado` y contrato del auditor; §6: cinco filas del 6 nov;
> §8 reescrito tras BE-33, A2, AF-02 y AF-07, con AF-08/AF-09 fuera de los pendientes de flujo). Versiones anteriores:
> `2026-11-05` (3.6: bitácora `2026-11-05` (§6: filas del 5 nov, bloque
> `B-GHOST-ADMIN`, I001 no autocorregible hasta A4, rol propio bloqueado por clave; §8 tras BE-02 hecho, `B-TESTS`
> deslizado al viernes y A4 adelantado; pendientes de flujo al día: `unfixable` hecho, AF-07 con fila).
> Versiones anteriores: `2026-11-04` (3.5: §0: fila de las fichas de estudio por ítem; §6: fila de ADR-0011; §8 tras
> BE-07 desmentida y BE-15 hecho, con la lista de pendientes de flujo al día); `2026-11-03` (3.4: §4: modelos en estilo 2.0 y dominio
> unificado con ADR; `import-linter` medido de verdad en local desde AF-05; §6: fila de ADR-0010; §8 tras `B-S1`, AF-05 y
> AF-04); `2026-11-02` (3.3: §4: medición de calidad citada a PLAN §6 en
> vez de copiada tres veces, CI con la compuerta; §5: `check.py` ya corre en el CI; §8 tras `B-FORMATO`, `B-CI` y `B-HIGIENE`);
> `2026-11-01` (3.2: §8 sin días ni fecha en el título; §0: regla de addenda en ADR-0009; §6: fila de
> ADR-0009);
> `2026-10-31` (3.1: §0: fila de composición ampliada con la secuencia de medias jornadas; §2: fila de deadline al día,
> regla de los domingos comodín y del fechado semanal, roles del equipo con el de David; §7: reparto propuesto a María
> Paula; §8);
> `2026-10-30` (3.0: §0: tabla hecho → dueño y política
> de copias, ADR-0008 —cambia una regla, por eso mayor—, regla de addendum y orden de resolución de huérfanas por el
> addendum de ADR-0008; §2: capacidad en tres regímenes hasta la entrega; §6: fila del ADR-0008 y fe de erratas de D1; §8). Versiones
> `2026-10-29` (2.10: §8), `2026-10-28` (2.9: §0 versionado, §6 ADR-0007), `2026-10-27` (§2, §4, §8; no
> subió versión ese día). Versionado según ADR-0007; la historia anterior vive en las bitácoras del 22 al 26 oct.

---

## 0. Cómo se mantienen estos documentos (léelo antes de editar cualquiera)

**Principio: un hecho tiene un solo dueño.** Los demás documentos lo citan, no lo repiten. La política de
copias es **ADR-0008**: un hecho duro (fecha, número, nombre de bloque, versión, estado, persona o rol) aparece a lo
sumo una vez por documento, nunca en un título, siempre con cita de forma fija al dueño (`(CONTEXT §2)`, `(PLAN §2b)`,
`(backlog ID)`, `(ADR-NNNN)`, `(AGENTS §N)`, `(README de sesiones)`, `(bitácora AAAA-MM-DD)`, `(docs/deuda/ID/)`); una
explicación puede resumirse con cita donde el documento la necesite; un documento vivo conserva lo que depende de, no
lo que explica. Si copia y dueño divergen, gana el dueño (para decisiones, el ADR más reciente).

**Mapa hecho → dueño.** Cualquier documento puede citar cualquier hecho con la forma fija; la última columna anota
solo las copias derivadas que un documento concreto lleva por diseño.

| Hecho | Dueño | Copia permitida (ADR-0008) |
|---|---|---|
| Deadline, forma de entrega, capacidad de trabajo (h/día, días/semana), roles del equipo, evaluadores, stakeholder | CONTEXT §2 | — |
| Lo que la propuesta aprobada compromete | CONTEXT §3 | — |
| Criterio de alcance del MVP (la regla con la que se decide qué entra) | PLAN §1-D3 | — |
| Decisión por ítem (`Entra · B-x` / `Sale → B-FUTURO` / `Hecho`) y severidad | backlog, fila del ítem | — |
| Composición de bloques (qué ítems van juntos, de quién) y secuencia de medias jornadas numeradas dentro del bloque, sin fechas | PLAN §2b | los demás nombran el bloque, nunca listan sus ítems; PLAN §3 cita la secuencia por número (`B-RESERVAS m3`) y nunca la repite |
| Qué bloque se hace qué día | PLAN §3 | ninguna: los demás nombran el bloque, nunca el día |
| Hecho / no hecho de cada día, decisiones del día, lecciones, cuota | bitácora del día | PLAN §3, columna `Cierre`: `✔/◐/✘ DD` |
| Línea base y mediciones de calidad | PLAN §6 | — |
| Protocolo de usabilidad | PLAN §7 | — |
| Riesgos y mitigación | PLAN §8 | — |
| Decisiones de diseño y de proceso | ADR (inmutable; se supersede) | CONTEXT §6: una fila por ADR (fecha, decisión, efecto) |
| Reglas de código, arquitectura, tests, git | AGENTS.md (`CLAUDE.md` lo importa) | — |
| Qué se verifica con exit code | `scripts/check.py`, `scripts/check_docs.py` | — |
| Flujo agéntico: inventario (agentes, comandos, hooks, skills) | `.claude/` | — |
| Flujo agéntico: estado y diseño | CONTEXT §5 | — |
| Rituales de apertura y cierre; guía humana del flujo | README de sesiones (`docs/sesiones/README.md`) | — |
| Estado de saldado de un ítem (presente o ausente) | `docs/deuda/<ID>/` | — |
| Estado actual del proyecto y próximo paso | CONTEXT §4 y §8 | — |
| Dudas de estudio | `docs/aprendizaje/preguntas.md` | la bitácora del día: conteo y enlace |
| Ficha de estudio de un ítem de deuda (antes / cómo se saldó / qué preguntaría un jurado) | `docs/aprendizaje/fichas/<ID>.md` | la bitácora del día: enlace; "Después" solo al cerrar el ítem |
| Versión de un documento vivo | su encabezado (ADR-0007) | — |

La tabla crece por incidente: cuando aparece una divergencia sobre información cuyo dueño no está registrado aquí, se
determina el dueño (el documento que cambiaría **de fondo** si el hecho cambiara) y se añade la fila ese día. Si parece
afectar a más de un documento, la sesión sigue el orden del addendum de ADR-0008: partir (cada parte, su dueño) → si no
se parte, uno decide y el otro lleva copia citada → solo si dos deciden de fondo, consultar a David; en los tres casos
llega con una propuesta y David valida antes de que la tabla crezca. Esas divergencias se detectan al leer (de forma
oportunista: aperturas que contrastan, revisiones de David), por la regla "hecho duro sin cita" de `check_docs.py`
cuando exista, o al ir a consignar un hecho y no encontrar su fila (ADR-0008, puntos 3 y 5 y addendum).
Naturaleza de cada archivo: los ADR son inmutables: un ADR aceptado no se edita, se supersede, o recibe un **addendum
fechado** que aclara o corrige una omisión sin alterar el texto original ni cambiar la decisión (si la decisión cambia,
es un ADR nuevo; regla en **ADR-0009**, tras los dos addenda de ADR-0008); CONTEXT, PLAN, backlog y `docs/sesiones/` son
vivos y versionados; las bitácoras son append-only (si algo cambió, se escribe en la entrada del día en que cambió).

**Rituales de apertura y de cierre:** viven en un solo sitio, `docs/sesiones/README.md`. Toda sesión
los sigue; este archivo no los repite para que no diverjan.

**Versionado (ADR-0007):** este archivo, `PLAN.md`, `backlog.md` y los artefactos de `docs/sesiones/` se versionan
**como archivos**: una línea `Versión X.Y — fecha` en el encabezado, seguida solo de las bitácoras que explican esa
versión. Las secciones no llevan versión ni fecha de revisión; las fechas dentro del texto son fechas de hechos.
Mayor (X.0) cuando cambia una premisa (deadline, alcance, capacidad, reglas); menor (X.Y) cuando cambia el
contenido. Se incrementa una vez por día de cambios (es decir, cuando el archivo y/o sus contenidos sufren de modificaciones), en el ritual de cierre.

Así no hay que "releer todo": el único documento que resume estado es este, y se revisa por
secciones.

**Los días viven solo en el cronograma de `PLAN.md` §3.** El backlog y este archivo referencian
**bloques de trabajo** (`B-BE01`, `B-RESERVAS`…, definidos en `PLAN.md` §2b), nunca días. Un
deslizamiento del plan mueve bloques entre filas del cronograma y no toca ningún otro documento.
(Lección del 26 oct: 56 filas del backlog llevaban días copiados y quedaron falsas tras un deslizamiento.)

## 1. Acuerdo de trabajo

- **Piloto:** David. **Copiloto:** la IA, en rol de ingeniero senior / profesor con paciencia.
- **Estándar:** no "que funcione", sino "bien hecho y entendido". Toda decisión no trivial se
  explica con el trade-off que prioriza, por qué, y qué implicaciones tiene.
- **Prueba de fuego:** David debe poder sustentar cada parte del código ante un jurado.
- **Honestidad:** la IA dice las cosas como son, incluso si contradicen el plan. No se fabrica
  evidencia de ningún tipo (decisión D1 del plan).
- **Verificar antes de aceptar:** David contrasta cada triage o diagnóstico de la IA contra el
  código (el 23 oct eso cerró tres ítems que la IA daba por pendientes).
- Idioma: español; jerga técnica en inglés cuando es el estándar.

## 2. Hechos duros

| Hecho | Detalle |
|---|---|
| **Deadline** | **11 de enero de 2027** (prórroga aceptada, comunicada a David el 27 oct 2026). Hasta entonces el deadline era el 7 nov 2026; `PLAN.md` v1.x se construyó sobre esa fecha; PLAN 2.0 (31 oct) se construye sobre la nueva. La entrega sigue siendo **en línea** (enlace de Drive). |
| **Qué se entrega** | Solo el **documento final**. No hay demo en vivo ese día; la sustentación se define después si el documento se aprueba. |
| **Capacidad** | **Un solo régimen hasta la entrega: Bogotá hasta nuevo aviso** (declarado por David el 7 nov, en vigor desde el 9 nov; sustituye a los tres regímenes del 30 oct: el de Prado no arranca porque la mudanza no está prevista). Lunes a viernes **2 m/día** (08:00–12:00 y 14:00–18:00); **sábado 1 m** (mañana); domingo descanso → **11 m/semana planificables** (44 h). **Tarde del sábado = comodín** (David, 9 nov): no es descanso declarado sino tiempo que David no compromete porque no sabe si lo tendrá; nunca entra en el presupuesto (disponibles − secuencia se calcula sin ella), pero siempre que exista es de trabajo, sirve tanto para repagar déficit como para adelantar secuencia, se decide ese mismo sábado y queda registrada en la bitácora del día y en la columna `Cierre`. **Domingos (David, 31 oct, sin cambio):** descanso por defecto; un domingo puede usarse como **comodín de recuperación**: nunca entra en el presupuesto, se decide al cierre del último día trabajado de la semana y solo si el colchón es cero o negativo (nunca para adelantar secuencia), y queda registrado como excepción (bitácora del domingo, marca en `Cierre`, versión de lo que toque). Diferencia entre los dos comodines: el del sábado adelanta y se decide el sábado; el del domingo solo repaga y se decide al cierre. **Días sin trabajo hasta la entrega:** 24, 25 y 31 dic y 1 ene; los festivos colombianos (16 nov y 8 dic son candidatos) los declara David al fechar cada semana. **Fechado semanal:** la semana siguiente se fecha al cierre del último día trabajado de la anterior (PLAN §3, acordeón). La unidad de planificación es la media jornada de 4 h (`m`). **Si David se mudara a Prado:** ese día se escribe el régimen (solo mañanas; señal de internet caída hasta 2 días sin aviso; cortes de luz de horas) y sube la versión mayor; hasta entonces el plan no asume esos riesgos. Sueño 21:00–05:30, no negociable. Hora Colombia. |
| **Roles del equipo** | **David:** código, calidad, pruebas, artefactos técnicos (UML, MER, OpenAPI, manual de despliegue) y capítulos de arquitectura, metodología y resultados; responde por la bitácora diaria (README de sesiones). **María Paula Ramos Carrillo** (compañera de tesis): documento. Reparto acordado en la reunión `(bitácora 2026-11-02)`: ella amplía la especificación de requisitos con las historias de usuario que David le entrega y redacta esa sección (OE1); completa wireframes y diagramas de UX/UI con la retroalimentación de David (OE2); redactó los avances de metodología, que David revisa para que la narrativa de Scrum sea correcta; manuales y documentación son de los dos (OE4). Resultados por objetivo y conclusiones: sin dueño acordado; el plan los asume de David en `B-TESIS` hasta que se decida. |
| **Evaluadores** | Desconocidos. Supuesto de diseño: al menos uno sabe de ingeniería de software → código defendible, no perfecto. |
| **Stakeholder** | Gerente de ASOPRADO, Juan Guillermo: aliado total, valida y firma lo que sea **verdad**. Para él Ecotur es una idea que no presiona; para la universidad resuelve un problema real de diversificación. La propuesta compromete "dejar" el prototipo, no garantizar su adopción. Palabras del gerente (23 oct): "vaya implementándolo como usted piensa y lo pulimos sobre la marcha". |

## 3. Lo que la propuesta aprobada compromete (esto es la ley)

**Título:** Prototipo y desarrollo de Ecotur-ASOPRADO: ecosistema digital web y móvil para la
gestión, promoción y comercialización de la oferta turística del distrito de adecuación de
tierras de Prado, Tolima. **Tutor:** Juan José Betancourt Lozano. **Modalidad:** investigación.

**Objetivo general:** prototipo de ecosistema digital (app multiplataforma móvil/web + sistema
web administrativo) que **optimice la gestión de reservas** y la promoción de servicios
turísticos de ASOPRADO.

**Objetivos específicos (literal):** (1) diagnosticar y formalizar requerimientos con **Marco
Lógico**; (2) diseñar arquitectura y UX/UI con wireframes y **UML** (componentes, secuencia,
entidad-relación, casos de uso); (3) construir Backend API, Frontend Web y App Móvil con
**integración continua**; (4) evaluar con **pruebas de caja negra y de usabilidad** y consolidar
**documentación técnica y de usuario**.

**Entregables (sección 5):** app Flutter para turistas (oferta "Ruta del Arroz", disponibilidad,
reservas); panel administrativo web (PWA; inventarios, usuarios, métricas de ventas); API
FastAPI documentada (OpenAPI); repositorio con Clean Architecture; documentación de arquitectura
(UML + MER); **manual técnico de despliegue**; **manual de usuario final**.

**Pruebas (4.2.4):** API, caja negra por módulo, **usabilidad en campo con miembros de ASOPRADO**.

**Metodología (sección 4):** Scrum + **"AI-Augmented Development… asistido por IA y verificado
por el equipo humano"**. → El flujo agéntico es parte de la metodología declarada.

### 3.6 Cabos sueltos de la propuesta y cómo se resuelven (estado al 24 oct)
| Cabo | Resolución |
|---|---|
| Pasarela de pagos (wireframes la nombran; presupuesto dice "No aplica") | **Decidido:** Wompi sandbox, puerto + adaptador, corte fijo (`B-PAGOS`, PLAN §3). ADR de pagos: pendiente de redacción (en `B-PAGOS`); tomará el siguiente número libre. |
| "Gestión de reservas" prometida | **No existía nada** (ni tabla ni lógica). Se construye en `B-RESERVAS` según **ADR-0002**. |
| "Disponibilidad en tiempo real" | Se redacta como "consulta de disponibilidad por fecha, por petición" (`GET /packages/{id}/availability`). Sin websockets. |
| "Modelo de aprendizaje supervisado" (4.2.2) | No aplica al alcance; se justifica en el documento. |
| "Microservicios" (resumen) vs "modular" | Lo construido es un **monolito modular** con Clean Architecture; se argumenta como decisión correcta para un MVP. |
| PWA para el panel admin | **Entra** como build web de Flutter con vistas protegidas por rol; es instalable (manifest + service worker por defecto de Flutter web). **No** se implementa modo offline; el documento lo redacta así. |
| Cronograma original de 24 semanas | Sustituido por `docs/PLAN.md` (15 días). |

## 4. Estado técnico actual (verificado por David el 23 oct; actualizado 27 oct)

### Backend
- **Python 3.14 en dev, CI y producción** (**ADR-0004**, escrito por David el 25 oct). Antes convivían 3.14 (venv, CI) y 3.11 (Dockerfile, `.python-version`).
- **Stack:** FastAPI async, SQLAlchemy async, Alembic, Pydantic, uvicorn. Clean/Onion. Sin
  clases de dominio propias: los modelos SQLAlchemy son las entidades, declarados en estilo 2.0 (`Mapped[]`,
  `mapped_column`) desde el 3 nov (`B-S1`), con registro explícito en `app/models/__init__.py` y test (**ADR-0010**).
- **Hecho y verificado:** autenticación JWT, registro con hash, handlers globales de
  excepciones, `UserAccessPolicy` con ABAC jerárquico (cubre delete y update), auditoría básica
  (`test_audit.py`). Frontera de autorización decidida el 6 nov (**ADR-0012**): rol en el guard, dato en la política; las dos
  rutas que no la cumplían la cumplen desde BE-40 (PR #94): `GET /auditoria/` ya no repite la comprobación de rol en el
  servicio, `POST /usuarios/admin` tiene guard de superadmin propio (`get_current_superadmin_user`, en un
  `superadmin_router`) y la política no conserva reglas de solo rol; la identidad se inyecta solo con `UserDep`,
  `AdminDep` y `SuperadminDep` (`app/api/dependencies.py`). **Desde el 11 nov (BE-39, PR #91) toda ruta tiene test de rechazo:**
  `tests/test_route_guards.py` lleva la tabla de las 17 rutas protegidas y la de las 9 públicas, un inventario que falla si
  una ruta no está en ninguna, y los casos de rechazo (sin token → 401; turista → 403 en las de admin y superadmin; admin →
  403 en la de superadmin; código exacto en las de usuario y en las públicas); quitar o debilitar un guard pone la suite en
  rojo, también el de `/auditoria/` desde BE-40 `(backlog BE-40)`. **Desde el 27 oct, los cuatro contratos de capas de `import-linter` se cumplen**
  (`B-BE01`: `storage.py` y `security.py` dejaron de arrastrar FastAPI; ADR-0006): ningún servicio conoce
  el transporte HTTP, ni directa ni transitivamente.
- **Configuración (A4, 10 nov; ADR-0013):** toda la configuración se lee en `app/core/config.py` (`Settings` de
  pydantic-settings y `get_settings()` con caché), validada al arrancar: cinco variables obligatorias (`DATABASE_URL`,
  `JWT_SECRET_KEY`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `AZURE_STORAGE_CONNECTION_STRING`); si falta una, la app no arranca y
  el error nombra el campo sin imprimir valores. La capa HTTP la recibe por `Depends(get_settings)`; el código sin petición
  llama a `get_settings()`; el motor y Alembic usan `get_database_settings()` (solo la URL, para que el CD siga migrando
  con `DATABASE_URL` sola). 0 `os.getenv` y 0 `load_dotenv` en `app/` y `alembic/`. La suite fija su entorno en el
  `conftest.py` de la raíz y no depende de `.env` ni de variables del CI. El orden de los imports ya no decide nada:
  `unfixable = ["I001"]` salió de `pyproject.toml`. Las tres Web Apps ya definen las cinco obligatorias (inventario del
  10 nov, `docs/deuda/A4/verificacion.md`, adenda 5); no definen `CORS_ORIGINS` (puesta en `staging`, §8).
- **No existe:** módulo de reservas (ver ADR-0002), pagos, paginación, recuperación de
  contraseña, `display_order` de paquetes.
- **Tests y calidad:** pytest + mocks; la medición vigente (tests, cobertura, ruff, mypy, contratos) es la última columna
  de `(PLAN §6)` y no se copia aquí. Tooling desde el 24 oct: `ruff`, `mypy`, `import-linter`, `pytest-cov`, unidos
  en `scripts/check.py` (AGENTS §6); desde el 6 nov (BE-33, PR #81) la compuerta global quedó en rojo solo por lo que tenía dueño
  en A4 (8 I001 y 5 `str | None`) y BE-32 (1 I001); rigió el trinquete de ADR-0005 hasta A4. **Desde el 10 nov (A4, PR #88) la compuerta pasa completa sin `--soft` en local y sin tolerar nada en el CI** (cifras en `(PLAN §6)`); **desde el 11 nov (CI duro, PR #89) el CI ejecuta `python scripts/check.py` sin `--soft` y sin grupo de variables: un paso en rojo bloquea el PR, y ADR-0005 queda superado.** **Las versiones de todas las dependencias están fijadas en `constraints.txt`** (77, generadas del venv de desarrollo; ADR-0014, BE-46, PR #92): el CI y el `Dockerfile` instalan con `-c constraints.txt`, así que local, CI e imagen ejecutan lo mismo; cambiar una versión es regenerar el archivo en el mismo PR. Desde el 3 nov (AF-05) un paso cuya herramienta falta sale en rojo (un
  "4 KEPT" ya no puede ser un paso que no corrió) y desde el 9 nov (AF-12) ningún paso depende de un ejecutable de `venv/Scripts/`:
  import-linter corre por su entry point con el intérprete de la compuerta, como ruff, mypy y pytest con `-m`. Los tests de `scripts/check_docs.py` corren en la suite pero fuera de la cobertura. **Desde BE-32 (7 nov, PR #85) mypy mide también `tests/`**: `pyproject.toml` `files` incluye `"tests"`, la suite propia quedó en 0 errores y los 4 que mypy reporta ahí son `SECRET_KEY` de A4; además 0 aserciones de mock sin argumentos y 3 copias HTTP menos `(backlog BE-32)`. El diagnóstico de la suite (mocks sin
  `spec`, setup duplicado, aserciones sobre texto, sesión ≠ `get_db`, huecos B2/B3/B4) es la fila
  §9/BE-15 del backlog y se corrige en `B-TESTS`.
- **Deuda y features:** inventario completo con decisión por ítem en `docs/backlog.md`.

### CI/CD e infraestructura (operativa)
GitHub → Azure DevOps → Azure (Web App for Containers + BD administrada) → Docker Hub.
Tres entornos (`develop`, `staging`, `main`) con resource group propio. PR → webhook → CI
(`scripts/check.py` completa, sin tolerar nada, con las dependencias de `constraints.txt`; ADR-0014) → merge → CD construye y publica imagen con tag del entorno →
la Web App la hala al reiniciar. Operación: 2 clics.

### Frontend (Flutter, MVVM; web + Android)
- Servicios ya separados **por recurso** (`audit_service`, `auth_service`, `catalog_service`,
  `session_service`, `user_service`); en `B-FE-RESERVAS` se añade `reservation_service`.
- **No existe:** manejo de 401 (sesión vencida no redirige al login), sistema de diseño,
  skeleton loaders, flujo de reserva/pago, historial, métricas.
- Kanban con desplazamiento horizontal en pantallas estrechas (patrón aceptable; falta señal
  visual). Hover solo en algunos botones. Texto seleccionable parcial.

## 5. Flujo agéntico (estado al 26 oct)

- **Decidido:** ADR-0001 (se conservan `deuda-verificador` y `handoff-auditor` con poda; se reescribe el
  paso 6 de `plan-redactor`; el determinismo pasa a herramientas ejecutadas por el ejecutor, el auditor y
  el CI; decisiones → ADR) y ADR-0005 (trinquete contra la línea base mientras la compuerta global esté en
  rojo; caduca al quedar en verde; la verificación registra el hash medido y el ejecutor lo compara). **ADR-0005 quedó
  superado el 11 nov**: la compuerta pasa completa en `develop` y el CI la ejecuta sin `--soft`; el criterio de cada fase
  vuelve a ser la compuerta en verde.
- **Runtime principal: Claude Code**, con **compatibilidad con OpenCode** como requisito (posible trabajo
  futuro con otras personas). Diseño de compatibilidad:
  - Las reglas del proyecto viven **una sola vez** en `AGENTS.md`; `CLAUDE.md` lo importa (`@AGENTS.md`) y
    añade solo lo específico de Claude Code.
  - La compuerta de calidad vive en `scripts/check.py`, un punto de entrada tool-neutral: los hooks de
    Claude Code lo invocan automáticamente; en OpenCode los agentes lo invocan por instrucción.
  - Los cuerpos de los agentes se escriben sin sintaxis específica de una herramienta; solo el frontmatter
    cambia entre `.claude/agents/` y `.opencode/agent/`. `.opencode/` queda **congelado** como evidencia
    histórica; cuando haga falta, se genera desde `.claude/` con un script corto.
- **Inventario:** no se describe aquí para que no se desactualice. Los agentes son los archivos de
  `.claude/agents/`; los comandos, los de `.claude/commands/`; hooks y permisos, `.claude/settings.json` y
  `.claude/hooks/`; skills, `.claude/skills/`. La guía de uso para humanos (cuándo, qué hace, qué no hace)
  es la tabla de comandos de `docs/sesiones/README.md`, y `scripts/check_docs.py` verifica que ambas
  coincidan (la guía con el inventario).
- **Estado:** v1 construida el 24 oct; **primer ciclo completo ejecutado el 27 oct** con `B-BE01` (verificar →
  planear → 4 fases con auditoría → `/pr`), con dos calibraciones ese día (frontmatter de los agentes entre
  comillas; propuesta de reglas para la sesión Mentor, pendiente). Pendientes de flujo con dueño en §8.7;
  `check.py` corre en el CI de Azure desde `B-CI` `(PLAN §2b)`.
  Desde AF-02 (6 nov) `check_docs.py --estado` lee el veredicto del último bloque de `gaps.md`, y el prompt del auditor
  dicta el encabezado y la línea de veredicto exactos (AF-07, mismo día); `--cierre` evalúa fechas en el huso del proyecto. El 7 nov (BE-32) el contrato se cumplió en las nueve auditorías y los ejecutores pusieron `current_target: null` al terminar; el ejecutor de la fase I se detuvo sin commitear ante una enmienda que no podía aplicarse sin empeorar la compuerta, que es lo que el protocolo exige. Un ítem de nueve fases sin lógica de `app/` costó ~27 min por fase (11:24–17:11). El 9 nov (AF-12/AF-13) el flujo corrió
  con la compuerta rota al arrancar (abortaba sin RESUMEN en la máquina de David): el verificador midió los pasos por separado, la
  adenda aceptó esa línea base y la aceptación de cada fase exigió RESUMEN impreso; el ejecutor de A descartó la salida de una
  comprobación (`> /dev/null`) y el auditor encontró la causa del exit 1 (AF-15) porque la guardó: la salida de la compuerta no se
  descarta nunca (nota en AF-09). Cuando un bloqueo de entorno deja de reproducirse a mitad del ítem, la evidencia pasa a ser
  estructural (exe renombrado → `4 kept`; exe inexistente → rojo con RESUMEN) y así se declara en el PR. El 10 nov (A4, nueve fases, nueve PASS) se
  encontró y arregló por qué los agentes reportaban "Context7 no disponible" desde el primer día: los cuatro declaran una
  lista cerrada `tools:` y un subagente con lista recibe solo lo listado; `plan-redactor` y `fase-ejecutor` llevan ahora
  `mcp__context7__*` (AF-16) y el plan de A4 cita Context7 en sus Referencias. El planificador atrapó con una lectura del
  pipeline de CD un error de la adenda del Mentor (Alembic con el `Settings` completo habría roto las migraciones) y lo
  resolvió con `DatabaseSettings`. Ritmo medido: ~15–20 min por fase con su auditoría, también con lógica de `app/`. El 11 nov (BE-39, cinco fases, cinco PASS)
  dos de las cinco fases nacieron de enmiendas: una de la revisión del plan por el Mentor y otra de un opcional del auditor
  de la fase A, las dos sobre límites de la propia tabla de tests; David fijó el criterio (un hallazgo sobre el artefacto del
  ítem se corrige en el ítem con una fase nueva; lo que queda fuera de su alcance recibe fila). Para aplicar una enmienda
  con fases ya ejecutadas se invoca a `plan-redactor` con un mensaje directo, no con `/deuda-planear`. El primer ítem bajo
  el CI estricto destapó que el CI instalaba versiones distintas de las de desarrollo (ADR-0014), y un PR se mezcló con un
  solo commit porque el resto no estaba subido: antes de mezclar se miran commits y archivos en GitHub, no solo el CI.
- **Artefactos de datos por ítem** (`docs/deuda/<ID>/`): `verificacion.md`, `plan.md`, `progress.json`,
  `handoff-<fase>.md`, `gaps.md`. El estado de un ítem es lo que existe en su carpeta; no hay índice aparte.

## 6. Decisiones tomadas (índice)

| Fecha | Decisión | Dueño | Impacto en el documento de grado |
|---|---|---|---|
| 23 oct | D1 Pruebas de usabilidad reales y remotas (gerente como admin + 4–5 perfil turista; SUS). Sesión con el gerente: fecha por concretar (la propuesta del 2 nov no fue confirmada por él; aplazada, bitácora 2026-10-29). | `PLAN.md` §1, §7 | Cap. de evaluación (obj. específico 4): protocolo, SUS, resultados |
| 23 oct | D2 Simplificar el flujo agéntico; determinismo por herramientas; runtime Claude Code compatible con OpenCode. | **ADR-0001** | Cap. de metodología (desarrollo asistido por IA) y lecciones aprendidas |
| 23 oct | D3 Alcance del MVP (entra / sale). | `PLAN.md` §1, `backlog.md` | Alcance del prototipo y cap. de trabajo futuro |
| 23 oct | Modelo de reservas: un paquete, una fecha, una reserva; `party_size` en el paquete; ventanas de disponibilidad; índice único parcial; precio congelado; expiración perezosa. Validado con gerencia. | **ADR-0002** | Cap. de diseño (MER, diagrama de clases, secuencia de reserva) y requisitos |
| 23 oct | Nombre de paquete **no** único (gerencia). | `backlog.md` BE-06 | Requisitos (regla de negocio) |
| 23 oct | El gerente sí espera reordenar paquetes desde el kanban → `display_order`. | `backlog.md` BE-08 | Requisitos y manual de usuario |
| 25 oct | Una sola versión de Python (3.14) en desarrollo, CI y producción. | **ADR-0004** | Cap. de arquitectura/despliegue y manual técnico |
| 25–26 oct | Trinquete de calidad contra la línea base mientras la compuerta global esté en rojo (caduca al quedar en verde); la verificación registra el hash medido y el ejecutor lo compara. | **ADR-0005** | Cap. de metodología (introducción de herramientas de calidad en código existente) |
| 25 oct | PR con commits atómicos se mezclan con *merge commit*, no squash. | `.claude/commands/pr.md`, `docs/sesiones/README.md` | Cap. de metodología (control de versiones) |
| 26 oct | Bloques de trabajo: la composición vive en `PLAN.md` §2b y los días solo en el cronograma; backlog y CONTEXT referencian bloques. | `CONTEXT.md` §0, `PLAN.md` §2b | Cap. de metodología (gestión del plan) |
| 26 oct | Finales de línea normalizados a LF en el repositorio. | `.gitattributes` | — |
| 27 oct | Cronograma v1.6: segundo deslizamiento pagado con recortes explícitos; superado el mismo día por la prórroga (entrega 11 ene 2027). | `PLAN.md` (línea de estado), §2 | Cap. de metodología (gestión del plan con hechos) |
| 27 oct | El adaptador de almacenamiento lanza excepciones de dominio (nunca `HTTPException`); lista blanca de URLs del CDN; copia síncrona antes de borrar; `InvalidImageUrlError` → 400 por contrato con el cliente (remapeo a 422 con P2). Supersede el residuo de `storage.py` de ADR-0003. | **ADR-0006** | Cap. de arquitectura (manejo de errores por capas) y resultados (contrato de capas 4 KEPT, cobertura) |
| 28 oct | Versionado de los documentos vivos: la versión es del archivo, no de una sección; mayor cuando cambia una premisa, menor cuando cambia el contenido; encabezado con solo referencias a bitácoras; aplica a CONTEXT, PLAN, backlog y `docs/sesiones/`. | **ADR-0007** | Cap. de metodología (gestión documental del proyecto) |
| 30 oct | Copias derivadas de un hecho: hecho duro a lo sumo una vez por documento, con cita de forma fija al dueño; explicaciones resumidas con cita; gana el dueño; mapa hecho → dueño solo en §0, crece por incidente; verificación acotada en el cierre por `check_docs.py`. | **ADR-0008**, `CONTEXT.md` §0, README de sesiones paso 3 | Cap. de metodología (evaluator-optimizer con revisión humana, bitácoras 28–30 oct) |
| 1 nov | Addenda a ADR aceptados: sección fechada y firmada al final; puede aclarar, corregir una omisión, afinar un criterio o decir cómo se cumple un punto; no puede cambiar la decisión ni el alcance (eso es ADR nuevo); tres addenda son señal de superseder. Segundo addendum de ADR-0008 el mismo día: R6 y R7 de `check_docs.py` corren solo con `--cierre`. | **ADR-0009**, ADR-0008 (addendum 1 nov), `CONTEXT.md` §0 | Cap. de metodología (cómo evolucionan las decisiones registradas) |
| 3 nov | Dominio unificado y estilo de modelos: los modelos SQLAlchemy son las entidades (retroactivo: práctica desde `20486ad`, citada en AGENTS §3 sin ADR); todo modelo en estilo 2.0, nulabilidad solo por la anotación, tipo SQL explícito donde el tipo Python no lo determina, `Enum` con `name=`, relaciones anotadas, registro explícito con test; un refactor de modelos se prueba con `alembic check` antes y después (M0 = M1). | **ADR-0010**, AGENTS §3 (PR de AF-04) | Cap. de diseño (modelo de datos) y de resultados (mypy 44 → 10 sin tocar el esquema) |
| 4 nov | La app y el test usan sesiones distintas en la suite: `get_db` se sustituye por una sesión nueva por petición, aparte de la `db_session` del test, sobre la misma conexión SQLite (`StaticPool`); dos reglas al escribir tests, "commit antes de la petición" y "refresh después"; límite aceptado: aislamiento de sesión, no de transacción (aislamiento real exige Postgres, BE-31). | **ADR-0011**, AGENTS §5 (PR de cierre del 4 nov) | Cap. de pruebas (la suite puede detectar un `commit()` olvidado antes del UoW de `B-RESERVAS`) |
| 5 nov | Nadie cambia su propio rol, superadmin incluido: la política bloquea la **clave** `role` en toda auto-edición (403), no su valor; crear usuarios con rol es otro camino. Confirmada por el flujo (BE-02). | `docs/deuda/BE-02/` (verificación con adenda, plan), `app/services/user_access_policy.py` | Cap. de diseño (autorización) |
| 5 nov | Los "rincones" que una verificación mide fuera de su alcance no se arreglan de paso: cada uno recibe fila; los cinco de BE-02 forman el bloque `B-GHOST-ADMIN` (que ningún jurado pueda dejar la plataforma sin administrador). | `docs/backlog.md` (BE-34..BE-38), `PLAN.md` §2b | Cap. de metodología (gestión de deuda) |
| 5 nov | I001 se reporta pero no se autocorrige (`unfixable = ["I001"]` en `pyproject.toml`) hasta que A4 centralice la configuración: reordenar imports de `app/` cambia el orden de carga. Cierra la opción abierta el 2 nov; sustituye la edición por Bash para esquivar el hook (S1). | `pyproject.toml`, `(bitácora 2026-11-05)` | Cap. de metodología (compuerta) |
| 5 nov | Lo rojo de la compuerta debe tener dueño en el backlog: una cifra en PLAN §6 es medición, no trabajo. BE-33 recoge lo manual sin dueño de `B-FORMATO`; A4 lo que depende de configuración. | `docs/backlog.md` (BE-33), `docs/aprendizaje/fichas/BE-33.md` | Cap. de metodología (gestión de deuda) |
| 6 nov | Frontera de autorización: el rol se decide en el guard HTTP, el dato en `UserAccessPolicy`, ninguna regla se comprueba dos veces, toda ruta protegida tiene un test de rechazo probado con mutante, una sola forma de inyectar identidad. A2 cierra como decisión; el trabajo es BE-39/BE-40 (`B-GUARD-TESTS`). | **ADR-0012** (con addendum del mismo día) | Cap. de diseño (autorización) y de pruebas (la suite debe vigilar el guard) |
| 6 nov | Tests de firma JWT (token firmado con otra clave → 401/400, mutación `verify_signature=False`) como **precondición de A4**, antes de tocar `jwt.decode`; en el plan de A4, además, test con la clave de `.env.example` y `Settings` sin valor por defecto para `JWT_SECRET_KEY`. | `docs/backlog.md` (A4) | Cap. de pruebas (un test de seguridad prueba el rechazo) |
| 6 nov | Huso del proyecto en `check_docs.py`: desfase fijo `timezone(timedelta(hours=-5))` (stdlib) en vez de `zoneinfo`, que falla en el venv de Windows sin `tzdata`; Colombia sin horario de verano desde 1993. `read_progress` no se toca: la excepción (`progress.json` que el SO no deja leer) se declara, no se codifica. | `docs/deuda/AF-02/` (E0), `scripts/check_docs.py` | Cap. de metodología (herramientas de verificación documental) |
| 6 nov | Hallazgos "de más" de una verificación de un ítem de decisión reciben filas y bloque, nunca se hacen bajo ese ítem (A2 → BE-39/BE-40, `B-GUARD-TESTS`); y los pendientes de flujo repetidos reciben fila (AF-09) en vez de vivir en CONTEXT §8. | `docs/backlog.md`, `PLAN.md` §2b | Cap. de metodología (gestión de deuda) |
| 6 nov | "Modo ejemplo" para las sesiones de estudio y Mentor: con la frase "explícamelo con un ejemplo concreto, paso a paso, y la regla al final", la sesión responde con dato real → acciones en orden → punto de ruptura → regla al final. | README de sesiones (`estudio.md`, `mentor.md`) | Cap. de metodología (desarrollo asistido por IA: cómo se estudia lo construido) |
| 7 nov | La sesión Mentor responde siempre en "modo ejemplo" (dato real, acciones en orden, punto de ruptura, regla) y sin etiquetas abstractas sin desplegar ("S–M", "~15 puntos"); tras cada auditoría, tres líneas fijas: `verificacion.md` se toca o no, `plan.md` se toca (E*n*) o no, commits antes de la siguiente fase. | README de sesiones (`mentor.md`) | Cap. de metodología (cómo se revisa lo que produce el flujo) |
| 7 nov | La batería documental del cierre (`--copias`, `--huerfanas`, `--cierre`, `--estado`) la ejecuta Claude Code con un prompt fijo y la sesión Mentor revisa la salida; la VM del Mentor no puede correrla. Fila AF-10 para convertirla en comando. | `docs/backlog.md` (AF-10), README de sesiones (paso 3) | Cap. de metodología (verificación documental) |
| 7 nov | Una enmienda que debilita un test se repara dentro del ítem con una fase nueva antes del PR (E3 de BE-32: `await_count == 1`); un commit con mensaje inexacto no se reescribe, se declara en la descripción del PR (segunda vez: `b9a8907`, `91af6e8`). Una enmienda que dicta código se mide antes de escribirse (columnas, RED con la configuración real). | `docs/deuda/BE-32/plan.md` (E3, E4), bitácora `2026-11-07` | Cap. de metodología (revisión humana del flujo; errores del revisor) |
| 7 nov | D8 (enviar una copia del mensaje con otro asunto) declarado inmatable por decisión no analizada de David ("flip de moneda"), para no detenerse ese día; se revisa al estudiar BE-32. | `docs/deuda/BE-32/plan.md` (E0, Residuales) | Cap. de pruebas (límites declarados de la mutación) |
| 7 nov | Capacidad hasta nuevo aviso declarada por David (no viaja a Prado) y **la semana siguiente se planifica en la apertura de la próxima sesión, no en este cierre**; ese día se actualizan §2 y PLAN §3 (versión mayor si David lo considera cambio de premisa). | bitácora `2026-11-07`; recogida en §2 el 9 nov | Cap. de metodología (gestión del plan con hechos) |
| 9 nov | Cambio de premisa (CONTEXT 4.0, PLAN 3.0): un solo régimen hasta la entrega, Bogotá, 11 m/semana; la tarde del sábado es comodín que adelanta o repaga y se decide el mismo sábado (distinto del domingo). Ruta de la semana: A4 → CI duro (`--soft` fuera, ADR-0005 superado) → `B-GUARD-TESTS` completo → `B-GHOST-ADMIN` completo (David: el día de la demostración ningún jurado puede degradarse ni dejar la plataforma sin superadmin) → puesta en `staging` → `B-RESERVAS`. El bloqueo del cliente Flutter (preflight `OPTIONS` rechazado) es la lista blanca de SEC1 funcionando contra un origen no configurado: se resuelve por configuración (`CORS_ORIGINS`), sin código ni flujo. BE-31: la suite sigue sobre SQLite, defendible porque sus huecos están declarados (ADR-0011, fila BE-31); la suite sobre Postgres sigue en `B-FUTURO`. Tests de firma de A4: fase A del plan, no a mano. | `CONTEXT.md` §2, `PLAN.md` §3 y §8, bitácora `2026-11-09` | Cap. de metodología (gestión del plan con hechos; CI duro como entregable) y de pruebas (qué no mide la suite y por qué) |
| 9 nov | Tres reglas de proceso del día. (1) **Falso positivo de `check_docs.py`** (la herramienta se equivoca, el documento está bien): no se detiene el trabajo; se esquiva en el documento con la edición mínima que no cambie ningún hecho, se declara en la bitácora con la causa verificada y el defecto recibe fila `AF-xx` en `B-FUTURO`; nunca se arregla el script "de paso" ni se deja la compuerta de cierre en rojo por una razón falsa (primer caso: AF-11, `_cells()` y el pipe escapado). (2) **Fila hija:** una fila del backlog puede saldarse como fase del ítem de otra cuando la verificación de este la midió y comparten archivos; la fila lo dice, la carpeta es una, el PR es uno (BE-01 con P1 y A7 lo hizo sin regla; AF-12 con AF-13 la escribe en AGENTS §8). (3) **La compuerta no depende de ejecutables de `venv/Scripts/`**: import-linter por su entry point (AF-12) y un paso que no arranca sale en rojo con RESUMEN (AF-13); apagar Smart App Control se descartó (irreversible, ajeno al repo). Además: el hint de instalación se conserva (fallo explícito), y la salida de la compuerta nunca se descarta (AF-09). | README de sesiones (paso 3), AGENTS §6 y §8 (`3e47d99`), `docs/deuda/AF-12/`, `docs/backlog.md` (AF-11, AF-14, AF-15) | Cap. de metodología (verificación documental; compuerta portable frente a políticas del sistema operativo; evidencia estructural cuando un bloqueo de entorno desaparece) |
| 10 nov | Configuración centralizada: un único módulo `app/core/config.py` con `Settings` (pydantic-settings) y `get_settings()` con caché; cinco variables obligatorias y no vacías, `MAIL_FROM` opcional con `MAIL_USERNAME` como valor si falta; `.env` de la raíz ubicado por la ruta del módulo, el entorno del proceso gana, `extra="ignore"`, errores de arranque sin valores; `Depends(get_settings)` en la capa HTTP y llamada directa donde no hay petición; `DatabaseSettings` para el motor y las migraciones; la suite fija su entorno en un `conftest.py` de la raíz. | **ADR-0013**, `docs/deuda/A4/` (adenda de 13 puntos, plan con E0 y E1) | Cap. de arquitectura (configuración y arranque; fallo ruidoso frente a valores por defecto silenciosos), de despliegue (variables por entorno) y de resultados (primera compuerta en verde completa) |
| 10 nov | Decisiones de proceso del día. (1) **A4 pasa de `B-PAGOS` a `B-TESTS`**: va en el bloque por dependencia (es lo que deja la compuerta en verde y permite el CI duro), no por tema. (2) **AF-16 antes de planear**, no en el cierre: los agentes del flujo corren en modelos más pequeños que el Mentor y necesitan documentación al día. (3) **`MAIL_FROM` no es obligatoria**: David mostró con un correo real que el remitente visible lo pone la cuenta autenticada de Gmail; hacerla obligatoria habría exigido tocar tres Web Apps sin cambiar nada para el destinatario. (4) **Un límite de commits intermedios se declara en el PR en vez de reordenar fases** (E0.7: entre las fases E y G la app en local no lee bien `.env`; la suite, el CI y Azure no lo sufren). (5) **Un hallazgo de auditoría anterior al ítem recibe fila, no arreglo** (BE-42, `scope` del bearer, a `B-GUARD-TESTS`). (6) Un commit con mensaje inexacto que aún no está en el remoto y es el último se corrige con `--amend` (`54cbfb9`); si ya está en el remoto, se declara en el PR (regla del 7 nov). | `docs/backlog.md` (A4, AF-16, BE-42..BE-45), `PLAN.md` §2b, `docs/deuda/A4/plan.md` (E0, E1), bitácora `2026-11-10` | Cap. de metodología (revisión humana del flujo: dos correcciones de David al Mentor y una del planificador; gestión de deuda; documentación al día para los agentes) |
| 11 nov | Versiones de dependencias fijadas: `constraints.txt` con la versión exacta de toda distribución instalada (directa o transitiva), generado del venv de desarrollo; `pyproject.toml` sigue declarando qué se necesita; el CI y la imagen instalan con `-c constraints.txt`; cambiar una versión es regenerar el archivo en el mismo PR; lo exclusivo de Linux se fija a mano desde el log del CI. | **ADR-0014**, `docs/backlog.md` (BE-46) | Cap. de despliegue y de metodología (builds reproducibles; el CI estricto atrapó una deriva de versiones el primer día) |
| 11 nov | Decisiones de proceso del día. (1) **CI duro hecho** y ADR-0005 superado: el CI no tolera nada; el residual 7 del plan de A4 (`conftest.py` de la raíz fuera de `mypy.files`) se acepta, no se hace. (2) **Un hallazgo sobre el propio artefacto de un ítem se corrige dentro del ítem, con una fase nueva** (David: "un ítem saldado no debería dejar 3 más por saldar a menos que no sea buena idea corregir sus hallazgos emergentes"); lo que queda fuera de su alcance sigue recibiendo fila (regla del 5 nov). Aplicado dos veces en BE-39 (E0 → fase D; E2 → fase E). (3) **La bitácora se escribe por tramos**, en cada punto de control, no solo en el cierre. (4) **Antes de mezclar un PR se comprueban en GitHub el número de commits y los archivos cambiados**, no solo el color del CI (PR #90 mezcló un commit de veintiuno); el asunto del merge `ed98db7` quedó inexacto y se declara, no se reescribe. (5) Un commit con mensaje inexacto que no es el último no se corrige con rebase si otros artefactos citan hashes posteriores (`fb109e7`). (6) Trabajo emergente crítico (dependencias sin fijar) se hace entero el mismo día en un PR corto sin flujo, con fila y ADR. | `docs/deuda/BE-39/plan.md` (E0–E3), `docs/backlog.md` (BE-39, BE-46, BE-47), bitácora `2026-11-11` | Cap. de metodología (revisión humana del flujo; gestión de deuda emergente; errores de proceso declarados) y de pruebas (tests de rechazo con mutantes) |
| pendiente | Pagos: puerto `PaymentGateway`, `WompiAdapter`, `FakeAdapter`, webhook idempotente. | ADR de pagos (`B-PAGOS`, tomará el siguiente número libre) | Cap. de diseño (secuencia de pago) y arquitectura |

## 7. Preguntas abiertas

- Qué tiene ya María Paula del documento (Drive pendiente desde el 31 oct; no se trató el 2 nov; el reparto ya está acordado: §2).
- Quién redacta resultados por objetivo y conclusiones y recomendaciones (sin dueño acordado; §2).
- Fecha de la próxima reunión con María Paula; en ella, plantillas de caja negra, consentimiento y SUS y apoyo en
  las sesiones de usabilidad, que la reunión del 2 nov no cerró.
- ¿Debe un admin ver en el historial de auditoría lo hecho por un superadmin? Hoy lo ve: `GET /auditoria/` admite a los dos
  roles por igual y la consulta no filtra por quién pregunta, mientras la política sí oculta los superadmins a un admin en
  el listado de usuarios. Sin decidir por David `(bitácora 2026-11-12)`. Si la respuesta es que no, es una regla de dato:
  va en la política `(ADR-0012)`, con fila propia en el backlog, fuera de BE-40.
- Para mencionar al gerente cuando convenga (no bloquean; están asumidas en ADR-0002): precio
  por paquete completo, antelación mínima 1 día, 30 min para pagar una reserva pendiente,
  tarifa de temporada alta como trabajo futuro.

## 8. Próximo paso

Dónde estamos (estado al cierre de la bitácora `2026-11-11`): **`B-TESTS` cerrado y `B-GUARD-TESTS m1` hecho.** El CI ejecuta la
compuerta sin `--soft` (PR #89, `4956346`; ADR-0005 superado). BE-39 saldada (PR #91, `a0578ae`): cinco fases, cinco PASS,
`tests/test_route_guards.py` con 45 casos y el inventario de rutas; **622 tests · 96,47 % · ruff 0 · mypy 0 · 4 kept** `(PLAN §6)`.
Todas las dependencias fijadas en `constraints.txt` (PR #92, `6d649df`; ADR-0014, BE-46). `develop` = `a612215` (PR #93,
cierre documental del 11 nov) más el commit de post-cierre. Ruta sin cambios: **`B-GUARD-TESTS m2` → `B-GHOST-ADMIN` → puesta en `staging` → `B-RESERVAS`** `(PLAN §3)`.

0. **Pendiente al abrir:** comprobar que la Web App de `develop` arranca tras los despliegues del 11 nov (`/docs` responde).
   Es la primera imagen construida con `-c constraints.txt`: vuelve a FastAPI 0.135.1 desde la versión sin fijar que el CD
   instaló ese día.
1. **`B-GUARD-TESTS m2`:** `/deuda-verificar BE-40` en `item/be-40` desde `develop`, y después BE-42 (los dos tocan
   `app/api/dependencies.py`). Notas ya escritas en sus filas: la Verificación final de BE-40 incluye M4 sola (debe caer
   `test_admin_route_rejects_tourist[GET /auditoria/]`) y el guard de superadmin amplía `PROTECTED_ROUTES`
   (`guard="superadmin"`, caso "admin → 403"); BE-42 actualiza `make_token`. Toda ruta nueva o cambiada se registra en las
   tablas de `tests/test_route_guards.py` (AGENTS §3).
2. **`B-GHOST-ADMIN`** (BE-34..BE-38), completo `(PLAN §3)`. BE-34 toma sus credenciales de `Settings`; **BE-47** (test de que
   `TEST_ENVIRONMENT` cubre todos los campos) entra con ella, como fase si su verificación la mide `(backlog BE-47)`.
3. **Puesta en `staging`** (media jornada, configuración, sin flujo): `CORS_ORIGINS` con el origen exacto del frontend en
   las tres Web Apps (decisión 5 de `docs/deuda/SEC1/`); **rotar el `JWT_SECRET_KEY` de `staging`** (hoy es el mismo que el de
   `develop`); PR `develop` → `staging`, **comprobando commits y archivos antes de mezclar**; login y registro desde el cliente
   contra `staging` (correo real: cierra la revisión visual de BE-33 D); `grep` de `role` en el cliente Flutter (cierra la nota
   de BE-02); **dump de `staging` para `B-RESERVAS m2`**. BE-43 (`.dockerignore`) si David decide halarla ese día.
4. **`B-RESERVAS`** (m1 decide BE-31: `sqlite_where` espejo en el `Index`; la suite sobre Postgres sigue en `B-FUTURO`). Sus
   rutas nacen registradas en `PROTECTED_ROUTES` o `PUBLIC_ROUTES`. Luego el orden de PLAN §3. `B-PAGOS m2` añade el
   conmutador Fake/Wompi como un campo de `Settings`.
5. Pendientes chicos sin `m`: **línea de ADR-0014 en AGENTS §2** (commit de David: las versiones viven en `constraints.txt`;
   una librería nueva entra en `pyproject.toml` y en `constraints.txt` en el mismo PR), y en ese mismo commit quitar el
   fragmento repetido de `AGENTS.md:43-44` (viñeta de ADR-0013, de `3ca990a`); fila en la tabla de CONTEXT §0 para
   "versión exacta de cada dependencia → `constraints.txt`" (propuesta del Mentor, la valida David); en el `.env` local,
   `FRONTEND_URL=http://localhost:3000`, y borrar el paquete 73 de prueba; fichas `fichas/BE-02.md`, BE-32 (opcional; revisa
   D8), **A4** y **BE-39** (qué es un mutante, por qué M4 no cae, qué vigila el inventario), con las 3 dudas abiertas de
   `preguntas.md`, en una sesión Estudio; mensaje a María Paula para fijar reunión y entregarle las historias de usuario
   (CONTEXT §7).
6. **Ritual de cierre:** paso 3 con la batería de `check_docs.py` ejecutada por Claude Code (prompt en la bitácora
   `2026-11-09`, pegando la salida completa; AF-10 la hará comando) y la salida revisada por la sesión Mentor antes del
   commit de cierre. La VM del Mentor no puede correr `check_docs.py` (Python 3.10): toda edición documental del Mentor se
   valida con `./venv/Scripts/python.exe scripts/check_docs.py` antes de commitear. La bitácora se escribe por tramos
   durante el día.
7. Pendientes de flujo (no urgentes, con dueño; pasan a filas `AF-xx` cuando se decida atacarlos): YAML estricto en
   `check_docs.py`; `/pr` con `#N`; formalizar en `docs/sesiones/` las reglas del Mentor (solo `git log`/`status`/`diff`, el
   10 nov volvió a correr un `git fetch --dry-run`; nada fuera de `docs/`; propuesta y permiso antes de escribir;
   excepciones declaradas en bitácora); `mentor.md` más ligero por cuota y **que diga Opus, no Fable**, salvo decisiones que
   paguen su juicio `(bitácora 2026-11-02)` (el 4, el 6, el 7, el 9, el 10 y el 11 nov corrieron en Fable por excepción declarada:
   seis seguidas, la regla escrita ya no describe lo que se hace); conectar la carpeta del repo antes del primer mensaje
   (seis días seguidos sin hacerlo); deny list de plumbing de git (`commit-tree`, `update-ref`, `replace`,
   `filter-branch`, `reset`) y AGENTS §9 "reescribir historia por cualquier medio" `(bitácora 2026-11-02)`;
   `.github/pull_request_template.md` diverge de la skill `pr-author` (copia sin dueño); los conteos de los RED de
   herramienta en los planes se escriben por `error:` o por id, no por líneas; un mutante se mide sobre el commit de la
   fase; "plan de una página" (AGENTS §8) frente a "plan que dicta" (A4: 641 líneas y nueve fases en una tarde): el dato
   del 10 nov favorece al plan que dicta, se delibera con ese dato `(bitácora 2026-11-06)`; dar Context7 también al
   verificador y al auditor si alguna vez lo necesitan (AF-16 los dejó fuera por mínimo privilegio); añadir al ciclo típico
   del README de sesiones "antes de mezclar: commits y archivos del PR en GitHub" (PR #90); invocar a
   `plan-redactor` directamente para enmiendas con fases ya ejecutadas (nota en AF-09); revisar si los prompts de
   `.claude/agents/` aún describen el trinquete de ADR-0005, ya superado (los edita David). Ya con fila: AF-08,
   AF-09 y AF-10; AF-06, AF-11, AF-14 y AF-15 en `B-FUTURO`.

## 9. Sesiones de IA
Cualquier sesión (ingeniería, documento, estudio, mentor) arranca con los prompts de `docs/sesiones/` y el ritual
de apertura descrito allí; ninguna conversación es fuente de verdad. Preguntas de estudio:
`docs/aprendizaje/preguntas.md` (único dueño de las dudas; la bitácora solo las cuenta y enlaza).
