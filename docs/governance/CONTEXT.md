# CONTEXT.md - Estado Actual del Proyecto

> **Ultima actualizacion:** 2026-03-25
> **Actualizado por:** Claude (Governor — credenciales vinculadas + framework v4.7 + tareas Ronda 6)
> **Proxima revision:** al completar dry-runs E2E en n8n UI

---

## Estado general

| Campo         | Valor |
|---------------|-------|
| Fase          | Fase 2.0 — **BLOQUEANTE:** code nodes en staging son placeholders, no código real. Drift 100%. |
| Estabilidad   | Staging healthy. Credenciales PostgreSQL/SMTP vinculadas. Pero code nodes (normalizer, scorer, dispatcher, persist) tienen solo comentarios placeholder. |
| Bloqueantes   | Codex debe generar workflow JSON con code nodes inyectados desde `app/code-nodes/*.js` y reimportar. Sin esto, el pipeline no procesa datos. |
| Ultimo cambio | Gemini ENTRADA-024 detectó drift 100% en code nodes. Codex ENTRADA-038 confirmó. Ronda 8 creada para fix definitivo. |

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
- [ ] @CODEX: Dry-run nodo FortiGate en staging UI — capturar respuesta JSON (equivalente HTTP ejecutado 2026-03-23 con `HTTP 200`; revalidado desde R720 el 2026-03-24 con `HTTP 200` y payload `results[]` usando extracción limpia de `.env`; queda pendiente solo evidencia UI)
- [ ] @CODEX: Dry-run nodo Wazuh en staging UI — capturar respuesta JSON (equivalente HTTP validado 2026-03-25 contra `https://192.168.206.10:9201`; pendiente solo evidencia UI del nodo)
- [ ] @CODEX: Dry-run nodo Zabbix en staging UI — capturar respuesta JSON (equivalente HTTP ejecutado 2026-03-24 con JSON-RPC `result[]`; pendiente evidencia UI)
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
- [x] @CODEX: SSH al R720: probar conectividad al Wazuh Indexer (Resuelto por Claude 2026-03-25: nginx proxy instalado en servidor Wazuh, puerto 9201 con whitelist R720. Dry-run desde R720: 5,962 alertas nivel >= 7)
- [x] @CODEX: Agregar `WAZUH_INDEXER_URL` y `WAZUH_INDEXER_BASIC_AUTH` al `.env` del R720 (Completado por Claude 2026-03-25: `WAZUH_INDEXER_URL=https://192.168.206.10:9201`, Basic Auth configurado)
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

- [x] @CODEX: SSH al R720 y ejecutar dry-run HTTP equivalente de FortiGate desde el servidor: `curl -k -H "Authorization: Bearer $FORTIGATE_API_KEY" "https://$FORTIGATE_HOST/api/v2/log/memory/event/system?vdom=root&rows=5"` — capturar respuesta JSON completa en log (completado 2026-03-24; `HTTP 200`, `REMOTE_IP=192.168.0.14`, payload real con `results[]`)
- [x] @CODEX: SSH al R720 y ejecutar dry-run HTTP equivalente de Wazuh Indexer: `curl -sk -H "Authorization: $WAZUH_INDEXER_BASIC_AUTH" "$WAZUH_INDEXER_URL/wazuh-alerts-*/_search" -H "Content-Type: application/json" -d '{"size":3,"sort":[{"timestamp":{"order":"desc"}}],"query":{"bool":{"must":[{"range":{"rule.level":{"gte":7}}},{"range":{"timestamp":{"gte":"now-1h"}}}]}}}'` — capturar respuesta (completado 2026-03-25; `HTTP 200`, 122 hits en la ultima hora, evidencia de `srcip=190.94.224.126`)
- [x] @CODEX: SSH al R720 y ejecutar dry-run HTTP equivalente de Zabbix: `curl -s "$ZABBIX_API_URL" -H "Authorization: Bearer $ZABBIX_API_TOKEN" -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"trigger.get","params":{"output":"extend","limit":5,"min_severity":3},"id":1}'` — capturar respuesta (completado 2026-03-24; devolvió JSON-RPC con `result[]`)
- [x] @CODEX: Ejecutar test de persistencia PostgreSQL desde R720: `docker exec n8n_threat_db psql -U delcop_threat -d threat_intel -c "INSERT INTO iocs (ioc_value, ioc_type, severity, confidence, source, tags, metadata) VALUES ('1.2.3.4', 'ip_v4', 'medium', 50, 'dry-run-test', ARRAY['test'], '{}') ON CONFLICT DO NOTHING; SELECT count(*) FROM iocs WHERE source='dry-run-test';"` — confirmar que pg-upsert funciona (completado 2026-03-24 via `SELECT upsert_ioc(...)`; inserción confirmada)
- [x] @CODEX: Limpiar dato de test: `docker exec n8n_threat_db psql -U delcop_threat -d threat_intel -c "DELETE FROM iocs WHERE source='dry-run-test';"` (completado 2026-03-24)

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

