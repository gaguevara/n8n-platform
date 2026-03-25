# FRAMEWORK_CAPABILITIES.md — Catálogo de Capacidades del Framework

## Propósito

Inventario local del framework realmente disponible en este repositorio. Sirve para que agentes y humanos identifiquen rápido qué herramientas existen, cuáles son externas y cómo validarlas.

---

## 1. Identidad operativa

| Campo | Valor |
|-------|-------|
| Directorio actual | `framework_multiagent` |
| Adapter principal | `.multiagent/adapters/framework-multiagent.json` |
| `project_name` del adapter | `framework-multiagent` |
| Agentes activos | `CLAUDE`, `CODEX`, `GEMINI` |
| Estado del catálogo | Generado en el repo base v4.5 |

> Nota: el nombre del directorio actual usa `_` y el adapter usa `-`. `SESSION_BOOTSTRAP.md` lo trata como alerta operativa para evitar trabajar en el repo equivocado.

---

## 2. Núcleo del framework

| Capacidad | Comando / Archivo | Estado |
|-----------|-------------------|--------|
| Status por agente | `python .multiagent/core/engine.py --config .multiagent/adapters/framework-multiagent.json --base . status` | Operativo |
| Sync de `LOG_INDEX.md` | `python .multiagent/core/engine.py --config .multiagent/adapters/framework-multiagent.json --base . sync-index --write` | Operativo |
| Validación por adapter | `python .multiagent/core/engine.py --config .multiagent/adapters/framework-multiagent.json --base . validate <file>` | Operativo |
| Router de validación | `.multiagent/core/validation_router.py` | Operativo |
| Fallback PowerShell para sync | `.multiagent/core/sync_index.ps1` | Operativo |
| Patrones del harness | `.multiagent/core/patterns/` | Operativo |

---

## 3. Tooling externo del framework

| Herramienta | Cómo se integra | Estado |
|-------------|------------------|--------|
| Context7 | MCP server configurado en `.mcp.json` y ejecutado vía `npx -y @upstash/context7-mcp@latest` | Configurado |
| skills.sh | CLI externa vía `npx skills ...` para descubrir/instalar skills comunitarios | Disponible si hay Node/npm |

- `Context7` es documentación externa en tiempo real; no existe como carpeta del repo.
- `skills.sh` es un instalador/catálogo externo; los skills aparecen en `.agents/skills/` solo después de instalarlos.

### Bibliotecas Context7 verificadas o preparadas

- IDs ya verificados en la trazabilidad del repo: `/anthropics/claude-code`, `/openai/codex`, `/google-gemini/gemini-cli`
- Consulta ya validada en logs: `resolve-library-id("pre-commit")`
- Objetivos útiles para este framework: `pre-commit`, `pytest`, `ruff`, `detect-secrets`
- Context7 no instala librerías en el repositorio; resuelve documentación y snippets vía MCP

---

## 4. Skills detectados en este repo

### Skills internos del framework (`.claude/skills/`)

- `adapt-project`
- `bootstrap-repo`
- `cross-review`
- `failure-to-rule`
- `gc-audit`
- `security-scan`
- `spec-create`
- `sync-agent-context`
- `validate-change`

### Skills comunitarios instalados (`.agents/skills/`)

- `axiom-file-protection-ref`
- `code-review-security`
- `python-best-practices`
- `python-testing-patterns`

---

## 5. Validadores configurados por adapter

| Patrón | Comando |
|--------|---------|
| `.py` | `python -m py_compile {file}` |
| `.md` | `python -c "import os,sys; sys.exit(0 if os.path.getsize('{file}')>0 else 1)"` |
| `.json` | `python -m json.tool {file}` |
| `.sh` | `python -c "open('{file}').read()"` |
| `.yaml` | `python -c "import yaml; yaml.safe_load(open('{file}'))"` |

---

## 6. Paths clave de gobernanza

| Tipo | Ruta |
|------|------|
| Estado vivo | `docs/governance/CONTEXT.md` |
| SSOT de reglas | `docs/governance/PROJECT_RULES.md` |
| Trazabilidad central | `docs/governance/LOG_INDEX.md` |
| Roles de agentes | `docs/governance/AGENT_ROLES.md` |
| Catálogo de capacidades | `docs/governance/FRAMEWORK_CAPABILITIES.md` |
| Logs por agente | `docs/logs/` |
| Specs activas | `docs/sdlc/` |

---

## 7. Comandos base de validación

```bash
python -m ruff check .multiagent/core .multiagent/tests
pytest .multiagent/tests -q
python .multiagent/core/engine.py --config .multiagent/adapters/framework-multiagent.json --base . status
python .multiagent/core/engine.py --config .multiagent/adapters/framework-multiagent.json --base . sync-index --write
```

---

## 8. Restricciones operativas actuales

- Host objetivo: Windows/PowerShell con fallbacks documentados
- Logs de agentes: append-only desde v4.5
- Gobernanza: preferir append o `insert-after-anchor`, no rewrites amplios
- El adapter y el nombre del directorio actual no coinciden exactamente; el bootstrap ahora lo alerta

---

*Última actualización: 2026-03-23 — Fuente: adapter real + estructura actual del repo*
