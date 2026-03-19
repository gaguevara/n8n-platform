# DELCOP SGSI — Threat Intelligence Automation

## Documento de Arquitectura y Despliegue

**Código del proyecto:** SGSI-TI-001
**Versión:** 1.0
**Fecha:** 2026-03-18
**Autor:** Gerencia de IT — DELCOP Colombia SAS
**Clasificación:** Confidencial

---

## 1. Objetivo

Automatizar la recolección, normalización, puntuación y alerta de Indicadores de Compromiso (IoCs) provenientes de la infraestructura de seguridad de DELCOP Holdings, integrando fuentes internas (FortiGate, Wazuh, AWS GuardDuty, Zabbix) y externas (AbuseIPDB, AlienVault OTX, VirusTotal).

## 2. Alcance

| Incluido | Excluido |
|---|---|
| Ingesta automatizada de 6+ fuentes | Respuesta automatizada (playbooks SOAR) |
| Normalización y deduplicación de IoCs | Integración con DIAN para facturación electrónica (ver nota) |
| Scoring de amenazas con confianza 0-100 | Correlación avanzada tipo SIEM |
| Persistencia en PostgreSQL | Threat hunting manual |
| Alertas a Slack/Teams/Email | Dashboard web (fase 2) |
| Auditoría de ejecución (workflow_runs) | |

**Nota sobre DIAN:** La fuente DIAN se incluye como feed regulatorio con frecuencia de 24h. No genera IoCs de amenaza directos sino alertas de cambio normativo que pueden impactar la postura de compliance.

## 3. Arquitectura

