-- ─────────────────────────────────────────────────────────────────────────────
-- Supabase DDL — Module 3 AI interaction tables
-- Run in Supabase SQL editor (project: polynovea)
--
-- Three tables:
--   1. module3_council_sessions     — full AI debate tree per brief request
--   2. module3_prediction_outcomes  — actual vs predicted comparison (feedback loop)
--   3. module3_venue_session_index  — running session counter and history unlock flag
-- ─────────────────────────────────────────────────────────────────────────────


-- ─────────────────────────────────────────────────────────────────────────────
-- 1. module3_council_sessions
-- Stores the full 3-round debate tree for every Module 3 brief.
-- Mirrors the structure of venue_council_sessions (Module 2) but adds
-- Module 3-specific fields: session_number, session_mode, brief_type,
-- prediction_snapshot, and intelligence_mode.
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS module3_council_sessions (
    id                  BIGSERIAL PRIMARY KEY,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Venue identification
    venue_id            TEXT,           -- NULL if venue not found in M2 DB
    venue_name          TEXT NOT NULL,

    -- Session context
    session_number      INT  NOT NULL,  -- 1-based; used for theory vs history mode
    session_mode        TEXT NOT NULL,  -- pre_session | mid_session | post_session
    brief_type          TEXT NOT NULL DEFAULT 'full',
    intelligence_mode   TEXT NOT NULL,  -- theory | history

    -- The question the operator asked (or default question)
    question            TEXT NOT NULL,

    -- Full 3-round debate tree (proprietary training data)
    debate_tree         JSONB,          -- {nemotron: {r1, r2}, deepseek: {r1, r2}, mistral/qwen: {r1, r2}}
    models_errored      TEXT[],         -- model names that errored during the run

    -- Synthesis (final answer streamed to operator)
    synthesis_model     TEXT NOT NULL DEFAULT 'nemotron',
    synthesis           TEXT,

    -- Structured prediction snapshot (pre_session only — enables M3→M2 feedback loop)
    prediction_snapshot JSONB,          -- null for mid_session and post_session briefs

    -- Outcome metadata
    consensus_reached   BOOLEAN,
    duration_ms         INT
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_m3_council_venue_name
    ON module3_council_sessions (venue_name);

CREATE INDEX IF NOT EXISTS idx_m3_council_venue_id
    ON module3_council_sessions (venue_id)
    WHERE venue_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_m3_council_session_mode
    ON module3_council_sessions (session_mode, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_m3_council_created_at
    ON module3_council_sessions (created_at DESC);

COMMENT ON TABLE module3_council_sessions IS
    'Full Module 3 AI debate tree per brief request. '
    'The prediction_snapshot column (pre_session only) is the key to the '
    'M3→M2 feedback loop — it stores structured predictions before the session '
    'so they can be compared against actual outcomes in module3_prediction_outcomes.';

COMMENT ON COLUMN module3_council_sessions.prediction_snapshot IS
    'Structured JSON prediction extracted from pre_session synthesis. '
    'Example: {predicted_peak_time, predicted_crowd_energy_peak, atmosphere_interventions, ...}. '
    'NULL for mid_session and post_session briefs.';


-- ─────────────────────────────────────────────────────────────────────────────
-- 2. module3_prediction_outcomes
-- The feedback loop table: actual session outcomes logged against prior predictions.
-- Populated after a session ends, linking back to the prediction_snapshot
-- from the pre_session council session. Over 5-10 sessions this enables
-- prompt calibration and compounding intelligence accuracy.
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS module3_prediction_outcomes (
    id                      BIGSERIAL PRIMARY KEY,
    logged_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Link to the pre-session council brief that made the predictions
    council_session_id      BIGINT REFERENCES module3_council_sessions (id) ON DELETE SET NULL,

    -- Venue identification (denormalised for query convenience)
    venue_id                TEXT,
    venue_name              TEXT NOT NULL,
    session_number          INT  NOT NULL,

    -- What the AI predicted (snapshot at brief time)
    prediction_snapshot     JSONB,   -- copied from council session for self-contained rows

    -- What actually happened (filled in by operator/dashboard after session)
    actual_peak_time        TEXT,    -- HH:MM observed
    actual_crowd_energy     TEXT,    -- LOW | MEDIUM | HIGH
    actual_avg_dwell_min    INT,
    actual_table_turns      NUMERIC(4,2),
    actual_primary_segment  TEXT,

    -- Outcome assessment
    accuracy_notes          TEXT,    -- operator free-text: what matched, what didn't
    prediction_accuracy     TEXT,    -- HIGH | MEDIUM | LOW (operator rating)

    -- Raw session KPI summary for deeper analysis
    session_kpi_summary     JSONB    -- {avg_occupancy, peak_occupancy, bar_queue_peak, etc.}
);

CREATE INDEX IF NOT EXISTS idx_m3_outcomes_venue_name
    ON module3_prediction_outcomes (venue_name, session_number);

CREATE INDEX IF NOT EXISTS idx_m3_outcomes_council_session
    ON module3_prediction_outcomes (council_session_id)
    WHERE council_session_id IS NOT NULL;

COMMENT ON TABLE module3_prediction_outcomes IS
    'Actual session outcomes logged against AI pre-session predictions. '
    'This is the M3→M2 feedback loop mechanism: as actuals accumulate, '
    'prediction accuracy can be tracked and prompts calibrated. '
    'Target: 5-10 sessions per venue before prompt adjustment cycle.';

COMMENT ON COLUMN module3_prediction_outcomes.prediction_accuracy IS
    'Operator-rated accuracy: HIGH (>70% of predictions matched actuals), '
    'MEDIUM (40-70%), LOW (<40%). Used to trigger prompt recalibration.';


-- ─────────────────────────────────────────────────────────────────────────────
-- 3. module3_venue_session_index
-- Running session counter per venue. Tracks total sessions run through M3,
-- whether the venue has unlocked history mode (session 3+), and a brief
-- excerpt of the last session synthesis for context in future prompts.
-- Upserted on every brief request (Prefer: resolution=merge-duplicates).
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS module3_venue_session_index (
    id                      BIGSERIAL PRIMARY KEY,
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    first_session_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Venue identification
    venue_id                TEXT UNIQUE,   -- unique constraint for upsert by venue_id
    venue_name              TEXT NOT NULL,

    -- Session tracking
    last_session_number     INT  NOT NULL DEFAULT 1,
    history_mode_unlocked   BOOLEAN NOT NULL DEFAULT FALSE,  -- TRUE when last_session_number >= 3

    -- Last session synthesis excerpt (first 500 chars — for context in next brief)
    last_session_summary    TEXT
);

-- The upsert key — backend uses venue_name for merge-duplicates
CREATE UNIQUE INDEX IF NOT EXISTS idx_m3_session_index_venue_name
    ON module3_venue_session_index (LOWER(venue_name));

COMMENT ON TABLE module3_venue_session_index IS
    'Running session counter and history unlock flag per venue. '
    'Upserted (not inserted) on every Module 3 brief request. '
    'history_mode_unlocked = TRUE when last_session_number >= 3, '
    'which switches the intelligence layer from theory to history mode.';

COMMENT ON COLUMN module3_venue_session_index.history_mode_unlocked IS
    'FALSE for sessions 1-2 (theory mode: research + M2 profile only). '
    'TRUE for session 3+ (history mode: adds prior session summaries and actual outcomes). '
    'This is the mechanism that makes the intelligence compound over time.';
