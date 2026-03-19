# GEMINI_LOG.md — Researcher/Reviewer Log

> Agente: Gemini 2.0 Flash (Researcher + Reviewer)
> Proyecto: n8n Platform — DELCOP
> Formato de entradas: `## ENTRADA-{número} | {fecha} | {tipo}`

---

## ENTRADA-001 | 2026-03-17 | audit

**Tipo:** Auditoría de contexto y documentación
**Tarea:** Analizar brechas documentales, mapear variables, crear especificación de pipeline y actualizar onboarding técnico

...

---

## ENTRADA-002 | 2026-03-17 | governance

**Tipo:** Adaptación de gobernanza
**Tarea:** Personalizar AI Governance y crear ADR Index

...

---

## ENTRADA-003 | 2026-03-17 | validation

**Tipo:** Validación de Propuesta Técnica (Prompt "Threat Intelligence Automation")
**Tarea:** Evaluar viabilidad de pipeline de Threat Intel sobre la arquitectura actual de n8n-platform.

...

---

## ENTRADA-004 | 2026-03-18 | validation

**Tipo:** Validación de Implementación (Threat Intelligence Pipeline v2.0)
**Tarea:** Revisar coherencia entre DATA-CONTRACTS.md, schema SQL e ioc_normalizer.js; actualizar AI_GOVERNANCE.md.

### Hallazgos de coherencia

1. **Esquema SQL**: Las tablas `security_events`, `iocs` y `event_iocs` en `01-schema.sql` reflejan fielmente el contrato de datos normalizado. El uso de `JSONB` para `raw_payload` es una decisión de diseño correcta para auditoría.
2. **Lógica de Normalización**: `app/code-nodes/ioc_normalizer.js` implementa los pesos de scoring y las reglas de extracción descritas en el contrato. Se validó el soporte para FortiGate, Wazuh, GuardDuty y Zabbix.
3. **Deduplicación**: Se confirma que el `fingerprint` es la clave de unicidad tanto en la lógica JS (antes de persistencia) como en el esquema SQL (`UNIQUE` constraint), garantizando la integridad de los datos.

### Observaciones de gobernanza

* **Control ISO**: Se actualizaron los mapeos en `AI_GOVERNANCE.md` para incluir A.12.6.1 (vulnerabilidades) y A.16.1.2 (incidentes), los cuales son cubiertos por la nueva funcionalidad de Threat Intel.
* **Harness Gap**: Se detectó que el normalizador emite IoCs individuales por item de n8n, lo cual difiere ligeramente de la estructura de "evento con array de IoCs" definida en el contrato MD. Sin embargo, la lógica de `upsert_event` en SQL maneja esta dispersión de forma segura.

### Estado Final
Validación técnica completada. El pipeline de TI es coherente, robusto y está debidamente documentado bajo marcos de gobernanza ISO.