- [x] @CODEX: Reimportar workflow final en staging (con nodos UTM + Wazuh Indexer) — desactivado (completado 2026-03-24 via variante segura preservando IDs/credenciales y `errorWorkflow` real)
- [x] @CODEX: Ejecutar `docker compose -f infra/docker-compose.staging.yml ps -a` y `curl http://192.168.0.70:5678/healthz` — confirmar staging sigue healthy (completado 2026-03-24; 3 servicios `healthy`, health previa `{\"status\":\"ok\"}`)
- [x] @CODEX: Ejecutar `python .multiagent/core/engine.py --config .multiagent/adapters/n8n-platform.json --base . status` para confirmar estado de los 3 agentes (completado 2026-03-24)
- [x] @CODEX: Limpiar archivos temporales en R720 (`/tmp/threat-intel-main.*.json`, `.tmp/codex-staging/`) (completado 2026-03-24)

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

- [x] @CODEX: `git pull` en R720 hasta commit `77a8a4d` (framework v4.6 + normalizer fixes) (completado 2026-03-24; R720 actualizado a `4cfb764`)
- [x] @CODEX: Reimportar workflow actualizado en staging (desactivado) — incluye normalizer con soporte `hits.hits[]._source` y `alert_dispatcher` con `$env` fix (completado 2026-03-24; verificación fresca del export reimportado)
- [x] @CODEX: Ejecutar dry-run FortiGate desde R720: `curl -k -H "Authorization: Bearer $FORTIGATE_API_KEY" "https://$FORTIGATE_HOST/api/v2/log/memory/event/system?vdom=root&rows=5"` — capturar JSON en log (completado 2026-03-24; `FORTIGATE_HOST=https://192.168.0.14`, `HTTP 200`, respuesta real con `results[]`)
- [x] @CODEX: Ejecutar dry-run Zabbix desde R720: `curl -s "$ZABBIX_API_URL" -H "Authorization: Bearer $ZABBIX_API_TOKEN" -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"trigger.get","params":{"output":"extend","limit":5,"min_severity":3},"id":1}'` — capturar JSON (completado 2026-03-24)
- [x] @CODEX: Test PostgreSQL upsert desde R720: `docker exec n8n_threat_db psql -U delcop_threat -d threat_intel -c "SELECT upsert_ioc('1.2.3.4', 'ip_v4', 'medium', 50, 'dry-run-test', ARRAY['test'], '{}');"` — si la función no existe, usar INSERT directo. Luego DELETE del dato de test. (completado 2026-03-24; función real detectada con firma `upsert_ioc(p_value text, p_type ioc_type, p_tags text[], p_metadata jsonb)`)
- [x] @CODEX: Verificar staging health: `docker compose ps -a` + `curl healthz` + engine status (completado 2026-03-24; compose healthy y engine status OK)
- [x] @CODEX: Limpiar temporales en R720: `/tmp/threat-intel-main.*.json`, `.tmp/codex-staging/` (completado 2026-03-24)

### @GEMINI - Researcher/Reviewer (Ronda 4)

- [x] @GEMINI: Validar que `AGENT_SKILLS_MATRIX.md` (nuevo en v4.6) es coherente con los roles de `AGENT_ROLES.md` — identificar skills faltantes o redundantes para el contexto n8n
- [x] @GEMINI: Revisar `docs/templates/FRAMEWORK_CAPABILITIES.md` y adaptarlo al proyecto n8n-platform — actualizar con capacidades reales (Context7 validado, skills.sh instalados, engine 29 tests)
- [x] @GEMINI: Investigar cómo exponer el Wazuh Indexer (puerto 9200) desde el servidor Wazuh al R720 — opciones: SSH tunnel, nginx proxy, binding a 0.0.0.0 en opensearch.yml. Documentar la opción más segura en SOURCE_CONFIG_GUIDE.md

