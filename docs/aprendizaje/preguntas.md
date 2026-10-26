# Deuda de aprendizaje

Preguntas que surgen mientras construyo el MVP con IA y que estudio en la sesión de Estudio
(`docs/sesiones/estudio.md`). Una por línea; al resolverla, se mueve a "Resueltas" con dos líneas de
respuesta propia (con mis palabras, no copiadas). Es evidencia de "desarrollo asistido por IA, verificado
por el equipo humano" (propuesta, sección 4).

## Pendientes

- [ ] Por qué "lo que debe pasar siempre" se implementa como una herramienta que falla con exit code ≠ 0 y no como una instrucción en prosa a un LLM. Relación con CI como quality gate.
- [ ] ruff: qué es un linter, qué es un formateador, qué detecta y qué no.
- [ ] mypy: tipado estático gradual; qué detecta que pytest no; por qué importa que SQLAlchemy 2, Pydantic y FastAPI estén tipados.
- [ ] import-linter: contrato de capas, acoplamiento, dependencia transitiva (el caso `services → core → fastapi`).
- [ ] pytest-cov: qué mide la cobertura, qué no garantiza, qué significa "la cobertura no baja".
- [ ] Hooks y permisos en Claude Code frente a instrucciones en prosa: determinista vs. "la mayoría de las veces".
- [ ] ADR: formato de Nygard; por qué sustituye a una bitácora de decisiones; por qué no se edita, se supersede.
- [ ] Puertos y adaptadores: por qué una pasarela de pago se modela con un adaptador real y uno falso para tests.
- [ ] Índice único parcial en PostgreSQL y condiciones de carrera: por qué la invariante vive en la BD (ADR-0002).
- [ ] Unit of Work: por qué los repositorios no hacen `commit()` (hallazgo A3).
- [ ] JWT sin estado: por qué permite sesiones simultáneas y qué cuesta revocarlas (BE-12).
- [ ] `staged` vs `committed` vs `pushed`; por qué git muestra un rename como delete + add cuando el contenido cambia mucho.
- [ ] Merge commit vs squash: cuándo cada uno.
- [ ] Por qué `create_tourist_package` y `update_package_details` validan distinto las URL de imágenes (asimetría) y cómo se unifica con una sola función de clasificación de URL.
- [ ] Por qué `except Exception` se traga una `HTTPException` (jerarquía de excepciones) y cómo dejar pasar las de dominio.
- [ ] Commit hecho en `develop` por error (sin push): mover el commit a una rama con `git switch -c` + `git branch -f develop origin/develop`; por qué no `reset --hard`; reescribir historial no publicado vs `git revert` si ya hubo push.
- [ ] `git switch`/`git restore` (Git 2.23) vs `git checkout`: por qué se partió `checkout`, el peligro de `git checkout .`, detached HEAD y la ambigüedad rama/archivo con `--`.
- [ ] `--amend` después de un push: por qué el push sale rechazado (non-fast-forward) y por qué no se arregla con `git pull`; `--force` vs `--force-with-lease` a secas vs `--force-with-lease=<rama>:<hash>` vs `--force-if-includes` (el riesgo del fetch en segundo plano); cuándo es aceptable reescribir historia publicada (rama propia vs compartida).

## Resueltas

(ninguna todavía)
