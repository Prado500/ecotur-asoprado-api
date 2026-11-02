---
name: pr-author

description: Generates PR titles, PR descriptions and merge commit messages (squash/merge trade-offs) from a branch's commit messages, following GitHub docs and Conventional Commits. Use when the user asks for a PR description, PR title, merge commit message, "genera el PR", or asks whether reusing the last commit message as the merge message is valid.
---

# Ecotur-ASOPRADO PR Author

Esta skill garantiza que todo PR abierto en GitHub tenga título, descripción y
merge commit message profesionales, alineados con la documentación oficial de
GitHub y la especificación Conventional Commits 1.0.0.

## Cuándo usarla
- Cuando el usuario pida generar el título o la descripción de un PR.
- Cuando el usuario pregunte qué merge commit message usar o si es válido
  reutilizar el último commit message de la rama efímera.
- Al cerrar una rama con 1 o N commits y querer entregar todos los textos
  listos para copiar y pegar.

## Reglas duras de operación
- **NO ejecutes** `git commit`, `git push`, `gh pr create`, `gh pr merge` ni
  cambies de rama. Solo entregas los textos. El humano crea y mergea el PR.
- **Idioma**: títulos, descripciones y merge messages en INGLÉS (convención
  del repo), aunque la conversación sea en español.
- **Sin emojis** en títulos ni descripciones.

## Flujo de Trabajo

### Fase 1: Inspección (obligatoria, antes de redactar)
1. Ejecuta `git log <base>..HEAD --oneline` (o `git log --oneline -15`) y
   `git status --short` para conocer los commits reales de la rama.
2. Determina si la rama contiene **1 o N commits**: esto cambia las reglas
   del merge commit message (ver Reglas de GitHub abajo).
3. Detecta si el PR incluye cambios breaking, migraciones de DB, env vars
   nuevas o hallazgos reportados sin corregir: todo eso DEBE aparecer
   explícitamente en la descripción.

### Fase 2: Redacción

**1. PR title**
- Subject Conventional Commits (`type(scope): description`), imperativo,
  máximo ~72 caracteres.
- Rama de 1 commit: hereda su subject. Rama de N commits: resume el tema
  dominante del conjunto.

**2. PR description** (markdown), estructura:
- `## What changed` — bullets por archivo/área y su rol en el cambio.
- `## Why` — problema/riesgo/decisión que motiva el cambio.
- `## How` — interrelación de los archivos (si aplica).
- `## Testing` — checklist: pruebas nuevas/afectadas, comando de ejecución,
  comportamiento congelado por la suite.
- `## Impact & breaking changes` — solo si aplica: migraciones, env vars,
  cambios de contrato; si no aplica, escribir "None".
- `## Findings deferred` — solo si aplica: hallazgos vistos y NO corregidos
  a propósito (evita que parezcan omisiones).
- No duplicar el diff: describir decisiones y riesgos, no líneas de código.

**3. Merge commit message** — entregar DOS variantes con su trade-off:
- **Squash**: subject = PR title; body = "PR title + description".
  - Válido reutilizar el último commit message SOLO si la rama tiene
    exactamente 1 commit (así lo hace el defecto de GitHub).
  - NO válido con N commits: el squash debe describir el PR completo, no
    solo el último commit.
- **Merge (default)**: el defecto de GitHub es
  `Merge pull request #N from <branch>` (número + título del PR); evaluar
  si conviene reemplazarlo por "PR title + description".
- Si el repo usa **merge queue**, advertir que GitHub IGNORA cualquier
  headline/body personalizado en ese flujo.

## Reglas basadas en documentación oficial de GitHub (docs.github.com)
- Squash merge: con 1 commit, el defecto reutiliza título y mensaje de ESE
  commit; con 2+ commits, el defecto pasa a "título del PR + lista de
  commits". Configurable a "solo título" o "título + descripción"
  (Settings → Pull Requests → Allow squash merging).
- Merge commit normal: el defecto es "Merge pull request #N from <branch>";
  configurable a "PR title" o "PR title + description".
- Merge queue: el GraphQL `EnablePullRequestAutoMergeInput` documenta que
  cualquier `commitHeadline`/`commitBody` suministrado se descarta.

## Salida esperada
1. PR title listo para copiar y pegar.
2. PR description completa en markdown.
3. Merge commit message en dos variantes (squash y merge) con el trade-off
   explicado y la validez (o no) de reutilizar el último commit.

## Fuentes de autoridad
- Conventional Commits 1.0.0: https://www.conventionalcommits.org/en/v1.0.0/
- GitHub docs: "Configuring commit squashing for pull requests" y
  "Configuring commit merging for pull requests" (docs.github.com).
- GitHub docs: plantillas en `.github/pull_request_template.md`.
- `AGENTS.md` del repo (Protocolo Git: atomicidad, inglés, porqué + interrelación).
- Skill hermana `commit-author` (`.agents/skills/commit-author/SKILL.md`): los
  commit messages de la rama son la entrada canónica de esta skill.
