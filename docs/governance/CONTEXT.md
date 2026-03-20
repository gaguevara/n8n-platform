# CONTEXT.md - Estado Actual del Proyecto

> **Ultima actualizacion:** 2026-03-19
> **Actualizado por:** Claude (Governor — Fase 1.5: validación de triggers y fuentes en staging)
> **Proxima revision:** al completar configuración de fuentes y primer dry-run del pipeline

---

## Estado general

| Campo         | Valor |
|---------------|-------|
| Fase          | Fase 1.5 — Validación de triggers y fuentes de Threat Intel en staging |
| Estabilidad   | Staging healthy (R720 `192.168.0.70:5678`). Workflow robusteado. Error Handler listo para importar. |
| Bloqueantes   | Usuario configurando credenciales reales en n8n UI. Codex: dry-run E2E post-config |
| Ultimo cambio | Cross-review Gemini aprobado. Nuevas tareas: error workflow, Trellix IMAP, rate limits |

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

- [x] @CODEX: Verificar acceso SSH al Dell R720 desde la PC de oficina (`ssh $STAGING_USER@$STAGING_HOST`) y confirmar prerequisitos (Completado: acceso con clave habilitado; `docker`, `docker compose v5.1.0` y `git 2.43.0` disponibles)
- [x] @CODEX: Clonar repo en R720 si no existe (`/srv/n8n-platform`) o hacer `git pull origin main` si ya existe (Completado: repo existente actualizado de `9dc3929` a `14f03d8`)
- [x] @CODEX: Crear `.env` en R720 a partir de `.env.staging.example` con valores reales (generar `N8N_ENCRYPTION_KEY`, configurar IPs, passwords de threat-db y Redis) (Completado: `.env` real creado en `/srv/n8n-platform`)
- [x] @CODEX: Ejecutar `docker compose -f infra/docker-compose.staging.yml up -d` en R720 y verificar healthchecks de los 3 servicios (n8n, threat-db, threat-cache) (Completado: 3 servicios en `healthy` usando `docker compose --env-file .env`)
- [x] @CODEX: Importar workflow Threat Intel en staging (`make -C ops staging-import`) y verificar 30 nodos cargados (Completado: import OK en `n8n_staging`; 1 workflow con 30 nodos)
- [x] @CODEX: Validar que el schema SQL y seed se aplicaron correctamente en PostgreSQL de staging (7 tablas, 9 data sources) (Completado: `\dt` muestra 7 tablas; `data_sources=9`)
- [x] @CODEX: Verificar acceso al editor n8n desde navegador de oficina (`http://<IP_R720>:5678`) (Completado: `healthz` OK y raíz HTTP responde `200` en `http://192.168.0.70:5678`)

### @GEMINI - Researcher/Reviewer

- [x] @GEMINI: Investigar best practices de AWS ECS Fargate para n8n — networking, storage (EFS vs bind), secrets injection, logging (CloudWatch)
- [x] @GEMINI: Documentar requisitos de infraestructura AWS para n8n en `docs/sdlc/SPEC_AWS_PRODUCTION.md`: cluster ECS, task definition, RDS PostgreSQL, ECR repo, Secrets Manager, security groups, ALB
- [x] @GEMINI: Mapear todas las variables de `.env.example` a su mecanismo de inyección en ECS (Secrets Manager para criticas, SSM Parameter Store para sensibles, env vars para config)

### @CLAUDE - Governor

- [x] @CLAUDE: Cross-review del deploy de staging cuando Codex complete — validar healthchecks, schema, workflow, y conectividad LAN (Completado: Codex ENTRADA-012 validado — 3 servicios healthy, 7 tablas, 9 data sources, workflow importado en `192.168.0.70:5678`)
- [x] @CLAUDE: Aprobar SPEC_AWS_PRODUCTION.md cuando Gemini lo entregue (Completado: aprobado — Secrets Manager para 4 críticos, SSM para API keys, SGs mínimo privilegio)
- [x] @CLAUDE: Crear ADR-009 formalizando la estrategia de infraestructura AWS (ECS + RDS + Secrets Manager + ECR) (Completado: ADR-009 en ADR_INDEX.md — ECS Fargate, RDS PostgreSQL, Secrets Manager, ECR, ALB+ACM, CloudWatch)

