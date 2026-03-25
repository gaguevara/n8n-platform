# Evidencia de Cumplimiento ISO 27001:2022 — Control A.5.7

**Control A.5.7 (Inteligencia de Amenazas):** "Se debe recopilar y analizar información sobre amenazas a la seguridad de la información para producir inteligencia sobre amenazas."

Este documento consolida la evidencia técnica del diseño, implementación y validación del pipeline de Threat Intelligence en el proyecto n8n Platform DELCOP.

---

## 1. Recopilación de Información (Fuentes)

El sistema recolecta datos de múltiples fuentes internas y externas (OSINT), tal como se define en `docs/knowledge/SOURCE_CONFIG_GUIDE.md` y se implementa en `app/workflows/threat-intel-main.json`.

### 1.1 Fuentes Internas (Telemetría)
| Fuente | Método de Recolección | Estado de Validación (Staging) |
|---|---|---|
| **FortiGate (UTM)** | REST API (v2/log/memory) | ✅ Conectividad validada (HTTP 200) |
| **Wazuh (XDR)** | Indexer API (Elasticsearch DSL) | ✅ Diseño validado (v4.14 compatible) |
| **AWS GuardDuty** | AWS SDK (ListFindings/GetFindings) | ✅ Detector habilitado (us-east-1) |
| **Zabbix (NMS)** | JSON-RPC 2.0 (trigger.get) | ✅ Evidencia de respuesta (result[]) |

### 1.2 Fuentes Externas (Enriquecimiento/OSINT)
| Fuente | Propósito | Integración |
|---|---|---|
| **AbuseIPDB** | Reputación de IPs | Nodo HTTP (API v2) |
| **AlienVault OTX** | Pulses de amenazas | Nodo HTTP (API v1) |
| **VirusTotal** | Análisis de malware/hashes | Nodo HTTP (API v3) |

---

## 2. Análisis de Amenazas (Normalización y Scoring)

La información cruda es analizada y procesada mediante lógica de negocio en `app/code-nodes/` para producir inteligencia accionable.

### 2.1 Normalización (`ioc_normalizer.js`)
- **Extracción Estructural:** Parsea objetos complejos y arrays de las APIs de Wazuh, Zabbix y GuardDuty.
- **Extracción Heurística:** Uso de expresiones regulares para identificar IPv4 y hashes SHA256 embebidos en campos de texto (ej. mensajes de Antivirus de FortiGate).
- **Esquema Único:** Convierte diversos formatos a un contrato de datos estándar (`ip_v4`, `domain`, `hash_sha256`).

### 2.2 Calificación de Amenazas (`ioc_scorer.js`)
- **Source Trust:** Asignación de pesos según la fidelidad de la fuente (Wazuh: 0.90, FortiGate: 0.85, Zabbix: 0.60).
- **Severidad Dinámica:** Mapeo de prioridades nativas de la fuente a una escala unificada (Low, Medium, High, Critical).
- **Confianza:** Cálculo basado en la presencia de metadatos críticos y reputación OSINT.

---

## 3. Producción de Inteligencia (Persistencia y Alerta)

Los resultados del análisis se almacenan y distribuyen para la toma de decisiones y respuesta a incidentes.

### 3.1 Base de Datos de Inteligencia (`01-schema.sql`)
- **Tabla `iocs`:** Almacena indicadores únicos con su fingerprint, severidad y metadata.
- **Tabla `security_events`:** Registra el evento original completo (raw payload) para auditoría y análisis forense.
- **Deduplicación:** Lógica de `upsert_ioc` para evitar duplicidad y mantener el historial de avistamientos.

### 3.2 Distribución (Alerting)
- **Canales:** Slack, Microsoft Teams y Email.
- **Filtrado:** Despacho selectivo basado en severidad (ej. solo High/Critical a canales de respuesta inmediata).
- **Resiliencia:** El sistema está diseñado para fallar controladamente (`alert_dispatcher.js`) si un canal no está disponible.

---

## 4. Evidencia Operativa (Artefactos)

| Artefacto | Ubicación en Repo | Función |
|---|---|---|
| **Workflow Pipeline** | `app/workflows/threat-intel-main.json` | Motor de ejecución cron |
| **Data Contracts** | `docs/DATA-CONTRACTS.md` | SSOT de estructuras de datos |
| **Runbook** | `docs/knowledge/RUNBOOK_THREAT_INTEL.md` | Manual de procedimientos |
| **Validación Staging** | `docs/PHASE1_SUMMARY.md` | Resumen de dry-runs y estados |

---

## 5. Conclusión de Auditoría

El sistema implementado cumple con los requerimientos del control **ISO A.5.7** al establecer un ciclo completo de inteligencia:
1. **Planificación:** Definida en `SPEC_THREAT_INTEL.md`.
2. **Recolección:** Automatizada vía n8n desde 7 fuentes distintas.
3. **Procesamiento/Análisis:** Ejecutado en nodos de código especializados (JS).
4. **Difusión:** Automatizada vía integraciones de mensajería corporativa.

*Validado por Gemini (Researcher + Reviewer) — 2026-03-24*
