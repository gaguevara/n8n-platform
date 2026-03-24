# SESSION_BOOTSTRAP.md

## Propósito

Protocolo común de arranque para cualquier agente o desarrollador que inicie una sesión de trabajo en este repositorio. No iniciar cambios relevantes sin completar la secuencia de inicio.

---

## Secuencia obligatoria de inicio

```
0. Sincronizar con remote (si existe): `git pull origin main` (o `git stash && git pull && git stash pop` si hay cambios locales).
   - Si no hay remote configurado, omitir.
   - Si existe `.multiagent/adapters/*.json`, leer `project_name` del adapter principal y compararlo con el nombre del directorio actual.
   - Si no coincide -> ALERTAR al usuario antes de continuar. Es una alerta operativa, no un bloqueo automático.
1. Leer docs/governance/PROJECT_RULES.md
2. Si docs/governance/CONTEXT.md existe -> leerlo
   Si no existe -> ejecutar/adoptar framework via skill adapt-project antes de continuar
3. Leer overlay correspondiente en docs/governance/[AGENTE]_OVERLAY.md
4. Leer docs/governance/LOG_INDEX.md
5. Revisar últimas entradas relevantes en docs/logs/ de los otros agentes
6. Si la tarea involucra código → leer docs/knowledge/DESIGN_PRINCIPLES.md
7. Si hay dudas sobre habilidades esperadas → leer docs/skills/AGENT_SKILLS_MATRIX.md
8. Si la tarea tiene spec → leer docs/sdlc/SPEC_[NOMBRE].md
9. Determinar tipo de tarea → actuar según nivel
```

## Principio de Harness Engineering

> Cuando un agente falla, el problema es el entorno, no el agente.

Cada fallo repetido debe resultar en una mejora al harness (documentación, herramienta,
spec, constraint mecánica), no en repetir el prompt. Ver `docs/harness/HARNESS.md`.

---

## Arranque adaptativo

### Caso A — Tarea puntual y clara
Ejecutar directamente. Validar de inmediato. Registrar resultado en el log del agente.

### Caso B — Proyecto existente con contexto suficiente
No repetir cuestionarios. Leer estructura, reglas, decisiones activas y logs recientes. Continuar sobre la base existente.

### Caso C — Proyecto greenfield o contexto insuficiente
Solicitar o construir primero: objetivo, stack, restricciones, alcance. No proponer arquitectura cerrada sin ese mínimo contexto.

### Caso D — Cambio de alto riesgo
Se considera alto riesgo si afecta: arquitectura, autenticación/autorización, secretos, cifrado, esquema de datos, CI/CD de producción, integraciones críticas, o controles de auditoría.

En este caso:
- Elaborar plan breve antes de ejecutar
- Identificar archivos e impacto
- Registrar plan en el log del agente
- Requerir validación cruzada obligatoria

---

## Regla anti-loop

- Mismo error 2 veces consecutivas sin nueva evidencia → **STOP**. Reportar: error exacto, log, comando, hipótesis de causa raíz.
- Error distinto con hipótesis nueva → máximo 1 intento adicional con la hipótesis documentada.
- No repetir comandos equivalentes a ciegas.
- Registrar siempre: error, hipótesis, evidencia, siguiente acción recomendada.

---

## Reglas de preservación

- Los logs `*_LOG.md` son **append-only**. Solo agregar nuevas entradas al final del archivo.
- Nunca editar, truncar ni reordenar entradas previas de logs sin aprobación explícita del Governor o del humano responsable.
- Al modificar archivos maestros de gobernanza (`PROJECT_RULES.md`, `SESSION_BOOTSTRAP.md`, overlays, `CONTEXT.md`, `LOG_INDEX.md`), agregar al final de la sección existente o insertar después de un anchor estable.
- No reescribir secciones completas para introducir una regla puntual. Si una regla previa debe eliminarse, requiere aprobación explícita del Governor o del humano responsable.

---

## Cierre de sesión

Antes de dar una tarea por terminada:

1. Registrar en `docs/logs/[AGENTE]_LOG.md`
2. Actualizar `docs/governance/LOG_INDEX.md` con el último LOG-ID
3. Actualizar `docs/governance/CONTEXT.md` si cambió el estado del proyecto
   - Las tareas DEBEN estar bajo la sección del agente asignado (`### @AGENTE - Rol`)
   - No crear subsecciones temáticas que fragmenten los pendientes
4. Actualizar `docs/governance/PROJECT_RULES.md` si cambió una regla o decisión estable
5. Escalar a revisión cruzada si el cambio afecta áreas críticas (ver sección 8 de PROJECT_RULES.md)

---

## Fuentes de conocimiento externo

El framework integra dos fuentes complementarias para que los agentes trabajen con informacion actualizada:

### Context7 (MCP) — documentacion de librerias
- Provee documentacion en tiempo real de las librerias del stack del proyecto
- Uso: `resolve-library-id` para encontrar libreria, `query-docs` para consultar
- Configurado en `.mcp.json`
- Es tooling externo via MCP/npx; no es una carpeta del repositorio ni un archivo de gobernanza.
- **Para que:** saber *que hace* cada libreria (APIs, parametros, ejemplos)

### skills.sh — mejores practicas y seguridad
- Provee +89K skills comunitarios de buenas practicas, seguridad y calidad
- Instalacion: `npx skills add -y <owner/repo@skill-name>`
- `find-skills` se instala durante adapt-project para descubrir skills relevantes
- Es tooling externo via npm; solo aparece en `.agents/skills/` cuando se instala explicitamente.
- **Para que:** saber *como usar bien* cada tecnologia (guidelines, hardening, patrones)

Los skills propios del framework estan en `.claude/skills/`. Los skills comunitarios los complementan, no los reemplazan.

---

## Fallbacks Windows

Cuando el host no tenga herramientas POSIX instaladas, usar estas alternativas:

- `pre-commit` -> `python -m pre_commit run --all-files`
- `hadolint` -> `docker run --rm -i hadolint/hadolint < Dockerfile`
- `shellcheck` -> `docker run --rm -i koalaman/shellcheck-alpine`
- `sync-index` -> `python .multiagent/core/engine.py --config .multiagent/adapters/framework-multiagent.json --base . sync-index --write`
- `sync-index` manual -> `powershell -ExecutionPolicy Bypass -File .multiagent/core/sync_index.ps1`

Toda escritura desde scripts PowerShell debe usar `Out-File -Encoding UTF8` o equivalente.