---

## Pendientes activos — Fase 1.5: Validación de Triggers y Fuentes (Staging)

> **Prerequisito:** Staging healthy en R720 (`192.168.0.70:5678`) ✅
> **Objetivo:** Configurar credenciales, validar conectividad y ejecutar dry-run de cada fuente del pipeline Threat Intel

### Inventario de fuentes y triggers

| Fuente | Trigger | Frecuencia | API / Protocolo | Env Vars requeridas | Red |
|--------|---------|------------|-----------------|---------------------|-----|
| FortiGate | Cron | 5 min | REST v2 (`/api/v2/log/event/system`) | `FORTIGATE_HOST`, `FORTIGATE_API_KEY` | LAN |
| Wazuh | Cron | 2 min | REST v4 (auth JWT → `/alerts`) | `WAZUH_API_URL`, `WAZUH_API_USER`, `WAZUH_API_PASSWORD` | LAN/AWS |
| GuardDuty | Cron | 5 min | AWS API (`GetFindings`) | `AWS_REGION`, `GUARDDUTY_DETECTOR_ID`, IAM credentials | AWS |
| Zabbix | Cron | 5 min | JSON-RPC 2.0 (`trigger.get`) | `ZABBIX_API_URL`, `ZABBIX_API_TOKEN` | LAN |
| AbuseIPDB | Cron (OSINT) | 15 min | REST v2 (`/api/v2/blacklist`) | `ABUSEIPDB_API_KEY` | Internet |
| OTX AlienVault | Cron (OSINT) | 15 min | REST v1 (`/pulses/subscribed`) | `OTX_API_KEY` | Internet |
| Trellix ePO | IMAP/Outlook | Event-driven | Email parsing | `TRELLIX_IMAP_*` o Microsoft Graph | Internet/M365 |
| VirusTotal | Cron (planificado) | 15 min | REST v3 | `VIRUSTOTAL_API_KEY` | Internet — **Fase 1.1, no incluir ahora** |

### Canales de alerta

| Canal | Tipo | Env Var | Umbral |
|-------|------|---------|--------|
| Slack | Webhook | `SLACK_WEBHOOK_URL` | score >= 70 |
| Teams | Webhook | `TEAMS_WEBHOOK_URL` | score >= 70 |
| Email | SMTP | `ALERT_EMAIL_TO`, `ALERT_EMAIL_FROM`, SMTP credential en n8n | score >= 85 |

### Credenciales n8n UI requeridas

| Credential | Tipo | Necesario para |
|------------|------|----------------|
| `postgres` | PostgreSQL | Nodos `pg-upsert` y `pg-audit-log` — conexión a threat_intel DB |
| `smtp` | SMTP | Nodo `email-alert` — envío de alertas críticas |

### @CODEX - Implementer/DevOps

**Infraestructura base (hacer primero):**
- [ ] @CODEX: Configurar credencial PostgreSQL en n8n staging UI — host: `threat-db`, port: `5432`, db: `threat_intel`, user/pass de `.env`
- [ ] @CODEX: Configurar credencial SMTP en n8n staging UI — usar relay SMTP de DELCOP o M365
- [ ] @CODEX: Ejecutar test manual del nodo `pg-upsert` para confirmar que n8n puede escribir en PostgreSQL

**Fuentes internas (LAN):**
- [ ] @CODEX: Validar conectividad desde R720 al FortiGate (`curl -k https://$FORTIGATE_HOST/api/v2/cmdb/system/status`) y configurar API key en `.env` staging
- [ ] @CODEX: Validar conectividad desde R720 a Wazuh (`curl -k -u user:pass $WAZUH_API_URL/security/user/authenticate`) y configurar credenciales en `.env` staging
- [ ] @CODEX: Validar conectividad desde R720 a Zabbix (`curl $ZABBIX_API_URL -d '{"jsonrpc":"2.0","method":"apiinfo.version","id":1}'`) y configurar token en `.env` staging

