# CONTEXT.md - Estado Actual del Proyecto

> **Ultima actualizacion:** 2026-03-18
> **Actualizado por:** Claude (Governor — integración Threat Intelligence pipeline)
> **Proxima revision:** al completar cualquier tarea pendiente

---

## Estado general

| Campo         | Valor                                          |
|---------------|------------------------------------------------|
| Fase          | Threat Intelligence pipeline integrado (Fase 1.0) |
| Estabilidad   | En validacion — compose actualizado, pendiente levantar stack |
| Bloqueantes   | Validacion Docker local + staging desde oficina |
| Ultimo cambio | Merge threat-intel-merge-package + compose + env |

---

## Pendientes inmediatos

### @CODEX - Implementer/DevOps

- [x] @CODEX: Validar que `infra/docker-compose.local.yml` es valido (`docker compose config`) (Completado: config valido tras hacer opcional `../.env` y agregar `healthcheck`)
- [x] @CODEX: Revisar `scripts/export-workflows.sh`, `scripts/import-workflows.sh` y `scripts/backup.sh` - agregar `set -euo pipefail` si falta (Completado: los 3 scripts ya lo incluyen; sintaxis validada con Git Bash)
- [x] @CODEX: Ejecutar `pre-commit install` y verificar que los hooks pasan en estado actual (Completado: hook instalado y `pre-commit run --all-files` en verde; se agrego `.secrets.baseline`)
- [x] @CODEX: Validar sintaxis del `infra/Dockerfile` con `hadolint` (si disponible) o revision manual (Completado: revision manual; `hadolint` local no disponible y Docker daemon ausente)

### @GEMINI - Researcher/Reviewer

- [x] @GEMINI: Analizar brechas de documentacion en el repo - comparar estructura actual vs PROJECT_RULES.md section 9 (Completado: `.env.example` y staging spec identificados como gaps)
- [x] @GEMINI: Evaluar si se necesita `docs/sdlc/SPEC_STAGING_PIPELINE.md` para documentar el pipeline staging->prod (Completado: creado en `docs/sdlc/`)
- [x] @GEMINI: Actualizar `docs/governance/ONBOARDING.md` con setup local exacto (Completado: agregada seccion tecnica)
- [x] @GEMINI: Mapear todas las variables de entorno del proyecto (`.env.example`, compose files) y reportar brechas (Completado: creado `.env.example`)

### @CLAUDE - Governor

- [x] @CLAUDE: Crear `docs/governance/CONTEXT_SECURITY.md` con inventario de secretos/variables sensibles (Completado)
- [x] @CLAUDE: Revisar trabajo de @CODEX en scripts y docker-compose (cross-review) (Completado: aprobado con 1 aviso TAG=latest)
- [x] @CLAUDE: Consolidar resultados cuando Codex y Gemini completen sus tareas iniciales (Completado)
- [x] @CLAUDE: Crear ADR-005 - pipeline staging->prod formalizado (Completado: SPEC aprobada)

### Threat Intelligence — pendientes activos

- [ ] @CODEX: Validar `docker compose -f infra/docker-compose.local.yml config` con los nuevos servicios (threat-db, threat-cache) (Autor: Claude, Fecha: 2026-03-18)
- [ ] @CODEX: Levantar stack completo (`docker compose up -d`) y verificar healthchecks de los 3 servicios (Autor: Claude, Fecha: 2026-03-18)
- [ ] @CODEX: Verificar que el schema SQL se ejecuta correctamente en PostgreSQL (`01-schema.sql` + `seed_reference_data.sql`) (Autor: Claude, Fecha: 2026-03-18)
- [ ] @CODEX: Importar `threat-intel-main.json` en n8n y verificar que los 30 nodos cargan sin errores (Autor: Claude, Fecha: 2026-03-18)
- [ ] @GEMINI: Revisar `docs/DATA-CONTRACTS.md` y validar coherencia con el schema SQL y los code nodes (Autor: Claude, Fecha: 2026-03-18)
- [ ] @GEMINI: Verificar que los controles ISO 27001 mapeados en EXTERNAL_REVIEW_NOTES son correctos y actualizar AI_GOVERNANCE.md (Autor: Claude, Fecha: 2026-03-18)
- [ ] @CLAUDE: Cross-review de la validacion de Codex cuando complete el stack levantado (Autor: Claude, Fecha: 2026-03-18)