### 3.1 Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────────┐
│                     FASE 1: INGESTA                             │
│                                                                 │
│  ┌──────────┐ ┌────────┐ ┌───────────┐ ┌────────┐ ┌─────────┐ │
│  │ FortiGate│ │ Wazuh  │ │ GuardDuty │ │ Zabbix │ │  OSINT  │ │
│  │  (5min)  │ │ (2min) │ │  (5min)   │ │ (5min) │ │ (15min) │ │
│  └────┬─────┘ └───┬────┘ └─────┬─────┘ └───┬────┘ └────┬────┘ │
│       │           │            │            │           │       │
│       └─────────┐ │ ┌──────────┘   ┌────────┘  ┌───────┘       │
│                 ▼ ▼ ▼              ▼            ▼               │
│              ┌─────────────────────────────┐                    │
│              │     Set Source Name          │                    │
│              └────────────┬────────────────┘                    │
│                           ▼                                     │
│              ┌─────────────────────────────┐                    │
│              │       Merge All             │                    │
│              └────────────┬────────────────┘                    │
└───────────────────────────┼─────────────────────────────────────┘
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                FASE 2: NORMALIZACIÓN & SCORING                │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Code Node: ioc_normalizer.js                            │  │
│  │                                                         │  │
│  │  1. Detectar fuente → seleccionar normalizador          │  │
│  │  2. Extraer IoCs (IP, domain, hash, CVE, URL, email)   │  │
│  │  3. Filtrar whitelist (IPs internas, dominios DELCOP)   │  │
│  │  4. Deduplicar por (value + type) en batch              │  │
│  │  5. Calcular threat score:                              │  │
│  │     score = (severity × trust × recency) + type_bonus   │  │
│  │  6. Clasificar: critical(85+), high(70+), medium(50+)   │  │
│  │  7. Marcar: _should_alert, _should_persist              │  │
│  └─────────────────────────────────────────────────────────┘  │
└──────────────────────────┬────────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
┌─────────────────────────┐  ┌─────────────────────────┐
│   FASE 3: PERSISTENCIA  │  │    FASE 4: ALERTAS      │
│                         │  │                         │
│  IF _should_persist     │  │  IF _should_alert       │
│  ├→ upsert_ioc()       │  │  ├→ Format Slack        │
│  ├→ INSERT sighting     │  │  ├→ Format Teams        │
│  └→ Audit log           │  │  └→ Format Email        │
│                         │  │     (solo critical)     │
│  PostgreSQL             │  │                         │
│  ├ iocs                 │  │  Switch → Webhook/SMTP  │
│  ├ sightings            │  │                         │
│  ├ alerts               │  └─────────────────────────┘
│  └ workflow_runs        │
└─────────────────────────┘
```

### 3.2 Estructura JSON de Intercambio entre Nodos

Después del normalizador, todos los items siguen este schema:

```json
{
  "ioc_value": "185.220.101.34",
  "ioc_type": "ip_v4",
  "severity": "high",
  "confidence": 78,
  "alert_level": "high",
  "observed_at": "2026-03-18T14:30:00Z",
  "source": "fortigate",
  "tags": ["ips", "anomaly", "botnet"],
  "metadata": {
    "fortigate_logid": "0419016384",
    "policy_id": 12,
    "action": "blocked",
    "service": "HTTPS",
    "dst": "10.0.1.50",
    "dst_port": 443,
    "src_interface": "wan1",
    "dst_interface": "lan"
  },
  "_should_alert": true,
  "_should_persist": true,
  "_normalized_at": "2026-03-18T14:30:05Z"
}
```

### 3.3 Lógica de Scoring

| Factor | Peso | Ejemplo |
|---|---|---|
| `severity_score` (base) | 10-100 | critical=100, high=80, medium=50 |
| `source_trust` (multiplicador) | 0.3-0.95 | VirusTotal=0.95, Zabbix=0.6 |
| `recency_decay` (multiplicador) | 0.3-1.0 | <1h=1.0, >30d=0.3 |
| `ioc_type_bonus` (sumando) | 5-30 | CVE=30, hash_sha256=25, IP=10 |

**Fórmula:** `min(100, round(severity × trust × recency + type_bonus))`

**Umbrales de alerta:**
- ≥85 → `critical` → Alerta inmediata (Slack + Teams + Email)
- ≥70 → `high` → Alerta inmediata (Slack + Teams)
- ≥50 → `medium` → Solo persistencia, sin alerta
- <50 → `low` → Descartado (no persiste)

## 4. Fuentes de Datos — Configuración Específica

### 4.1 FortiGate (FortiOS REST API)

**Endpoint:** `GET /api/v2/log/event/system`
**Auth:** Bearer token (API key generada desde FortiGate GUI → System → API Users)
**Filtros críticos por logid:**

| LogID | Tipo | Descripción |
|---|---|---|
| 0100032001 | IPS | Intrusión detectada |
| 0100032002 | IPS | Anomalía de protocolo |
| 0419016384 | AV | Virus detectado |
| 0316013056 | WebFilter | URL bloqueada por categoría |
| 0211008192 | AppCtrl | Aplicación bloqueada |

**Riesgo:** La API de FortiGate tiene rate limiting. Con poll de 5min y 100 rows/request no debería haber problema, pero monitorear headers `X-RateLimit-Remaining`.

**Acción requerida:** Crear API user en FortiGate con perfil de solo lectura (read-only) al log. Nunca usar credenciales de admin.

### 4.2 Wazuh (REST API v4)

**Auth:** Dos pasos: POST `/security/user/authenticate` → JWT → GET `/alerts`
**Filtro:** `rule.level>7` (solo medium+ para evitar ruido)
**Campos clave extraídos:**
- `data.srcip` / `data.dstip` → IoC tipo IP
- `data.vulnerability.cve` → IoC tipo CVE
- `rule.id`, `rule.description` → metadata
- `agent.name` → contexto del host afectado

**Riesgo:** El token JWT de Wazuh expira en 900s (15min). Con poll de 2min, cada ejecución necesita re-autenticarse. El workflow ya maneja esto (nodo auth → nodo alerts en secuencia).

### 4.3 AWS GuardDuty

**Auth:** AWS IAM (Access Key + Secret). Idealmente usar IAM Role si n8n corre en EC2/ECS.
**Filtro:** `Severity >= 4.0` (medium+), `updatedAt` últimos 5 min
**Findings relevantes:**
- `Recon:EC2/PortProbeUnprotectedPort`
- `UnauthorizedAccess:EC2/SSHBruteForce`
- `Trojan:EC2/BlackholeTraffic`
- `CryptoCurrency:EC2/BitcoinTool.B!DNS`

**Recomendación:** Complementar con AWS SecurityHub para correlacionar con Inspector y Macie.

### 4.4 Zabbix (JSON-RPC 2.0)

**Auth:** API Token (generado en Administration → General → API tokens)
**Método:** `trigger.get` con `min_severity: 3` (Average+)
**Limitación:** Zabbix no es un sistema de seguridad per se. Los IoCs extraídos son limitados a IPs presentes en nombres/valores de triggers. Útil para detectar hosts comprometidos que generen tráfico anómalo.

### 4.5 OSINT Feeds

| Feed | API | Rate Limit | Tier Gratis |
|---|---|---|---|
| AbuseIPDB | REST v2 | 1000/day | Sí (con registro) |
| AlienVault OTX | REST v1 | Sin límite documentado | Sí |
| VirusTotal | REST v3 | 4/min, 500/day | Sí (limitado) |

**Nota:** VirusTotal gratis es muy limitado. Para uso serio, considerar Community API o comprar quota.

## 5. Base de Datos

### 5.1 Modelo de Datos

Ver `sql/schema.sql` para DDL completo. Tablas principales:

- **`iocs`**: Tabla maestra de indicadores. Dedup por `(ioc_value, ioc_type)`. Upsert via función `upsert_ioc()` que incrementa `sighting_count` y toma el mayor score.
- **`sightings`**: Cada observación individual de un IoC. Un IoC puede tener N sightings de M fuentes.
- **`alerts`**: Registro de alertas enviadas. Permite tracking de acknowledgment.
- **`workflow_runs`**: Auditoría de cada ejecución del pipeline. Registra items procesados, creados, alertados.
- **`data_sources`**: Catálogo de fuentes configuradas.

### 5.2 Retención

- **sightings:** 90 días (configurable via `cleanup_old_sightings()`)
- **iocs:** Indefinido (marcar como `resolved` pero no borrar)
- **alerts:** 365 días
- **workflow_runs:** 30 días

### 5.3 Vista Materializada

`ioc_summary` se refresca post-ingesta via `SELECT refresh_ioc_summary()`. Proporciona stats agregados para futuro dashboard.

## 6. Seguridad del Despliegue

### 6.1 Gestión de Credenciales

| Práctica | Implementación |
|---|---|
| Secrets en .env | `.env` fuera del repo, solo `.env.example` commiteado |
| n8n Encryption Key | `N8N_ENCRYPTION_KEY` cifra todas las credentials almacenadas en n8n |
| PostgreSQL solo localhost | Puerto 5432 bindeado a `127.0.0.1`, no expuesto |
| Redis con password | `--requirepass` configurado |
| API keys rotación | Documentar calendario de rotación (mínimo cada 90 días) |
| FortiGate read-only | API user con perfil limitado a lectura de logs |
| AWS IAM least privilege | Policy solo con `guardduty:GetFindings`, `guardduty:ListFindings` |

### 6.2 Seguridad de Red

```
Internet ──► [Reverse Proxy / FortiGate] ──► n8n:5678
                                              │
                                    delcop-threat-network (bridge)
                                              │
                                    ┌─────────┼─────────┐
                                    ▼         ▼         ▼
                                  postgres  redis     (futuro)
                                  :5432     :6379
                                  (localhost only)
