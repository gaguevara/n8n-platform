# FRAMEWORK_CAPABILITIES.md - n8n Platform DELCOP

## Proposito

Referencia rapida del estado real del framework multi-agente aplicado en este proyecto: capacidades activas, comandos utiles, skills detectados, validadores y limites operativos.

---

## 1. Engine operativo

| Capacidad | Comando base | Estado |
|-----------|--------------|--------|
| Estado de agentes | `python .multiagent/core/engine.py --config .multiagent/adapters/n8n-platform.json --base . status` | Operativo |
| Validacion por archivo | `python .multiagent/core/engine.py --config .multiagent/adapters/n8n-platform.json --base . validate <archivo> --json` | Operativo |
| Sincronizacion de indice | `python .multiagent/core/engine.py --config .multiagent/adapters/n8n-platform.json --base . sync-index --write` | Operativo |
| Monitoreo watchdog | `python .multiagent/core/proto_watch.py --status` / `--once` | Operativo |
| Patrones de edicion segura | Pattern 09 `insert-after-anchor` | Operativo |

Notas:
- Framework aplicado sobre adapter de proyecto `n8n-platform`.
- `proto_watch.py` esta presente en `.multiagent/core/`.
- El engine del framework tiene 29 tests esperados en la suite actual.

---

## 2. Agentes activos

| Agente | Rol | Archivo de entrada | Log |
|--------|-----|--------------------|-----|
| CLAUDE | Governor + Architect | `CLAUDE.md` | `docs/logs/CLAUDE_LOG.md` |
| CODEX | Implementer + DevOps | `AGENTS.md` | `docs/logs/CODEX_LOG.md` |
| GEMINI | Researcher + Reviewer | `GEMINI.md` | `docs/logs/GEMINI_LOG.md` |

---

## 3. Paths clave

| Recurso | Ruta |
|---------|------|
| Adapter principal | `.multiagent/adapters/n8n-platform.json` |
| Reglas del proyecto | `docs/governance/PROJECT_RULES.md` |
| Estado vivo | `docs/governance/CONTEXT.md` |
| Indice de trazabilidad | `docs/governance/LOG_INDEX.md` |
| Roles | `docs/governance/AGENT_ROLES.md` |
| Matriz de skills | `docs/skills/AGENT_SKILLS_MATRIX.md` |
| Changelog framework | `docs/CHANGELOG.md` |

---

## 4. MCP y tooling externo

| Fuente | Configuracion | Estado |
|--------|---------------|--------|
| Context7 | `.mcp.json` -> `@upstash/context7-mcp@latest` | Configurado |
| skills.sh | Skills detectados en `.agents/skills/` y `.claude/skills/` | Disponible |

---

## 5. Skills detectados

### 5.1 Skills del proyecto
- `adapt-project`
- `bootstrap-repo`
- `cross-review`
- `failure-to-rule`
- `gc-audit`
- `security-scan`
- `spec-create`
- `sync-agent-context`
- `validate-change`

### 5.2 Skills de soporte del stack
- `aws-ecs-fargate`
- `docker-security-guide`
- `postgres-patterns`

---

## 6. Validadores del adapter

| Extension | Validador |
|-----------|-----------|
| `.json` | `python -m json.tool {file}` |
| `.yml` / `.yaml` | `python -c "import yaml; yaml.safe_load(open('{file}'))"` |
| `.sh` | `bash -n {file}` |
| `.md` | `python -c "import os,sys; sys.exit(0 if os.path.getsize('{file}')>0 else 1)"` |

Windows fallbacks documentados:
- `pre-commit` -> `python -m pre_commit run --all-files`
- `sync-index` -> `powershell -ExecutionPolicy Bypass -File .multiagent/core/sync_index.ps1`
- `hadolint` / `shellcheck` -> via contenedores Docker

---

## 7. Restricciones actuales

- Host principal: Windows 11 + PowerShell.
- Los scripts `.sh` requieren fallback en Windows cuando no existe `/bin/bash`.
- El workflow de Threat Intel usa una variante segura para staging porque el JSON versionado no embebe automaticamente los code nodes ni las credenciales de runtime.
- Wazuh Indexer sigue bloqueado por topologia de red (`127.0.0.1:9200` en el host Wazuh).

---

## 8. Estado de adopcion

- Version del adapter del proyecto: `4.6`
- Bootstrap actualizado: `SESSION_BOOTSTRAP.md`
- Archivo de capacidades generado: `si`
- Matriz de skills presente: `si`
- Pattern 09 presente: `si`
- `proto_watch.py` presente: `si`

---

Ultima actualizacion: 2026-03-24 - Codex
