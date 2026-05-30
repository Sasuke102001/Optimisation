-- =============================================================================
-- M3 → M2 Feed Tables — AWS RDS (M2 database)
-- Run as m2 superuser against M2 RDS BEFORE creating m3_app_user.
--
-- These tables are written by M3 via m3_app_user (INSERT/UPDATE only).
-- M2 recalibration pipeline reads them to update venue_demographic_scores.
--
-- All rows carry: venue_id, session_number, session_mode, day_of_week,
-- session_start_hour — required for M2's Bayesian coverage weighting.
--
-- session_mode semantics:
--   observation_only   = no SE intervention active       → M2 weights highest
--   engineering_active = SE intervention live            → M2 weights lower / may exclude
--   post_intervention  = within 15-min cooldown after    → M2 treats with caution
-- =============================================================================


-- =============================================================================
-- m3_kpi_observations
-- Zone-level KPI RAG readings per session interval.
-- Feeds: operational_quality, group_energy, retention_strength in M2.
-- =============================================================================

CREATE TABLE IF NOT EXISTS m3_kpi_observations (
    id                  BIGSERIAL PRIMARY KEY,

    -- session anchor
    venue_id            INT  NOT NULL REFERENCES venues(id) ON DELETE CASCADE,
    session_number      INT  NOT NULL,
    session_mode        VARCHAR(30) NOT NULL DEFAULT 'observation_only'
                            CHECK (session_mode IN ('observation_only','engineering_active','post_intervention')),
    day_of_week         INT  NOT NULL CHECK (day_of_week BETWEEN 1 AND 7),   -- ISO: 1=Mon 7=Sun
    session_start_hour  INT  NOT NULL CHECK (session_start_hour BETWEEN 0 AND 23),

    -- observation
    zone                TEXT,                       -- NULL = venue-wide
    kpi_family_slug     TEXT NOT NULL,              -- matches m3_kpi_families.slug
    rag_status          VARCHAR(10) NOT NULL CHECK (rag_status IN ('green','amber','red')),
    score               FLOAT CHECK (score BETWEEN 0.0 AND 1.0),  -- normalized 0–1 mean of signal readings
    signal_count        INT,                        -- number of readings behind this assessment
    dominant_signal     TEXT,                       -- signal_label that drove the RAG outcome
    observed_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    notes               TEXT
);

CREATE INDEX IF NOT EXISTS idx_m3_kpi_obs_venue_session
    ON m3_kpi_observations (venue_id, session_number);
CREATE INDEX IF NOT EXISTS idx_m3_kpi_obs_mode
    ON m3_kpi_observations (venue_id, session_mode, observed_at DESC);


-- =============================================================================
-- m3_dwell_observations
-- Dwell-time distributions per table / segment per session.
-- Feeds: fitness_for_social_dwell, retention_strength in M2.
-- =============================================================================