```

**Recomendaciones críticas:**

1. **n8n detrás de reverse proxy** con TLS. Nunca exponer puerto 5678 directo a internet.
2. **Network segmentation:** El docker network `delcop-threat-network` es bridge aislado. Solo n8n tiene acceso a postgres y redis.
3. **Webhook URL:** Si se usan webhooks entrantes (ej. para recibir alertas de Wazuh push), configurar autenticación en el webhook de n8n (header auth o HMAC).
4. **Docker socket:** Nunca montar `/var/run/docker.sock` en el contenedor de n8n.
5. **Actualizaciones:** Fijar versiones de imágenes en producción. No usar `:latest`.

### 6.3 Checklist de Hardening

- [ ] `.env` con permisos `600` (solo owner)
- [ ] `N8N_ENCRYPTION_KEY` generado con `openssl rand -hex 32`
- [ ] PostgreSQL password con mínimo 20 caracteres, generado aleatoriamente
- [ ] FortiGate API user con trusted host configurado (solo IP del servidor n8n)
- [ ] Wazuh API user con role limitado (solo `agents:read`, `alerts:read`)
- [ ] AWS IAM user con policy inline, sin permisos de escritura
- [ ] Backup automatizado de PostgreSQL (pg_dump a S3 o bucket)
- [ ] Monitoreo de health checks de los contenedores
- [ ] Log rotation configurado para Docker logs

## 7. Despliegue

### 7.1 Prerequisitos

```bash
# Verificar versiones
docker --version    # >= 20.10
docker compose version  # >= 2.0
```

### 7.2 Pasos

```bash
# 1. Clonar o copiar el proyecto
cd /opt/delcop
git clone <repo> threat-intel
cd threat-intel

