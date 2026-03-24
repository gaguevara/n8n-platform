# CONTEXT.md - Estado Actual del Proyecto

> **Ultima actualizacion:** 2026-03-23
> **Actualizado por:** Codex (Implementer — Ronda 1 parcial ejecutada)
> **Proxima revision:** cuando exista una ruta usable desde R720 hacia Wazuh Indexer o se defina un proxy/tunel

---

## Estado general

| Campo         | Valor |
|---------------|-------|
| Fase          | Fase 1.8 — Framework v4.6 aplicado. Rondas 1-3 Gemini completadas. Codex: Ronda 2-3 pendientes. |
| Estabilidad   | Staging healthy. Workflow desactivado. UTM nodes agregados. Framework v4.6: 29 tests, Pattern 09, proto_watch. |
| Bloqueantes   | Wazuh Indexer: `127.0.0.1:9200` en servidor Wazuh — no accesible desde R720. Requiere exposición/túnel por usuario. |
| Ultimo cambio | Framework v4.6 aplicado + cross-review Codex 027-028 + Gemini 018 aprobados. No hay secretos en Git. |

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
- [ ] @CODEX: Dry-run nodo Wazuh en staging UI — capturar respuesta JSON (bloqueado: el workflow ya apunta al Indexer API, pero falta validar la URL/credencial efectiva accesible desde el R720)
- [ ] @CODEX: Dry-run nodo Zabbix en staging UI — capturar respuesta JSON (equivalente HTTP ejecutado 2026-03-23 con `HTTP 200`; pendiente evidencia UI)
- [x] @CODEX: Migrar auth Zabbix de body `auth` a header `Authorization: Bearer` (best practice Zabbix 7.0+) (completado 2026-03-23 en workflow reimportado de staging)
- [x] @CODEX: Corregir endpoint de ingesta Wazuh para la version real del API en staging (hallazgo 2026-03-23: `/alerts` devuelve `404` tras auth exitosa)

**>>> ÚLTIMA RONDA (cierre de sesión) <<<**
- [x] @CODEX: **URGENTE** — Desactivar workflow en n8n staging UI (completado 2026-03-23 via `n8n unpublish:workflow`; export verificado con `active:false`)
- [x] @CODEX: Corregir nodos Wazuh en workflow JSON según investigación de Gemini (completado 2026-03-23: migrado a Indexer API `wazuh-alerts-*/_search`)
- [x] @CODEX: Reimportar workflow corregido en staging (desactivado) para dry-runs manuales (completado 2026-03-23 via import seguro preservando IDs/credenciales)
- [x] @GEMINI: Investigar endpoint correcto Wazuh v4.14 para alertas — Context7 confirma que `/alerts` no existe; documentado en SOURCE_CONFIG_GUIDE.md (Completado ENTRADA-017: Indexer API puerto 9200 identificado)
- [x] @CLAUDE: Cross-review corrección Wazuh — Codex 026 + Gemini 017 aprobados (Indexer API, workflow desactivado, .env actualizado)

---

## RONDA 1 — Hardening y limpieza (autónoma, sin intervención de usuario)

> **Objetivo:** Limpiar repo, agregar nodos UTM al workflow, validar Wazuh Indexer desde R720, actualizar ECS template

### @CODEX - Implementer/DevOps (Ronda 1)

