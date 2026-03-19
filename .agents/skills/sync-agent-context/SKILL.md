---
name: sync-agent-context
description: Sincroniza archivos de contexto entre agentes (AGENTS.md, GEMINI.md, AGENTS.md) cuando cambian documentos de gobernanza. Usar despues de modificar PROJECT_RULES, CONTEXT, AGENT_ROLES u otros docs compartidos.
---

# Sync Agent Context

Mantiene los archivos de entrada de cada agente sincronizados con los documentos de gobernanza.

## Cuando se activa

Despues de cambios en:
- `docs/governance/PROJECT_RULES.md`
- `docs/governance/CONTEXT.md`
- `docs/governance/AGENT_ROLES.md`
- `.multiagent/adapters/*.json`

## Proceso

### 1. Verificar que archivos de agente existen
- `AGENTS.md` (raiz) — entry point para Codex
- `AGENTS.md` (raiz) — entry point para Codex CLI
- `GEMINI.md` (raiz) — entry point para Gemini CLI

Si alguno no existe, crearlo siguiendo el formato de los existentes.

### 2. Verificar consistencia
Para cada archivo de agente, confirmar que:
- Referencias a archivos de gobernanza son correctas (rutas validas)
- El rol asignado coincide con `AGENT_ROLES.md`
- El formato de log indicado coincide con `log_entry_pattern` del adapter
- Los comandos del engine usan el adapter correcto

### 3. Ejecutar script si existe
```bash
bash update-agent-context.sh 2>/dev/null || echo "Script not available, sync manual"
```

### 4. Verificar con engine
```bash
python .multiagent/core/engine.py --config .multiagent/adapters/framework-multiagent.json status
```
Confirmar que el engine puede parsear los logs de los 3 agentes.

### 5. Resultado
Reportar que archivos se actualizaron y si hay inconsistencias detectadas.
Registrar en log con tag [SYNC].
