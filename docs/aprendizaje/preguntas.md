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

- [ ] Subagentes de Claude Code: por qué cada invocación de `/implementar`, `/auditar`… nace con contexto fresco (prompt del agente + `CLAUDE.md`/`AGENTS.md` + tarea) y solo devuelve su informe; qué acumula la sesión principal y por qué eso justifica `/clear` entre bloques. Relación con el "contexto fresco" que exige ADR-0001. (27 oct 2026)
- [ ] `git diff -w` / `git show -w`: cómo revisar un diff generado por IA cuando el hook reformatea el archivo entero; qué ignora `-w` y qué no (líneas partidas). Por qué "David lee el diff" no es ceremonia: el hueco de la promoción parcial en `create` cumplía el plan y lo atrapó solo la lectura humana. (27 oct 2026)
- [ ] `except Exception` como ocultador de bugs: por qué un 503 falso ("CDN no disponible") es peor que un 500 verdadero; "un punto de traducción por frontera" (infra → dominio en el adaptador, dominio → HTTP en `main.py`, ADR-0003/0006); qué se atrapa (`AzureError`) y qué se deja subir. (27 oct 2026)
- [ ] Validar todo antes de ejecutar efectos externos: por qué `create` clasifica todas las URLs antes de la primera promoción y `update` antes del primer borrado; qué pasa cuando una operación con efectos no transaccionales (CDN) falla a la mitad (blobs huérfanos, BE-26). (27 oct 2026)
- [ ] Azure Blob: copia síncrona (`requires_sync=True`, `copy_status`) vs asíncrona con sondeo; qué exige del origen; niveles de acceso Private / Blob / Container y por qué "Blob" es correcto para un CDN de fotos cuando los nombres son UUID y solo un admin autenticado sube. (27 oct 2026)
- [ ] 400 vs 422 para `InvalidImageUrlError`: semántica HTTP (422 = bien formado pero inválido) frente a contrato con el cliente (`{"detalle": [...]}` vs `{"detail": str}`); por qué tener los códigos en una sola tabla hace que el remapeo sea una línea (ADR-0003, ADR-0006, BE-24). (27 oct 2026)
- [ ] "Paquete nuevo = todo desde el contenedor temporal": qué es un blob compartido, por qué `delete_image` lo rompe (BE-25) y qué se pierde al prohibir reutilizar imágenes (trade-off aceptado para el MVP). (27 oct 2026)
- [ ] Trinquete por conjunto, no por conteo: por qué "mypy ≤ 10 en el archivo" permite cambiar un error viejo por uno nuevo y "mismas líneas y códigos" no; cuándo es legítimo desviarse de la letra de ADR-0005 (errores en archivos tocados causados por otros ítems: A4, S1). (27 oct 2026)
- [ ] YAML frontmatter: por qué un escalar sin comillas no puede contener `: ` (mapping values are not allowed here); CRLF vs LF, `.gitattributes` `text=auto eol=lf`, `git ls-files --eol`, y por qué un guardarraíl que se lee al arrancar necesita una verificación que falle ruidosamente (`check_docs.py` podría parsear los frontmatter). (27 oct 2026)
- [ ] Modelo y esfuerzo por tarea: "el modelo barato va donde hay una compuerta determinista que atrape sus errores; el caro donde el producto es el juicio"; cómo se midió hoy (plan en Fable alto = 3 % de cuota; cada fase en Sonnet medio ≈ 1 %) y qué riesgo queda (mismo modelo escribe código y tests → puede equivocarse coherentemente; por eso el plan lista los casos de prueba). (27 oct 2026)

## Resueltas

- [x] ADR-0005: qué significa el "riesgo aceptado" de dos fases concurrentes con líneas base distintas; quién
  mide la línea base y quién la compara (verificador, ejecutor, auditor) y por qué el auditor no puede detectar
  una regresión si su línea base está desactualizada. (26 oct 2026)
  > El riesgo aceptado consiste en que la disciplina es lo único que evita que ocurra el registro de un
  > baseline en el momento indebido, produciendo como resultado, en escenarios de ejecución paralela de fases
  > pertenecientes a ítems de deuda distintos, que el auditor permita el avance en la ejecución de fases aún
  > cuando en realidad se ha introducido más deuda de la verdaderamente saldada.
  > (la disciplina es 1 ítem de deuda a la vez; no se avanza al siguiente hasta que cada fase del anterior
  > haya sido auditada y mergeada).
- [x] Guardarraíl de línea base del ADR-0005: qué commit anota el verificador y contra cuál compara el
  ejecutor; por qué registrar `HEAD` y comparar con `merge-base` entra en bucle al re-verificar y, peor, no
  detecta que `develop` avance; por qué el diseño correcto anota y compara la punta de `origin/develop`
  tras `git fetch` y nunca mira la rama del ítem. (26 oct 2026)
  > Como se crea una rama por ítem, cuando el verificador anota la punta de la rama, el ejecutor compara
  > contra el commit de develop del que nació la rama: si ya hubo commit del verificacion.md, nunca van a
  > coincidir y el ejecutor se la pasa pidiendo re-verificaciones. Y si develop avanza (alguien más mete
  > deuda en remoto), ni la punta ni el merge-base de mi rama se mueven, así que no se detecta nada.
  > La solución: un mecanismo en vez de disciplina; el verificador anota la punta de origin/develop y el
  > ejecutor compara contra esa misma punta tras fetch, sin mirar el head de la rama específica.
