---
name: commit-author

description: Generates professional, atomic Conventional Commits commit messages after inspecting git status/diff/log. Use when the user asks for a commit message, says "hazme el commit message", wants commits drafted for pending changes, or needs trade-off analysis of type/scope/body choices.
---

# Ecotur-ASOPRADO Commit Author

Esta skill garantiza que todo commit message propuesto cumpla la especificación
Conventional Commits 1.0.0 y el Protocolo Git de `AGENTS.md` (commits atómicos,
semántica estricta, cuerpo que explica el porqué y la interrelación de archivos).

## Cuándo usarla
- Cuando el usuario pida generar, revisar o mejorar un commit message.
- Al terminar una sesión de cambios y querer entregar el/los mensajes listos para copiar y pegar.
- Cuando el usuario pregunte qué `type`/`scope` usar o si un cambio es breaking.

## Reglas duras de operación
- **NO ejecutes** `git commit`, `git pull`, `git merge`, `git push` ni cambies de rama. El humano es el único responsable de la sincronización y del commit final. Solo entrega el/los mensajes.
- **Atomicidad**: un commit hace una sola cosa (un feat o un fix). Si los cambios pendientes cubren varios temas, propone UN commit por tema y lista exactamente qué archivos (o hunks) agrupa cada uno.
- **Sin tocar código**: esta skill es de solo lectura sobre el working tree.

## Flujo de Trabajo

### Fase 1: Inspección (obligatoria, antes de redactar)
1. Ejecuta `git status --short`, `git diff --stat` y `git log --oneline -15`.
2. Analiza los cambios reales vs. archivos untracked; identifica secretos, artefactos o archivos ajenos al tema.
3. Agrupa archivos por cohesión temática y decide si se necesitan 1 o N commits.
4. Alinea el `scope` con los scopes ya usados en el historial del repo.

### Fase 2: Redacción
Estructura obligatoria (Conventional Commits 1.0.0):

```
<type>[optional scope]: <description>

[body opcional, separado por línea en blanco]

[footer(s) opcionales: BREAKING CHANGE: ..., Ref: #n, ...]
```

Reglas de formato:
- `<description>`: imperativo, minúscula inicial, sin punto final, máximo ~72 caracteres en la línea de subject.
- Idioma: el mensaje completo en INGLÉS (convención del repo), aunque la conversación sea en español.
- Sin emojis, sin "wip", sin menciones vacías.

Elección de `type` (señal semántica REAL del cambio):
- `feat`: nueva capacidad observable (bump minor en SemVer).
- `fix`: corrección de bug (bump patch).
- `refactor`: cambio de estructura sin cambio de comportamiento.
- `test`: SOLO pruebas/fixtures, cero cambios en producción.
- `docs`, `chore`, `perf`, `ci`, `build`: solo cuando corresponda.
- **Antipatrones a evitar**: usar `feat` para cambios de solo-tests (corrompe el changelog/semver), usar `chore` para deliverables reales, mezclar dos temas en un subject.

`BREAKING CHANGE` o `type(scope)!:` SOLO si el contrato público cambia; si no aplica, se omite sin mencionarlo.

Cuerpo (body) — lo que exige AGENTS.md:
- Explica el PORQUÉ del cambio (qué problema/riesgo/decisión lo motiva) y CÓMO se interrelacionan los archivos modificados, como un ingeniero senior en la descripción de un Pull Request.
- Bullets por archivo cuando haya 2+ archivos con roles distintos.
- Documenta decisiones diferidas o hallazgos vistos a propósito (evita que parezcan omisiones).

## Salida esperada
Para cada commit propuesto, entrega:
1. Bloque de texto listo para copiar y pegar (subject + body).
2. Resumen breve de trade-offs: por qué ese `type`/`scope` y no otro.
3. Lista de archivos a stagear para ESE commit + advertencias de staging (archivos que NO deben incluirse).

## Fuentes de autoridad
- Conventional Commits 1.0.0: https://www.conventionalcommits.org/en/v1.0.0/
- `AGENTS.md` (raíz del repo), sección "Protocolo Git (El Antipatrón de Documentación)".
- Historial real del repo (`git log`): la fuente final del estilo de scopes y granularidad aceptados.
