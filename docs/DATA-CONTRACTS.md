# Data Contracts — Threat Intelligence Pipeline

**Proyecto:** SGSI-TI-001
**Versión:** 2.0
**Fecha:** 2026-03-18

---

## 1. Contrato JSON estándar: Evento normalizado

Todos los normalizadores (FortiGate, Wazuh, GuardDuty, Zabbix, Trellix, OSINT) DEBEN producir items que cumplan este schema. El scorer y el persistence layer dependen de estos campos.

### Campos obligatorios

| Campo | Tipo | Descripción |
|---|---|---|
| `event_id` | string | ID único del evento en la fuente. Si no existe, generar: `{source}_{timestamp}_{hash4}` |
| `source` | string | Nombre de la fuente: `fortigate`, `wazuh`, `guardduty`, `zabbix`, `trellix`, `abuseipdb`, `otx` |
| `observed_at` | ISO 8601 | Timestamp de cuando ocurrió el evento en la fuente |
| `severity` | enum | `info`, `low`, `medium`, `high`, `critical` |
| `title` | string | Resumen corto del evento (< 200 chars) |
| `iocs` | array | Lista de IoCs extraídos (ver schema abajo) |
| `raw_payload` | object | Payload original sin modificar |

### Campos opcionales (asset)

| Campo | Tipo | Descripción |
|---|---|---|
| `asset_hostname` | string | Hostname del equipo afectado |
| `asset_ip` | string | IP del equipo afectado (puede ser interna) |
| `asset_user` | string | Usuario asociado (e.g., `DOMAIN\username`) |
| `asset_domain` | string | Dominio AD/OU |
| `asset_org_path` | string | Ruta organizacional (e.g., `My Organization\AWS\XCOL\H0LDTQ2`) |
| `description` | string | Descripción larga del evento |
| `metadata` | object | Campos específicos de la fuente |

### Campos agregados por el scorer

| Campo | Tipo | Descripción |
|---|---|---|
| `score` | integer (0-100) | Puntuación de amenaza |
| `confidence` | integer (0-100) | Confianza en el score |
| `decision` | enum | `alert`, `review`, `store`, `discard` |

### Schema de un IoC dentro del array `iocs[]`

```json
{
  "ioc_value": "string",
  "ioc_type": "ip_v4|ip_v6|domain|url|hash_md5|hash_sha1|hash_sha256|email|cve|file_name|registry_key|user_agent|cidr",
  "role": "indicator|context|enrichment",
  "tags": ["string"],
  "metadata": {}
}
```

- `role: indicator` — IoC externo accionable (IP pública maliciosa, hash de malware)
- `role: context` — Dato interno no accionable pero relevante (IP privada, hostname)
- `role: enrichment` — Dato agregado post-normalización (VT score, AbuseIPDB report)

---

## 2. Ejemplos por fuente

### FortiGate

```json
{
  "event_id": "fortigate_0419016384_1711900800",
  "source": "fortigate",
  "observed_at": "2026-03-18T14:30:00Z",
  "severity": "high",
  "title": "IPS: Anomaly detected from 185.220.101.34",
  "asset_hostname": null,
  "asset_ip": "10.0.1.50",
  "asset_user": null,
  "iocs": [
    {
      "ioc_value": "185.220.101.34",
      "ioc_type": "ip_v4",
      "role": "indicator",
      "tags": ["ips", "anomaly"],
      "metadata": {"fortigate_logid": "0419016384", "action": "blocked"}
    }
  ],
  "raw_payload": {"srcip": "185.220.101.34", "dstip": "10.0.1.50", "action": "blocked"},
  "metadata": {"policy_id": 12, "service": "HTTPS"}
}
```

### Wazuh

```json
{
  "event_id": "wazuh_1711900800_a3f2",
  "source": "wazuh",
  "observed_at": "2026-03-18T14:25:00Z",
  "severity": "high",
  "title": "CVE-2024-21887 detected on agent web-server-01",
  "asset_hostname": "web-server-01",
  "asset_ip": "10.0.2.15",
  "asset_user": null,
  "iocs": [
    {
      "ioc_value": "CVE-2024-21887",
      "ioc_type": "cve",
      "role": "indicator",
      "tags": ["vulnerability", "ivanti"],
      "metadata": {"cvss": 9.1, "package": "ivanti-connect-secure"}
    }
  ],
  "raw_payload": {},
  "metadata": {"rule_id": "23504", "agent": "web-server-01", "decoder": "json"}
}
```

### Trellix (email)

