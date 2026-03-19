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

---

## ENTRADA-005 | 2026-03-19 | research + spec

**Tipo:** Investigación y documentación de AWS ECS
**Tarea:** Investigar best practices de AWS ECS Fargate para n8n, documentar SPEC_AWS_PRODUCTION.md y mapear variables de entorno.

### Archivos creados/modificados
- `docs/sdlc/SPEC_AWS_PRODUCTION.md` (Nuevo)
- `docs/governance/CONTEXT.md`

### Resumen de análisis y best practices (ECS Fargate + n8n)
1. **Networking:** ALB es necesario para terminación SSL pública, redirigiendo al puerto interno de Fargate (5678) en subredes privadas.
2. **Storage:** Para n8n puro sin Queue, el almacenamiento efímero de Fargate con BD PostgreSQL en RDS es suficiente. Si se requieren binarios en disco compartido entre múltiples instancias, es obligatorio EFS.
3. **Secrets:** Es crítico el uso de AWS Secrets Manager (vía la directiva `secrets` del Task Definition) para inyectar `N8N_ENCRYPTION_KEY`, contraseñas de BD y credenciales de TI, evitando exponerlos como variables de entorno nativas.
4. **Logging:** Amazon CloudWatch (`awslogs`) para recolección de logs estándar del Task Definition.

### Mapeo de Variables `.env.example`
Se mapearon las variables de la siguiente forma en el nuevo SPEC:
- **Plaintext / Environment:** `TZ`, `N8N_PORT`, `RDS_HOST`, URLs no críticas (`WEBHOOK_URL`).
- **AWS Secrets Manager (Críticos):** `N8N_ENCRYPTION_KEY`, `RDS_PASSWORD`, `THREAT_DB_PASSWORD`, `REDIS_PASSWORD`.
- **SSM Parameter Store (Sensibles):** API Keys de integraciones de Threat Intelligence (`FORTIGATE_API_KEY`, etc).

### Estado Final
Se ha generado la especificación detallada del entorno de producción de AWS y se completaron los pendientes de investigación de la Fase 1. El entorno de producción debe ser desplegado basándose en `SPEC_AWS_PRODUCTION.md`.
