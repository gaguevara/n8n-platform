# CONTEXT.md - Estado Actual del Proyecto

> **Ultima actualizacion:** 2026-03-22
> **Actualizado por:** Claude (Governor — Cross-review Fase 1.6 + tareas Fase 1.7)
> **Proxima revision:** al completar dry-runs de todas las fuentes + credenciales Wazuh/Zabbix

---

## Estado general

| Campo         | Valor |
|---------------|-------|
| Fase          | Fase 1.7 — Dry-run por fuente + preparación Fase 2 AWS |
| Estabilidad   | Staging healthy (R720). FortiGate corregido+reimportado. Normalizer UTM actualizado. |
| Bloqueantes   | Credenciales Wazuh y Zabbix — pendientes del usuario |
| Ultimo cambio | Cross-review Codex ENTRADA-019/020 + Gemini ENTRADA-013/014 aprobados |

---

## Pendientes por Agente (v4.4+)

### @CODEX - Implementer/DevOps

- [x] @CODEX: Verificar acceso SSH al Dell R720 y prerequisitos (Docker, Git)
- [x] @CODEX: Clonar/Actualizar repo en R720 (`/srv/n8n-platform`)
- [x] @CODEX: Crear `.env` en R720 con valores reales de staging
- [x] @CODEX: Levantar stack staging en R720 y verificar healthchecks
- [x] @CODEX: Importar workflow Threat Intel en staging UI
- [x] @CODEX: Validar schema SQL y seed en PostgreSQL de staging
- [x] @CODEX: Verificar acceso al editor n8n en `192.168.0.70:5678`
- [x] @CODEX: Configurar credencial PostgreSQL en n8n staging UI
- [x] @CODEX: Configurar credencial SMTP en n8n staging UI
- [x] @CODEX: Importar `error-handler.json` y vincularlo al pipeline principal
- [x] @CODEX: Verificar GuardDuty habilitado y `DETECTOR_ID`
- [x] @CODEX: Corregir referencia incorrecta en `docs/governance/ONBOARDING.md`
- [ ] @CODEX: Ejecutar test manual del nodo `pg-upsert` en n8n UI (staging)
- [x] @CODEX: Validar conectividad y configurar API key FortiGate en `.env` staging
- [x] @CODEX: Reimportar `threat-intel-main.json` corregido en n8n staging (endpoint FortiGate fix) (Completado: workflow reimportado en R720 el 2026-03-22; export valida `/api/v2/log/memory/event/system` y normalizador actualizado)
- [ ] @CODEX: Validar conectividad y configurar credenciales Wazuh en `.env` staging
- [ ] @CODEX: Validar conectividad y configurar token Zabbix en `.env` staging
- [ ] @CODEX: Registrar AbuseIPDB y configurar API key en `.env` staging
- [ ] @CODEX: Registrar OTX AlienVault y configurar API key en `.env` staging
- [ ] @CODEX: Crear webhook Slack/Teams de prueba y configurar en `.env` staging
- [ ] @CODEX: Ejecutar dry-run vía n8n UI de cada fuente configurada
- [ ] @CODEX: Reiniciar compose en R720 tras cargar nuevas env vars
- [ ] @CODEX: Ejecutar dry-run del nodo FortiGate en staging UI y capturar respuesta (Fase 1.7)
- [ ] @CODEX: Agregar nodos adicionales al workflow para IPS (`utm/ips`) y Antivirus (`utm/virus`) (Fase 1.7)
- [ ] @CODEX: Crear repositorio ECR en AWS (Fase 2)
- [ ] @CODEX: Crear secretos en AWS Secrets Manager (Fase 2)
- [ ] @CODEX: Crear cluster ECS y task definition (Fase 2)
- [ ] @CODEX: Crear instancia RDS PostgreSQL para producción (Fase 2)
- [ ] @CODEX: Build + push de imagen a ECR y deploy inicial (Fase 2)

### @GEMINI - Researcher/Reviewer

