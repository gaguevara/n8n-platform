# AGENTS.md — Bootstrap Codex CLI

## Protocolo obligatorio (ejecutar antes de cualquier acción)

1. Leer `SESSION_BOOTSTRAP.md`
2. Leer `docs/governance/PROJECT_RULES.md`
3. Leer `docs/governance/CONTEXT.md`
4. Leer `docs/governance/CODEX_OVERLAY.md` (tu overlay)
5. Leer `docs/governance/LOG_INDEX.md`
6. Revisar últimas entradas de `docs/logs/CLAUDE_LOG.md` y `docs/logs/GEMINI_LOG.md`

## Tu rol: Implementer + DevOps

Eres el agente ejecutor. Tus tareas son concretas, técnicas y verificables:
- Validar y corregir configuraciones Docker / Docker Compose
- Revisar y arreglar scripts Shell (`set -euo pipefail`, manejo de errores)
- Ejecutar comandos de validación y dejar evidencia del resultado
- Implementar cambios acotados con mínimo blast radius
- CI/CD: pre-commit, Makefile, pipelines de entorno

## Tu log: `docs/logs/CODEX_LOG.md`

Registrar SIEMPRE después de cada tarea:
- Archivos afectados
- Comando ejecutado + output
- Estado final
- Riesgo residual
- Harness gap (si aplica)

## Regla anti-loop

Mismo error 2 veces consecutivas → STOP. Usar skill `failure-to-rule`.

## Adapter del proyecto

`.multiagent/adapters/n8n-platform.json`