### @CLAUDE - Governor (Ronda 4)

- [x] @CLAUDE: Cross-review dry-runs Codex Ronda 4 (FortiGate HTTP 200, Zabbix JSON-RPC OK, PostgreSQL upsert_ioc OK)
- [x] @CLAUDE: Cross-review adaptación Gemini Ronda 4 (skills matrix alineado, capabilities creado, Wazuh exposure documentado)
- [x] @CLAUDE: Desbloqueo Wazuh Indexer: nginx proxy instalado en servidor Wazuh (puerto 9201, whitelist R720), dry-run 5,962 alertas, .env staging actualizado
- [ ] @CLAUDE: Registrar ADR-012: fuentes validadas y su estado de activación post dry-runs
- [ ] @CLAUDE: Commit + push de consolidación Ronda 4+5

---

## RONDA 5 — Activación de fuentes internas (autónoma)

> **Objetivo:** Reimportar workflow con Wazuh desbloqueado, dry-run E2E de las 3 fuentes internas, preparar activación de triggers cron
> **Prerequisito:** Wazuh Indexer accesible desde R720 ✅ (nginx proxy en 9201)

### @CODEX - Implementer/DevOps (Ronda 5)

- [x] @CODEX: `git pull` en R720 y reimportar workflows con credenciales reales (Completado por Claude 2026-03-25: Postgres `a0K3DCm6QM9FVDAx` + SMTP `cFZPbwEu9RSx0KY9` vinculados, nodo deprecated eliminado, ambos workflows reimportados)
- [x] @CODEX: Dry-run Wazuh Indexer desde R720: `curl -sk -H "Authorization: $WAZUH_INDEXER_BASIC_AUTH" "$WAZUH_INDEXER_URL/wazuh-alerts-*/_search" -H "Content-Type: application/json" -d '{"size":3,"sort":[{"timestamp":{"order":"desc"}}],"query":{"bool":{"must":[{"range":{"rule.level":{"gte":7}}},{"range":{"timestamp":{"gte":"now-1h"}}}]}}}'` — capturar JSON con IPs atacantes reales (completado 2026-03-25; `HTTP 200`, muestra con `srcip=190.94.224.126`, `agent.ip=192.168.206.12`)
- [ ] @CODEX: Ejecutar nodo Wazuh manualmente en n8n UI (staging) — trigger manual → verificar que el normalizer parsea `hits.hits[]._source` correctamente y extrae IoCs
- [ ] @CODEX: Ejecutar nodo FortiGate manualmente en n8n UI — verificar datos reales fluyen hasta el merge node
- [ ] @CODEX: Ejecutar nodo Zabbix manualmente en n8n UI — verificar datos reales fluyen hasta el merge node
- [ ] @CODEX: Ejecutar pipeline completo manualmente (trigger manual del workflow completo) — verificar que los datos fluyen desde ingesta → normalizer → scorer → persistence (PostgreSQL) → no alerting (sin webhooks configurados)
- [ ] @CODEX: Consultar PostgreSQL tras pipeline manual: `SELECT ioc_value, ioc_type, severity, source, sighting_count FROM iocs ORDER BY last_seen DESC LIMIT 10;` — confirmar que hay IoCs reales persistidos

### @GEMINI - Researcher/Reviewer (Ronda 5)

- [x] @GEMINI: Verificar que el workflow JSON en Git tiene `WAZUH_INDEXER_URL` (no `WAZUH_API_URL`) en el nodo de alertas — confirmar coherencia con `.env.example`
- [x] @GEMINI: Actualizar ACTIVATION_CHECKLIST.md marcando Wazuh Indexer como desbloqueado y documentando la configuración del proxy nginx
- [x] @GEMINI: Preparar recomendación de intervalos de cron para producción — ¿2 min para Wazuh es demasiado agresivo con 5.7M alertas? Calcular carga estimada (ENTRADA-021: 5-10 min recomendado inicial)

### @CLAUDE - Governor/Architect (Ronda 5)

- [ ] @CLAUDE: Cross-review dry-runs Codex Ronda 5 (Wazuh real, pipeline E2E, IoCs en PostgreSQL)
- [ ] @CLAUDE: Cross-review Gemini Ronda 5 (checklist, intervalos de cron)
- [ ] @CLAUDE: Decisión de activación: ¿activar triggers cron de fuentes internas (FortiGate, Wazuh, Zabbix) en staging?
- [ ] @CLAUDE: Registrar ADR-012 con decisión final de activación

