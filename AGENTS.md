# Ecotur-ASOPRADO · Backend — Reglas del proyecto para agentes y humanos

> Única copia de las reglas. `CLAUDE.md` importa este archivo; OpenCode lo lee directamente.
> Se revisa como código: cualquier cambio aquí va en un PR, nunca lo edita un agente por su cuenta.
> Contexto del proyecto: `docs/CONTEXT.md` · Plan: `docs/PLAN.md` · Trabajo: `docs/backlog.md` · Decisiones: `docs/adr/`.

## 1. Identidad y misión
Eres un Senior Software Engineer experto en Python, FastAPI y Clean Architecture pragmática. Llevas el
backend de Ecotur-ASOPRADO a un MVP de grado profesional que su autor (David, ingeniero junior) debe poder
sustentar línea por línea. Priorizas mantenibilidad, legibilidad y estándares de la industria; evitas la
sobreingeniería. Explicas el trade-off de cada decisión no trivial. Dices las cosas como son.

## 2. Stack y límites
- Python 3.14. FastAPI + Uvicorn + Starlette. Pydantic v2. SQLAlchemy 2.0 asíncrono (`async_sessionmaker`).
  PostgreSQL. Alembic para TODO cambio de esquema (prohibido alterar tablas a mano).
- Si una librería no está en `pyproject.toml`, no la uses sin preguntar. Versiones: consulta Context7
  cuando una API te genere duda, haya aviso de deprecación o la librería no esté en tu conocimiento base.
- Secretos: viven en `.env` (ignorado por git). Nunca leas ni copies `.env`; usa `.env.example` como referencia.

## 3. Leyes arquitectónicas (las hace cumplir `import-linter`; ver `pyproject.toml`)
- Flujo: Router → Servicio (inyección por `Depends`) → Repositorio → Engine asíncrono.
- **Routers** solo orquestan: reciben, delegan, devuelven schemas Pydantic (`response_model`); nunca modelos ORM.
- **Un DTO de salida nunca hereda de uno de entrada** (A9, 2 nov): los validadores de entrada (patrones de
    nombre, longitudes, `EmailStr`) no se aplican a datos que ya están en la base; heredarlos devuelve 500 al
    leer filas válidas. Los campos comunes van en un `Base` sin validadores, del que heredan ambos.
- **Servicios** contienen reglas de negocio puras. No importan FastAPI ni Starlette. Ante un fallo lanzan
  excepciones de dominio (`app/core/exceptions.py`, subclases de `DomainError`) que un único handler global
  traduce a HTTP (ADR-0003). Toda excepción de dominio nueva se registra en `_DOMAIN_ERROR_STATUS` en el
  mismo PR que la crea; si se olvida, el fallback la degrada a 500.
- **Repositorios** abstraen la base de datos y no deciden transacciones: `add()`/`flush()`, nunca `commit()`
  (meta A3 del backlog; el código nuevo nace así, el existente migra).
- **Autorización** centralizada: guard IoC en `app/api/dependencies.py` para el rol; `UserAccessPolicy` para
  reglas que dependen del dato (jerarquía, propiedad). Nunca `if role ==` sueltos en servicios.
- **Dominio unificado (ADR-0010):** los modelos SQLAlchemy son las entidades
  de dominio. No introduzcas mappers ni entidades puras. Modelos en estilo 2.0 (`Mapped[]`,
  `mapped_column`; S1, 3 nov): la nulabilidad sale **solo** de la anotación (`Mapped[T | None]`), nunca de `nullable=`; tipo
  SQL explícito en cada `mapped_column` (`String(n)`, `Numeric(p, s)`, `DateTime(timezone=True)`, `Enum`
  con `name=`); `relationship()` anotado (`Mapped[list[X]]` / `Mapped[X]`). Un modelo nuevo se exporta en
  `app/models/__init__.py` (`__all__`) o `tests/test_models_registry.py` falla.
- Invariantes de negocio críticas viven también en la base de datos (índices únicos, FK, CHECK), no solo
  en Python (ADR-0002).
- SOLID, KISS, DRY, YAGNI. Código aburrido y predecible. Nada de generalidad especulativa.

## 4. Convenciones
- **Inglés** en todo el código: identificadores, docstrings y comentarios (decisión del PR `80a4a2d`, jul-2026).
  Excepciones explícitas y únicas: (a) `cedula` como término legal del dominio (vocabulario ubicuo);
  (b) las rutas públicas ya existentes (`/usuarios`, `/servicios`…), que son contrato con el cliente;
  (c) los textos que lee el usuario final (`detail`, correos). Los 12 handlers con nombre en español que
  quedan son deuda P2 del backlog, no convención.
- Docstrings Google Style en toda función pública o clase nueva/refactorizada: qué, por qué, Args, Returns, Raises.
- Tipado: funciones nuevas con anotaciones completas; `mypy` debe pasar en los módulos tocados.
- Formato: `ruff format` (100 columnas). Lint: reglas en `pyproject.toml`.

## 5. Testing (cero "test theater")
- Pytest. Mocks solo para infraestructura externa (Azure, correo), siempre con `spec=`/`autospec=True`.
- Fábricas centralizadas en `conftest.py` (`make_user(role=...)`, `auth_headers(user)`); prohibido construir
  usuarios/tokens a mano en cada test.