CREATE TABLE IF NOT EXISTS m3_dwell_observations (
    id                  BIGSERIAL PRIMARY KEY,

    -- session anchor
    venue_id            INT  NOT NULL REFERENCES venues(id) ON DELETE CASCADE,
    session_number      INT  NOT NULL,
    session_mode        VARCHAR(30) NOT NULL DEFAULT 'observation_only'
                            CHECK (session_mode IN ('observation_only','engineering_active','post_intervention')),
    day_of_week         INT  NOT NULL CHECK (day_of_week BETWEEN 1 AND 7),
    session_start_hour  INT  NOT NULL CHECK (session_start_hour BETWEEN 0 AND 23),

    -- observation
    table_label         TEXT,                       -- e.g. "T3", "bar-left" — NULL = venue avg
    inferred_segment    TEXT,                       -- which M2 segment this group appears to be
    dwell_minutes       INT  NOT NULL,
    group_size          INT,
    observed_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_m3_dwell_obs_venue_session
    ON m3_dwell_observations (venue_id, session_number);
CREATE INDEX IF NOT EXISTS idx_m3_dwell_obs_segment
    ON m3_dwell_observations (venue_id, inferred_segment, session_mode);


-- =============================================================================
-- m3_segment_table_log
-- Granular per-table segment observations logged by operator during session.
-- Feeds: alignment_score recalibration in venue_demographic_scores.
-- =============================================================================

CREATE TABLE IF NOT EXISTS m3_segment_table_log (
    id                  BIGSERIAL PRIMARY KEY,

    -- session anchor
    venue_id            INT  NOT NULL REFERENCES venues(id) ON DELETE CASCADE,
    session_number      INT  NOT NULL,
    session_mode        VARCHAR(30) NOT NULL DEFAULT 'observation_only'
                            CHECK (session_mode IN ('observation_only','engineering_active','post_intervention')),
    day_of_week         INT  NOT NULL CHECK (day_of_week BETWEEN 1 AND 7),
    session_start_hour  INT  NOT NULL CHECK (session_start_hour BETWEEN 0 AND 23),

    -- observation
    table_label         TEXT,
    segment_id          TEXT NOT NULL,              -- matches M2 segment_id vocabulary
    group_size          INT,
    confidence          FLOAT CHECK (confidence BETWEEN 0 AND 1),
    logged_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    operator_note       TEXT
);

CREATE INDEX IF NOT EXISTS idx_m3_seg_tbl_log_venue_session
    ON m3_segment_table_log (venue_id, session_number);
CREATE INDEX IF NOT EXISTS idx_m3_seg_tbl_log_segment
    ON m3_segment_table_log (venue_id, segment_id, session_mode);


-- =============================================================================
-- m3_kpi_dimension_map
-- Maps M3 KPI family slugs to M2 fitness dimension columns.
-- Written once by M3 team. Read by M2 recalibration pipeline at runtime.
-- Tells M2 which fitness dimension each observed KPI family affects,
-- in which direction, and with what relative weight.
--
-- M2 recalibration script JOINs m3_kpi_observations to this table to know
-- which venue_fitness_dimensions column to update and how.
-- =============================================================================

CREATE TABLE IF NOT EXISTS m3_kpi_dimension_map (
    id              SERIAL PRIMARY KEY,
    kpi_family_slug TEXT        NOT NULL,
    m2_dimension    TEXT        NOT NULL,   -- exact column name in venue_fitness_dimensions
    direction       VARCHAR(10) NOT NULL CHECK (direction IN ('positive', 'negative')),
    weight          FLOAT       NOT NULL DEFAULT 1.0 CHECK (weight > 0 AND weight <= 1.0),
    notes           TEXT,
    UNIQUE (kpi_family_slug, m2_dimension)
);

INSERT INTO m3_kpi_dimension_map (kpi_family_slug, m2_dimension, direction, weight, notes) VALUES
  ('crowd_energy', 'fitness_for_group_energy', 'positive', 1.0, 'Direct measure of group energy and dancefloor activation'),
  ('crowd_energy', 'operational_quality',      'positive', 0.6, 'Active, engaged crowd reflects well-run operation'),
  ('environment',  'operational_quality',      'positive', 0.8, 'Sound/temperature/atmosphere coherence is an operational quality signal'),
  ('commercial',   'retention_strength',       'positive', 1.0, 'Long dwell + bar activity = strong retention'),
  ('commercial',   'fitness_for_social_dwell', 'positive', 0.7, 'Tables staying = venue supports social dwell behaviour'),
  ('crowd_stress', 'operational_quality',      'negative', 1.0, 'Fatigue/overcrowding/discomfort degrades operational quality score')
ON CONFLICT (kpi_family_slug, m2_dimension) DO NOTHING;

-- Dimensions intentionally NOT in this map (M3 does not have data for these):
--   fitness_for_office_lunch    -- M3 runs evening sessions only
--   fitness_for_destination_visit -- needs acquisition/marketing signals
--   fitness_for_repeat_habit    -- comes from survey recalibration (Phase 8)
--   monetization_potential      -- needs spend data, not available from KPI taps


-- =============================================================================
-- m3_app_user permissions
-- Run AFTER the tables above are created. Replace 'your_password' first.
-- =============================================================================

-- CREATE ROLE m3_app_user WITH LOGIN PASSWORD 'your_password';

-- GRANT USAGE ON SCHEMA public TO m3_app_user;

-- -- Read access to all M2 tables M3 needs for fetch_m2_venue_context()
-- GRANT SELECT ON
--     venues,
--     venue_demographic_scores,
--     venue_fitness_dimensions,
--     primitives_scores,
--     venue_similarity_deltas,
--     fitness_delta_rules,
--     drift_signals
-- TO m3_app_user;

-- -- Write access to M3 feed tables only
-- GRANT INSERT, UPDATE ON
--     m3_kpi_observations,
--     m3_dwell_observations,
--     m3_segment_table_log,
--     m3_segment_validation_feedback,
--     m3_venue_behavioral_outcomes
-- TO m3_app_user;

-- -- m3_kpi_dimension_map is read-only for m3_app_user (written at setup, never at runtime)
-- GRANT SELECT ON m3_kpi_dimension_map TO m3_app_user;

-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO m3_app_user;