---

## RONDA 6 — Dry-run E2E y preparación de activación (autónoma)

> **Objetivo:** Ejecutar pipeline completo en staging, verificar persistencia, preparar decisión de activación
> **Prerequisito:** Credenciales vinculadas ✅, 3 fuentes responden ✅, framework v4.7 ✅

### @CODEX - Implementer/DevOps (Ronda 6)

- [ ] @CODEX: Verificar que el workflow en staging tiene las credenciales correctas: exportar con `n8n export:workflow` y confirmar que `pg-upsert`, `pg-audit-log` y `email-alert` apuntan a `a0K3DCm6QM9FVDAx` / `cFZPbwEu9RSx0KY9` (no `CONFIGURAR`)
- [ ] @CODEX: SSH al R720, ejecutar pipeline completo manualmente via n8n CLI o trigger: verificar que los datos fluyen ingesta → normalizer → scorer → PostgreSQL
- [ ] @CODEX: Consultar PostgreSQL tras ejecución: `docker exec n8n_threat_db psql -U delcop_threat -d threat_intel -c "SELECT ioc_value, ioc_type, severity, source, sighting_count FROM iocs ORDER BY last_seen DESC LIMIT 10;"` — confirmar IoCs reales persistidos
- [ ] @CODEX: Verificar tabla `workflow_runs`: `docker exec n8n_threat_db psql -U delcop_threat -d threat_intel -c "SELECT * FROM workflow_runs ORDER BY finished_at DESC LIMIT 5;"` — confirmar audit log
- [ ] @CODEX: Si el pipeline funciona E2E, activar solo el trigger cron de **Zabbix** (5 min) como piloto — monitorear por 15 minutos que no hay crash loops ni errores repetidos

### @GEMINI - Researcher/Reviewer (Ronda 6)

- [x] @GEMINI: Revisar el workflow exportado de staging y verificar que no quedan placeholders `CONFIGURAR` en ningún nodo (ENTRADA-024: Hallazgo crítico de placeholders persistentes en credentials)
- [x] @GEMINI: Validar que `ioc_normalizer.js` embebido en el workflow de staging coincide con `app/code-nodes/ioc_normalizer.js` en Git — detectar drift si hay diferencias (ENTRADA-024: 100% de drift detectado en code nodes)
- [x] @GEMINI: Preparar checklist de monitoreo post-activación: qué métricas revisar en las primeras 24h (ejecuciones exitosas, IoCs creados, errores, uso de disco PostgreSQL) — Ver `docs/knowledge/MONITORING_CHECKLIST.md`

### @CLAUDE - Governor/Architect (Ronda 6)

- [ ] @CLAUDE: Cross-review dry-run E2E de Codex (IoCs en PostgreSQL, audit log, sin errores)
- [ ] @CLAUDE: Cross-review Gemini (drift check, checklist monitoreo)
- [ ] @CLAUDE: Decisión de activación progresiva: Zabbix primero (5 min), luego FortiGate (5 min), luego Wazuh (10 min según recomendación Gemini)
- [ ] @CLAUDE: Registrar ADR-012 con decisión de activación y plan de rollback

---

## RONDA 7 — Fix drift staging + reimport definitivo (autónoma)

> **Objetivo:** Corregir drift entre Git y staging (Zabbix auth, code-nodes), reimportar workflow definitivo, ejecutar pipeline E2E
> **Prerequisito:** Credenciales vinculadas ✅, Ronda 6 tasks

### @CODEX - Implementer/DevOps (Ronda 7)

- [ ] @CODEX: Exportar workflow actual de staging (`n8n export:workflow --id=0d5f2e64...`), comparar contra `app/workflows/threat-intel-main.json` en Git — listar todas las diferencias (drift de code-nodes embebidos, Zabbix auth, posiciones, etc.)
- [ ] @CODEX: Generar variante segura del workflow: tomar el JSON de Git (con credenciales reales ya vinculadas) y preservar IDs/credenciales del export de staging. Reimportar en staging.
- [ ] @CODEX: Tras reimport, ejecutar test manual del pipeline completo desde n8n UI o via `curl` al webhook de test si existe
- [ ] @CODEX: Verificar IoCs en PostgreSQL: `docker exec n8n_threat_db psql -U delcop_threat -d threat_intel -c "SELECT ioc_value, ioc_type, severity, source FROM iocs ORDER BY last_seen DESC LIMIT 10;"`
- [ ] @CODEX: Si E2E funciona, activar cron **Zabbix** (5 min) como piloto y monitorear 15 min sin errores