**Fuentes AWS:**
- [ ] @CODEX: Verificar si GuardDuty está habilitado en la cuenta AWS (`aws guardduty list-detectors`), obtener `DETECTOR_ID` y configurar IAM credentials para n8n

**Fuentes OSINT (Internet):**
- [ ] @CODEX: Registrar cuenta gratuita en AbuseIPDB, obtener API key y configurar `ABUSEIPDB_API_KEY` en `.env` staging
- [ ] @CODEX: Registrar cuenta gratuita en OTX AlienVault, obtener API key y configurar `OTX_API_KEY` en `.env` staging

**Canales de alerta:**
- [ ] @CODEX: Crear webhook de Slack (o Teams) de prueba en canal `#security-alerts-test` y configurar `SLACK_WEBHOOK_URL` en `.env` staging

**Validación end-to-end:**
- [ ] @CODEX: Ejecutar dry-run manual de cada fuente configurada: trigger manual en n8n UI → verificar que los datos fluyen hasta PostgreSQL (tabla `iocs`) y que las alertas llegan al canal configurado
- [ ] @CODEX: Reiniciar compose en R720 (`docker compose restart`) para cargar las nuevas env vars después de cada cambio en `.env`

### @GEMINI - Researcher/Reviewer

- [x] @GEMINI: Documentar el procedimiento exacto para crear un API user read-only en FortiGate (perfil, trusted hosts, generación de API key) con capturas o pasos de GUI (Completado en `docs/knowledge/SOURCE_CONFIG_GUIDE.md`)
- [x] @GEMINI: Documentar el procedimiento para crear un usuario Wazuh con roles limitados (`agents:read`, `alerts:read`) — API o GUI de Wazuh Dashboard (Completado en `docs/knowledge/SOURCE_CONFIG_GUIDE.md`)
- [x] @GEMINI: Documentar el procedimiento para generar API token en Zabbix (Administration → API tokens) con permisos mínimos (Completado en `docs/knowledge/SOURCE_CONFIG_GUIDE.md`)
- [x] @GEMINI: Investigar si GuardDuty está habilitado en la cuenta AWS `043019737945` y qué política IAM mínima necesita n8n (`guardduty:ListFindings`, `guardduty:GetFindings`) (Completado: Habilitado, Detector `68c960313fc4628bdf683f052e953cf5`)
- [x] @GEMINI: Validar que el workflow maneja correctamente el caso de fuente sin datos (empty response) — que no genere errores ni alertas falsas (Completado: Fix aplicado en `ioc_normalizer.js` y `continueOnFail` en nodos HTTP)

### @GEMINI - Researcher/Reviewer (nuevas tareas)

- [x] @GEMINI: Crear workflow de error (`error-handler.json`) para n8n — debe capturar fallos del pipeline principal, registrar en `workflow_runs` con status `error`, y notificar por Slack con contexto del fallo (Completado en `app/workflows/error-handler.json`)
- [x] @GEMINI: Documentar procedimiento de configuración de Trellix ePO via IMAP (buzón compartido M365 `trellix-alerts@delcop.com.co`) en `SOURCE_CONFIG_GUIDE.md` — incluir permisos Graph API si se usa Microsoft Outlook Trigger (Completado en `docs/knowledge/SOURCE_CONFIG_GUIDE.md`)
- [x] @GEMINI: Crear `docs/sdlc/SPEC_ERROR_HANDLING.md` — especificar estrategia de retry, dead-letter, timeouts y alertas para el pipeline TI (Completado en `docs/sdlc/SPEC_ERROR_HANDLING.md`)
- [x] @GEMINI: Revisar rate limits de cada fuente OSINT y documentar cuántas ejecuciones/día consume el pipeline con los intervalos actuales (AbuseIPDB: 96/día de 1000 free, OTX: sin límite documentado) (Completado en `docs/knowledge/SOURCE_CONFIG_GUIDE.md`)

