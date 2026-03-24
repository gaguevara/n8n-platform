# CHANGELOG.md — Framework Multi-Agente

## [4.5.0] — 2026-03-23

### SPEC-003: Agent Safety (9 ISC)
- Reglas append-only y anti-rewrite para proteger logs y gobernanza
- Verificación de proyecto correcto en bootstrap
- FRAMEWORK_CAPABILITIES.md generado por adapt-project
- Pattern 09: insert-after-anchor
- Tooling externo explicado en overlays
- CONTEXT.md con anchors mecánicos por agente
- Rutas reales en adapt-project
- Consolidación de reviews de 3 proyectos (n8n, Odoo, SGSI)

## [4.4.0] — 2026-03-20

### SPEC-002 completada + Context7/skills.sh + piloto n8n
- SPEC-002: Framework Hardening (Windows UX + Onboarding)
- Windows fallbacks: sync_index.ps1, docs en SESSION_BOOTSTRAP
- ONBOARDING reestructurado 70/30 (técnico/framework)
- Context7 (MCP) + skills.sh integrados como fuentes externas
- adapt-project detecta agentes activos, genera .gitkeep, UTF-8
- CONTEXT.md como contrato mecánico con `### @AGENTE - Rol`
- Piloto n8n-platform validado (score 8.1/10)
- Community skills instalados: python-best-practices, code-review-security
- Limpieza: archive/genesis/, zips obsoletos, version tags

## [4.2.0] — 2026-03-17

### SPEC-001: Robust Validation Router + Ruff
- validation_router.py standalone (pathlib, sin env vars)
- ruff configurado en pyproject.toml y pre-commit
- 15/15 tests passing (test_engine + test_validation_router)
- Auto-dispatch protocol para los 3 agentes
- adapt-project skill creado

## [4.1.0] — 2026-03-14

### Merge: v3.1 governance + v4 engine + skills oficiales
- `.multiagent/` — Core engine v4 ejecutable
- `.claude/skills/` — 7 skills formato oficial (SKILL.md + scripts/)
- `.claude/rules/` — Vacío, listo para project-specific FTR rules
- `docs/` — Governance, knowledge, harness, SDLC, logs
- hooks.json.example corregido (rutas .multiagent/)
- ZIP con rutas POSIX
- Sin contenido project-specific

## [4.0.0] — 2026-03-12
- Core engine Python + 8 patterns + adapter JSON + FTR template + 9 tests

## [3.1.0] — 2026-03-04
- .claude/ rules/hooks/commands/skills + path-scoped rules + PreCompact hooks

## [3.0.0] — 2026-03-04
- Knowledge base + Skills catalog + Harness + Spec-Driven + SDLC + pre-commit

## [2.0.0] — 2026-03-01
- Framework governance multi-agente base

## [1.0.0] — 2026-02-24
- Concepto inicial
