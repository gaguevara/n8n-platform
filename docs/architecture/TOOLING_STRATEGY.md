# TOOLING_STRATEGY.md — Estrategia de Skills, MCP y Context7

> **Alcance:** Este documento aplica al proyecto `framework-multiagent`
> (primer caso de uso del framework). La plantilla base del framework
> solo define el *mecanismo* de skills; cada proyecto define los suyos.
>
> **Versión:** 1.1
> **Fecha:** 2026-03-16
> **Autor:** Claude Opus 4.6 (Governor / Architect)
> **Principio:** Los skills se definen por las necesidades del proyecto,
> no por una plantilla genérica. No hay un número fijo.

---

## 1. Contexto del proyecto

| Campo | Valor |
|-------|-------|
| Proyecto | Framework multi-agente para desarrollo en VS Code |
| Stack del core | Python 3.12+ (engine), Markdown (gobernanza), JSON (config), Bash (scripts) |
| Agentes | Claude Code, Codex CLI, Gemini CLI |
| Entorno | Windows 11 + VS Code + terminales bash |
| Objetivo | El framework se gestiona a sí mismo (primer caso de uso) |

---

## 2. Análisis de necesidades → Skills

Los skills NO se definen por template sino por necesidades reales del proyecto.

### 2.1 Necesidades identificadas

| # | Necesidad | Descripción | Frecuencia |
|---|-----------|-------------|------------|
| N1 | Orientación en el repo | Agente nuevo o al inicio de sesión necesita entender el proyecto | Cada sesión |
| N2 | Validación post-cambio | Lint + test + scan después de cada modificación de código | Cada cambio |
| N3 | Escalado de fallos | Convertir errores repetidos en reglas permanentes del harness | Cuando anti-loop activa |
| N4 | Planificación de features | Crear spec formal antes de implementar | Cada feature nueva |
| N5 | Revisión cruzada | Un agente diferente al autor valida cambios significativos | Cada cambio significativo |
| N6 | Auditoría de consistencia | Detectar drift docs↔código, dead code, TODOs stale | Periódica |
| N7 | Seguridad | Escaneo de CVEs, secrets, container vulnerabilities | Post-deps, periódica |
| N8 | Documentación actualizada | Acceso a docs de librerías/frameworks en tiempo real | Cada implementación |
| N9 | Sincronización de contexto | Mantener archivos de config de todos los agentes en sync | Post-cambio governance |
| N10 | Adaptación a proyecto nuevo | Generar adapter + archivos de agente al instalar el framework | Onboarding |

### 2.2 Mapeo: Necesidad → Skill → Agente que lo ejecuta

| Necesidad | Skill | Claude | Codex | Gemini |
|-----------|-------|:------:|:-----:|:------:|
| N1 | `bootstrap-repo` | Ejecuta | Equivalente vía AGENTS.md | Equivalente vía GEMINI.md |
| N2 | `validate-change` | Ejecuta | Ejecuta (nativo en sandbox) | Ejecuta (vía shell) |
| N3 | `failure-to-rule` | Ejecuta | Documenta en log | Documenta en log |
| N4 | `spec-create` | Ejecuta | Consultado | Consultado |
| N5 | `cross-review` | Ejecuta | Ejecuta | Ejecuta |
| N6 | `gc-audit` | Ejecuta | Ejecuta (dead code) | Ejecuta (doc drift) |
| N7 | `security-scan` | Ejecuta | Ejecuta (CVEs, deps) | Ejecuta (web advisories) |
| N8 | **Context7 (MCP)** | ✅ MCP nativo | ✅ MCP nativo | ✅ MCP nativo |
| N9 | `sync-agent-context` | Ejecuta | Informado | Informado |
| N10 | `adapt-project` | Ejecuta | Ejecuta (genera configs) | Ejecuta (genera docs) |

---

## 3. Configuración de skills por agente

### 3.1 Claude Code — Skills (`.claude/skills/`)

Formato: directorio con `SKILL.md` (frontmatter YAML + instrucciones markdown).

**Skills existentes a mantener (del proyecto):**

| Skill | Necesidad | Ajuste requerido |
|-------|-----------|------------------|
| `bootstrap-repo` | N1 | Ninguno — funcional |
| `validate-change` | N2 | Adaptar validators a cross-platform (usar python wrappers) |
| `failure-to-rule` | N3 | Ninguno — funcional como concepto |
| `spec-create` | N4 | Ninguno |
| `cross-review` | N5 | Ninguno |
| `gc-audit` | N6 | Ninguno |
| `security-scan` | N7 | Verificar que scripts funcionen en Windows/bash |

**Skills nuevos a crear (cuando la necesidad se materialice):**

