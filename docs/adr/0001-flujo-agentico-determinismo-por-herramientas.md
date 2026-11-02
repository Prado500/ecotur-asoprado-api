# ADR-0001 — Simplificar el flujo agéntico: determinismo por herramientas, no por prosa

- **Estado:** aceptado (David, oct 23)
- **Fecha:** 2026-10-23
- **Ubicación en el repo:** `docs/adr/0001-flujo-agentico-determinismo-por-herramientas.md`
- **Formato:** ADR según Nygard (contexto → decisión → consecuencias), una página, vive junto al código.

## Decisión (resumen)

Se conserva la **forma** del flujo actual (verificar → planear → aprobar → ejecutar → auditar) y
dos de sus tres agentes casi intactos. Se **elimina el paso 6 b–d de `plan-redactor`** (premisas,
validación contra fuentes en rondas, rúbrica C1–C5, bitácora multicolumna, delta, citas por
decisión, scoreboard) y se sustituye por **compuertas deterministas** (ruff, mypy, import-linter,
pytest con cobertura mínima) que corren el ejecutor, el auditor y el CI. Las decisiones no
triviales se registran como **ADR**. El runtime pasa a **Claude Code**; `.opencode/` se congela
como artefacto histórico (evidencia de iteración para el documento de grado), no se borra.

## Contexto

- El flujo fue generado con OpenCode + DeepSeek. Tras dos semanas de análisis, David documentó
  25 observaciones (Word "Modificaciones", archivado en
  `docs/archive/flujo-agentico-v0/observaciones-flujo-v0.md`). Leídas una a una contra el código fuente de los seis
  `.md`, se distribuyen así:
  - **~85 %** (1, 1.1, 1.1.2, 2, 3.x, 4, 5, 6, 7.x, 8, 9, 10.x, 11, 13.x, 14.x, 15, 16.x, 17,
    20, 21.x, 22, 23) son ambigüedades **dentro del paso 6 de `plan-redactor`**: cómo iterar
    premisas y criterios, qué registrar en qué bitácora, qué hacer al agotar rondas, cómo evitar
    que ajustar una premisa invalide otra. Ninguna tiene respuesta "correcta": son consecuencias
    de intentar especificar en prosa un procedimiento epistemológico para un LLM.
  - **~10 %** (12, 18, 19, 24) tratan de `deuda-verificador` y del paso ABSORBER. La 19 está en
    gran parte ya cubierta por el propio prompt ("Mapea TODOS los ficheros… grep global");
    falta una frase: *el grep global se ejecuta siempre antes del veredicto, también cuando el
    informe parece desmentido*.
  - **~5 %** (25) trata del `handoff-auditor`: complacencia de las sesiones ejecutoras. El diseño
    ya lo mitiga (auditor con contexto fresco que lee el diff y corre pytest); falta que corra la
    compuerta completa, no solo pytest.
- Síntoma de fondo (observación 12 de David): el paso 6 obliga a un solo agente a absorber,
  planear, extraer premisas, buscar fuentes, iterar, documentar en cuatro sitios y graduar una
  rúbrica. Eso agota el contexto y degrada la calidad de todo lo anterior.

## Qué dicen las fuentes de autoridad (verificadas hoy)

1. **Anthropic — *Effective context engineering for AI agents*.** Los prompts deben estar a la
   "altitud correcta": entre *"hardcoding complex, brittle logic in their prompts to elicit exact
   agentic behavior"* (un extremo) y la vaguedad (el otro). El objetivo es *"the smallest
   possible set of high-signal tokens"*, porque *"context must be treated as a finite resource
   with diminishing marginal returns"*. Respalda también la **nota estructurada persistida**
   (*structured note-taking*): `verificacion.md`, `plan.md` y `progress.json` son exactamente
   eso y se conservan.
2. **Claude — *Steering Claude Code: skills, hooks, rules, subagents*.** *"Keep CLAUDE.md under
   200 lines, give it an owner, and review changes to it like code."* Los hooks *"provide more
   deterministic control"* y *"are deterministically triggered"*; una instrucción en prosa Claude
   *"will follow… most of the time"*. Es decir: lo que debe pasar **siempre** va en un hook o en
   una permission, no en un párrafo.
3. **Anthropic — *Building effective agents*.** *"Begin with the simplest possible solution"* y
   *"add complexity only when it demonstrably improves outcomes"*; *"the most successful agent
   implementations use simple, composable patterns rather than complex frameworks"*. El patrón
   *evaluator-optimizer* existe, pero con un evaluador barato y claro; el paso 6 lo convertía en
   un tribunal de cinco criterios con dos rondas y cuatro registros.
4. **Import Linter** (docs oficiales): contratos `layers`/`forbidden` que fallan con exit code ≠ 0
   cuando una capa importa lo que no debe. Es la forma determinista de hacer cumplir la Clean
   Architecture que hoy se le pide al LLM "verificar" en C1/C2.
5. **ADR — Nygard (2011), vía Martin Fowler y arc42.** Un ADR es *"a short document that captures
   and explains a single decision"*; *"keep decision records in the source repository"*; una vez
   aceptado *"it should never be reopened or changed — instead it should be superseded"*. Es el
   sustituto profesional de "bitácora de decisiones con evidencia y trade-offs".

## Veredicto por archivo

