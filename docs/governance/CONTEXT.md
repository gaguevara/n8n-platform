# CONTEXT.md - Estado Actual del Proyecto

> **Ultima actualizacion:** 2026-03-19
> **Actualizado por:** Claude (Governor — replanificación Fase 1/2: staging + producción AWS)
> **Proxima revision:** al completar deploy staging (Fase 1)

---

## Estado general

| Campo         | Valor |
|---------------|-------|
| Fase          | Fase 1 — Deploy Staging (Dell R720) |
| Estabilidad   | Local validado. Staging y producción pendientes |
| Bloqueantes   | Acceso SSH a R720, prerequisitos Docker en R720 |
| Ultimo cambio | Replanificación: Local → Staging (R720) → Producción (AWS ECS) |

---

## Pendientes completados (Fase 0 — Local)

<details>
<summary>Ver tareas completadas de desarrollo local y Threat Intel</summary>

- [x] @CODEX: Validar `docker compose -f infra/docker-compose.local.yml config` con los nuevos servicios (threat-db, threat-cache)
- [x] @CODEX: Levantar stack completo (`docker compose up -d`) y verificar healthchecks de los 3 servicios
- [x] @CODEX: Verificar que el schema SQL se ejecuta correctamente en PostgreSQL (`01-schema.sql` + `seed_reference_data.sql`)
- [x] @CODEX: Importar `threat-intel-main.json` en n8n y verificar que los 30 nodos cargan sin errores
- [x] @CODEX: Ejecutar `hadolint` sobre `infra/Dockerfile` cuando Docker daemon este activo
- [x] @CODEX: Validar si `latest` debe mantenerse o fijarse por tag
- [x] @CODEX: Crear `app/workflows/.gitkeep` para versionar el directorio vacio
- [x] @CODEX: Corregir referencia incorrecta en `docs/governance/ONBOARDING.md`
- [x] @GEMINI: Revisar `docs/DATA-CONTRACTS.md` y validar coherencia con el schema SQL y los code nodes
- [x] @GEMINI: Verificar que los controles ISO 27001 mapeados en EXTERNAL_REVIEW_NOTES son correctos y actualizar AI_GOVERNANCE.md
- [x] @GEMINI: Adaptar `docs/governance/AI_GOVERNANCE.md` al proyecto n8n DELCOP
- [x] @GEMINI: Crear `docs/architecture/ADR_INDEX.md` indexando los 5 ADRs activos del proyecto
- [x] @CLAUDE: Cross-review de la validacion de Codex cuando complete el stack levantado
- [x] @CLAUDE: Auditar ECS Task Definition en AWS → **Cerrado: no existe infraestructura n8n en AWS aún. Replanificado como Fase 2 (producción)**

</details>

---

## Pendientes activos — Fase 1: Deploy Staging (Dell R720)

### @CODEX - Implementer/DevOps

- [ ] @CODEX: Verificar acceso SSH al Dell R720 desde la PC de oficina (`ssh $STAGING_USER@$STAGING_HOST`) y confirmar prerequisitos (Docker, Docker Compose v2, Git)
- [ ] @CODEX: Clonar repo en R720 si no existe (`/srv/n8n-platform`) o hacer `git pull origin main` si ya existe
- [ ] @CODEX: Crear `.env` en R720 a partir de `.env.staging.example` con valores reales (generar `N8N_ENCRYPTION_KEY`, configurar IPs, passwords de threat-db y Redis)
- [ ] @CODEX: Ejecutar `docker compose -f infra/docker-compose.staging.yml up -d` en R720 y verificar healthchecks de los 3 servicios (n8n, threat-db, threat-cache)
- [ ] @CODEX: Importar workflow Threat Intel en staging (`make -C ops staging-import`) y verificar 30 nodos cargados
- [ ] @CODEX: Validar que el schema SQL y seed se aplicaron correctamente en PostgreSQL de staging (7 tablas, 9 data sources)
- [ ] @CODEX: Verificar acceso al editor n8n desde navegador de oficina (`http://<IP_R720>:5678`)

### @GEMINI - Researcher/Reviewer

- [x] @GEMINI: Investigar best practices de AWS ECS Fargate para n8n — networking, storage (EFS vs bind), secrets injection, logging (CloudWatch)
- [x] @GEMINI: Documentar requisitos de infraestructura AWS para n8n en `docs/sdlc/SPEC_AWS_PRODUCTION.md`: cluster ECS, task definition, RDS PostgreSQL, ECR repo, Secrets Manager, security groups, ALB
- [x] @GEMINI: Mapear todas las variables de `.env.example` a su mecanismo de inyección en ECS (Secrets Manager para criticas, SSM Parameter Store para sensibles, env vars para config)

### @CLAUDE - Governor

- [ ] @CLAUDE: Cross-review del deploy de staging cuando Codex complete — validar healthchecks, schema, workflow, y conectividad LAN
- [x] @CLAUDE: Aprobar SPEC_AWS_PRODUCTION.md cuando Gemini lo entregue (Completado: aprobado — Secrets Manager para 4 críticos, SSM para API keys, SGs mínimo privilegio)
- [ ] @CLAUDE: Crear ADR-009 formalizando la estrategia de infraestructura AWS (ECS + RDS + Secrets Manager + ECR)

---