| Skill | Necesidad | Trigger | Qué hace |
|-------|-----------|---------|----------|
| `sync-agent-context` | N9 | Después de cambios en governance docs | Ejecuta update-agent-context.sh, verifica consistencia |
| `adapt-project` | N10 | Al instalar framework en proyecto nuevo | Genera adapter JSON, archivos de agente, estructura de logs |

**Hooks de Claude Code (`.claude/settings.json` o hooks.json):**

```json
{
  "hooks": {
    "PreCompact": [{
      "matcher": "*",
      "hooks": [{
        "type": "prompt",
        "prompt": "CRITICAL: Re-read CLAUDE.md. Anti-loop: 2 fails = STOP. Post-change: validate-change. Log all activity."
      }]
    }],
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{
        "type": "command",
        "command": "python \"$CLAUDE_PROJECT_DIR/.multiagent/core/validation_router.py\""
      }]
    }]
  }
}
```

### 3.2 Codex CLI — Skills y configuración

Formato: AGENTS.md (raíz) + skills en `~/.codex/skills/` o `~/.agents/skills/` + config.toml.

**AGENTS.md** (ya existe `update-agent-context.sh` que lo genera):
```markdown
# AGENTS.md — Instrucciones para Codex CLI

## Bootstrap obligatorio
1. Leer SESSION_BOOTSTRAP.md
2. Leer docs/governance/PROJECT_RULES.md
3. Leer docs/governance/CONTEXT.md
4. Leer docs/governance/CODEX_OVERLAY.md
5. Revisar docs/governance/LOG_INDEX.md

## Rol: Implementer + DevOps
- Leer AGENT_ROLES.md §2.2 para responsabilidades completas
- Liderar Fase 2 (Ingeniería) del pipeline tri-agente
- Registrar actividad en docs/logs/CODEX_LOG.md
- Formato de log: ## ENTRADA-{number}

## Reglas
- Anti-loop: mismo error 2 veces = STOP
- Post-cambio: lint → test → scan
- Cambio mínimo necesario (Pattern 08)
- Evidence over opinion (Pattern 06)
```

**config.toml** (MCP servers para Codex):
```toml
# Context7 — documentación actualizada
[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp@latest"]

# GitHub — PRs, issues, repos
[mcp_servers.github]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-github"]
env = { GITHUB_PERSONAL_ACCESS_TOKEN = "${GITHUB_PAT}" }
```

### 3.3 Gemini CLI — Configuración

Formato: GEMINI.md (raíz) + settings.json + extensiones.

**GEMINI.md** (entry point para Gemini CLI):
```markdown
# GEMINI.md — Instrucciones para Gemini CLI

## Bootstrap obligatorio
1. Leer SESSION_BOOTSTRAP.md
2. Leer docs/governance/PROJECT_RULES.md
3. Leer docs/governance/CONTEXT.md
4. Leer docs/governance/GEMINI_OVERLAY.md
5. Revisar docs/governance/LOG_INDEX.md

## Rol: Researcher + Context Sentinel
- Leer AGENT_ROLES.md §2.3 para responsabilidades completas
- Liderar Fase 1 (Investigación) del pipeline tri-agente
- Registrar actividad en docs/logs/GEMINI_LOG.md
- Formato de log: ## ENTRADA-{number}

## Reglas
- Anti-loop: mismo error 2 veces = STOP
- Context before action — siempre
- Mantener CONTEXT.md actualizado
- Evidence over opinion (Pattern 06)
```

**settings.json** (MCP para Gemini):
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    }
  },
  "context": {
    "fileName": ["GEMINI.md", "SESSION_BOOTSTRAP.md"]
  }
}
```

---

## 4. Context7 — Integración para los 3 agentes

### 4.1 Qué es Context7

Context7 es un MCP server que provee documentación actualizada de cualquier librería
o framework, accesible desde los 3 CLIs vía el protocolo MCP estándar.

### 4.2 Por qué es necesario para este proyecto

| Sin Context7 | Con Context7 |
|-------------|-------------|
| Agente genera código con API obsoleta | Consulta docs actuales antes de generar |
| Agente alucina sobre params de una función | Obtiene firma real de la librería |
| Humano debe copiar docs al chat | Agente consulta directamente |
| Cada agente tiene knowledge cutoff diferente | Todos acceden a la misma fuente actualizada |

### 4.3 Instalación por agente

| Agente | Configuración | Comando |
|--------|--------------|---------|
| **Claude Code** | `.mcp.json` en raíz del proyecto | Ya configurado en la sesión actual |
| **Codex CLI** | `~/.codex/config.toml` | `codex mcp add context7 -- npx -y @upstash/context7-mcp@latest` |
| **Gemini CLI** | `~/.gemini/settings.json` | Agregar bloque `mcpServers.context7` manualmente |

### 4.4 Uso esperado

```
Agente necesita implementar algo con una librería
    │
    ▼
