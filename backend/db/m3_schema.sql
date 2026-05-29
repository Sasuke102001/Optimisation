-- =============================================================================
-- M3 Operational Schema — Azure PostgreSQL (polynovea_m3)
-- Run against the polynovea_m3 database (not postgres):
--   psql "host=polynovea-m3.postgres.database.azure.com port=5432 user=subrojitroy dbname=polynovea_m3 sslmode=require" -f db/m3_schema.sql
-- =============================================================================

-- =============================================================================
-- VENUE ANCHOR
-- venue_id is always the canonical M2 venue_id from M2's venues table.
-- M3 never generates its own venue IDs.
-- =============================================================================

CREATE TABLE IF NOT EXISTS m3_venues (
    id          BIGSERIAL PRIMARY KEY,
    venue_id    INT  NOT NULL UNIQUE,   -- M2 canonical venues.id
    venue_name  TEXT NOT NULL,
    area        TEXT,
    city        TEXT,
    active      BOOLEAN NOT NULL DEFAULT TRUE,
    added_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- REFERENCE TABLES  (seeded from pipeline output at startup)
-- =============================================================================

CREATE TABLE IF NOT EXISTS m3_behavioral_states (
    id                BIGSERIAL PRIMARY KEY,
    slug              TEXT NOT NULL UNIQUE,
    label             TEXT NOT NULL,
    description       TEXT,
    source_file       TEXT,
    aliases           JSONB NOT NULL DEFAULT '[]',
    final_confidence  FLOAT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS m3_kpi_families (
    id                BIGSERIAL PRIMARY KEY,
    slug              TEXT NOT NULL UNIQUE,
    label             TEXT NOT NULL,
    description       TEXT,
    zone              TEXT,                              -- NULL = venue-wide
    layer             TEXT CHECK (layer IN ('A','B','C')),
    source_file       TEXT,
    section_id        TEXT,
    aliases           JSONB NOT NULL DEFAULT '[]',
    final_confidence  FLOAT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS m3_kpi_signals (
    id           BIGSERIAL PRIMARY KEY,
    family_id    BIGINT NOT NULL REFERENCES m3_kpi_families(id) ON DELETE CASCADE,
    slug         TEXT NOT NULL UNIQUE,
    label        TEXT NOT NULL,
    source_type  TEXT NOT NULL CHECK (source_type IN ('manual','counter','derived','sensor')),
    unit         TEXT,
    description  TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS m3_interventions (
    id                BIGSERIAL PRIMARY KEY,
    slug              TEXT NOT NULL UNIQUE,
    label             TEXT NOT NULL,
    description       TEXT,
    trigger_state     TEXT,   -- behavioral state that typically triggers this
    timing_window     TEXT,   -- e.g. "15–30 min into session"
    expected_effect   TEXT,
    source_file       TEXT,
    section_id        TEXT,
    aliases           JSONB NOT NULL DEFAULT '[]',
    final_confidence  FLOAT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- SESSION
-- =============================================================================

CREATE TABLE IF NOT EXISTS m3_sessions (
    id                  BIGSERIAL PRIMARY KEY,
    venue_id            INT  NOT NULL,              -- M2 canonical venue_id (cross-DB, no FK)
    session_number      INT  NOT NULL,
    session_mode        TEXT NOT NULL DEFAULT 'observation_only'
                            CHECK (session_mode IN ('observation_only','engineering_active','post_intervention')),
    table_config        JSONB,                      -- zone layout, table count, capacity
    opened_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at           TIMESTAMPTZ,
    day_of_week         INT,   -- 1=Mon 7=Sun (ISO); set by application at INSERT
    session_start_hour  INT,   -- 0-23; set by application at INSERT
    notes               TEXT,
    UNIQUE (venue_id, session_number)
);

-- =============================================================================
-- KPI ASSESSMENT
-- =============================================================================

CREATE TABLE IF NOT EXISTS m3_kpi_assessments (
    id            BIGSERIAL PRIMARY KEY,
    session_id    BIGINT NOT NULL REFERENCES m3_sessions(id) ON DELETE CASCADE,
    family_id     BIGINT NOT NULL REFERENCES m3_kpi_families(id),
    zone          TEXT,                             -- NULL = venue-wide
    assessed_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    rag_status    TEXT CHECK (rag_status IN ('green','amber','red')),
    notes         TEXT
);

CREATE TABLE IF NOT EXISTS m3_kpi_signal_readings (
    id              BIGSERIAL PRIMARY KEY,
    assessment_id   BIGINT NOT NULL REFERENCES m3_kpi_assessments(id) ON DELETE CASCADE,
    signal_id       BIGINT REFERENCES m3_kpi_signals(id),
    signal_label    TEXT,       -- fallback when signal not in m3_kpi_signals
    value_numeric   FLOAT,
    value_text      TEXT,
    recorded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- INTERVENTION TRACKING
-- post_intervention cooldown = 15 min after ended_at (enforced in application)
-- =============================================================================

CREATE TABLE IF NOT EXISTS m3_intervention_log (
    id                  BIGSERIAL PRIMARY KEY,
    session_id          BIGINT NOT NULL REFERENCES m3_sessions(id) ON DELETE CASCADE,
    intervention_id     BIGINT REFERENCES m3_interventions(id),
    intervention_label  TEXT,           -- fallback for ad-hoc interventions
    started_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at            TIMESTAMPTZ,
    operator_notes      TEXT
);

-- =============================================================================
-- BEHAVIORAL STATE TRACKING
-- =============================================================================

CREATE TABLE IF NOT EXISTS m3_session_states (
    id           BIGSERIAL PRIMARY KEY,
    session_id   BIGINT NOT NULL REFERENCES m3_sessions(id) ON DELETE CASCADE,
    state_id     BIGINT REFERENCES m3_behavioral_states(id),
    state_label  TEXT,
    zone         TEXT,
    inferred_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    confidence   FLOAT,
    source       TEXT CHECK (source IN ('ai_inferred','operator_tagged','rule_triggered'))
);

-- =============================================================================
-- SHOW ENGINEERING SUGGESTIONS
-- =============================================================================

CREATE TABLE IF NOT EXISTS m3_se_suggestions (
    id                  BIGSERIAL PRIMARY KEY,
    session_id          BIGINT NOT NULL REFERENCES m3_sessions(id) ON DELETE CASCADE,
    intervention_id     BIGINT REFERENCES m3_interventions(id),
    suggestion_text     TEXT NOT NULL,
    suggested_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    generation_mode     TEXT CHECK (generation_mode IN ('council','fast')),
    council_debate_ref  TEXT        -- Supabase debate tree id
);

CREATE TABLE IF NOT EXISTS m3_se_triggers (
    id              BIGSERIAL PRIMARY KEY,
    suggestion_id   BIGINT NOT NULL REFERENCES m3_se_suggestions(id) ON DELETE CASCADE,
    trigger_type    TEXT NOT NULL
                        CHECK (trigger_type IN ('kpi_rag','state_inferred','operator_request','timer')),
    trigger_detail  JSONB
);

CREATE TABLE IF NOT EXISTS m3_se_feedback (
    id              BIGSERIAL PRIMARY KEY,
    suggestion_id   BIGINT NOT NULL REFERENCES m3_se_suggestions(id) ON DELETE CASCADE,
    outcome         TEXT NOT NULL CHECK (outcome IN ('acted','dismissed','deferred')),
    operator_note   TEXT,
    recorded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- CUSTOMER SURVEY & SEGMENT VALIDATION
-- =============================================================================

CREATE TABLE IF NOT EXISTS m3_customer_survey_responses (
    id                  BIGSERIAL PRIMARY KEY,
    session_id          BIGINT NOT NULL REFERENCES m3_sessions(id) ON DELETE CASCADE,
    visit_occasion      TEXT CHECK (visit_occasion IN ('lunch_break','leisure','date_night','with_friends')),
    visit_frequency     TEXT CHECK (visit_frequency IN ('first_time','monthly','weekly')),
    occupation_type     TEXT CHECK (occupation_type IN ('student','working','business_owner','other')),
    music_feel          TEXT CHECK (music_feel IN ('yes','somewhat','no')),
    dwell_extension     TEXT CHECK (dwell_extension IN ('quieter','louder','same_energy')),
    submitted_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS m3_segment_validation_log (
    id                          BIGSERIAL PRIMARY KEY,
    session_id                  BIGINT NOT NULL REFERENCES m3_sessions(id) ON DELETE CASCADE,
    venue_id                    INT  NOT NULL,
    segment_id                  TEXT NOT NULL,
    m2_predicted_alignment      FLOAT,
    m3_observed_alignment       FLOAT,
    delta                       FLOAT GENERATED ALWAYS AS (m3_observed_alignment - m2_predicted_alignment) STORED,
    survey_response_count       INT NOT NULL DEFAULT 0,
    logged_at                   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================================================
-- INDEXES
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_m3_sessions_venue          ON m3_sessions (venue_id);
CREATE INDEX IF NOT EXISTS idx_m3_sessions_venue_num      ON m3_sessions (venue_id, session_number);
CREATE INDEX IF NOT EXISTS idx_m3_kpi_assess_session      ON m3_kpi_assessments (session_id);
CREATE INDEX IF NOT EXISTS idx_m3_kpi_assess_session_zone ON m3_kpi_assessments (session_id, zone);
CREATE INDEX IF NOT EXISTS idx_m3_signal_readings_assess  ON m3_kpi_signal_readings (assessment_id);
CREATE INDEX IF NOT EXISTS idx_m3_intv_log_session        ON m3_intervention_log (session_id);
CREATE INDEX IF NOT EXISTS idx_m3_intv_log_active         ON m3_intervention_log (session_id, ended_at)
                                                          WHERE ended_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_m3_session_states_session  ON m3_session_states (session_id, inferred_at DESC);
CREATE INDEX IF NOT EXISTS idx_m3_se_suggestions_session  ON m3_se_suggestions (session_id);
CREATE INDEX IF NOT EXISTS idx_m3_survey_session          ON m3_customer_survey_responses (session_id);
CREATE INDEX IF NOT EXISTS idx_m3_seg_valid_venue         ON m3_segment_validation_log (venue_id, segment_id);