## Pendientes — Fase 2: Infraestructura AWS y Deploy Producción

> **Prerequisito:** Fase 1 completada y validada en staging

### @CODEX - Implementer/DevOps

- [ ] @CODEX: Crear repositorio ECR en AWS para la imagen n8n-delcop
- [ ] @CODEX: Crear secretos en AWS Secrets Manager: `N8N_ENCRYPTION_KEY`, `RDS_PASSWORD`, `THREAT_DB_PASSWORD`, `REDIS_PASSWORD`
- [ ] @CODEX: Crear cluster ECS `n8n-cluster` y task definition con referencias a Secrets Manager (no env vars planas)
- [ ] @CODEX: Crear instancia RDS PostgreSQL para n8n producción (aplicar schema + seed)
- [ ] @CODEX: Build + push de imagen a ECR (`make -C ops push-ecr`) y deploy inicial (`make -C ops deploy-prod`)
- [ ] @CODEX: Verificar healthcheck de n8n en ECS, importar workflow y validar operación

### @GEMINI - Researcher/Reviewer

- [ ] @GEMINI: Validar que los secretos en Secrets Manager no tienen valores por defecto ni placeholders
- [ ] @GEMINI: Revisar security groups y networking del ECS service vs RDS vs internet (principio de minimo privilegio)
- [ ] @GEMINI: Actualizar AI_GOVERNANCE.md con controles de producción AWS (A.9.4.1 acceso, A.10.1.1 cifrado, A.12.1.2 gestión de cambios)

### @CLAUDE - Governor

- [ ] @CLAUDE: Cross-review final de infraestructura AWS antes del primer deploy a producción
- [ ] @CLAUDE: Auditar ECS Task Definition — confirmar que `N8N_ENCRYPTION_KEY` y `RDS_PASSWORD` usan Secrets Manager (no env vars planas)
- [ ] @CLAUDE: Actualizar CONTEXT_SECURITY.md con el estado real de protección de secretos en producción

---

## Entornos

| Entorno    | Estado    | URL / Host            | Notas |
|------------|-----------|-----------------------|-------|
| Local      | Validado  | http://localhost:5678 | Docker Desktop, SQLite, threat-db en host `5433` |
| Staging    | Disponible| Dell R720 (LAN)       | VMware/Docker, SQLite/Volume |
| Produccion | Configurado | AWS ECS Fargate     | PostgreSQL RDS |

---

## Workflows activos

| Workflow | Archivo | Estado |
|----------|---------|--------|
| DELCOP Threat Intelligence - Main Pipeline | `app/workflows/threat-intel-main.json` | Importado y validado localmente - 30 nodos |

---

## Decisiones recientes

| Fecha      | Decision | Por |
|------------|----------|-----|
| 2026-03-16 | Adopcion framework multi-agente v4.2 | Claude |
| 2026-03-16 | Stack detectado: Docker + n8n + AWS ECS | Claude |
| 2026-03-17 | Activacion de Codex y Gemini como agentes | Claude |
| 2026-03-17 | Distribucion de tareas por rol | Claude |
| 2026-03-17 | Validaciones iniciales de Codex completas | Codex |
| 2026-03-17 | Stack local de n8n levantado y validado | Codex |
| 2026-03-17 | Politica latest validada contra upstream | Codex |
| 2026-03-17 | Pendientes de Codex revalidados y depurados | Codex |
| 2026-03-17 | Auditoria documental y .env.example | Gemini |
| 2026-03-17 | ADR-005 aprobado - SPEC_STAGING_PIPELINE | Claude |
| 2026-03-17 | CONTEXT_SECURITY.md creado | Claude |
| 2026-03-18 | Threat Intel pipeline aprobado (SPEC_THREAT_INTEL) | Claude |
| 2026-03-18 | ADR-006/007/008: PostgreSQL separada, scoring deterministico, code-nodes | Claude |
| 2026-03-18 | Compose local+staging actualizados con threat-db y threat-cache | Claude |
| 2026-03-19 | Compose local parametrizado para `THREAT_DB_HOST_PORT=5433` por conflicto local en `5432` | Codex |
| 2026-03-19 | `00-create-dbs.sh` corregido para usar `postgres` como maintenance DB y evitar doble aplicacion del schema | Codex |
| 2026-03-19 | `threat-intel-main.json` actualizado con `id` raiz estable para import CLI reproducible | Codex |
| 2026-03-19 | Validacion runtime local completada: stack healthy, schema+seed aplicados, workflow importado | Codex |
| 2026-03-19 | Auditoria AWS: no existe infra n8n en ECS — replanificado como Fase 1 (staging) + Fase 2 (AWS) | Claude |
| 2026-03-19 | Tareas distribuidas: 7 Codex, 3 Gemini, 3 Claude para Fase 1; 6 Codex, 3 Gemini, 3 Claude para Fase 2 | Claude |

---

## Notas de sesion

- 3 agentes activos: Claude (Governor), Codex (Implementer), Gemini (Researcher).
- Codex arranca con `AGENTS.md` y overlay en `docs/governance/CODEX_OVERLAY.md`.
- Gemini arranca con `GEMINI.md` y overlay en `docs/governance/GEMINI_OVERLAY.md`.
- Adapter del proyecto: `.multiagent/adapters/n8n-platform.json`.
