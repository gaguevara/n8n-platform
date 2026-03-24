# Análisis de Mapeo de Campos (Ronda 2)

Validación de las respuestas JSON esperadas vs. el mapeo implementado en `ioc_normalizer.js` basado en los dry-runs y conocimiento de las APIs.

| Fuente | Campo Origen (JSON) | Campo Normalizado (n8n) | Estado / Tipo Esperado |
|--------|---------------------|--------------------------|------------------------|
| **FortiGate** | `results[].srcip` / `results[].dstip` | `ioc_value` (ip_v4) | ✅ Verificado (HTTP 200 en dry-run) |
| **FortiGate** | `results[].level` / `severity` | `severity` | ✅ Mapeo a enum interno |
| **FortiGate** | `results[].msg` (Regex SHA256) | `ioc_value` (hash_sha256) | ✅ Extraído correctamente |
| **Wazuh** (Indexer) | `hits.hits[]._source.rule.level` | `severity` | ✅ Ajustado en Ronda 1 |
| **Wazuh** (Indexer) | `hits.hits[]._source` (Regex IPv4) | `ioc_value` (ip_v4) | ✅ Ajustado en Ronda 1 |
| **Zabbix** | `result[].priority` | `severity` | ✅ Verificado (HTTP 200 en dry-run) |
| **Zabbix** | `result[].name` / `description` (Regex) | `ioc_value` (ip_v4) | ✅ Verificado |

## Análisis de Scoring (`ioc_scorer.js`)
Los pesos asignados (`source_trust`) son coherentes con la fidelidad técnica de las fuentes observadas:
- **FortiGate (0.85):** Dedicado a seguridad, alta fidelidad.
- **Wazuh (0.90):** SIEM/XDR, correlación nativa, muy alta fidelidad.
- **Zabbix (0.60):** Monitoreo general, requiere filtrado de ruido (no todo evento de red es un IoC), fidelidad media.

## Análisis de Dispatcher (`alert_dispatcher.js`)
El nodo de dispatch ha sido corregido para usar `$env` de n8n y evaluar correctamente la existencia de los webhooks de Slack y Teams antes de despachar el payload, asegurando una falla controlada (*graceful fail*) que evita caídas del pipeline.