Context7: resolve-library-id("nombre-librería")
    │ → Devuelve library ID con snippets y benchmark
    ▼
Context7: query-docs(libraryId, "cómo hacer X")
    │ → Devuelve docs actualizadas + ejemplos de código
    ▼
Agente implementa con información correcta
```

### 4.5 Librerías relevantes disponibles en Context7

Para este proyecto, las más útiles son:

| Library ID | Snippets | Benchmark | Para qué |
|-----------|----------|-----------|----------|
| `/anthropics/claude-code` | 740 | 74.93 | Skills, hooks, MCP de Claude Code |
| `/openai/codex` | 694 | 65.14 | Skills, AGENTS.md, MCP de Codex |
| `/google-gemini/gemini-cli` | 1,656 | 69.88 | Extensions, settings de Gemini |
| `/affaan-m/everything-claude-code` | 2,874 | 75.87 | Skills y configs battle-tested |
| `/luohaothu/everything-codex` | 1,497 | 48.35 | Skills y configs para Codex |

---

## 5. MCP Servers recomendados para este proyecto

### 5.1 Tier 1 — Instalar ahora

| Server | Para qué | Todos los agentes |
|--------|---------|:-----------------:|
| **Context7** | Docs actualizadas de libs | ✅ |

### 5.2 Tier 2 — Instalar cuando se necesite

| Server | Para qué | Agente principal |
|--------|---------|:----------------:|
| **GitHub MCP** | PRs, issues, repos sin CLI | Codex, Claude |
| **Playwright MCP** | Testing de UI si hay frontend | Gemini |

### 5.3 Regla de gestión

> **Máximo ~10 MCP servers habilitados por proyecto.**
> Cada server agrega definiciones de tools al contexto del agente.
> Preferir CLI nativo cuando existe (ej: `gh` > GitHub MCP).

---

## 6. Flujo de adaptación actualizado

El proceso de adaptar el framework a un proyecto debe incluir esta evaluación de tooling:

```
Adaptar framework a proyecto nuevo
    │
    ├── 1. Detectar stack → definir validators
    ├── 2. Evaluar necesidades → definir skills POR NECESIDAD
    ├── 3. Identificar librerías usadas → configurar Context7
    ├── 4. Generar archivos de agente:
    │      ├── .claude/skills/   (skills que apliquen)
    │      ├── AGENTS.md         (instrucciones para Codex)
    │      ├── GEMINI.md         (instrucciones para Gemini)
    │      └── .mcp.json         (MCP servers necesarios)
    ├── 5. Configurar hooks relevantes al stack
    └── 6. Verificar que cada agente puede bootstrappear
```

Este flujo NO es fijo en el número de skills — se agregan o quitan según
lo que el proyecto necesite. Un proyecto web tendrá skills diferentes
a uno de backend puro o a uno de infraestructura.

---

## 7. Gaps actuales en este proyecto

| Gap | Acción | Prioridad | Responsable |
|-----|--------|-----------|-------------|
| ~~No existe AGENTS.md para Codex~~ | ~~Crear con bootstrap protocol~~ | ~~Alta~~ | **RESUELTO** |
| ~~No existe GEMINI.md para Gemini~~ | ~~Crear con bootstrap protocol~~ | ~~Alta~~ | **RESUELTO** |
| ~~Context7 no configurado en .mcp.json~~ | ~~Crear .mcp.json~~ | ~~Alta~~ | **RESUELTO** |
| Skills solo definidos para Claude Code | Documentar equivalentes para Codex/Gemini | Media | Cada agente |
| Hooks no activados (.json.example) | Activar hooks reales post-bootstrap | Media | Claude |
| update-agent-context.sh no es un skill invocable | Convertir en skill o dejar como script | Baja | Decision pendiente |

---

## Apéndice A — Formato de skills por CLI

### Claude Code
```
.claude/skills/nombre-skill/
├── SKILL.md          ← frontmatter YAML + instrucciones
├── scripts/          ← scripts ejecutables (opcional)
├── references/       ← archivos de referencia (opcional)
└── examples/         ← ejemplos (opcional)
```

### Codex CLI
```
~/.codex/skills/nombre-skill/
└── SKILL.md          ← frontmatter YAML + instrucciones
# O invocable como /nombre-skill en el chat
# Instrucciones globales en AGENTS.md (raíz del proyecto)
```

### Gemini CLI
```
# No tiene directorio de skills — usa:
GEMINI.md             ← instrucciones en raíz del proyecto
~/.gemini/settings.json  ← configuración + MCP
/extensions install <url> ← extensiones desde GitHub
```

---

*Documento creado: 2026-03-16 por Claude Opus 4.6 (Governor / Architect)*
*Los skills se definen por necesidad del proyecto, no por template.*