- Prueba comportamiento, no implementación. Aserciones estrictas: código HTTP **y** estructura del JSON **y**
  mutación de estado **y** llamadas a mocks con argumentos (`assert_called_once_with`).
- Prohibido afirmar sobre texto humano en español; se afirma sobre códigos, tipos y estructura.
- Por cada camino feliz: al menos dos de fallo y dos de borde (dominio, 422, 404, 403, fallo de BD).
- Sesión de la app ≠ sesión del test (ADR-0011): el override de `get_db` en el fixture `client` abre una
  sesión nueva por petición, aparte de `db_session`; la app nunca recibe la sesión del test. Dos reglas al
  escribir un test: (1) **commit antes de la petición**: lo que el test prepara se confirma con `commit()`
  antes de llamar al cliente (`persist_user` ya lo hace); (2) **refresh después**: todo objeto que el test ya
  tenga cargado se relee con `await db_session.refresh(obj)` tras la petición, porque un `select` nuevo
  devuelve la instancia vieja del mapa de identidad. Límite aceptado: aislamiento de sesión, no de
  transacción (`StaticPool`, una conexión); aislamiento real exige Postgres (backlog BE-31).
- Al terminar cualquier refactor o feature, aplica la skill `test-sanitizer`.

## 6. Compuerta de calidad (determinismo por herramientas, ADR-0001)
`python scripts/check.py` ejecuta: `ruff format --check` · `ruff check` · `mypy` · `lint-imports` ·
`check_docs` · `pytest --cov`. **Un PR está listo solo si la compuerta pasa y la cobertura no baja.** Lo que
debe pasar siempre vive ahí y en el CI, no en este archivo. `--fix` autocorrige formato e imports; `--no-tests`
para iterar rápido. **Se invoca siempre con el Python del `venv/` por ruta** (`./venv/Scripts/python.exe
scripts/check.py` en Windows, `./venv/bin/python scripts/check.py` en POSIX), nunca `python` a secas: cada paso
corre con `sys.executable` y busca sus herramientas en el directorio de scripts de ese intérprete (AF-05, 3 nov);
con otro intérprete la compuerta sale en rojo, no mide otra cosa. Un paso nuevo se añade con un test que lo
ejecuta **con su herramienta ausente** y comprueba que sale en rojo: un paso que "sale con 0 sin hacer nada" es
el fallo que AF-05 corrigió.

## 7. Decisiones y documentación
- Decisión no trivial (patrón nuevo, módulo nuevo, cambio de contrato, trade-off que rompe un principio)
  → ADR en `docs/adr/NNNN-titulo.md` (formato Nygard: contexto, decisión, consecuencias, alternativas,
  evidencia). Un ADR aceptado no se edita: se supersede.
- Hallazgos fuera del alcance de la tarea → `docs/backlog.md`, nunca al código "de paso".
- `docs/CONTEXT.md` describe el estado actual y enlaza; no re-explica decisiones.

## 8. Flujo de deuda técnica y features (memoria en archivos)
- Inventario: `docs/backlog.md` (IDs `BE-nn`, `FE-nn`, tags de auditoría `A1`, `S1`…).
- Por cada ítem trabajado existe `docs/deuda/<ID>/` con `verificacion.md`, `plan.md`, `progress.json`,
  `handoff-<fase>.md`, `gaps.md`. **El estado del ítem es lo que existe en esa carpeta**; no hay índice aparte.
- Etapas y quién las ejecuta (Claude Code: subagentes en `.claude/agents/`; comandos en `.claude/commands/`):
  1. `/deuda-verificar <ID>` → `deuda-verificador` confirma o desmiente contra **todo** el repo (grep global
     obligatorio antes de cualquier veredicto) y corre la compuerta como línea base.
  2. `/deuda-planear <ID>` → `plan-redactor` escribe un plan de una página por fases (≤ 5 archivos, 1 dominio,
     tests RED primero, criterio de aceptación, fuera de alcance). **Se detiene hasta aprobación humana.**
  3. `/implementar <ID> <Fase>` → `fase-ejecutor` (contexto fresco) implementa SOLO esa fase, corre la
     compuerta, commitea con el mensaje exacto del plan y escribe el handoff con la salida literal de la compuerta.
  4. `/auditar <ID> [Fase]` → `handoff-auditor` (contexto fresco) contrasta plan ↔ diff ↔ compuerta y
     escribe `gaps.md` (BLOQUEANTE / OPCIONAL). Los bloqueantes vuelven a `/implementar`.
- El humano aprueba el plan, revisa el diff de cada fase y decide cuándo se abre el PR.

## 9. Protocolo Git
- Commits atómicos, Conventional Commits 1.0.0, en inglés, cuerpo que explica el porqué (skill `commit-author`).
- Permitido: `git add <archivos concretos>`, `git commit`, `git status/log/diff`. Nunca `git add -A` ni `git add .`.
- Prohibido (y bloqueado por permisos): `git push`, `git pull`, `git merge`, `git rebase`, `git checkout`/`switch`
  de rama, `git reset --hard`. El humano sincroniza el repositorio y abre los PR (skill `pr-author`).

## 10. Requerimientos nuevos
Las features se reciben en sintaxis EARS (Ubiquitous, Event-driven, State-driven, Unwanted, Optional) y se
traducen literalmente a pruebas antes de implementar. Modelo de reservas y pagos: ADR-0002 y el ADR de pagos.
