// ============================================================
// NODO: Trellix Email Parser (formato real DELCOP)
// Tipo: Code Node (JavaScript) en n8n
// Input: items[] desde nodo IMAP Trigger / Outlook Trigger
//
// FORMATO REAL del correo (texto plano, NO HTML con tablas):
//
//   From: do-not-reply@manage.trellix.com
//   To: comite.seguridad@delcop.com.co,...
//   Subject: (vacío o genérico)
//
//   Body (texto plano, campos separados por espacios/tabs):
//   ──────────────────────────────────────────────────────
//   9/29/25 3:00 PM ENDPATP_1070
//   35104 Critical Trojan JTI/Suspect.524610!2e5a8590cf68 True
//   Adaptive Threat Protection Blocked
//   AWS\osierra 192.168.1.68 H0LDTQ2
//   My Organization\AWS\XCOL\H0LDTQ2
//   mshta.exe
//   ──────────────────────────────────────────────────────
//
// Estructura deducida por línea:
//   L1: fecha hora evento_id
//   L2: event_code severity threat_type threat_name [bool]
//   L3: módulo_protección acción
//   L4: dominio\usuario IP hostname
//   L5: ruta_organizacional\hostname
//   L6: proceso/archivo ejecutado
// ============================================================

const TRELLIX_FROM = 'do-not-reply@manage.trellix.com';

const SEVERITY_MAP = {
  'critical': 'critical',
  'high': 'high',
  'medium': 'medium',
  'med': 'medium',
  'low': 'low',
  'informational': 'info',
  'info': 'info'
};

function isPrivateIP(ip) {
  const p = ip.split('.').map(Number);
  return (
    p[0] === 10 ||
    (p[0] === 172 && p[1] >= 16 && p[1] <= 31) ||
    (p[0] === 192 && p[1] === 168) ||
    ip === '127.0.0.1'
  );
}