- [x] @GEMINI: Investigar best practices de AWS ECS Fargate para n8n
- [x] @GEMINI: Documentar requisitos de infraestructura AWS en `docs/sdlc/SPEC_AWS_PRODUCTION.md`
- [x] @GEMINI: Mapear variables de `.env.example` a mecanismos de inyección en ECS
- [x] @GEMINI: Documentar configuración de FortiGate, Wazuh y Zabbix en `SOURCE_CONFIG_GUIDE.md`
- [x] @GEMINI: Investigar estado de GuardDuty en cuenta AWS
- [x] @GEMINI: Validar manejo de "empty response" en `ioc_normalizer.js`
- [x] @GEMINI: Crear workflow `error-handler.json` y `SPEC_ERROR_HANDLING.md`
- [x] @GEMINI: Documentar configuración de Trellix ePO via IMAP
- [x] @GEMINI: Revisar rate limits de fuentes OSINT
- [x] @GEMINI: Crear runbook de operación en `docs/knowledge/RUNBOOK_THREAT_INTEL.md`
- [x] @GEMINI: Preparar template de Task Definition ECS en `docs/architecture/ECS_TASK_DEFINITION_TEMPLATE.json`
- [x] @GEMINI: Investigar alternativa al `n8n execute` CLI para dry-run en staging
- [x] @GEMINI: Actualizar AI_GOVERNANCE.md con controles de producción AWS
- [x] @GEMINI: Investigar endpoints adicionales de FortiGate relevantes para TI (IPS, virus, webfilter, app-ctrl) y documentar en SOURCE_CONFIG_GUIDE.md (Completado: Endpoints UTM documentados)
- [x] @GEMINI: Revisar ioc_normalizer.js para soportar estructura de respuesta /api/v2/log/memory/* (campo results[] vs logs[]) (Completado: Soporte para arrays y extracción UTM robustecida)
- [ ] @GEMINI: Investigar normalización de logs Wazuh y Zabbix — validar que `normalizeWazuh()` y `normalizeZabbix()` soportan estructura real de API (Fase 1.7)
- [ ] @GEMINI: Documentar pruebas de dry-run esperadas por fuente en RUNBOOK_THREAT_INTEL.md (Fase 1.7)
- [x] @GEMINI: Revisar Security Groups y networking de producción (Completado ENTRADA-014: Redis SG, NAT Gateway, VPC Endpoints)
- [ ] @GEMINI: Validar que secretos en AWS no tienen valores por defecto (Fase 2)
- [x] @GEMINI: Adaptar `docs/governance/AI_GOVERNANCE.md` al proyecto n8n DELCOP (Finalizado: Integrados controles AWS y Framework v4.4)

### @CLAUDE - Governor

- [x] @CLAUDE: Cross-review del deploy de staging (Codex)
- [x] @CLAUDE: Aprobar SPEC_AWS_PRODUCTION.md (Gemini)
- [x] @CLAUDE: Crear ADR-009 formalizando estrategia AWS
- [x] @CLAUDE: Cross-review de credenciales/fuentes (Gemini)
- [x] @CLAUDE: Verificar que API keys no quedaron trackeadas en Git
- [x] @CLAUDE: Cross-review de remediación staging (Codex)
- [x] @CLAUDE: Cross-review hallazgo FortiGate endpoint (validado y corregido en workflow)
- [x] @CLAUDE: Cross-review Codex ENTRADA-019/020 + Gemini ENTRADA-013/014 (Fase 1.6 aprobada)
- [ ] @CLAUDE: Cross-review de dry-runs por fuente cuando Codex los ejecute (Fase 1.7)
- [ ] @CLAUDE: Aprobar activación automática (triggers cron) tras validación total
- [ ] @CLAUDE: Registrar ADR-010 (Fuentes activas vs pendientes)
- [ ] @CLAUDE: Cross-review final de infraestructura AWS (Fase 2)
- [ ] @CLAUDE: Auditar ECS Task Definition para uso de Secrets Manager (Fase 2)
- [ ] @CLAUDE: Actualizar CONTEXT_SECURITY.md con estado real de producción (Fase 2)

---

## Entornos

| Entorno    | Estado    | URL / Host            | Notas |
|------------|-----------|-----------------------|-------|
| Local      | Validado  | http://localhost:5678 | Docker Desktop, SQLite, threat-db en host `5433` |
| Staging    | Healthy   | http://192.168.0.70:5678 | Dell R720, Docker, 3 servicios healthy |
| Produccion | No existe | AWS ECS Fargate (plan) | Infraestructura por crear (Fase 2) |

---

## Decisiones recientes (ADRs)

| ID | Fecha | Decision | Por |
|----|-------|----------|-----|
| ADR-001 | 2026-03-16 | Usar imagen oficial n8n sin modificaciones | Claude |
| ADR-002 | 2026-03-16 | Pipeline 3-entornos: local→staging→prod | Claude |
| ADR-005 | 2026-03-17 | SPEC_STAGING_PIPELINE aprobada | Claude |
| ADR-008 | 2026-03-18 | Code-nodes embebidos en JSON para n8n | Claude |
| ADR-009 | 2026-03-20 | Estrategia AWS (ECS Fargate + RDS + Secrets Manager) | Claude |

---

## Notas de sesion

- 3 agentes activos: Claude (Governor), Codex (Implementer), Gemini (Researcher).
- Framework v4.4 activo: git pull obligatorio, Context7, skills.sh habilitados.
- Backlog unificado por agente (sin subsecciones temáticas).
