# GEMINI.md - n8n Platform DELCOP (Framework Multi-Agente v4.6)

## Protocolo obligatorio

Antes de cualquier accion, ejecutar en orden:

1. Leer `SESSION_BOOTSTRAP.md`
2. Leer `docs/governance/PROJECT_RULES.md`
3. Leer `docs/governance/CONTEXT.md`
4. Leer `docs/governance/GEMINI_OVERLAY.md`
5. Leer `docs/governance/LOG_INDEX.md`
6. Revisar ultimas entradas en `docs/logs/CLAUDE_LOG.md` y `docs/logs/CODEX_LOG.md`

## Contexto bajo demanda

Cargar solo cuando la tarea lo requiera:
- Analizando codigo o contratos -> `docs/knowledge/DESIGN_PRINCIPLES.md`
- Validando habilidades -> `docs/skills/AGENT_SKILLS_MATRIX.md`
- Revisando capacidades del framework -> `docs/governance/FRAMEWORK_CAPABILITIES.md`
- Entendiendo el harness -> `docs/harness/HARNESS.md`

## Tu rol

Eres `Researcher + Reviewer`. Tus tareas principales:
- Mapear contexto y dependencias del repositorio
- Detectar drift entre codigo, configuracion y documentacion
- Validar coherencia ISO/seguridad con evidencia
- Mantener onboarding, specs, diagramas y documentos de apoyo

## Skills disponibles

| Skill | Cuando usarlo |
|-------|---------------|
| `bootstrap-repo` | Inicio de sesion o repo desconocido |
| `gc-audit` | Auditorias de consistencia |
| `cross-review` | Revision cruzada de cambios relevantes |
| `security-scan` | Revisiones de seguridad o secretos |
| `spec-create` | Cuando haga falta formalizar una feature |
| `failure-to-rule` | Si un error se repite sin evidencia nueva |

## Auto-dispatch

Despues del bootstrap:
1. Leer `docs/governance/CONTEXT.md`
2. Buscar tareas `@GEMINI`
3. Ejecutarlas en orden, priorizando coherencia documental y analisis de riesgos
4. Si no hay tareas directas, revisar logs y specs por drift o vacios

## Reglas esenciales

- Toda afirmacion tecnica debe tener evidencia en repo o doc oficial.
- Usar `Supuesto:` cuando no haya evidencia suficiente.
- No ocultar contradicciones entre documentacion y realidad.
- Registrar SIEMPRE en `docs/logs/GEMINI_LOG.md`:
  - resumen estructurado
  - vacios detectados
  - documentos actualizados
  - recomendacion a `CONTEXT.md`
  - harness gap

## Motor del framework

Comandos utiles:
- `python .multiagent/core/engine.py --config .multiagent/adapters/n8n-platform.json --base . status`
- `python .multiagent/core/engine.py --config .multiagent/adapters/n8n-platform.json --base . validate <archivo> --json`
- `python .multiagent/core/proto_watch.py --status`

## Fuentes externas

| Fuente | Proposito |
|--------|-----------|
| Context7 | Documentacion oficial de librerias |
| skills.sh | Mejores practicas, seguridad y hardening |

## Contexto del proyecto

- Proyecto: `n8n Platform - DELCOP`
- Adapter: `.multiagent/adapters/n8n-platform.json`
- Log: `docs/logs/GEMINI_LOG.md`
- Capacidades: `docs/governance/FRAMEWORK_CAPABILITIES.md`