- [x] @CODEX: Limpiar directorio `.agent/` del repo — es duplicado de `.agents/` (hallazgo Gemini ENTRADA-016). Confirmar que `.agents/skills/` tiene los skills activos y eliminar `.agent/` (completado 2026-03-23)
- [x] @CODEX: Agregar 2 nodos HTTP adicionales al workflow JSON (`app/workflows/threat-intel-main.json`) para IPS (`/api/v2/log/memory/utm/ips`) y Antivirus (`/api/v2/log/memory/utm/virus`). Copiar estructura del nodo FortiGate existente, misma auth, agregar `vdom=root`. Conectar al mismo merge node (completado 2026-03-23)
- [ ] @CODEX: SSH al R720: probar conectividad al Wazuh Indexer — ejecutar `curl -k -u admin:admin https://192.168.206.10:9200/ 2>&1` (probar puerto 9200 con credenciales default, si falla probar con las credenciales de Wazuh Manager). Documentar IP:puerto real y credencial funcional (evidencia nueva 2026-03-23: Manager API expone `indexer.hosts=["https://127.0.0.1:9200"]`; desde R720 `192.168.206.10:9200` devuelve `000` y `wazuh.delcop.local` no resuelve)
- [ ] @CODEX: Agregar `WAZUH_INDEXER_URL` y `WAZUH_INDEXER_BASIC_AUTH` al `.env` del R720 con los valores descubiertos en el paso anterior (bloqueado hasta tener endpoint/credencial usable desde el R720)
- [x] @CODEX: Validar JSON del workflow con `node -e "JSON.parse(require('fs').readFileSync('app/workflows/threat-intel-main.json','utf8')); console.log('OK')"` después de agregar nodos UTM (completado 2026-03-23)
- [x] @CODEX: Ejecutar `git pull` en R720, reimportar workflow actualizado (con nodos UTM) desactivado en staging (completado 2026-03-23; R720 actualizado a `2306ade` e import seguro aplicado)

### @GEMINI - Researcher/Reviewer (Ronda 1)

- [x] @GEMINI: Actualizar `ECS_TASK_DEFINITION_TEMPLATE.json` — agregar `WAZUH_INDEXER_URL` (environment) y `WAZUH_INDEXER_BASIC_AUTH` (secrets/SSM) que faltan tras la migración a Indexer API
- [x] @GEMINI: Revisar `ioc_normalizer.js` función `normalizeWazuh()` — verificar que parsea correctamente la estructura de respuesta del Indexer API (`hits.hits[]._source` vs `data.affected_items[]`). Si hay diferencia, proponer fix
- [x] @GEMINI: Crear checklist de activación pre-cron en `docs/knowledge/ACTIVATION_CHECKLIST.md` — lista de verificaciones que deben pasar antes de activar cada trigger: conectividad, credencial, dry-run OK, pg-upsert OK, canal de alerta configurado

### @CLAUDE - Governor (Ronda 1)

- [x] @CLAUDE: Cross-review de Codex Ronda 1 (limpieza .agent/, nodos UTM, conectividad Wazuh Indexer) — Aprobado: `.agent/` limpiado, UTM nodes correctos, Wazuh Indexer bloqueado por red (127.0.0.1:9200)
- [x] @CLAUDE: Cross-review de Gemini Ronda 1 (ECS template, normalizer Indexer, checklist activación) — Aprobado: `hits.hits[]._source` implementado, ACTIVATION_CHECKLIST completo
- [x] @CLAUDE: Verificar que no hay secretos en archivos trackeados — Verificado: solo interpolaciones `${VAR}` y defaults dev

---

## RONDA 2 — Validación E2E por fuente (autónoma)

> **Objetivo:** Dry-run de cada fuente configurada, test de persistencia PostgreSQL, configurar canal de alerta
> **Prerequisito:** Ronda 1 completada

### @CODEX - Implementer/DevOps (Ronda 2)

- [ ] @CODEX: SSH al R720 y ejecutar dry-run HTTP equivalente de FortiGate desde el servidor: `curl -k -H "Authorization: Bearer $FORTIGATE_API_KEY" "https://$FORTIGATE_HOST/api/v2/log/memory/event/system?vdom=root&rows=5"` — capturar respuesta JSON completa en log
- [ ] @CODEX: SSH al R720 y ejecutar dry-run HTTP equivalente de Wazuh Indexer: `curl -k -u "$WAZUH_USER:$WAZUH_PASS" "https://$WAZUH_INDEXER:9200/wazuh-alerts-*/_search" -H "Content-Type: application/json" -d '{"size":5,"query":{"range":{"rule.level":{"gte":7}}}}'` — capturar respuesta
- [ ] @CODEX: SSH al R720 y ejecutar dry-run HTTP equivalente de Zabbix: `curl -s "$ZABBIX_API_URL" -H "Authorization: Bearer $ZABBIX_API_TOKEN" -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"trigger.get","params":{"output":"extend","limit":5,"min_severity":3},"id":1}'` — capturar respuesta
- [ ] @CODEX: Ejecutar test de persistencia PostgreSQL desde R720: `docker exec n8n_threat_db psql -U delcop_threat -d threat_intel -c "INSERT INTO iocs (ioc_value, ioc_type, severity, confidence, source, tags, metadata) VALUES ('1.2.3.4', 'ip_v4', 'medium', 50, 'dry-run-test', ARRAY['test'], '{}') ON CONFLICT DO NOTHING; SELECT count(*) FROM iocs WHERE source='dry-run-test';"` — confirmar que pg-upsert funciona
- [ ] @CODEX: Limpiar dato de test: `docker exec n8n_threat_db psql -U delcop_threat -d threat_intel -c "DELETE FROM iocs WHERE source='dry-run-test';"`

