# Resumen Ejecutivo - Fase 1 (Threat Intel)

**Fecha:** 2026-03-23
**Estado:** Fase 1 completada (Staging)

## 1. Qué se logró
Durante la Fase 1, se diseñó, implementó y validó el pipeline de Threat Intelligence automatizado usando n8n.
- **Entorno de Staging Estable:** Se levantó el stack en el servidor Dell R720 con Docker Compose (`n8n`, `threat-db` PostgreSQL, `threat-cache` Redis) y todos se reportan *healthy*.
- **Workflow Implementado:** Workflow principal JSON versionado e importado con éxito (30 nodos). Contiene nodos para recolección de 7 fuentes (FortiGate, Wazuh, GuardDuty, Zabbix, AbuseIPDB, OTX AlienVault, Trellix), deduplicación, scoring, y despacho de alertas.
- **Correcciones Estructurales Clave:**
  - Migración de Wazuh de su Manager API obsoleto (`/alerts`) a su **Indexer API** (puerto 9200) para búsqueda de alertas en Elasticsearch.
  - Corrección de endpoint de FortiGate a `/api/v2/log/memory/event/system?vdom=root`.
  - Migración de autenticación Zabbix a *Bearer Token*.
- **Arquitectura y Gobernanza:** Formalización de ADRs (001 a 011), implementación de un workflow secundario de "Error Handler", y generación de runbooks operativos y checklist de activación cron.

## 2. Auditoría de Coherencia (Data Contracts vs BD vs Code)
Se revisaron `DATA-CONTRACTS.md`, `01-schema.sql` y `ioc_normalizer.js`.
- **Estado:** Coherecia funcional alta, pero con una derivación arquitectónica (*drift*).
- **Hallazgo:** `DATA-CONTRACTS.md` define un contrato orientado a *Eventos* (un evento con array de IoCs). Sin embargo, `ioc_normalizer.js` aplana esto y produce una salida orientada a *IoCs* (un item individual por cada IoC encontrado).
- **Impacto:** Ninguno a nivel funcional porque el nodo persistidor fue adaptado para consumir este formato aplanado directamente, pero requiere que `DATA-CONTRACTS.md` sea actualizado en la Fase 2 para reflejar que la mensajería interna en n8n es "IoC-centric" por facilidad de procesamiento en batch.

## 3. Métricas
- **Fuentes validadas en conectividad:** 4 (FortiGate, Wazuh, Zabbix, GuardDuty).
- **Fuentes pendientes de credenciales:** 3 (AbuseIPDB, OTX, Trellix).
- **Nodos en workflow principal:** 30
- **Nodos en workflow de error:** 6
- **Entradas de Log:** > 60 entradas cruzadas entre Claude, Codex y Gemini garantizando trazabilidad y cross-review.
- **ADRs generados:** 11 vigentes.

## 4. Qué queda pendiente (Bloqueantes del Usuario)
Para pasar a la Fase 2 (Producción en AWS ECS), el usuario debe:
1. Proporcionar API keys reales de AbuseIPDB y OTX AlienVault.
2. Definir los webhooks reales de Slack y Teams.
3. Crear credenciales formales en la UI de n8n para PostgreSQL y SMTP.
4. Dar el *GO* explícito para activar los cron triggers (usando la `ACTIVATION_CHECKLIST.md`).
