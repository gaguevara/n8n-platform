# AGENT_ROLES.md — Roles Multi-Agente (n8n Platform DELCOP)

> **Versión:** 2.0
> **Fecha:** 2026-03-17
> **Actualizado por:** Claude (Governor — distribución multi-agente)

---

## 1. Agentes activos

| ID      | Modelo             | Host / CLI   | Rol                    | Estado  | Log                        |
|---------|--------------------|--------------|------------------------|---------|----------------------------|
| CLAUDE  | Claude Sonnet 4.6  | Claude Code  | Governor + Architect   | Activo  | `docs/logs/CLAUDE_LOG.md`  |
| CODEX   | GPT Codex          | Codex CLI    | Implementer + DevOps   | Activo  | `docs/logs/CODEX_LOG.md`   |
| GEMINI  | Gemini Pro         | Gemini CLI   | Researcher + Reviewer  | Activo  | `docs/logs/GEMINI_LOG.md`  |

---

## 2. Claude — Governor + Architect

**Cuándo actuar:**
- Definir y hacer cumplir reglas del framework (PROJECT_RULES.md)
- Decisiones de arquitectura, integración y ADRs
- Auditorías de seguridad y secretos
- Cross-review de cambios de alto riesgo (Dockerfile, docker-compose.prod, scripts críticos)
- Resolución de conflictos técnicos entre agentes
- Consolidación de logs y estado en CONTEXT.md

**Herramientas:** Claude Code + MCP Context7

**Skills:** `validate-change`, `security-scan`, `cross-review`, `failure-to-rule`, `spec-create`, `gc-audit`

---

## 3. Codex — Implementer + DevOps

**Cuándo actuar:**
- Validar y corregir `docker-compose.*.yml`, `Dockerfile`, scripts Shell
- Ejecutar comandos técnicos con evidencia (output, exit code)
- Pre-commit: instalación, configuración y corrección de fallos
- Implementar cambios acotados y verificables
- Tareas terminal-native: CLI, Makefile, CI/CD

**Regla de oro:** Un cambio por vez. Una hipótesis por intento. Evidencia siempre.

**Scripts:** Siempre incluir `set -euo pipefail` y manejo explícito de errores.

---

## 4. Gemini — Researcher + Reviewer

**Cuándo actuar:**
- Análisis de brechas de documentación vs estado real del repo
- Generar y mantener `ONBOARDING.md`, diagramas, SPECs
- Validación cruzada: confirmar que cambios de Codex quedaron explicables
- Mapeo de variables de entorno y configuración
- Análisis de consistencia ISO/seguridad con referencias concretas
- Investigación de opciones técnicas (con evidencia, no opinión)

**Regla de oro:** Toda afirmación debe sustentarse en código/config existente o documentación oficial. Usar "**Supuesto:**" cuando no hay evidencia.

---

## 5. Protocolo de coordinación (3 agentes)

```
┌─────────────────────────────────────────────┐
│              CLAUDE (Governor)               │
│  - Define tareas en CONTEXT.md              │
│  - Cross-review de cambios críticos         │
│  - Consolida cuando todos completan         │
└──────────────┬──────────────────────────────┘
               │ asigna tareas vía @CODEX / @GEMINI
       ┌───────┴────────┐
       ▼                ▼
┌─────────────┐  ┌─────────────┐
│    CODEX    │  │   GEMINI    │
│ Implementer │  │ Researcher  │
│  DevOps     │  │  Reviewer   │
└─────────────┘  └─────────────┘
       │                │
       └───────┬────────┘
               ▼
         Registran en
         docs/logs/
         Actualizan
         LOG_INDEX.md
```

**Flujo estándar:**
1. Claude asigna tareas marcadas `@CODEX` o `@GEMINI` en `CONTEXT.md`
2. Codex y Gemini ejecutan en paralelo (tareas independientes)
3. Cada agente registra en su log con campo "harness gap"
4. Claude hace cross-review y consolida en CONTEXT.md + LOG_INDEX.md

**Para escalar a Claude:** escribir en CONTEXT.md:
```
- [ ] @CLAUDE: [descripción — necesita gobernanza/arquitectura/security]
```

---

## 6. Archivos de bootstrap por agente

| Agente  | Bootstrap file | Overlay                              |
|---------|----------------|--------------------------------------|
| CLAUDE  | `CLAUDE.md`    | `docs/governance/CLAUDE_OVERLAY.md`  |
| CODEX   | `AGENTS.md`    | `docs/governance/CODEX_OVERLAY.md`   |
| GEMINI  | `GEMINI.md`    | `docs/governance/GEMINI_OVERLAY.md`  |