const IP_REGEX = /\b(?:(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\b/g;
const HASH_MD5 = /\b[a-fA-F0-9]{32}\b/g;
const HASH_SHA256 = /\b[a-fA-F0-9]{64}\b/g;
const CVE_REGEX = /CVE-\d{4}-\d{4,}/gi;

function extractHashFromThreatName(threatName) {
  if (!threatName) return null;
  const bangPart = threatName.split('!')[1];
  if (bangPart) {
    const clean = bangPart.replace(/[^a-fA-F0-9]/g, '');
    if (clean.length === 32) return { type: 'hash_md5', value: clean };
    if (clean.length === 40) return { type: 'hash_sha1', value: clean };
    if (clean.length === 64) return { type: 'hash_sha256', value: clean };
    return { type: 'partial', value: clean };
  }
  return null;
}

function parseTrellixDate(dateStr) {
  if (!dateStr) return new Date().toISOString();
  try {
    const match = dateStr.match(/(\d{1,2})\/(\d{1,2})\/(\d{2})\s+(\d{1,2}):(\d{2})\s*(AM|PM)/i);
    if (match) {
      let [, month, day, year, hours, minutes, ampm] = match;
      year = parseInt(year) + 2000;
      hours = parseInt(hours);
      if (ampm.toUpperCase() === 'PM' && hours !== 12) hours += 12;
      if (ampm.toUpperCase() === 'AM' && hours === 12) hours = 0;
      return new Date(year, parseInt(month) - 1, parseInt(day), hours, parseInt(minutes)).toISOString();
    }
  } catch (e) { /* fall through */ }
  return new Date().toISOString();
}

const SUSPICIOUS_PROCESSES = [
  'mshta.exe', 'wscript.exe', 'cscript.exe', 'powershell.exe',
  'cmd.exe', 'regsvr32.exe', 'rundll32.exe', 'certutil.exe',
  'bitsadmin.exe', 'msiexec.exe', 'wmic.exe', 'schtasks.exe',
  'psexec.exe', 'net.exe', 'net1.exe', 'sc.exe'
];

function parseTrellixEmail(emailBody, emailDate) {
  const body = (emailBody || '').replace(/\r\n/g, '\n').replace(/\r/g, '\n');
  const lines = body.split('\n').map(l => l.trim()).filter(l => l.length > 0);

  if (lines.length < 3) {
    return { parsed: false, reason: 'Too few lines', raw: body.slice(0, 500) };
  }

  const result = {
    event_date: emailDate || new Date().toISOString(),
    event_id: null, event_code: null,
    severity: 'medium', threat_type: null, threat_name: null,
    protection_module: null, action_taken: null,
    user: null, domain: null, source_ip: null, hostname: null,
    org_path: null, process: null, parsed: true
  };

  // L1: "9/29/25 3:00 PM ENDPATP_1070"
  const l1 = lines[0];
  const dateMatch = l1.match(/(\d{1,2}\/\d{1,2}\/\d{2}\s+\d{1,2}:\d{2}\s*(?:AM|PM)?)/i);
  if (dateMatch) result.event_date = parseTrellixDate(dateMatch[1]);
  const l1Parts = l1.split(/\s+/);
  result.event_id = l1Parts[l1Parts.length - 1];

  // L2: "35104 Critical Trojan JTI/Suspect.524610!2e5a8590cf68 True"
  if (lines.length > 1) {
    const l2Parts = lines[1].split(/\s+/);
    if (/^\d+$/.test(l2Parts[0])) result.event_code = l2Parts[0];
    for (const part of l2Parts) {
      if (SEVERITY_MAP[part.toLowerCase()]) { result.severity = SEVERITY_MAP[part.toLowerCase()]; break; }
    }
    const sevIdx = l2Parts.findIndex(p => SEVERITY_MAP[p.toLowerCase()]);
    if (sevIdx >= 0 && sevIdx + 1 < l2Parts.length) result.threat_type = l2Parts[sevIdx + 1];
    const threatToken = l2Parts.find(p => (p.includes('/') || p.includes('!')) && !/^\d+$/.test(p));
    if (threatToken) result.threat_name = threatToken;
  }

  // L3: "Adaptive Threat Protection Blocked"
  if (lines.length > 2) {
    const l3 = lines[2];
    const actions = ['blocked', 'detected', 'cleaned', 'deleted', 'quarantined', 'allowed', 'denied', 'would block'];
    for (const act of actions) {
      if (l3.toLowerCase().includes(act)) {
        result.action_taken = act;
        result.protection_module = l3.replace(new RegExp(act, 'i'), '').trim();
        break;
      }
    }
    if (!result.action_taken) result.protection_module = l3;
  }

  // L4: "AWS\osierra 192.168.1.68 H0LDTQ2"
  if (lines.length > 3) {
    const l4 = lines[3];
    const ipMatch = l4.match(IP_REGEX);
    if (ipMatch) result.source_ip = ipMatch[0];
    const userMatch = l4.match(/([A-Za-z0-9_.-]+)\\([A-Za-z0-9_.-]+)/);
    if (userMatch) { result.domain = userMatch[1]; result.user = userMatch[2]; }
    const l4Parts = l4.split(/\s+/);
    const lastTok = l4Parts[l4Parts.length - 1];
    if (lastTok && !lastTok.match(IP_REGEX) && !lastTok.includes('\\')) result.hostname = lastTok;
  }

  // L5: "My Organization\AWS\XCOL\H0LDTQ2"
  if (lines.length > 4) result.org_path = lines[4];

  // L6: "mshta.exe"
  if (lines.length > 5) result.process = lines[5];

  return result;
}

// --- Pipeline ---
const results = [];

for (const item of $input.all()) {
  const email = item.json;
  const from = email.from?.text || email.from || '';
  const body = email.text || email.textPlain || email.html || '';
  const emailDate = email.date || email.headers?.date || new Date().toISOString();

  if (!from.toLowerCase().includes('trellix.com') &&
      !from.toLowerCase().includes('mcafee.com')) {
    continue;
  }

  const parsed = parseTrellixEmail(body, emailDate);

  if (!parsed.parsed) {
    results.push({ json: {
      ioc_value: `TRELLIX_UNPARSED_${Date.now()}`, ioc_type: 'file_name',
      severity: 'info', observed_at: emailDate, _source: 'trellix', _source_name: 'trellix',
      tags: ['trellix', 'parse_error'],
      metadata: { reason: parsed.reason, raw: parsed.raw, email_from: from },
      _should_persist: false, _should_alert: false
    }});
    continue;
  }

  const baseMeta = {
    trellix_event_id: parsed.event_id,
    trellix_event_code: parsed.event_code,
    threat_type: parsed.threat_type,
    threat_name: parsed.threat_name,
    protection_module: parsed.protection_module,
    action_taken: parsed.action_taken,
    user: parsed.user ? `${parsed.domain || ''}\\${parsed.user}` : null,
    hostname: parsed.hostname,
    org_path: parsed.org_path,
    process: parsed.process,
    source_ip_internal: parsed.source_ip,
    lolbin: parsed.process ? SUSPICIOUS_PROCESSES.includes(parsed.process.toLowerCase()) : false
  };

  const tags = ['trellix', parsed.threat_type, parsed.action_taken, parsed.protection_module].filter(Boolean);
  let hasIoC = false;

  // IoC 1: Threat name (firma de detección)
  if (parsed.threat_name) {
    results.push({ json: {
      ioc_value: parsed.threat_name, ioc_type: 'file_name', severity: parsed.severity,
      observed_at: parsed.event_date, _source: 'trellix', _source_name: 'trellix',
      tags, metadata: baseMeta
    }});
    hasIoC = true;
  }

  // IoC 2: Hash del threat name (si es completo)
  const hashInfo = extractHashFromThreatName(parsed.threat_name);
  if (hashInfo && hashInfo.type !== 'partial') {
    results.push({ json: {
      ioc_value: hashInfo.value.toLowerCase(), ioc_type: hashInfo.type, severity: parsed.severity,
      observed_at: parsed.event_date, _source: 'trellix', _source_name: 'trellix',
      tags, metadata: { ...baseMeta, hash_source: 'threat_name_extraction' }
    }});
    hasIoC = true;
  }

  // IoC 3: IP pública (si aplica)
  if (parsed.source_ip && !isPrivateIP(parsed.source_ip)) {
    results.push({ json: {
      ioc_value: parsed.source_ip, ioc_type: 'ip_v4', severity: parsed.severity,
      observed_at: parsed.event_date, _source: 'trellix', _source_name: 'trellix',
      tags, metadata: baseMeta
    }});
    hasIoC = true;
  }

  // IoC 4: Hashes completos y CVEs del body
  for (const h of [...new Set(body.match(HASH_SHA256) || [])]) {
    results.push({ json: {
      ioc_value: h.toLowerCase(), ioc_type: 'hash_sha256', severity: parsed.severity,
      observed_at: parsed.event_date, _source: 'trellix', _source_name: 'trellix',
      tags, metadata: { ...baseMeta, hash_source: 'email_body' }
    }});
    hasIoC = true;
  }
  for (const cve of [...new Set(body.match(CVE_REGEX) || [])]) {
    results.push({ json: {
      ioc_value: cve.toUpperCase(), ioc_type: 'cve', severity: parsed.severity,
      observed_at: parsed.event_date, _source: 'trellix', _source_name: 'trellix',
      tags, metadata: baseMeta
    }});
    hasIoC = true;
  }

  // Evento interno sin IoC externo (IP privada, hash parcial)
  // Igual se registra para auditoría y correlación
  if (!hasIoC) {
    results.push({ json: {
      ioc_value: `${parsed.hostname || 'unknown'}:${parsed.process || 'unknown'}:${parsed.threat_name || 'unknown'}`,
      ioc_type: 'file_name', severity: parsed.severity,
      observed_at: parsed.event_date, _source: 'trellix', _source_name: 'trellix',
      tags: [...tags, 'internal_event', 'no_external_ioc'],
      metadata: { ...baseMeta, _note: 'Internal event with private IP. No external IoC. Registered for audit and correlation.' }
    }});
  }
}

if (results.length === 0) {
  return [{ json: { _skip: true, message: 'No Trellix emails in batch' } }];
}

return results;