### @CLAUDE - Governor

- [x] @CLAUDE: Cross-review de cada credencial/fuente configurada antes de activar el trigger cron correspondiente (Completado: Gemini ENTRADA-007 — SOURCE_CONFIG_GUIDE.md validado, ioc_normalizer.js fix aprobado, continueOnFail en 6 nodos HTTP aprobado)
- [x] @CLAUDE: Verificar que las API keys y tokens NO quedaron en archivos trackeados (solo en `.env` del R720) (Completado: grep confirma solo placeholders en `.env.example`/`.env.staging.example`; `.env` en `.gitignore`)
- [ ] @CLAUDE: Aprobar activación del workflow en modo automático (triggers cron activos) una vez validadas todas las fuentes
- [ ] @CLAUDE: Registrar ADR-010 con la decisión de fuentes activas vs pendientes y sus justificaciones

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
- [x] @GEMINI: Actualizar AI_GOVERNANCE.md con controles de producción AWS (A.9.4.1 acceso, A.10.1.1 cifrado, A.12.1.2 gestión de cambios) (Completado: Revisión de riesgos y controles ISO actualizada)

### @CLAUDE - Governor

- [ ] @CLAUDE: Cross-review final de infraestructura AWS antes del primer deploy a producción
- [ ] @CLAUDE: Auditar ECS Task Definition — confirmar que `N8N_ENCRYPTION_KEY` y `RDS_PASSWORD` usan Secrets Manager (no env vars planas)
- [ ] @CLAUDE: Actualizar CONTEXT_SECURITY.md con el estado real de protección de secretos en producción

---

## Entornos

| Entorno    | Estado    | URL / Host            | Notas |
|------------|-----------|-----------------------|-------|
| Local      | Validado  | http://localhost:5678 | Docker Desktop, SQLite, threat-db en host `5433` |
| Staging    | Healthy   | http://192.168.0.70:5678 | Dell R720, Docker, 3 servicios healthy, workflow importado |
| Produccion | No existe | AWS ECS Fargate (planificado) | Infraestructura por crear (Fase 2) |

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
| 2026-03-19 | Deploy de staging ejecutado en R720: SSH, pull, `.env`, compose, import workflow, schema+seed y acceso HTTP validados | Codex |
| 2026-03-19 | Cross-review staging aprobado por Claude (ENTRADA-009) | Claude |
| 2026-03-19 | Fase 1.5: distribución de tareas para validación de 7 fuentes TI + 3 canales alerta en staging | Claude |
| 2026-03-19 | Cross-review Gemini Fase 1.5: SOURCE_CONFIG_GUIDE, ioc_normalizer fix, continueOnFail aprobados | Claude |
| 2026-03-19 | Nuevas tareas Gemini: error workflow, Trellix IMAP, SPEC_ERROR_HANDLING, rate limits | Claude |
| 2026-03-19 | Gemini completó 4 tareas nuevas: error-handler.json, SPEC_ERROR_HANDLING, Trellix IMAP, rate limits | Gemini |
| 2026-03-19 | Codex trigger-validation: GuardDuty confirmado, egress OSINT verificado, credenciales n8n pendientes | Codex |
| 2026-03-20 | Cross-review Gemini ENTRADA-008 aprobado: error workflow, SPEC_ERROR_HANDLING, rate limits | Claude |
| 2026-03-20 | ADR-009 creado: ECS Fargate + RDS + Secrets Manager + ECR + ALB + CloudWatch | Claude |

---

## Notas de sesion

- 3 agentes activos: Claude (Governor), Codex (Implementer), Gemini (Researcher).
- Codex arranca con `AGENTS.md` y overlay en `docs/governance/CODEX_OVERLAY.md`.
- Gemini arranca con `GEMINI.md` y overlay en `docs/governance/GEMINI_OVERLAY.md`.
- Adapter del proyecto: `.multiagent/adapters/n8n-platform.json`.
