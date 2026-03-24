// ============================================================
// NODO: IoC Normalizer & Scoring Engine
// Tipo: Code Node (JavaScript) en n8n
// Input: items[] desde cualquier fuente (FortiGate, Wazuh, etc.)
// Output: items[] normalizados con score de amenaza
// ============================================================

// --- Configuración de scoring ---
const SCORING_WEIGHTS = {
  // Pesos por tipo de fuente
  source_trust: {
    wazuh: 0.9,
    fortigate: 0.85,
    guardduty: 0.9,
    zabbix: 0.6,
    abuseipdb: 0.8,
    otx: 0.75,
    virustotal: 0.95,
    osint_feed: 0.5,
    trellix: 0.85,  // ex-FireEye, buena detección pero via email = menos contexto
    dian: 0.3  // regulatorio, no es threat intel directo
  },
  // Pesos por severidad de la fuente original
  severity_score: {
    critical: 100,
    high: 80,
    medium: 50,
    low: 25,
    info: 10
  },
  // Bonus por tipo de IoC (algunos son más accionables)
  ioc_type_bonus: {
    ip_v4: 10,
    ip_v6: 10,
    domain: 15,
    url: 20,
    hash_sha256: 25,
    hash_sha1: 20,
    hash_md5: 15,
    cve: 30,
    email: 5,
    file_name: 10,
    registry_key: 20,
    user_agent: 5,
    cidr: 15
  },
  // Multiplicador por antigüedad (IoCs recientes pesan más)
  recency_decay: {
    hours_1: 1.0,
    hours_24: 0.9,
    days_7: 0.7,
    days_30: 0.5,
    older: 0.3
  }
};

// Umbrales de alerta
const ALERT_THRESHOLDS = {
  critical: 85,  // Alerta inmediata
  high: 70,      // Alerta en batch (cada 15 min)
  medium: 50,    // Solo log
  low: 0         // Descarta
};

