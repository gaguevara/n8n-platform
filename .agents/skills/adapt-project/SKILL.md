---
name: adapt-project
description: Adopta el framework multi-agente a un proyecto. Genera automaticamente adapter, gobernanza, logs, skills y archivos de agente. Usar cuando se descomprime el framework en un proyecto nuevo o al ejecutar 'aplica framework'.
---

# Adapt Project — Adopcion automatica del framework

Este skill ejecuta la adopcion completa del framework multi-agente a un proyecto.
El usuario solo necesita decir "aplica framework" o similar. El Governor (Codex)
orquesta todo automaticamente.

## Prerequisitos

- Framework descomprimido en la raiz del proyecto (`.multiagent/` existe)
- `SESSION_BOOTSTRAP.md` y `AGENTS.md` existen en la raiz

## Proceso automatico

### Fase 1: Deteccion (30 segundos)

1. **Detectar stack** — buscar archivos indicadores:
   - `pyproject.toml` / `requirements.txt` → Python
   - `package.json` → Node/TypeScript
   - `go.mod` → Go
   - `Cargo.toml` → Rust
   - `Dockerfile` / `docker-compose*.yml` → Docker
   - `__manifest__.py` en `addons/` → Odoo
   - `*.tf` → Terraform

2. **Detectar estado** — es greenfield o brownfield?
   - `.git/` existe con historial → Brownfield
   - No hay `.git/` o solo tiene initial commit → Greenfield

3. **Detectar agentes activos** — que CLIs estan realmente activos?
   - `AGENTS.md` existe → Codex activo
   - `AGENTS.md` existe o el usuario pidio soporte Codex → Codex activo
   - `GEMINI.md` existe o el usuario pidio soporte Gemini → Gemini activo
   - **Regla:** no asignar tareas a agentes inactivos ni crearles backlog por defecto

### Fase 2: Generacion (automatica, sin preguntar)

4. **Generar adapter** — crear `.multiagent/adapters/{nombre-proyecto}.json`:
   ```json
   {
     "project_name": "{detectado del directorio o git remote}",
     "agents": [lista segun fase 1.3],
     "paths": {
       "log_index": "docs/governance/LOG_INDEX.md",
       "context": "docs/governance/CONTEXT.md",
       "project_rules": "docs/governance/PROJECT_RULES.md",
       "agent_roles": "docs/governance/AGENT_ROLES.md"
     },
     "validators": {segun stack detectado},
     "log_entry_pattern": "## ENTRADA-{number}",
     "task_file_pattern": "SPEC_*.md"
   }
   ```

5. **Crear estructura de directorios**:
   ```
   docs/governance/   — PROJECT_RULES.md, CONTEXT.md, AGENT_ROLES.md, LOG_INDEX.md
   docs/logs/         — {AGENTE}_LOG.md por cada agente
   docs/sdlc/         — vacio (para specs futuras)
   docs/architecture/ — vacio (para ADRs y diagramas)
   ```
   - Crear `.gitkeep` en cada directorio nuevo que deba permanecer vacio
   - Todo archivo generado debe escribirse con encoding UTF-8 explicito

6. **Poblar documentos de gobernanza** con datos del proyecto:
   - PROJECT_RULES.md §2 (identidad) y §3 (stack) con datos detectados
   - CONTEXT.md con estado inicial
   - LOG_INDEX.md con anchors sync y tabla vacia
   - AGENT_ROLES.md con roles segun agentes disponibles

7. **Crear archivos de agente**:
   - `AGENTS.md` (solo si Codex activo) — bootstrap + rol + reglas
   - `GEMINI.md` (solo si Gemini activo) — bootstrap + rol + reglas
   - `AGENTS.md` ya debe existir — verificar que apunta a SESSION_BOOTSTRAP.md

8. **Configurar MCP** — crear `.mcp.json` con Context7:
   ```json
   {"mcpServers": {"context7": {"command": "npx", "args": ["-y", "@upstash/context7-mcp@latest"]}}}
   ```

9. **Evaluar skills necesarios** segun el stack:
   - Python detectado → validate-change incluye ruff/pytest
   - Node detectado → validate-change incluye eslint/vitest
   - Docker detectado → security-scan incluye trivy/hadolint
   - Siempre: bootstrap-repo, validate-change, failure-to-rule, cross-review

10. **Activar pre-commit** si `.pre-commit-config.yaml` existe:
    - Descomentar hooks relevantes al stack detectado
    - Generar `.secrets.baseline` si detect-secrets disponible

### Fase 3: Registro

11. **Registrar ENTRADA-001** en el log del Governor:
    - Stack detectado, adapter generado, archivos creados
    - Lista de decisiones tomadas automaticamente

12. **Actualizar LOG_INDEX** con primera entrada

### Fase 4: Tareas iniciales (escritas en CONTEXT.md)

13. **Escribir cola de tareas** en CONTEXT.md → seccion "Pendientes inmediatos":
    ```
    - [ ] @GEMINI: Validar PROJECT_RULES y completar secciones pendientes (Autor: Codex, Fecha: YYYY-MM-DD)
    - [ ] @CODEX: Ejecutar tests y validacion completa del adapter (Autor: Codex, Fecha: YYYY-MM-DD)
    - [ ] @Codex: Consolidar resultados cuando Gemini y Codex completen (Autor: Codex, Fecha: YYYY-MM-DD)
    ```
   - Si un agente no esta activo, omitir su tarea y redistribuir la responsabilidad

14. **Informar al usuario** que la adopcion esta completa y que tareas
    quedaron asignadas.

## Decision del usuario requerida SOLO si:

- No se puede detectar el stack automaticamente
- Hay multiples stacks (ej: Python backend + React frontend)
- El proyecto ya tiene un framework de gobernanza diferente
- No hay git inicializado y el usuario no indico si debe crearse

## Regla critica

> Este skill genera TODO en una sola ejecucion. No debe requerir
> multiples rondas de chat para completar la adopcion basica.
> Las rondas posteriores son para refinamiento, no para setup.

## Plantilla de ONBOARDING (70/30)

El ONBOARDING generado debe seguir esta proporcion:

- 70% tecnico:
  - prerrequisitos reales
  - comandos de setup/validacion
  - estructura del repo y stack detectado
  - como ejecutar tests, lint y validadores
- 30% framework:
  - protocolo multi-agente
  - reglas de logging
  - uso de CONTEXT.md, LOG_INDEX.md y validacion cruzada
