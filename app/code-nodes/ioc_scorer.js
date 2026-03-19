// ============================================================
// NODO: IoC Scorer (determinístico)
// Tipo: Code Node (JavaScript) en n8n
// Input: items[] normalizados por ioc_normalizer.js
// Output: items[] con score, confidence, decision
//
// SEPARADO del normalizer por diseño:
//   - El normalizer extrae y limpia datos
//   - El scorer evalúa riesgo y decide acción
//   - Puedes ajustar scoring sin tocar normalización
// ============================================================

// --- Configuración ---

const SOURCE_TRUST = {
  wazuh: 0.90,      fortigate: 0.85,   guardduty: 0.90,
  zabbix: 0.60,     trellix: 0.85,     abuseipdb: 0.80,
  otx: 0.75,        virustotal: 0.95,  osint_feed: 0.50,
  dian: 0.30
};

const SEVERITY_BASE = {
  critical: 100,  high: 80,  medium: 50,  low: 25,  info: 10
};

const IOC_TYPE_BONUS = {
  cve: 30,          hash_sha256: 25,   hash_sha1: 20,
  hash_md5: 15,     url: 20,           domain: 15,
  ip_v4: 10,        ip_v6: 10,         cidr: 15,
  registry_key: 20, file_name: 10,     email: 5,
  user_agent: 5
};

// Recencia: IoCs más frescos pesan más
function getRecencyMultiplier(timestamp) {
  if (!timestamp) return 0.3;
  const ageHours = (Date.now() - new Date(timestamp).getTime()) / 3600000;
  if (ageHours <= 1) return 1.0;
  if (ageHours <= 24) return 0.9;
  if (ageHours <= 168) return 0.7;   // 7 días
  if (ageHours <= 720) return 0.5;   // 30 días
  return 0.3;
}

// Bonus contextuales
function getContextBonus(item) {
  let bonus = 0;
  const meta = item.metadata || {};

  // LOLBin detectado: +15
  if (meta.lolbin === true) bonus += 15;

  // IP pública: +10 (ya filtrada por normalizer, si llegó es externa)
  if (item.ioc_type === 'ip_v4' && !meta.source_ip_internal) bonus += 10;

  // Acción bloqueada: -10 (la amenaza fue contenida)
  if (meta.action_taken === 'blocked') bonus -= 10;

  // Múltiples IoCs del mismo evento: +5 por cada uno extra
  // (seteado por normalizer como _ioc_count)
  if (item._ioc_count && item._ioc_count > 1) {
    bonus += Math.min((item._ioc_count - 1) * 5, 20);
  }

  return bonus;
}

// Umbrales de decisión
const THRESHOLDS = {
  alert: 70,    // score >= 70 → alerta inmediata
  review: 50,   // 50 <= score < 70 → revisión humana
  store: 20,    // 20 <= score < 50 → solo persistir
  discard: 0    // score < 20 → descartar
};

// --- Pipeline ---

const output = [];

for (const item of $input.all()) {
  const data = item.json;

  // Si ya viene con error de normalización, pasar
  if (data._error || data._skip) {
    output.push(item);
    continue;
  }

  const source = data.source || data._source || 'unknown';
  const trust = SOURCE_TRUST[source] || 0.5;
  const sevBase = SEVERITY_BASE[data.severity] || 10;
  const typeBonus = IOC_TYPE_BONUS[data.ioc_type] || 0;
  const recency = getRecencyMultiplier(data.observed_at);
  const contextBonus = getContextBonus(data);

  // Score = (severity × trust × recency) + type_bonus + context_bonus
  let score = Math.round((sevBase * trust * recency) + typeBonus + contextBonus);
  score = Math.max(0, Math.min(100, score));

  // Confidence: qué tan seguro estamos del score
  // Alto trust + IoC completo + reciente = alta confianza
  let confidence = Math.round(trust * 100);
  if (data.ioc_type?.startsWith('hash_')) confidence = Math.min(confidence + 10, 100);
  if (data.metadata?.partial) confidence = Math.max(confidence - 30, 10);

  // Decisión determinística
  let decision;
  if (score >= THRESHOLDS.alert) decision = 'alert';
  else if (score >= THRESHOLDS.review) decision = 'review';
  else if (score >= THRESHOLDS.store) decision = 'store';
  else decision = 'discard';

  output.push({
    json: {
      ...data,
      score,
      confidence,
      decision,
      // Flags para nodos downstream
      _should_alert: decision === 'alert',
      _should_review: decision === 'review',
      _should_persist: decision !== 'discard',
      _scored_at: new Date().toISOString(),
      _scoring_factors: {
        severity_base: sevBase,
        source_trust: trust,
        recency_multiplier: recency,
        type_bonus: typeBonus,
        context_bonus: contextBonus,
        formula: '(severity × trust × recency) + type_bonus + context_bonus'
      }
    }
  });
}

return output;