### Pendientes - siguiente ciclo

- [x] @CODEX: Ejecutar `hadolint` sobre `infra/Dockerfile` cuando Docker daemon este activo (Completado: warning `DL3007` por uso de `latest`; sin errores de sintaxis)
- [x] @CODEX: Validar si `latest` debe mantenerse o fijarse por tag (Completado: por requerimiento de usuario se mantiene `latest`; validado contra upstream el 2026-03-17: `docker.n8n.io/n8nio/n8n:latest` resuelve a `2.12.2`)
- [ ] @CLAUDE: Auditar ECS Task Definition en AWS - verificar uso de Secrets Manager para `N8N_ENCRYPTION_KEY` y `RDS_PASSWORD` (bloqueado: requiere acceso AWS desde oficina)
- [x] @CODEX: Crear `app/workflows/.gitkeep` para versionar el directorio vacio (Completado: el archivo ya existia; pendiente previo quedo obsoleto)
- [x] @CODEX: Corregir referencia incorrecta en `docs/governance/ONBOARDING.md` - apuntaba a `docs/agents/` y ahora apunta a `docs/governance/`
- [x] @GEMINI: Adaptar `docs/governance/AI_GOVERNANCE.md` al proyecto n8n DELCOP (Completado: Personalizado con responsables y ToS)
- [x] @GEMINI: Crear `docs/architecture/ADR_INDEX.md` indexando los 5 ADRs activos del proyecto (Completado: Creado con detalle de decisiones)

---

## Entornos

| Entorno    | Estado      | URL / Host            | Notas                        |
|------------|-------------|-----------------------|------------------------------|
| Local      | Disponible  | http://localhost:5678 | Docker Desktop, SQLite       |
| Staging    | Disponible  | Dell R720 (LAN)       | VMware/Docker, SQLite/Volume |
| Produccion | Configurado | AWS ECS Fargate       | PostgreSQL RDS               |

---

## Workflows activos

| Workflow | Archivo | Estado |
|----------|---------|--------|
| DELCOP Threat Intelligence - Main Pipeline | `app/workflows/threat-intel-main.json` | Integrado — pendiente validacion en n8n |

---

## Decisiones recientes

| Fecha      | Decision                                  | Por    |
|------------|-------------------------------------------|--------|
| 2026-03-16 | Adopcion framework multi-agente v4.2      | Claude |
| 2026-03-16 | Stack detectado: Docker + n8n + AWS ECS   | Claude |
| 2026-03-17 | Activacion de Codex y Gemini como agentes | Claude |
| 2026-03-17 | Distribucion de tareas por rol            | Claude |
| 2026-03-17 | Validaciones iniciales de Codex completas | Codex  |
| 2026-03-17 | Stack local de n8n levantado y validado   | Codex  |
| 2026-03-17 | Politica latest validada contra upstream  | Codex  |
| 2026-03-17 | Pendientes de Codex revalidados y depurados | Codex |
| 2026-03-17 | Auditoria documental y .env.example       | Gemini |
| 2026-03-17 | ADR-005 aprobado - SPEC_STAGING_PIPELINE  | Claude |
| 2026-03-17 | CONTEXT_SECURITY.md creado                | Claude |
| 2026-03-18 | Threat Intel pipeline aprobado (SPEC_THREAT_INTEL) | Claude |
| 2026-03-18 | ADR-006/007/008: PostgreSQL separada, scoring deterministico, code-nodes | Claude |
| 2026-03-18 | Compose local+staging actualizados con threat-db y threat-cache | Claude |

---

## Notas de sesion

- 3 agentes activos: Claude (Governor), Codex (Implementer), Gemini (Researcher).
- Codex arranca con `AGENTS.md` y overlay en `docs/governance/CODEX_OVERLAY.md`.
- Gemini arranca con `GEMINI.md` y overlay en `docs/governance/GEMINI_OVERLAY.md`.
- Adapter del proyecto: `.multiagent/adapters/n8n-platform.json`.
