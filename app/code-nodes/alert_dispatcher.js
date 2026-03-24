// ============================================================
// NODO: Alert Dispatcher
// Tipo: Code Node (JavaScript) en n8n
// Input: items[] con _should_alert === true
// Output: items[] formateados para Slack, Teams, o Email
// ============================================================

const ALERT_CONFIG = {
  slack: {
    webhook_env: 'SLACK_WEBHOOK_URL',  // Desde env vars de n8n
    channel: '#security-alerts',
    username: 'DELCOP ThreatBot',
    icon_emoji: ':shield:'
  },
  teams: {
    webhook_env: 'TEAMS_WEBHOOK_URL'
  },
  email: {
    to: $env.ALERT_EMAIL_TO || 'seguridad@delcop.com.co',
    from: $env.ALERT_EMAIL_FROM || 'n8n-threatintel@delcop.com.co',
    subject_prefix: '[DELCOP SGSI]'
  }
};

const SEVERITY_COLORS = {
  critical: '#FF0000',
  high: '#FF6600',
  medium: '#FFaa00',
  low: '#00CC00',
  info: '#0088CC'
};

const SEVERITY_EMOJI = {
  critical: '🔴',
  high: '🟠',
  medium: '🟡',
  low: '🟢',
  info: 'ℹ️'
};

function formatSlackPayload(ioc) {
  const color = SEVERITY_COLORS[ioc.alert_level] || '#808080';
  const emoji = SEVERITY_EMOJI[ioc.alert_level] || '❓';

  return {
    channel: ALERT_CONFIG.slack.channel,
    username: ALERT_CONFIG.slack.username,
    icon_emoji: ALERT_CONFIG.slack.icon_emoji,
    attachments: [{
      color: color,
      title: `${emoji} IoC Detectado: ${ioc.ioc_type.toUpperCase()}`,
      title_link: ioc.ioc_type === 'ip_v4'
        ? `https://www.abuseipdb.com/check/${ioc.ioc_value}`
        : ioc.ioc_type === 'cve'
        ? `https://nvd.nist.gov/vuln/detail/${ioc.ioc_value}`
        : undefined,
      fields: [
        { title: 'Valor', value: `\`${ioc.ioc_value}\``, short: true },
        { title: 'Severidad', value: ioc.severity.toUpperCase(), short: true },
        { title: 'Score', value: `${ioc.confidence}/100`, short: true },
        { title: 'Fuente', value: ioc.source, short: true },
        { title: 'Tags', value: (ioc.tags || []).join(', ') || 'N/A', short: false }
      ],
      footer: `DELCOP Threat Intelligence | ${ioc.observed_at}`,
      ts: Math.floor(new Date(ioc.observed_at).getTime() / 1000)
    }]
  };
}

function formatTeamsPayload(ioc) {
  const color = SEVERITY_COLORS[ioc.alert_level] || '808080';
  const emoji = SEVERITY_EMOJI[ioc.alert_level] || '❓';

  return {
    "@type": "MessageCard",
    "@context": "http://schema.org/extensions",
    themeColor: color.replace('#', ''),
    summary: `${emoji} IoC: ${ioc.ioc_value}`,
    sections: [{
      activityTitle: `${emoji} IoC Detectado: ${ioc.ioc_type.toUpperCase()}`,
      activitySubtitle: `Fuente: ${ioc.source} | Score: ${ioc.confidence}/100`,
      facts: [
        { name: "Valor", value: ioc.ioc_value },
        { name: "Tipo", value: ioc.ioc_type },
        { name: "Severidad", value: ioc.severity.toUpperCase() },
        { name: "Confianza", value: `${ioc.confidence}/100` },
        { name: "Observado", value: ioc.observed_at },
        { name: "Tags", value: (ioc.tags || []).join(', ') || 'N/A' }
      ],
      markdown: true
    }],
    potentialAction: ioc.ioc_type === 'ip_v4' ? [{
      "@type": "OpenUri",
      name: "Verificar en AbuseIPDB",
      targets: [{ os: "default", uri: `https://www.abuseipdb.com/check/${ioc.ioc_value}` }]
    }] : []
  };
}

function formatEmailPayload(ioc) {
  const emoji = SEVERITY_EMOJI[ioc.alert_level] || '❓';

  return {
    to: ALERT_CONFIG.email.to,
    from: ALERT_CONFIG.email.from,
    subject: `${ALERT_CONFIG.email.subject_prefix} ${emoji} ${ioc.alert_level.toUpperCase()}: ${ioc.ioc_type} - ${ioc.ioc_value}`,
    html: `
      <div style="font-family: Arial, sans-serif; max-width: 600px;">
        <div style="background: ${SEVERITY_COLORS[ioc.alert_level]}; color: white; padding: 12px 16px; border-radius: 4px 4px 0 0;">
          <h2 style="margin: 0;">${emoji} Alerta de Amenaza - ${ioc.alert_level.toUpperCase()}</h2>
        </div>
        <div style="border: 1px solid #ddd; border-top: none; padding: 16px;">
          <table style="width: 100%; border-collapse: collapse;">
            <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">Indicador</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee; font-family: monospace;">${ioc.ioc_value}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">Tipo</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">${ioc.ioc_type}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">Score</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">${ioc.confidence}/100</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">Fuente</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">${ioc.source}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">Observado</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">${ioc.observed_at}</td></tr>
            <tr><td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: bold;">Tags</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">${(ioc.tags || []).join(', ') || 'N/A'}</td></tr>
          </table>
          <div style="margin-top: 16px; padding: 12px; background: #f5f5f5; border-radius: 4px;">
            <strong>Metadata:</strong><br>
            <pre style="font-size: 12px; overflow-x: auto;">${JSON.stringify(ioc.metadata, null, 2)}</pre>
          </div>
        </div>
        <div style="padding: 8px; text-align: center; color: #888; font-size: 12px;">
          DELCOP SGSI - Threat Intelligence Automation | n8n
        </div>
      </div>
    `
  };
}

// --- Pipeline ---
const alertItems = $input.all().filter(item => item.json._should_alert);

if (alertItems.length === 0) {
  return [{ json: { _no_alerts: true, message: 'No items above alert threshold' } }];
}

// Generar payloads para todos los canales configurados
const output = [];

for (const item of alertItems) {
  const ioc = item.json;

  // Slack payload (si configurado)
  const slackWebhook = $env[ALERT_CONFIG.slack.webhook_env];
  if (slackWebhook) {
    output.push({
      json: {
        _channel: 'slack',
        _webhook_url: slackWebhook,
        payload: formatSlackPayload(ioc),
        ioc_id: `${ioc.ioc_type}::${ioc.ioc_value}`,
        alert_level: ioc.alert_level
      }
    });
  }

  // Teams payload (si configurado)
  const teamsWebhook = $env[ALERT_CONFIG.teams.webhook_env];
  if (teamsWebhook) {
    output.push({
      json: {
        _channel: 'teams',
        _webhook_url: teamsWebhook,
        payload: formatTeamsPayload(ioc),
        ioc_id: `${ioc.ioc_type}::${ioc.ioc_value}`,
        alert_level: ioc.alert_level
      }
    });
  }

  // Email solo para critical
  if (ioc.alert_level === 'critical') {
    output.push({
      json: {
        _channel: 'email',
        payload: formatEmailPayload(ioc),
        ioc_id: `${ioc.ioc_type}::${ioc.ioc_value}`,
        alert_level: ioc.alert_level
      }
    });
  }
}

return output;
