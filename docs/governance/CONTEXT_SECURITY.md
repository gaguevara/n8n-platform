# CONTEXT_SECURITY.md — Inventario de Secretos y Variables Sensibles

> **Generado por:** Claude (Governor — cross-review + security audit)
> **Última actualización:** 2026-03-25 — Gemini (Researcher — sync Fase 1)
> **Referencia:** ADR-010, SOURCE_CONFIG_GUIDE.md, CODEX_LOG ENTRADA-033

---

## 1. Clasificación de variables

### 🔴 CRÍTICAS — Nunca commitear, rotar ante exposición

| Variable             | Descripción                           | Entorno       | Dónde se usa                        |
|----------------------|---------------------------------------|---------------|-------------------------------------|
| `N8N_ENCRYPTION_KEY` | Clave de cifrado de credenciales n8n  | Todos         | `.env`, docker-compose              |
| `RDS_PASSWORD`       | Password PostgreSQL en AWS RDS        | Producción    | `.env`, ECS task definition         |
| `THREAT_DB_PASSWORD` | Password PostgreSQL Threat Intel      | Todos         | `.env`, docker-compose, ECS         |
| `REDIS_PASSWORD`     | Password Redis (Cache IoC)            | Todos         | `.env`, docker-compose, ECS         |
| `FORTIGATE_API_KEY`  | Token API Read-Only FortiGate         | Staging/Prod  | `.env`, workflow n8n                |
| `WAZUH_INDEXER_BASIC_AUTH` | Credencial Indexer (Elastic)    | Staging/Prod  | `.env`, workflow n8n                |
| `ZABBIX_API_TOKEN`   | API Token Zabbix (Bearer)             | Staging/Prod  | `.env`, workflow n8n                |
| `ABUSEIPDB_API_KEY`  | API Key OSINT AbuseIPDB               | Staging/Prod  | `.env`, workflow n8n                |
| `OTX_API_KEY`        | API Key OSINT AlienVault OTX          | Staging/Prod  | `.env`, workflow n8n                |

---

### 🟡 SENSIBLES — Controlar acceso, no exponer en logs

| Variable               | Descripción                           | Entorno       | Dónde se usa             |
|------------------------|---------------------------------------|---------------|--------------------------|
| `FORTIGATE_HOST`       | IP/FQDN del Firewall (LAN)            | Staging/Prod  | `.env`, workflow n8n     |
| `WAZUH_INDEXER_URL`    | URL del Indexer (vía Nginx Proxy)     | Staging/Prod  | `.env`, workflow n8n     |
| `SLACK_WEBHOOK_URL`    | Webhook de canal de alertas           | Staging/Prod  | `.env`, workflow n8n     |
| `TEAMS_WEBHOOK_URL`    | Webhook de canal de alertas           | Staging/Prod  | `.env`, workflow n8n     |
| `RDS_HOST`             | Endpoint RDS (expone topología AWS)   | Producción    | `.env`, ECS              |
| `AWS_ACCOUNT_ID`       | ID de cuenta AWS                      | Producción    | Makefile, scripts ECR    |

---

### 🟢 CONFIGURACIÓN — Sin riesgo de exposición directa

| Variable            | Descripción              | Default               |
|---------------------|--------------------------|-----------------------|
| `TZ`                | Zona horaria             | `America/Bogota`      |
| `N8N_PORT`          | Puerto local             | `5678`                |
| `AWS_REGION`        | Región AWS               | `us-east-1`           |
| `TAG`               | Tag de imagen Docker     | `latest`              |

---

## 2. Estado de Fuentes y Credenciales (Staging)

| Fuente         | Conectividad | Credencial | Estado de Activación |
|----------------|--------------|------------|----------------------|
| FortiGate      | ✅ HTTP 200  | ✅ Cargada | Esperando GO (Ronda 5 UI) |
| Wazuh Indexer  | ✅ HTTP 200  | ✅ Cargada | Esperando GO (Ronda 5 UI) |
| Zabbix         | ✅ HTTP 200  | ✅ Cargada | Esperando GO (Ronda 5 UI) |
| GuardDuty      | ✅ AWS OK    | ✅ IAM Role| Activa (lectura) |
| AbuseIPDB      | ❌ 401/403   | ⏳ Pendiente| Bloqueada (Usuario) |
| AlienVault OTX | ❌ 401/403   | ⏳ Pendiente| Bloqueada (Usuario) |

---

## 3. Mecanismos de protección activos

| Mecanismo              | Estado   | Evidencia                              |
|------------------------|----------|----------------------------------------|
| `.env` en `.gitignore` | ✅ Activo | Confirmado por Codex ENTRADA-001       |
| `detect-secrets` hook  | ✅ Activo | `.secrets.baseline` actualizado        |
| `.env.example` sin secretos | ✅ | Verificado — solo placeholders        |
| Nginx Proxy (Wazuh)    | ✅ Activo | Whitelist IP aplicada en 192.168.206.10|
| ECS Secrets Manager    | ⏳ Planificado | Documentado en ADR-009/SPEC_AWS   |

---

## 4. Riesgos residuales identificados

| Riesgo                                               | Severidad | Recomendación                                  |
|------------------------------------------------------|-----------|------------------------------------------------|
| `WAZUH_INDEXER_BASIC_AUTH` incoherente | 🟡 Bajo | Documentar que debe incluir el prefijo `Basic ` |
| Webhooks reales no configurados | 🟡 Medio | Usar variables de entorno en vez de IDs fijos |
| `TAG=latest` en producción | 🟡 Medio | Migrar a tag fijo post-Fase 1 |
| Auditoría de secretos AWS | 🔴 Alto | Pendiente validar que no existan valores default|

---

## 5. Checklist de auditoría periódica

- [x] Verificar que `.env` no está trackeado: `git ls-files .env`
- [ ] Ejecutar `python -m pre_commit run detect-secrets --all-files`
- [ ] Auditar ECS Task Definition en AWS Console — confirmar uso de Secrets Manager
- [x] Validar que `WAZUH_INDEXER_URL` apunta al proxy y no al binding local

---

> **Próxima revisión:** al iniciar Fase 2 (Producción AWS)
> **Escalar a:** Claude (Governor) ante cualquier exposición sospechosa
