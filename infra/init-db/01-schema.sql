-- ============================================================
-- DELCOP SGSI - Threat Intelligence Database Schema v2
-- PostgreSQL 16+
-- Modelo: security_events → event_iocs → iocs
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =========================
-- ENUMS
-- =========================

CREATE TYPE severity_level AS ENUM ('info', 'low', 'medium', 'high', 'critical');
CREATE TYPE ioc_type AS ENUM (
    'ip_v4', 'ip_v6', 'domain', 'url', 'hash_md5', 'hash_sha1',
    'hash_sha256', 'email', 'cve', 'file_name', 'registry_key',
    'user_agent', 'cidr'
);
CREATE TYPE event_status AS ENUM ('new', 'investigating', 'confirmed', 'false_positive', 'resolved');
CREATE TYPE event_decision AS ENUM ('store', 'alert', 'review', 'discard');

-- =========================
-- FUENTES
-- =========================

CREATE TABLE data_sources (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL UNIQUE,
    source_type     VARCHAR(50) NOT NULL,
    api_endpoint    TEXT,
    poll_interval   INTEGER NOT NULL DEFAULT 300,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    trust_score     NUMERIC(3,2) NOT NULL DEFAULT 0.50 CHECK (trust_score BETWEEN 0 AND 1),
    last_poll_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================
-- EVENTOS DE SEGURIDAD
-- =========================

CREATE TABLE security_events (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fingerprint     VARCHAR(255) NOT NULL UNIQUE, -- dedup key: hash(source+type+key_fields)
    source_id       INTEGER NOT NULL REFERENCES data_sources(id),
    source_ref      TEXT,                          -- ID en sistema origen

    -- Campos normalizados
    title           TEXT NOT NULL,
    description     TEXT,
    severity        severity_level NOT NULL DEFAULT 'info',
    observed_at     TIMESTAMPTZ NOT NULL,

    -- Asset afectado
    asset_hostname  VARCHAR(255),
    asset_ip        INET,
    asset_user      VARCHAR(255),
    asset_domain    VARCHAR(255),
    asset_org_path  TEXT,

    -- Scoring (determinístico)
    score           SMALLINT NOT NULL DEFAULT 0 CHECK (score BETWEEN 0 AND 100),
    confidence      SMALLINT NOT NULL DEFAULT 0 CHECK (confidence BETWEEN 0 AND 100),
    decision        event_decision NOT NULL DEFAULT 'store',

    -- Estado operativo
    status          event_status NOT NULL DEFAULT 'new',

    -- Payload crudo (auditoría)
    raw_payload     JSONB NOT NULL DEFAULT '{}',
    metadata        JSONB DEFAULT '{}',

    -- Timestamps
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at     TIMESTAMPTZ,
    resolved_by     VARCHAR(100)
);

CREATE INDEX idx_events_fingerprint ON security_events (fingerprint);
CREATE INDEX idx_events_source ON security_events (source_id, observed_at DESC);
CREATE INDEX idx_events_severity ON security_events (severity) WHERE status NOT IN ('resolved', 'false_positive');
CREATE INDEX idx_events_score ON security_events (score DESC) WHERE status = 'new';
CREATE INDEX idx_events_decision ON security_events (decision) WHERE decision IN ('alert', 'review');
CREATE INDEX idx_events_observed ON security_events (observed_at DESC);
CREATE INDEX idx_events_asset ON security_events (asset_hostname, asset_ip);
CREATE INDEX idx_events_metadata ON security_events USING gin (metadata);

-- =========================
-- IoCs
-- =========================

CREATE TABLE iocs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ioc_value       TEXT NOT NULL,
    ioc_type        ioc_type NOT NULL,
    first_seen_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sighting_count  INTEGER NOT NULL DEFAULT 1,
    tags            TEXT[] DEFAULT '{}',
    metadata        JSONB DEFAULT '{}',
    UNIQUE (ioc_value, ioc_type)
);

CREATE INDEX idx_iocs_value_trgm ON iocs USING gin (ioc_value gin_trgm_ops);
CREATE INDEX idx_iocs_type ON iocs (ioc_type);
CREATE INDEX idx_iocs_last_seen ON iocs (last_seen_at DESC);
CREATE INDEX idx_iocs_tags ON iocs USING gin (tags);

-- =========================
-- RELACIÓN EVENTO ↔ IoC
-- =========================

CREATE TABLE event_iocs (
    id              BIGSERIAL PRIMARY KEY,
    event_id        UUID NOT NULL REFERENCES security_events(id) ON DELETE CASCADE,
    ioc_id          UUID NOT NULL REFERENCES iocs(id) ON DELETE CASCADE,
    role            VARCHAR(50) DEFAULT 'indicator', -- indicator, context, enrichment
    notes           TEXT,
    UNIQUE (event_id, ioc_id)
);

CREATE INDEX idx_event_iocs_event ON event_iocs (event_id);
CREATE INDEX idx_event_iocs_ioc ON event_iocs (ioc_id);

-- =========================
-- ALERTAS
-- =========================

CREATE TABLE alerts (
    id              BIGSERIAL PRIMARY KEY,
    event_id        UUID NOT NULL REFERENCES security_events(id),
    channel         VARCHAR(50) NOT NULL,
    severity        severity_level NOT NULL,
    score           SMALLINT NOT NULL,
    payload         JSONB NOT NULL,
    sent_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by VARCHAR(100)
);

CREATE INDEX idx_alerts_event ON alerts (event_id);
CREATE INDEX idx_alerts_unack ON alerts (sent_at DESC) WHERE acknowledged_at IS NULL;

-- =========================
-- AUDIT LOG
-- =========================

