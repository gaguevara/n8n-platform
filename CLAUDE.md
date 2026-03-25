# CLAUDE.md — n8n Platform DELCOP (Framework Multi-Agente v4.7)

## Protocolo obligatorio

Antes de cualquier acción, ejecutar en orden:

1. Leer `SESSION_BOOTSTRAP.md` (raíz)
2. Leer `docs/governance/PROJECT_RULES.md` (SSOT del proyecto)
3. Leer `docs/governance/CONTEXT.md` (estado actual)
4. Leer tu overlay en `docs/governance/[AGENTE]_OVERLAY.md`
5. Leer `docs/governance/LOG_INDEX.md` (trazabilidad)
6. Revisar últimas entradas en `docs/logs/` de los otros agentes

## Contexto bajo demanda

Cargar solo cuando la tarea lo requiera:
- Generando/revisando código → `docs/knowledge/DESIGN_PRINCIPLES.md`
- Implementando feature con spec → `docs/sdlc/SPEC_[NOMBRE].md`
- Evaluando habilidades → `docs/skills/AGENT_SKILLS_MATRIX.md`
- Entendiendo el harness → `docs/harness/HARNESS.md`
- Ciclo SDLC → `docs/sdlc/SDLC_WORKFLOW.md`

## Skills disponibles

Los siguientes skills se activan automáticamente cuando son relevantes:

| Skill | Cuándo usarlo |
|-------|--------------|
| `security-scan` | Después de cambios en dependencias, Docker, configuración sensible |
| `validate-change` | Después de CADA modificación de código |
| `bootstrap-repo` | Al iniciar en repo nuevo o al inicio de sesión |
| `failure-to-rule` | Cuando el anti-loop se activa (2 fallos iguales) |
| `spec-create` | Cuando el usuario necesita planificar una feature nueva |
| `cross-review` | Cuando se completa un cambio significativo |
| `gc-audit` | Periódicamente o bajo demanda para auditar consistencia |

## Auto-dispatch (orquestacion automatica)

Al iniciar sesion, despues del bootstrap obligatorio:

1. Leer `docs/governance/CONTEXT.md` seccion "Pendientes inmediatos"
2. Buscar tareas marcadas con `@CLAUDE` o sin asignar que correspondan a tu rol (Governor)
3. Si hay tareas pendientes → ejecutarlas en orden de prioridad
4. Si no hay tareas asignadas → revisar logs de otros agentes para detectar:
   - Entradas nuevas que requieran validacion cruzada
   - Discrepancias abiertas en LOG_INDEX.md
   - SPECs en `docs/sdlc/` con estado "Propuesta" que requieran aprobacion
5. Si no hay nada pendiente → informar al usuario y pedir instrucciones

**No esperar a que el usuario diga "valida" o "consolida".**
Si hay trabajo pendiente en logs o CONTEXT.md, ejecutarlo proactivamente.

**Para asignar tareas a otros agentes**, escribir en CONTEXT.md:
```
- [ ] @GEMINI: [tarea de investigacion o contexto]
- [ ] @CODEX: [tarea de implementacion o validacion tecnica]
- [ ] @CLAUDE: [tarea de gobernanza o consolidacion]
```

## Reglas esenciales

- Framework multi-agente: multiples agentes pueden trabajar en el mismo repo.
- No modificar archivos sin leer contexto primero (Pattern 07).
- Investigar antes de cambiar (Pattern 01).
- Tests antes y despues de cada cambio (Pattern 02).
- Registrar actividad en `docs/logs/[AGENTE]_LOG.md` con campo "harness gap".
- Anti-loop: mismo error 2 veces = STOP → usar skill `failure-to-rule`.
- Principio harness: fallo repetido = mejorar entorno, no repetir prompt.
- Post-cambio: usar skill `validate-change`.
- Cambio minimo necesario (Pattern 08).
- Evidencia sobre opinion (Pattern 06).

## Motor del framework

El engine en `.multiagent/core/engine.py` provee:
- `status` — ver última entrada de log por agente
- `sync-index` — sincronizar LOG_INDEX automáticamente
- `validate <file>` — sugerir/ejecutar validador para un archivo

Configuración del proyecto en `.multiagent/adapters/n8n-platform.json`.

## Fuentes de conocimiento externo

| Fuente | Propósito | Uso |
|--------|-----------|-----|
| Context7 (MCP) | Documentación de librerías en tiempo real | `resolve-library-id` → `query-docs` |
| skills.sh | Mejores prácticas y seguridad (+89K skills) | `npx skills add -y <owner/repo@skill-name>` |

---

## Contexto del proyecto

- **Proyecto:** n8n Platform — DELCOP
- **Stack:** n8n + Docker + AWS ECS Fargate
- **Overlay activo:** `docs/governance/CLAUDE_OVERLAY.md`
- **Log activo:** `docs/logs/CLAUDE_LOG.md`
- **Adapter:** `.multiagent/adapters/n8n-platform.json`
