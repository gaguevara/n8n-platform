# CONTEXT.md - Estado Actual del Proyecto

> **Ultima actualizacion:** 2026-03-23
> **Actualizado por:** Claude (Governor — cross-review ronda staging + hallazgo Wazuh API)
> **Proxima revision:** próxima sesión — corregir Wazuh endpoint + dry-runs UI

---

## Estado general

| Campo         | Valor |
|---------------|-------|
| Fase          | Fase 1.7 — Wazuh endpoint fix + dry-runs UI pendientes |
| Estabilidad   | Staging healthy (3 servicios). Vars Wazuh/Zabbix cargadas. Zabbix migrado a Bearer. FortiGate/Zabbix dry-run HTTP OK. |
| Bloqueantes   | Wazuh `/alerts` no existe en v4 — requiere migrar a Indexer API o Manager API alternativo |
| Ultimo cambio | Codex ENTRADA-024: staging completo, hallazgo Wazuh endpoint |

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
- [x] @CODEX: Validar conectividad y configurar API key FortiGate en `.env` staging
- [x] @CODEX: Reimportar `threat-intel-main.json` corregido en n8n staging (endpoint FortiGate fix)

**>>> RONDA ACTUAL — ejecutar en orden <<<**
- [x] @CODEX: SSH al R720 y agregar vars Wazuh al `.env` (completado 2026-03-23)
- [x] @CODEX: SSH al R720 y agregar vars Zabbix al `.env` (completado 2026-03-23)
- [x] @CODEX: Reiniciar compose en R720 (`docker compose down && docker compose up -d`) y verificar healthchecks (completado 2026-03-23; Redis recuperado y 3 servicios healthy)
- [x] @CODEX: Reimportar workflow `threat-intel-main.json` actualizado (normalizers Wazuh/Zabbix/GuardDuty con soporte arrays) (completado 2026-03-23 via import seguro preservando IDs y credenciales de staging)
- [ ] @CODEX: Dry-run nodo FortiGate en staging UI — capturar respuesta JSON (equivalente HTTP ejecutado 2026-03-23 con `HTTP 200`; pendiente evidencia UI)
- [ ] @CODEX: Dry-run nodo Wazuh en staging UI — capturar respuesta JSON (bloqueado: auth OK `HTTP 200`, endpoint actual `/alerts` devuelve `HTTP 404`)
- [ ] @CODEX: Dry-run nodo Zabbix en staging UI — capturar respuesta JSON (equivalente HTTP ejecutado 2026-03-23 con `HTTP 200`; pendiente evidencia UI)
- [x] @CODEX: Migrar auth Zabbix de body `auth` a header `Authorization: Bearer` (best practice Zabbix 7.0+) (completado 2026-03-23 en workflow reimportado de staging)
- [x] @CODEX: Corregir endpoint de ingesta Wazuh para la version real del API en staging (hallazgo 2026-03-23: `/alerts` devuelve `404` tras auth exitosa)

**>>> ÚLTIMA RONDA (cierre de sesión) <<<**
- [ ] @CODEX: Corregir nodos Wazuh en workflow JSON: reemplazar `GET /alerts` por endpoint correcto según investigación de Gemini
- [ ] @CODEX: Reimportar workflow corregido en staging y ejecutar dry-run Wazuh

**Pendientes (próxima sesión):**
- [ ] @CODEX: Ejecutar test manual del nodo `pg-upsert` en n8n UI (staging)
- [ ] @CODEX: Agregar nodos adicionales al workflow para IPS (`utm/ips`) y Antivirus (`utm/virus`) (Fase 1.7)
- [ ] @CODEX: Registrar AbuseIPDB y configurar API key en `.env` staging
- [ ] @CODEX: Registrar OTX AlienVault y configurar API key en `.env` staging
- [ ] @CODEX: Crear webhook Slack/Teams de prueba y configurar en `.env` staging
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
- [x] @GEMINI: Investigar normalización de logs Wazuh y Zabbix — validar que `normalizeWazuh()` y `normalizeZabbix()` soportan estructura real de API (Completado ENTRADA-015: Soporte para arrays y metadatos robustecido)
- [x] @GEMINI: Documentar pruebas de dry-run esperadas por fuente en RUNBOOK_THREAT_INTEL.md (Completado ENTRADA-015: Sección 6 añadida)
- [x] @GEMINI: Documentar evidencia para ISO 27001 A.5.7 (Inteligencia de amenazas) con resultados de dry-runs (Completado ENTRADA-015: En Runbook)
- [x] @GEMINI: Revisar Security Groups y networking de producción (Completado ENTRADA-014: Redis SG, NAT Gateway, VPC Endpoints)
- [ ] @GEMINI: Investigar endpoint correcto de Wazuh v4.14 para obtener alertas de seguridad — Context7 confirma que `/alerts` no existe; opciones: Indexer API (`/wazuh-alerts*/_search`) o Manager API alternativo. Documentar en SOURCE_CONFIG_GUIDE.md con ejemplo de request/response
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
- [x] @CLAUDE: Validar TAREAS_INTEGRACION_MCP.md contra código actual (hallazgo: Zabbix auth legacy)
- [x] @CLAUDE: Cross-review Codex ENTRADA-021/022 + Gemini ENTRADA-015 (normalizers + review doc)
- [x] @CLAUDE: Completar review Governor en FRAMEWORK_RECOMMENDATIONS_REVIEW (10 adoptar ahora, 2 luego)
- [x] @CLAUDE: Cross-review Codex ENTRADA-023 + Gemini ENTRADA-016 (cierre review + auditoría)
- [x] @CLAUDE: Crear ADR-011 (framework v4.5 mejoras post-review — 12 recomendaciones priorizadas)
- [x] @CLAUDE: Registrar ADR-010 (Fuentes activas vs pendientes en staging)
- [x] @CLAUDE: Cross-review Codex ENTRADA-024/025 (staging vars + dry-runs + hallazgo Wazuh)
- [ ] @CLAUDE: Cross-review corrección Wazuh endpoint cuando Gemini/Codex la completen
- [ ] @CLAUDE: Cross-review de dry-runs por fuente cuando Codex los ejecute (Fase 1.7)
- [ ] @CLAUDE: Aprobar activación automática (triggers cron) tras validación total
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
| ADR-010 | 2026-03-23 | Fuentes activas vs pendientes en staging | Claude |
| ADR-011 | 2026-03-23 | Framework v4.5: mejoras post-review multi-agente | Claude + Codex + Gemini |

---

## Notas de sesion

- 3 agentes activos: Claude (Governor), Codex (Implementer), Gemini (Researcher).
- Framework v4.4 activo: git pull obligatorio, Context7, skills.sh habilitados.
- Backlog unificado por agente (sin subsecciones temáticas).
