---
description: Redacta título, descripción y mensaje de merge del PR de la rama actual hacia develop, con las skills commit-author y pr-author. Uso: /pr
---

Vas a preparar el PR de la rama actual hacia `develop`. Primero `git fetch origin` y
`git log --oneline origin/develop..HEAD` y `git diff --stat origin/develop..HEAD`; si la rama tiene cambios
sin commitear, detente y dímelo.

Aplica la skill `pr-author` sobre esos commits: título imperativo en Conventional Commits, descripción con
las secciones Por qué / Organización por commits / Cómo se probó (incluye la salida literal del RESUMEN de
`python scripts/check.py` si la corrí en la rama) / Residuales / Referencias (ADR, ítems del backlog), y el
mensaje de merge siguiendo el patrón del repo (`Merge pull request #N from <rama> - <título>`).
Estrategia: merge commit (los commits de este repo son atómicos por diseño); recomienda squash solo si los
commits de la rama no son atómicos, y di por qué.

No ejecutes `git push`, no abras el PR ni mezcles: eso lo hago yo en GitHub con lo que me entregues.