### @GEMINI - Researcher/Reviewer (Ronda 7)

- [ ] @GEMINI: Analizar el diff entre workflow Git vs staging export que genere Codex — documentar qué campos son drift real vs cambios cosméticos (posiciones, typeVersion, etc.)
- [x] @GEMINI: Verificar que `MONITORING_CHECKLIST.md` cubre el escenario de activación progresiva (Zabbix primero, luego FortiGate, luego Wazuh)
- [x] @GEMINI: Preparar template de `EVIDENCIA_ACTIVACION.md` para registrar fecha, hora y resultado de cada trigger activado (evidencia para ISO A.5.7)

### @CLAUDE - Governor (Ronda 7)

- [ ] @CLAUDE: Cross-review del diff staging vs Git y del reimport de Codex
- [ ] @CLAUDE: Cross-review de Gemini (análisis de drift, evidencia de activación)
- [ ] @CLAUDE: Si el piloto Zabbix funciona sin errores por 15 min → aprobar activación de FortiGate (5 min)
- [ ] @CLAUDE: Registrar ADR-012 con decisión de activación progresiva

---

## RONDA 8 — Fix crítico: inyectar code nodes reales en workflow + reimport definitivo (URGENTE)

> **Objetivo:** Resolver drift 100% en staging: inyectar código real de `app/code-nodes/*.js` en el workflow JSON, reimportar en staging, ejecutar E2E
> **Bloqueante:** Sin este fix, el pipeline no procesa datos — los code nodes son solo comentarios placeholder

### @CODEX - Implementer/DevOps (Ronda 8)

- [ ] @CODEX: Crear script o ejecutar manualmente: leer `app/code-nodes/ioc_normalizer.js`, `ioc_scorer.js`, `alert_dispatcher.js`, `ioc_persistence.js` y embeber su contenido en los campos `jsCode` de los nodos `code-normalizer`, `code-scorer`, `code-alert`, `code-persist` del workflow JSON (`app/workflows/threat-intel-main.json`). Preservar credenciales reales (`a0K3DCm6QM9FVDAx`, `cFZPbwEu9RSx0KY9`).
- [ ] @CODEX: Validar JSON resultante: `node -e "const wf=JSON.parse(require('fs').readFileSync('app/workflows/threat-intel-main.json','utf8')); console.log('nodes:', wf.nodes.length); wf.nodes.filter(n=>n.type.includes('code')).forEach(n=>console.log(n.name, ':', n.parameters.jsCode?.length || 0, 'chars'))"`
- [ ] @CODEX: `git pull` en R720, reimportar workflow con code nodes reales: `docker cp ... && n8n import:workflow`
- [ ] @CODEX: Ejecutar test manual del pipeline desde n8n UI — verificar que normalizer procesa datos reales de FortiGate/Wazuh/Zabbix
- [ ] @CODEX: Verificar IoCs en PostgreSQL tras ejecución: `SELECT ioc_value, ioc_type, severity, source FROM iocs ORDER BY last_seen DESC LIMIT 10;`
- [ ] @CODEX: Si E2E funciona → activar cron Zabbix (5 min) como piloto, monitorear 15 min

### @GEMINI - Researcher/Reviewer (Ronda 8)

- [ ] @GEMINI: Crear script de inyección reutilizable (`scripts/inject-code-nodes.py`) que lea los archivos `.js` de `app/code-nodes/` y los embeba automáticamente en el workflow JSON — para evitar drift futuro
- [ ] @GEMINI: Validar que el workflow JSON post-inyección tiene los 4 code nodes con código real (no placeholders) — contar chars de `jsCode` por nodo
- [ ] @GEMINI: Documentar el proceso de inyección en `RUNBOOK_THREAT_INTEL.md` sección nueva "Actualización de Code Nodes"

### @CLAUDE - Governor (Ronda 8)

- [ ] @CLAUDE: Cross-review del workflow JSON post-inyección (code nodes con código real, credenciales preservadas)
- [ ] @CLAUDE: Cross-review del script de inyección de Gemini
- [ ] @CLAUDE: Si E2E funciona → aprobar activación progresiva (Zabbix → FortiGate → Wazuh)
- [ ] @CLAUDE: Commit + push de consolidación con fix definitivo

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