### @GEMINI - Researcher/Reviewer (Ronda 2)

- [x] @GEMINI: Analizar las respuestas JSON capturadas por Codex (FortiGate, Wazuh, Zabbix) y validar que los campos esperados por `ioc_normalizer.js` están presentes. Documentar mapeo real vs esperado en una tabla
- [x] @GEMINI: Revisar `ioc_scorer.js` — verificar que los `source_trust` weights de las fuentes activas (fortigate=0.85, wazuh=0.90, zabbix=0.60) son coherentes con la calidad de datos observada en los dry-runs
- [x] @GEMINI: Revisar `alert_dispatcher.js` — verificar que los canales de alerta (Slack, Teams, Email) fallan gracefully si el webhook no está configurado (no debe crashear el pipeline)

### @CLAUDE - Governor (Ronda 2)

- [ ] @CLAUDE: Cross-review dry-runs de Codex — validar que cada fuente responde datos reales y no errores
- [ ] @CLAUDE: Cross-review análisis de Gemini — verificar coherencia entre respuestas reales y normalizers
- [ ] @CLAUDE: Actualizar `CONTEXT_SECURITY.md` con el estado real de cada fuente (activa/bloqueada/pendiente)

---

## RONDA 3 — Consolidación y preparación para activación (autónoma)

> **Objetivo:** Consolidar todo el trabajo, preparar el workflow para activación, documentar estado final
> **Prerequisito:** Ronda 2 completada

### @CODEX - Implementer/DevOps (Ronda 3)

- [ ] @CODEX: Reimportar workflow final en staging (con nodos UTM + Wazuh Indexer) — desactivado
- [ ] @CODEX: Ejecutar `docker compose -f infra/docker-compose.staging.yml ps -a` y `curl http://192.168.0.70:5678/healthz` — confirmar staging sigue healthy
- [ ] @CODEX: Ejecutar `python .multiagent/core/engine.py --config .multiagent/adapters/n8n-platform.json --base . status` para confirmar estado de los 3 agentes
- [ ] @CODEX: Limpiar archivos temporales en R720 (`/tmp/threat-intel-main.*.json`, `.tmp/codex-staging/`)

### @GEMINI - Researcher/Reviewer (Ronda 3)

- [x] @GEMINI: Auditoría final de coherencia: verificar que `DATA-CONTRACTS.md`, `ioc_normalizer.js`, `01-schema.sql` y el workflow JSON están alineados — campos, tipos, tablas
- [x] @GEMINI: Actualizar `RUNBOOK_THREAT_INTEL.md` sección 6 con los resultados reales de los dry-runs de Ronda 2
- [x] @GEMINI: Generar resumen ejecutivo de Fase 1 en `docs/PHASE1_SUMMARY.md`: qué se logró, qué queda pendiente, métricas (fuentes activas, nodos, entradas de log, ADRs)

### @CLAUDE - Governor (Ronda 3)

- [ ] @CLAUDE: Cross-review final de Ronda 3 — Codex (staging health + cleanup) y Gemini (auditoría + resumen)
- [ ] @CLAUDE: Registrar ADR-012 consolidando las fuentes validadas y su estado de activación
- [ ] @CLAUDE: Actualizar `CONTEXT_SECURITY.md` con inventario final de credenciales/fuentes por entorno
- [ ] @CLAUDE: Commit final de consolidación con todo el trabajo de las 3 rondas

---

## RONDA 4 — Framework v4.6 + staging final (autónoma)

> **Objetivo:** Validar framework v4.6 en staging, ejecutar dry-runs pendientes, preparar activación
> **Prerequisito:** Rondas 1-3 completadas (Gemini done, Codex parcial por Wazuh bloqueante)