| Archivo | Veredicto | Qué cambia |
|---|---|---|
| `agent/deuda-verificador.md` | **Conservar con poda** | (a) Quitar "Mantenimiento por reglas: codifícala como regla en este prompt": un agente que edita sus propios guardarraíles sin revisión humana produce deriva; los cambios a prompts se revisan como código. (b) Baseline = compuerta completa, no solo pytest. (c) Ruta Windows `venv\Scripts\python.exe` → comando portable (`make check` o `python -m …`). (d) Añadir la frase del grep global obligatorio antes de cualquier veredicto. (e) Entrada de deuda: el informe HTML **o** `docs/backlog.md`. |
| `agent/handoff-auditor.md` | **Conservar casi intacto** | Corre la compuerta completa (ruff, mypy, import-linter, pytest-cov), no solo pytest. El handoff del ejecutor debe pegar la salida literal de la compuerta; el auditor la re-ejecuta igual. Lo demás (contexto fresco, BLOQUEANTE/OPCIONAL, regla anti-scope-creep, nunca corrige código) es correcto y se mantiene. |
| `agent/plan-redactor.md` | **Reescribir el paso 6 y la sección "Fuentes de autoridad"** | Se conservan pasos 1–5 (ABSORBER → CONTRASTAR → AMPLIAR → ANÁLISIS → REDACTAR), 6e (residuales) y 7 (autoverificación). Se eliminan 6a–6d. Nuevo paso 6: *"Para cada API/librería que el plan use, consulta Context7 y anota versión + enlace en 'Referencias' (una línea cada una). Si el plan introduce una decisión no trivial (patrón nuevo, módulo nuevo, cambio de contrato), redacta un ADR en `docs/adr/` y enlázalo."* `resumen-humano.md` se funde en una sección "Resumen para aprobación" al inicio de `plan.md`. El `plan-consolidado-servicios.md` deja de referenciarse. |
| `command/nueva-deuda.md` | Conservar (renombrar `/deuda-preparar`) | Mismo orquestador; añade la fuente `docs/backlog.md`. |
| `command/verificar-deuda.md` | Conservar | Sin cambios de fondo. |
| `command/auditar-handoff.md` | Conservar | Sin cambios de fondo. |
| Apéndice A (prompt de sesión por fase) | Simplificar | En Claude Code la fase la ejecuta un subagente con contexto fresco invocado por `/implementar <tag> <fase>`: desaparece el copy-paste. El ritual se mantiene (baseline → RED → GREEN → compuerta → commit exacto → progress.json → handoff). Reglas de arquitectura y DoD viven en `CLAUDE.md`, no repetidas en cada prompt. |
| `.opencode/` | Congelar | Se deja en el repo como evidencia histórica; no se mantiene en paralelo. |

## Compuerta determinista (lo que sustituye a C1–C5)

| Criterio del flujo viejo | Sustituto determinista |
|---|---|
| C1 "no viola leyes de agents.md / no añade acoplamiento" | `import-linter` (contratos de capas) + `ruff` |
| C2 "no introduce anti-patrones" | `ruff` (reglas seleccionadas: bugbear, simplify, etc.) + `mypy` + revisión humana del diff |
| C3 "orden correcto de fases" | Regla de tamaño (≤5 archivos, 1 dominio) + la fase A es la más pequeña; se revisa en aprobación humana |
| C4 "trade-offs documentados" | ADR obligatorio cuando el plan declara una decisión no trivial |
| C5 "fuentes reales" | Sección "Referencias" con enlaces a docs oficiales vía Context7; sin bibliografía académica en el plan |
| Premisas validadas en rondas | Versiones fijadas en `pyproject.toml` + tipado (SQLAlchemy 2.x, Pydantic, FastAPI son typed: `mypy` detecta firmas incorrectas) + Context7 en el punto de uso |

## Consecuencias

- **Positivas:** el flujo cabe en el contexto de una sesión; cada regla "que debe pasar siempre"
  falla con exit code; las decisiones quedan en ADRs reutilizables en el capítulo de
  arquitectura; se eliminan ~85 % de las observaciones abiertas sin responderlas una a una.
- **Negativas / riesgos:** se pierde la trazabilidad "premisa → fuente → veredicto" por decisión
  menor (se acepta: esa granularidad no la tiene ningún equipo profesional); configurar
  `import-linter` exige nombrar explícitamente las capas del backend (trabajo del día 1, tarde);
  `mypy` sobre código vibecodeado producirá ruido inicial → estricto gradual, solo módulos tocados.
- **Para el documento de grado:** este ADR + las 25 observaciones + la línea base/final de
  métricas son el capítulo "desarrollo asistido por IA: lecciones aprendidas".

## Alternativas consideradas

1. **Corregir las 25 observaciones una por una** (plan original): descartada; coste estimado
   de días sin cota superior clara y resultado más largo y más ambiguo que el actual.
2. **Descartar el flujo entero y partir de cero:** descartada; `deuda-verificador` y
   `handoff-auditor` son buenos y ya están probados en el repo.
3. **Mantener OpenCode + DeepSeek como runtime:** descartada como principal (sin hooks
   deterministas equivalentes; dos runtimes en paralelo = doble mantenimiento); queda como
   opción para tareas masivas y baratas si se necesita.

## Fuentes

- Anthropic, *Effective context engineering for AI agents*:
  https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Claude, *Steering Claude Code: when to use CLAUDE.md, skills, hooks, rules, subagents*:
  https://www.claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more
- Anthropic, *Building effective agents* (citas tomadas del resumen de Latitude; original en
  anthropic.com/engineering): https://docs.latitude.so/examples/cases/building-effective-agents
- Import Linter, documentación oficial: https://import-linter.readthedocs.io/en/stable/readme.html
- M. Fowler, *Architecture Decision Record*: https://www.martinfowler.com/bliki/ArchitectureDecisionRecord.html
- arc42 FAQ sobre el formato de Nygard (2011): https://faq.arc42.org/questions/C-9-3/
