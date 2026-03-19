-- ============================================================
-- DELCOP SGSI - Seed Reference Data
-- Ejecutar después de schema.sql
-- ============================================================

-- Fuentes de datos registradas
INSERT INTO data_sources (name, source_type, api_endpoint, poll_interval, trust_score) VALUES
    ('fortigate',  'firewall',    'https://fortigate.delcop.local/api/v2',     300,  0.85),
    ('wazuh',      'siem',        'https://wazuh-manager:55000',               120,  0.90),
    ('guardduty',  'cloud_siem',  'https://guardduty.us-east-1.amazonaws.com', 300,  0.90),
    ('zabbix',     'monitoring',  'http://zabbix-server/api_jsonrpc.php',      300,  0.60),
    ('trellix',    'edr',         'imap://trellix-alerts@delcop.com.co',       60,   0.85),
    ('abuseipdb',  'osint',       'https://api.abuseipdb.com/api/v2',          900,  0.80),
    ('otx',        'osint',       'https://otx.alienvault.com/api/v1',         900,  0.75),
    ('virustotal', 'osint',       'https://www.virustotal.com/api/v3',         900,  0.95),
    ('dian',       'regulatory',  NULL,                                        86400, 0.30)
ON CONFLICT (name) DO NOTHING;