### @CODEX - Implementer/DevOps (Ronda 4)

- [ ] @CODEX: `git pull` en R720 hasta commit `77a8a4d` (framework v4.6 + normalizer fixes)
- [ ] @CODEX: Reimportar workflow actualizado en staging (desactivado) — incluye normalizer con soporte `hits.hits[]._source` y `alert_dispatcher` con `$env` fix
- [ ] @CODEX: Ejecutar dry-run FortiGate desde R720: `curl -k -H "Authorization: Bearer $FORTIGATE_API_KEY" "https://$FORTIGATE_HOST/api/v2/log/memory/event/system?vdom=root&rows=5"` — capturar JSON en log
- [ ] @CODEX: Ejecutar dry-run Zabbix desde R720: `curl -s "$ZABBIX_API_URL" -H "Authorization: Bearer $ZABBIX_API_TOKEN" -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"trigger.get","params":{"output":"extend","limit":5,"min_severity":3},"id":1}'` — capturar JSON
- [ ] @CODEX: Test PostgreSQL upsert desde R720: `docker exec n8n_threat_db psql -U delcop_threat -d threat_intel -c "SELECT upsert_ioc('1.2.3.4', 'ip_v4', 'medium', 50, 'dry-run-test', ARRAY['test'], '{}');"` — si la función no existe, usar INSERT directo. Luego DELETE del dato de test.
- [ ] @CODEX: Verificar staging health: `docker compose ps -a` + `curl healthz` + engine status
- [ ] @CODEX: Limpiar temporales en R720: `/tmp/threat-intel-main.*.json`, `.tmp/codex-staging/`

### @GEMINI - Researcher/Reviewer (Ronda 4)

- [ ] @GEMINI: Validar que `AGENT_SKILLS_MATRIX.md` (nuevo en v4.6) es coherente con los roles de `AGENT_ROLES.md` — identificar skills faltantes o redundantes para el contexto n8n
- [ ] @GEMINI: Revisar `docs/templates/FRAMEWORK_CAPABILITIES.md` y adaptarlo al proyecto n8n-platform — actualizar con capacidades reales (Context7 validado, skills.sh instalados, engine 29 tests)
- [ ] @GEMINI: Investigar cómo exponer el Wazuh Indexer (puerto 9200) desde el servidor Wazuh al R720 — opciones: SSH tunnel, nginx proxy, binding a 0.0.0.0 en opensearch.yml. Documentar la opción más segura en SOURCE_CONFIG_GUIDE.md

### @CLAUDE - Governor (Ronda 4)

- [ ] @CLAUDE: Cross-review dry-runs Codex Ronda 4 (FortiGate, Zabbix, PostgreSQL)
- [ ] @CLAUDE: Cross-review adaptación Gemini Ronda 4 (skills matrix, capabilities, Wazuh Indexer exposure)
- [ ] @CLAUDE: Registrar ADR-012: fuentes validadas y su estado de activación post dry-runs
- [ ] @CLAUDE: Commit + push de consolidación Ronda 4

---

## Pendientes post-rondas (requieren intervención de usuario)

- [ ] @USUARIO: Registrar cuenta en AbuseIPDB y proporcionar API key
- [ ] @USUARIO: Registrar cuenta en OTX AlienVault y proporcionar API key
- [ ] @USUARIO: Crear webhook Slack/Teams en canal `#security-alerts-test`
- [ ] @USUARIO: Decidir activación de triggers cron tras revisión de resultados de Ronda 3
- [ ] @USUARIO: Aprobar inicio de Fase 2 (infraestructura AWS)

## Pendientes Fase 2 (post-activación staging)

- [ ] @CODEX: Crear repositorio ECR en AWS
- [ ] @CODEX: Crear secretos en AWS Secrets Manager
- [ ] @CODEX: Crear cluster ECS y task definition
- [ ] @CODEX: Crear instancia RDS PostgreSQL para producción
- [ ] @CODEX: Build + push de imagen a ECR y deploy inicial
- [x] @GEMINI: Validar que secretos en AWS no tienen valores por defecto
- [ ] @CLAUDE: Cross-review final de infraestructura AWS
- [ ] @CLAUDE: Auditar ECS Task Definition para uso de Secrets Manager

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