// --- Regex patterns para extracción de IoCs ---
const IOC_PATTERNS = {
  ip_v4: /\b(?:(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\b/g,
  ip_v6: /\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b/g,
  domain: /\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b/g,
  url: /https?:\/\/[^\s<>"{}|\\^`\[\]]+/g,
  hash_md5: /\b[a-fA-F0-9]{32}\b/g,
  hash_sha1: /\b[a-fA-F0-9]{40}\b/g,
  hash_sha256: /\b[a-fA-F0-9]{64}\b/g,
  email: /\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b/g,
  cve: /CVE-\d{4}-\d{4,}/gi
};

// Whitelist: IPs y dominios internos DELCOP que NO deben generar alertas
const WHITELIST = {
  ips: [
    '10.0.0.0/8',
    '172.16.0.0/12',
    '192.168.0.0/16',
    '127.0.0.1'
    // Agregar IPs públicas de DELCOP aquí
  ],
  domains: [
    'delcop.com',
    'delcop.com.co',
    'delcop.com.ve',
    'amazonaws.com',
    'microsoft.com',
    'office365.com',
    'windows.net'
  ]
};

// --- Funciones auxiliares ---

function isPrivateIP(ip) {
  const parts = ip.split('.').map(Number);
  return (
    parts[0] === 10 ||
    (parts[0] === 172 && parts[1] >= 16 && parts[1] <= 31) ||
    (parts[0] === 192 && parts[1] === 168) ||
    ip === '127.0.0.1'
  );
}

function isWhitelistedDomain(domain) {
  return WHITELIST.domains.some(wl => domain === wl || domain.endsWith('.' + wl));
}

function getRecencyMultiplier(timestamp) {
  if (!timestamp) return SCORING_WEIGHTS.recency_decay.older;
  const ageMs = Date.now() - new Date(timestamp).getTime();
  const ageHours = ageMs / (1000 * 60 * 60);

  if (ageHours <= 1) return SCORING_WEIGHTS.recency_decay.hours_1;
  if (ageHours <= 24) return SCORING_WEIGHTS.recency_decay.hours_24;
  if (ageHours <= 168) return SCORING_WEIGHTS.recency_decay.days_7;
  if (ageHours <= 720) return SCORING_WEIGHTS.recency_decay.days_30;
  return SCORING_WEIGHTS.recency_decay.older;
}

function mapSeverity(sourceSeverity, sourceName) {
  // Normaliza severidades de distintas fuentes al enum interno
  const normalized = String(sourceSeverity).toLowerCase();

  // FortiGate usa números (0-4)
  if (sourceName === 'fortigate') {
    const map = { '0': 'info', '1': 'low', '2': 'medium', '3': 'high', '4': 'critical' };
    return map[normalized] || 'info';
  }

  // Wazuh usa niveles 0-15
  if (sourceName === 'wazuh') {
    const level = parseInt(normalized);
    if (level >= 12) return 'critical';
    if (level >= 8) return 'high';
    if (level >= 5) return 'medium';
    if (level >= 3) return 'low';
    return 'info';
  }

  // GuardDuty usa severity float 0.0-8.9
  if (sourceName === 'guardduty') {
    const sev = parseFloat(normalized);
    if (sev >= 7.0) return 'critical';
    if (sev >= 5.0) return 'high';
    if (sev >= 3.0) return 'medium';
    if (sev >= 1.0) return 'low';
    return 'info';
  }

  // Genérico: busca match directo
  if (['critical', 'high', 'medium', 'low', 'info'].includes(normalized)) {
    return normalized;
  }

  return 'info';
}

function calculateThreatScore(ioc) {
  const sourceTrust = SCORING_WEIGHTS.source_trust[ioc._source] || 0.5;
  const severityBase = SCORING_WEIGHTS.severity_score[ioc.severity] || 10;
  const typeBonus = SCORING_WEIGHTS.ioc_type_bonus[ioc.ioc_type] || 0;
  const recency = getRecencyMultiplier(ioc.observed_at);

  // Score = (base_severity * trust_factor * recency) + type_bonus
  // Capped a 100
  let score = Math.round((severityBase * sourceTrust * recency) + typeBonus);
  score = Math.min(score, 100);

  return score;
}

function classifyAlertLevel(score) {
  if (score >= ALERT_THRESHOLDS.critical) return 'critical';
  if (score >= ALERT_THRESHOLDS.high) return 'high';
  if (score >= ALERT_THRESHOLDS.medium) return 'medium';
  return 'low';
}

// --- Normalizadores por fuente ---

function normalizeFortiGate(item) {
  const rootData = item.json;
  const iocs = [];

  // FortiOS API puede devolver un objeto con .results[] o .logs[]
  // O n8n puede haber spliteado los resultados ya.
  const logEntries = rootData.results || rootData.logs || [rootData];

  for (const data of logEntries) {
    if (!data || typeof data !== 'object') continue;

    // 1. Extraer IPs de srcip/dstip
    if (data.srcip && !isPrivateIP(data.srcip)) {
      iocs.push({
        ioc_value: data.srcip,
        ioc_type: 'ip_v4',
        severity: mapSeverity(data.severity || data.level, 'fortigate'),
        observed_at: data.date ? `${data.date}T${data.time || '00:00:00'}Z` : new Date().toISOString(),
        _source: 'fortigate',
        tags: [data.type, data.subtype, data.action].filter(Boolean),
        metadata: {
          fortigate_logid: data.logid,
          policy_id: data.policyid,
          action: data.action,
          service: data.service,
          dst: data.dstip,
          attack: data.attack, // Para IPS
          virus: data.virus    // Para Antivirus
        }
      });
    }

    // 2. Si hay URL en el log (web filter, etc.)
    if (data.hostname) {
      iocs.push({
        ioc_value: data.hostname,
        ioc_type: 'domain',
        severity: mapSeverity(data.severity || data.level, 'fortigate'),
        observed_at: new Date().toISOString(),
        _source: 'fortigate',
        tags: ['webfilter', data.catdesc].filter(Boolean),
        metadata: { url: data.url, category: data.cat }
      });
    }

    // 3. Extraer IoCs de mensajes de texto en logs UTM (IPS/Virus)
    if (data.msg) {
      // Intentar extraer hashes si es un log de Antivirus
      for (const match of data.msg.matchAll(IOC_PATTERNS.hash_sha256)) {
        iocs.push({
          ioc_value: match[0],
          ioc_type: 'hash_sha256',
          severity: mapSeverity(data.severity || data.level, 'fortigate'),
          observed_at: new Date().toISOString(),
          _source: 'fortigate',
          tags: ['virus', data.virus].filter(Boolean),
          metadata: { virus: data.virus, action: data.action }
        });
      }
    }
  }

  return iocs;
}

function normalizeWazuh(item) {
  const rootData = item.json;
  const iocs = [];

  // Indexer API devuelve { hits: { hits: [ { _source: {} } ] } }
  // Manager API devolvía { data: { affected_items: [] } } o un item individual
  let alerts = [];
  if (rootData.hits?.hits) {
    alerts = rootData.hits.hits.map(h => h._source);
  } else if (rootData.data?.affected_items) {
    alerts = rootData.data.affected_items;
  } else if (rootData.id && rootData.rule) {
    alerts = [rootData];
  }

  for (const alert of alerts) {
    // Extraer IoCs del campo data (vulnerabilidades) o del root
    const rawText = JSON.stringify(alert);

    // IPs
    for (const match of rawText.matchAll(IOC_PATTERNS.ip_v4)) {
      if (!isPrivateIP(match[0])) {
        iocs.push({
          ioc_value: match[0],
          ioc_type: 'ip_v4',
          severity: mapSeverity(alert.rule?.level || '0', 'wazuh'),
          observed_at: alert.timestamp || new Date().toISOString(),
          _source: 'wazuh',
          tags: [alert.rule?.groups || [], alert.agent?.name].flat().filter(Boolean),
          metadata: {
            rule_id: alert.rule?.id,
            rule_description: alert.rule?.description,
            agent: alert.agent?.name,
            manager: alert.manager?.name,
            decoder: alert.decoder?.name
          }
        });
      }
    }

    // CVEs de Wazuh vulnerability detector
    if (alert.vulnerability?.cve || alert.data?.vulnerability?.cve) {
      const v = alert.vulnerability || alert.data.vulnerability;
      iocs.push({
        ioc_value: v.cve,
        ioc_type: 'cve',
        severity: mapSeverity(v.severity || alert.rule?.level, 'wazuh'),
        observed_at: alert.timestamp || new Date().toISOString(),
        _source: 'wazuh',
        tags: ['vulnerability', v.package?.name].filter(Boolean),
        metadata: {
          package: v.package,
          cvss: v.cvss,
          reference: v.reference
        }
      });
    }
  }

  return iocs;
}

function normalizeGuardDuty(item) {
  const rootData = item.json;
  const iocs = [];

  // GuardDuty API devuelve { Findings: [] } o un finding individual
  const findings = rootData.Findings || (rootData.Id && rootData.Type ? [rootData] : []);

  for (const finding of findings) {
    // Extraer IPs de remote/local
    const remoteIp = finding.Service?.Action?.NetworkConnectionAction?.RemoteIpDetails?.IpAddressV4
      || finding.Service?.Action?.PortProbeAction?.PortProbeDetails?.[0]?.RemoteIpDetails?.IpAddressV4;

    if (remoteIp && !isPrivateIP(remoteIp)) {
      iocs.push({
        ioc_value: remoteIp,
        ioc_type: 'ip_v4',
        severity: mapSeverity(finding.Severity, 'guardduty'),
        observed_at: finding.Service?.EventFirstSeen || new Date().toISOString(),
        _source: 'guardduty',
        tags: [finding.Type, finding.Service?.Action?.ActionType].filter(Boolean),
        metadata: {
          finding_id: finding.Id,
          finding_type: finding.Type,
          resource_type: finding.Resource?.ResourceType,
          instance_id: finding.Resource?.InstanceDetails?.InstanceId,
          region: finding.Region,
          account_id: finding.AccountId,
          count: finding.Service?.Count
        }
      });
    }

    // Dominios maliciosos (DNS findings)
    if (finding.Service?.Action?.DnsRequestAction?.Domain) {
      const domain = finding.Service.Action.DnsRequestAction.Domain;
      if (!isWhitelistedDomain(domain)) {
        iocs.push({
          ioc_value: domain,
          ioc_type: 'domain',
          severity: mapSeverity(finding.Severity, 'guardduty'),
          observed_at: finding.Service?.EventFirstSeen || new Date().toISOString(),
          _source: 'guardduty',
          tags: ['dns', finding.Type].filter(Boolean),
          metadata: { finding_type: finding.Type, protocol: finding.Service?.Action?.DnsRequestAction?.Protocol }
        });
      }
    }
  }

  return iocs;
}

function normalizeZabbix(item) {
  const rootData = item.json;
  const iocs = [];

  // Zabbix JSON-RPC devuelve { result: [] } o un trigger individual
  const triggers = rootData.result || (rootData.triggerid ? [rootData] : []);

  for (const data of triggers) {
    // Zabbix triggers con IPs en el nombre o valor
    const text = `${data.name || ''} ${data.description || ''} ${data.value || ''}`;

    for (const match of text.matchAll(IOC_PATTERNS.ip_v4)) {
      if (!isPrivateIP(match[0])) {
        iocs.push({
          ioc_value: match[0],
          ioc_type: 'ip_v4',
          severity: data.priority >= 4 ? 'high' : data.priority >= 2 ? 'medium' : 'low',
          observed_at: data.lastchange ? new Date(data.lastchange * 1000).toISOString() : new Date().toISOString(),
          _source: 'zabbix',
          tags: ['zabbix', data.hosts?.[0]?.host].filter(Boolean),
          metadata: {
            trigger_id: data.triggerid,
            host: data.hosts?.[0]?.host,
            priority: data.priority,
            status: data.status
          }
        });
      }
    }
  }

  return iocs;
}

function normalizeOSINTFeed(item) {
  const data = item.json;
  const results = [];

  // AbuseIPDB format
  if (data.ipAddress || data.data?.ipAddress) {
    const ipData = data.data || data;
    results.push({
      ioc_value: ipData.ipAddress,
      ioc_type: 'ip_v4',
      severity: ipData.abuseConfidenceScore >= 80 ? 'critical'
        : ipData.abuseConfidenceScore >= 50 ? 'high'
        : ipData.abuseConfidenceScore >= 25 ? 'medium' : 'low',
      observed_at: ipData.lastReportedAt || new Date().toISOString(),
      _source: 'abuseipdb',
      tags: ['abuseipdb', ipData.isp, ipData.countryCode].filter(Boolean),
      metadata: {
        abuse_score: ipData.abuseConfidenceScore,
        total_reports: ipData.totalReports,
        isp: ipData.isp,
        country: ipData.countryCode,
        usage_type: ipData.usageType
      }
    });
  }

  // AlienVault OTX pulse format
  if (data.indicators) {
    for (const ind of data.indicators) {
      const typeMap = {
        'IPv4': 'ip_v4', 'IPv6': 'ip_v6', 'domain': 'domain',
        'URL': 'url', 'FileHash-MD5': 'hash_md5',
        'FileHash-SHA1': 'hash_sha1', 'FileHash-SHA256': 'hash_sha256',
        'email': 'email', 'CVE': 'cve'
      };
      const mappedType = typeMap[ind.type];
      if (mappedType) {
        results.push({
          ioc_value: ind.indicator,
          ioc_type: mappedType,
          severity: 'medium', // OTX no da severity por indicador
          observed_at: ind.created || new Date().toISOString(),
          _source: 'otx',
          tags: data.tags || [],
          metadata: { pulse_id: data.id, pulse_name: data.name, description: ind.description }
        });
      }
    }
  }

  return results;
}

// --- Pipeline principal ---

const NORMALIZERS = {
  fortigate: normalizeFortiGate,
  wazuh: normalizeWazuh,
  guardduty: normalizeGuardDuty,
  zabbix: normalizeZabbix,
  abuseipdb: normalizeOSINTFeed,
  otx: normalizeOSINTFeed,
  osint_feed: normalizeOSINTFeed
};

// Determinar fuente desde el nodo anterior (set via n8n Set node)
const firstItem = $input.first();
if (!firstItem) {
  // Caso: entrada vacía (Merge no recibió nada)
  return [];
}

const sourceName = firstItem.json._source_name || 'unknown';
const normalizer = NORMALIZERS[sourceName];

if (!normalizer) {
  return [{ json: { error: `No normalizer for source: ${sourceName}`, _source: sourceName } }];
}

// Normalizar todos los items
let allIocs = [];
const allItems = $input.all();

if (allItems.length === 0 || (allItems.length === 1 && Object.keys(allItems[0].json).length === 0)) {
  return [];
}

for (const item of allItems) {
  try {
    const normalized = normalizer(item);
    allIocs.push(...normalized);
  } catch (err) {
    // Log error pero no detiene el pipeline
    allIocs.push({
      ioc_value: 'PARSE_ERROR',
      ioc_type: 'ip_v4',
      severity: 'info',
      _source: sourceName,
      _error: err.message,
      _raw: JSON.stringify(item.json).slice(0, 500)
    });
  }
}

// Deduplicar por (value + type) dentro del mismo batch
const seen = new Map();
const deduped = [];
for (const ioc of allIocs) {
  if (ioc.ioc_value === 'PARSE_ERROR') {
    deduped.push(ioc);
    continue;
  }
  const key = `${ioc.ioc_type}::${ioc.ioc_value}`;
  if (!seen.has(key)) {
    seen.set(key, true);
    deduped.push(ioc);
  }
}

// Calcular score y clasificar
const output = deduped.map(ioc => {
  if (ioc._error) return { json: ioc };

  const score = calculateThreatScore(ioc);
  const alertLevel = classifyAlertLevel(score);

  return {
    json: {
      ioc_value: ioc.ioc_value,
      ioc_type: ioc.ioc_type,
      severity: ioc.severity,
      confidence: score,
      alert_level: alertLevel,
      observed_at: ioc.observed_at,
      source: ioc._source,
      tags: ioc.tags || [],
      metadata: ioc.metadata || {},
      // Campos de control para nodos downstream
      _should_alert: alertLevel === 'critical' || alertLevel === 'high',
      _should_persist: score >= ALERT_THRESHOLDS.low,
      _normalized_at: new Date().toISOString()
    }
  };
});

return output;