CREATE TABLE audit_log (
    id              BIGSERIAL PRIMARY KEY,
    entity_type     VARCHAR(50) NOT NULL,   -- 'event', 'ioc', 'alert', 'workflow'
    entity_id       TEXT NOT NULL,
    action          VARCHAR(50) NOT NULL,   -- 'created', 'updated', 'alerted', 'resolved', 'escalated'
    actor           VARCHAR(100) NOT NULL DEFAULT 'system',  -- 'system', 'n8n', username
    details         JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_entity ON audit_log (entity_type, entity_id);
CREATE INDEX idx_audit_action ON audit_log (action, created_at DESC);
CREATE INDEX idx_audit_time ON audit_log (created_at DESC);

-- =========================
-- WORKFLOW RUNS (n8n auditoría)
-- =========================

CREATE TABLE workflow_runs (
    id              BIGSERIAL PRIMARY KEY,
    workflow_name   VARCHAR(100) NOT NULL,
    source_id       INTEGER REFERENCES data_sources(id),
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at     TIMESTAMPTZ,
    status          VARCHAR(20) NOT NULL DEFAULT 'running',
    events_ingested INTEGER DEFAULT 0,
    events_created  INTEGER DEFAULT 0,
    iocs_created    INTEGER DEFAULT 0,
    alerts_sent     INTEGER DEFAULT 0,
    error_message   TEXT,
    execution_meta  JSONB DEFAULT '{}'
);

CREATE INDEX idx_runs_status ON workflow_runs (status, started_at DESC);

-- =========================
-- FUNCIONES
-- =========================

-- Upsert IoC con acumulación de sightings
CREATE OR REPLACE FUNCTION upsert_ioc(
    p_value TEXT,
    p_type ioc_type,
    p_tags TEXT[] DEFAULT '{}',
    p_metadata JSONB DEFAULT '{}'
) RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO iocs (ioc_value, ioc_type, tags, metadata)
    VALUES (p_value, p_type, p_tags, p_metadata)
    ON CONFLICT (ioc_value, ioc_type) DO UPDATE SET
        last_seen_at = NOW(),
        sighting_count = iocs.sighting_count + 1,
        tags = ARRAY(SELECT DISTINCT unnest(iocs.tags || EXCLUDED.tags)),
        metadata = iocs.metadata || EXCLUDED.metadata
    RETURNING id INTO v_id;
    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- Insertar evento con dedup por fingerprint
CREATE OR REPLACE FUNCTION upsert_event(
    p_fingerprint VARCHAR(255),
    p_source_id INTEGER,
    p_source_ref TEXT,
    p_title TEXT,
    p_description TEXT,
    p_severity severity_level,
    p_observed_at TIMESTAMPTZ,
    p_asset_hostname VARCHAR(255),
    p_asset_ip INET,
    p_asset_user VARCHAR(255),
    p_asset_domain VARCHAR(255),
    p_asset_org_path TEXT,
    p_score SMALLINT,
    p_confidence SMALLINT,
    p_decision event_decision,
    p_raw_payload JSONB,
    p_metadata JSONB
) RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO security_events (
        fingerprint, source_id, source_ref, title, description,
        severity, observed_at, asset_hostname, asset_ip, asset_user,
        asset_domain, asset_org_path, score, confidence, decision,
        raw_payload, metadata
    ) VALUES (
        p_fingerprint, p_source_id, p_source_ref, p_title, p_description,
        p_severity, p_observed_at, p_asset_hostname, p_asset_ip, p_asset_user,
        p_asset_domain, p_asset_org_path, p_score, p_confidence, p_decision,
        p_raw_payload, p_metadata
    )
    ON CONFLICT (fingerprint) DO UPDATE SET
        score = GREATEST(security_events.score, EXCLUDED.score),
        confidence = GREATEST(security_events.confidence, EXCLUDED.confidence),
        updated_at = NOW(),
        metadata = security_events.metadata || EXCLUDED.metadata
    RETURNING id INTO v_id;
    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- Vista para dashboard/reporting
CREATE MATERIALIZED VIEW event_summary AS
SELECT
    ds.name as source_name,
    se.severity,
    se.status,
    se.decision,
    COUNT(*) as total,
    AVG(se.score) as avg_score,
    MAX(se.observed_at) as latest_observed
FROM security_events se
JOIN data_sources ds ON se.source_id = ds.id
WHERE se.observed_at > NOW() - INTERVAL '30 days'
GROUP BY ds.name, se.severity, se.status, se.decision;

CREATE UNIQUE INDEX idx_event_summary ON event_summary (source_name, severity, status, decision);

-- Refrescar vista
CREATE OR REPLACE FUNCTION refresh_event_summary() RETURNS void AS $$
BEGIN REFRESH MATERIALIZED VIEW CONCURRENTLY event_summary; END;
$$ LANGUAGE plpgsql;

-- Cleanup
CREATE OR REPLACE FUNCTION cleanup_old_data(retention_days INTEGER DEFAULT 90) RETURNS JSONB AS $$
DECLARE
    events_deleted INTEGER;
    audit_deleted INTEGER;
BEGIN
    DELETE FROM security_events WHERE observed_at < NOW() - (retention_days || ' days')::INTERVAL
        AND status IN ('resolved', 'false_positive');
    GET DIAGNOSTICS events_deleted = ROW_COUNT;

    DELETE FROM audit_log WHERE created_at < NOW() - (retention_days * 2 || ' days')::INTERVAL;
    GET DIAGNOSTICS audit_deleted = ROW_COUNT;

    RETURN jsonb_build_object('events_deleted', events_deleted, 'audit_deleted', audit_deleted);
END;
$$ LANGUAGE plpgsql;