# 2. Configurar environment
cp docker/.env.example docker/.env
chmod 600 docker/.env
# Editar .env con valores reales

# 3. Generar encryption key
echo "N8N_ENCRYPTION_KEY=$(openssl rand -hex 32)" >> docker/.env

# 4. Hacer ejecutable el script de init
chmod +x docker/create-multiple-dbs.sh

# 5. Levantar stack
cd docker
docker compose -f docker-compose.threat-intel.yml up -d

# 6. Verificar health
docker compose -f docker-compose.threat-intel.yml ps
docker compose -f docker-compose.threat-intel.yml logs -f n8n

# 7. Importar workflow en n8n UI
# Acceder a https://n8n.delcop.com.co
# Settings → Import from file → workflows/threat-intel-main.json

# 8. Configurar credenciales en n8n
# Settings → Credentials → Crear PostgreSQL, SMTP, etc.

# 9. Pegar código en Code nodes
# Abrir cada Code node y pegar contenido de scripts/*.js

# 10. Activar workflow
```

### 7.3 Verificación Post-Despliegue

```bash
# Verificar PostgreSQL
docker exec delcop-threat-db psql -U $POSTGRES_USER -d threat_intel -c "SELECT count(*) FROM data_sources;"

# Verificar Redis
docker exec delcop-threat-cache redis-cli -a $REDIS_PASSWORD ping

# Test manual del workflow
# En n8n UI: ejecutar manualmente y verificar que las fuentes responden
```

## 8. Cumplimiento Normativo

### 8.1 ISO 27001:2022

| Control | Implementación |
|---|---|
| A.5.7 Threat intelligence | Este proyecto implementa directamente este control |
| A.8.15 Logging | `workflow_runs` y `sightings` proveen trazabilidad |
| A.8.16 Monitoring activities | Alertas automatizadas con scoring |
| A.5.23 Information security for cloud services | GuardDuty + IAM least privilege |
| A.8.9 Configuration management | Docker Compose versionado, .env.example |

### 8.2 Ley 1581 de 2012 (Protección de Datos Personales — Colombia)

Los IoCs procesados (IPs, dominios, hashes) no constituyen datos personales per se. Sin embargo:
- Si un IoC se correlaciona con un usuario interno, la investigación subsecuente debe seguir el procedimiento de DELCOP para tratamiento de datos personales.
- Los logs de `sightings` que contengan IPs de empleados deben tratarse conforme a la política de privacidad interna.

### 8.3 Circular Externa 007 de 2018 (SFC — Ciberseguridad)

Aunque aplica a entidades financieras vigiladas, es buena práctica seguir los lineamientos de:
- Gestión de incidentes de ciberseguridad
- Monitoreo continuo de amenazas
- Reporte de incidentes significativos

## 9. Roadmap

| Fase | Descripción | Estimado |
|---|---|---|
| 1.0 (actual) | Pipeline de ingesta, normalización, alertas | Completado |
| 1.1 | Integración VirusTotal enrichment (lookup de hashes/IPs) | +2 semanas |
| 1.2 | Dashboard web (Grafana o React) sobre `ioc_summary` | +3 semanas |
| 2.0 | Respuesta automatizada: bloqueo en FortiGate via API | +4 semanas |
| 2.1 | Correlación temporal: detectar patrones de ataque | +6 semanas |
| 3.0 | Integración con MITRE ATT&CK framework (tagging) | +8 semanas |

## 10. Estructura del Proyecto

```
threat-intel-project/
├── docker/
│   ├── docker-compose.threat-intel.yml
│   ├── create-multiple-dbs.sh
│   └── .env.example
├── workflows/
│   └── threat-intel-main.json          # Importar en n8n
├── scripts/
│   ├── ioc_normalizer.js               # Code node: normalización + scoring
│   ├── alert_dispatcher.js             # Code node: formateo de alertas
│   └── ioc_persistence.js              # Code node: queries de persistencia
├── sql/
│   └── schema.sql                      # DDL PostgreSQL
└── docs/
    └── README.md                       # Este documento
```
