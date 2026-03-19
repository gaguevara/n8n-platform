# SPEC_THREAT_INTEL.md — Pipeline de Threat Intelligence

> **ID:** SGSI-TI-001
> **Estado:** Aprobada
> **Autor:** Claude App (prompt) + Claude Code (Governor cross-review)
> **Revisores:** Codex (ENTRADA-007/008), Gemini (ENTRADA-003)
> **Fecha:** 2026-03-18

---

## 1. Objetivo

Implementar un pipeline automatizado de inteligencia de amenazas que ingeste eventos de 6+ fuentes de seguridad, normalice IoCs a un contrato JSON unificado, aplique scoring determinístico y despache alertas por Slack/Teams/Email.

## 2. Fuentes de datos

| Fuente | Tipo | Protocolo | Frecuencia |
|--------|------|-----------|------------|
| FortiGate | Firewall | REST API | 5 min |
| Wazuh | SIEM | REST API | 2 min |
| AWS GuardDuty | Cloud SIEM | REST API | 5 min |
| Zabbix | Monitoring | JSON-RPC | 5 min |
| AbuseIPDB | OSINT | REST API | 15 min |
| OTX AlienVault | OSINT | REST API | 15 min |
| Trellix (Fase 1.1) | EDR/Email | IMAP | 1 min |

## 3. Arquitectura

```
[Cron Triggers] → [HTTP Requests] → [Set Source] → [Merge]
    → [IoC Normalizer & Scorer] → [IF: Persist?] → [PostgreSQL]
                                 → [IF: Alert?] → [Dispatcher] → [Slack/Teams/Email]
```

- **n8n**: Orquestador (30 nodos)
- **PostgreSQL 16**: DB dedicada `threat_intel` (separada de n8n SQLite)
- **Redis 7**: Cache de deduplicación + futuro queue mode

## 4. Decisiones arquitectónicas

- ADR-006: PostgreSQL dedicada para threat intel (no reemplaza SQLite de n8n)
- ADR-007: Scoring determinístico por fórmula, sin LLM en Fase 1
- ADR-008: Code nodes como source of truth en `app/code-nodes/`

## 5. Controles ISO 27001:2022

A.5.7 (Threat Intel), A.5.25 (Event Evaluation), A.5.28 (Evidence Collection), A.8.8 (Vuln Mgmt), A.8.15/16 (Logging/Monitoring)

## 6. Fases

| Fase | Alcance | Estado |
|------|---------|--------|
| 1.0 | Ingestion + normalization + scoring + alerts + persistence | **Actual** |
| 1.1 | Trellix email + VirusTotal enrichment | Siguiente |
| 2.0 | LLM-assisted triage (JSON schema, human-in-the-loop) | Futuro |
| 3.0 | Automated response (FortiGate API block) | Futuro |

## 7. Archivos del entregable

```
app/code-nodes/ioc_normalizer.js     — Normalización multi-fuente
app/code-nodes/ioc_scorer.js         — Scoring determinístico
app/code-nodes/alert_dispatcher.js   — Formato Slack/Teams/Email
app/code-nodes/ioc_persistence.js    — Queries parametrizados
app/code-nodes/trellix_email_parser.js — Parser Trellix (Fase 1.1)
app/workflows/threat-intel-main.json — Workflow importable
infra/init-db/00-create-dbs.sh       — Init multi-DB
infra/init-db/01-schema.sql          — DDL completo
infra/init-db/seed_reference_data.sql — Data sources iniciales
docs/THREAT-INTEL.md                 — Documentación pipeline
docs/DATA-CONTRACTS.md               — Contrato JSON + scoring
docs/THREAT-INTEL-TRELLIX.md         — Documentación Trellix
```