```json
{
  "event_id": "trellix_ENDPATP_1070_1727622000",
  "source": "trellix",
  "observed_at": "2025-09-29T15:00:00Z",
  "severity": "critical",
  "title": "Trojan detected: JTI/Suspect.524610!2e5a8590cf68 on H0LDTQ2",
  "asset_hostname": "H0LDTQ2",
  "asset_ip": "192.168.1.68",
  "asset_user": "AWS\\osierra",
  "asset_domain": "AWS",
  "asset_org_path": "My Organization\\AWS\\XCOL\\H0LDTQ2",
  "description": "Adaptive Threat Protection blocked Trojan via mshta.exe",
  "iocs": [
    {
      "ioc_value": "JTI/Suspect.524610!2e5a8590cf68",
      "ioc_type": "file_name",
      "role": "indicator",
      "tags": ["trellix", "trojan", "atp"],
      "metadata": {"threat_type": "Trojan", "action": "blocked"}
    }
  ],
  "raw_payload": {
    "line1": "9/29/25 3:00 PM ENDPATP_1070",
    "line2": "35104 Critical Trojan JTI/Suspect.524610!2e5a8590cf68 True",
    "line3": "Adaptive Threat Protection Blocked",
    "line4": "AWS\\osierra 192.168.1.68 H0LDTQ2",
    "line5": "My Organization\\AWS\\XCOL\\H0LDTQ2",
    "line6": "mshta.exe"
  },
  "metadata": {
    "trellix_event_id": "ENDPATP_1070",
    "trellix_event_code": "35104",
    "protection_module": "Adaptive Threat Protection",
    "action_taken": "blocked",
    "process": "mshta.exe",
    "lolbin": true,
    "hash_partial": "2e5a8590cf68"  // pragma: allowlist secret
  }
}
```

### AbuseIPDB (OSINT)

```json
{
  "event_id": "abuseipdb_185.220.101.34_1711900800",
  "source": "abuseipdb",
  "observed_at": "2026-03-18T12:00:00Z",
  "severity": "critical",
  "title": "IP 185.220.101.34 reported 847 times (confidence 100%)",
  "iocs": [
    {
      "ioc_value": "185.220.101.34",
      "ioc_type": "ip_v4",
      "role": "indicator",
      "tags": ["abuseipdb", "tor_exit", "DE"],
      "metadata": {"abuse_score": 100, "total_reports": 847, "isp": "Tor Exit", "country": "DE"}
    }
  ],
  "raw_payload": {},
  "metadata": {"usage_type": "Hosting"}
}
```

---

## 3. Fingerprint (deduplicación)

Cada evento genera un fingerprint para evitar duplicados:

```
fingerprint = SHA256(source + event_type + key_fields)
```

Donde `key_fields` varía por fuente:

| Fuente | Key fields |
|---|---|
| FortiGate | `logid + srcip + dstip + timestamp_truncated_5min` |
| Wazuh | `rule_id + agent + srcip + timestamp_truncated_5min` |
| GuardDuty | `finding_id` |
| Zabbix | `trigger_id + host` |
| Trellix | `event_id + hostname + threat_name` |
| OSINT | `ioc_value + ioc_type + source` |

El truncado de timestamp a 5 minutos evita duplicados del mismo evento en polls consecutivos.

La deduplicación ocurre en dos niveles:
1. **JS (Code node)**: Dedup en batch por fingerprint antes de enviar a SQL
2. **SQL**: `UNIQUE(fingerprint)` en `security_events` + `ON CONFLICT` como safety net

---

## 4. Scoring (determinístico)

### Fórmula

```
score = min(100, round(severity_base × source_trust × recency) + type_bonus + context_bonus)
```

### Factores

| Factor | Valores |
|---|---|
| `severity_base` | critical=100, high=80, medium=50, low=25, info=10 |
| `source_trust` | Per source: 0.30 (dian) to 0.95 (virustotal) |
| `recency` | ≤1h=1.0, ≤24h=0.9, ≤7d=0.7, ≤30d=0.5, older=0.3 |
| `type_bonus` | cve=30, sha256=25, url=20, domain=15, ip=10, email=5 |
| `context_bonus` | lolbin=+15, public_ip=+10, blocked=-10, multi_ioc=+5/each |

### Decisiones

| Score | Decisión | Acción |
|---|---|---|
| ≥ 70 | `alert` | Notificación inmediata (Slack + Teams; Email si ≥ 85) |
| 50-69 | `review` | Persistir + marcar para revisión humana |
| 20-49 | `store` | Solo persistir |
| < 20 | `discard` | No persistir |

---

## 5. Versionado del contrato

Cualquier cambio en campos obligatorios, enums, o lógica de scoring requiere:
1. Actualizar este documento
2. Actualizar `CHANGELOG.md`
3. Verificar compatibilidad con queries existentes en PostgreSQL
4. Notificar al equipo
