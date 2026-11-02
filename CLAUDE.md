@AGENTS.md

# Específico de Claude Code (lo que OpenCode no tiene)

- **Subagentes** (`.claude/agents/`): `deuda-verificador`, `plan-redactor`, `fase-ejecutor`, `handoff-auditor`.
  Cada uno corre en contexto propio; solo su informe final vuelve a la conversación.
- **Comandos** (`.claude/commands/`): `/deuda-verificar`, `/deuda-planear`, `/implementar`, `/auditar`,
  `/revisar <ID> <artefacto>` (segunda opinión senior, sin tocar nada), `/duda <pregunta>` (modo profesor,
  anota en `docs/aprendizaje/preguntas.md`) y `/pr` (título, descripción y merge
  message con las skills `commit-author` y `pr-author`).
- **Hooks** (`.claude/settings.json`): tras cada edición de un `.py`, `ruff format` + `ruff check --fix`
  sobre ese archivo; si quedan errores, se te devuelven para que los corrijas antes de seguir.
  La compuerta completa (`python scripts/check.py`) la corren `fase-ejecutor` y `handoff-auditor`.
- **Permisos** (`.claude/settings.json`): `git push/pull/merge/rebase/checkout`, `rm -rf` y la lectura de
  `.env` están denegados. Es la versión ejecutable de la sección 9 de AGENTS.md.
- **Skills** (`.claude/skills/`): `test-sanitizer`, `commit-author`, `pr-author`, `5-whys`, `senior-security`.
- Lee `docs/CONTEXT.md` al iniciar una sesión larga; es el estado del mundo.
