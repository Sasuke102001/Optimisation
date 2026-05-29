# Module 3 Database Plan

## Purpose

This document defines how the Module 3 database should be structured for:

- baseline venue KPI capture
- engineered show recommendations
- implementation validation
- historical venue learning
- future wiring to Module 2 behavioral intelligence
- future wiring to the Module 3 application and dashboard

This is a production-oriented planning document for Azure PostgreSQL.

It does not simplify the Module 3 architecture.
It preserves:

- venue history
- baseline vs implementation separation
- show-by-show recommendation lineage
- temporal linkage
- provenance
- future ontology linkage
- future contradiction tracking

---

## Core Principle

The top-level anchor should be `venue_id`.

That is correct because:

- venues keep increasing
- all learning is venue-specific over time
- the system must accumulate history per venue
- recommendations must improve as more implementations happen at a given venue

However, `venue_id` should not be the only operational anchor.

The actual working chain is:

`city -> venue -> session/show -> layer 1 observations -> recommendation -> layer 2 observations -> outcomes`

So:

- `venue_id` is the long-term anchor
- `session_id` is the per-show operational anchor

This avoids flattening repeated show history into one venue row.

---

## What The Database Must Support

The database must support three kinds of history for each venue:

1. Baseline natural sessions
- raw venue behavior without engineered intervention
- ideally at least first 5 natural operating days
- may continue later for rolling recalibration

2. Engineered implementation sessions
- pre-show Layer 1 baseline state
- show engineering recommendation
- implementation execution
- Layer 2 validation data
- customer feedback and operational outcomes

3. Longitudinal learning history
- recommendation lineage
- success/failure patterns
- contradiction patterns
- prediction vs reality gaps
- venue-conditioned performance over time

---

## Required Session Types

Every session must have a mode.

Recommended values:

- `baseline`
- `engineered`
- `natural_followup`
- `test`

Meaning:

- `baseline`: natural session before formal engineering program
- `engineered`: session where recommendation/intervention is used
- `natural_followup`: later non-engineered session kept for recalibration
- `test`: dry run, staging, or incomplete data capture

This prevents baseline and implementation data from being mixed carelessly.

---

## Recommended Top-Level Schema Groups

The DB should be organized conceptually into these groups:

1. Geography and venue registry
2. Session registry
3. Raw signal catalog and assignments
4. Raw signal observations
5. Derived metric catalog and observations
6. KPI catalog and assignments
7. Layer 1 KPI observations
8. Recommendation records
9. Layer 2 KPI observations
10. Outcomes and feedback
11. Provenance and audit
12. Amendments and schema evolution

---

## Proposed Core Tables

### 1. `cities`

Purpose:
- store the 4 city groupings
- support future city-level comparison

Fields:
- `id` UUID PK
- `city_code` TEXT UNIQUE NOT NULL
- `city_name` TEXT NOT NULL
- `country_name` TEXT NULL
- `timezone_name` TEXT NULL
- `is_active` BOOLEAN NOT NULL DEFAULT TRUE
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Notes:
- use a short stable code like `mum`, `blr`, etc

---

### 2. `venues`

Purpose:
- master registry for all venues
- primary long-term anchor

Fields:
- `id` UUID PK
- `venue_code` TEXT UNIQUE NOT NULL
- `venue_name` TEXT NOT NULL
- `city_id` UUID NOT NULL FK -> `cities.id`
- `external_source_id` TEXT NULL
- `venue_type` TEXT NULL
- `capacity_estimate` INTEGER NULL
- `address_line` TEXT NULL
- `locality` TEXT NULL
- `state_region` TEXT NULL
- `country_name` TEXT NULL
- `is_active` BOOLEAN NOT NULL DEFAULT TRUE
- `opened_for_program_at` TIMESTAMPTZ NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Notes:
- `venue_code` should be a human-stable operational identifier
- use `id` as the real relational anchor, not name

---

### 3. `venue_zone_templates`

Purpose:
- define zone labels that can be reused across venues

Fields:
- `id` UUID PK
- `zone_template_code` TEXT UNIQUE NOT NULL
- `display_name` TEXT NOT NULL
- `description` TEXT NULL
- `zone_category` TEXT NOT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Example categories:
- `entrance`
- `queue`
- `bar`
- `dancefloor`
- `circulation`
- `exit`
- `quiet_zone`
- `seating`

---

### 4. `venue_zones`

Purpose:
- define the real zones for a given venue
- support different venue layouts

Fields:
- `id` UUID PK
- `venue_id` UUID NOT NULL FK -> `venues.id`
- `zone_template_id` UUID NULL FK -> `venue_zone_templates.id`
- `zone_code` TEXT NOT NULL
- `display_name` TEXT NOT NULL
- `zone_order` INTEGER NOT NULL DEFAULT 0
- `is_active` BOOLEAN NOT NULL DEFAULT TRUE
- `notes` TEXT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Constraints:
- UNIQUE (`venue_id`, `zone_code`)

Important:
- a venue may add or rename zones later
- this must be configurable, not hardcoded

---

### 4a. `venue_tables`

Purpose:
- define the physical table layout for a venue, configured once
- each table has a fixed capacity and zone assignment
- this is the master registry that the floor logging UI reads from

Fields:
- `id` UUID PK
- `venue_id` UUID NOT NULL FK -> `venues.id`
- `zone_id` UUID NULL FK -> `venue_zones.id`
- `table_number` INTEGER NOT NULL
- `table_code` TEXT NOT NULL
- `display_label` TEXT NOT NULL
- `capacity` INTEGER NOT NULL
- `table_shape` TEXT NULL
- `position_x` NUMERIC NULL
- `position_y` NUMERIC NULL
- `is_active` BOOLEAN NOT NULL DEFAULT TRUE
- `notes` TEXT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Constraints:
- UNIQUE (`venue_id`, `table_number`)
- UNIQUE (`venue_id`, `table_code`)

Recommended `table_shape` values:
- `round`
- `square`
- `rectangular`
- `bar_seat`
- `booth`

Notes:
- `table_code` is the operator-facing label, e.g., `T1`, `T7`, `BAR-3`
- `capacity` is the max seating for that table, not the observed headcount
- `position_x` and `position_y` are optional grid coordinates for future visual floor map rendering
- a venue with 30 tables (some 2-tops, some 4-tops, some 6-tops) simply has 30 rows here
- this is configured once at venue onboarding and rarely changes

---

### 5. `session_types`

Purpose:
- normalized event/session type reference

Fields:
- `id` UUID PK
- `session_type_code` TEXT UNIQUE NOT NULL
- `display_name` TEXT NOT NULL
- `description` TEXT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Examples:
- `baseline_night`
- `club_show`
- `live_music`
- `special_event`
- `private_event`
- `weekday_service`

---

### 6. `venue_sessions`

Purpose:
- one row per operating session / show / implementation day
- primary operational anchor

Fields:
- `id` UUID PK
- `venue_id` UUID NOT NULL FK -> `venues.id`
- `city_id` UUID NOT NULL FK -> `cities.id`
- `session_type_id` UUID NULL FK -> `session_types.id`
- `session_mode` TEXT NOT NULL
- `session_number_for_venue` INTEGER NOT NULL
- `session_name` TEXT NOT NULL
- `session_date` DATE NOT NULL
- `started_at` TIMESTAMPTZ NULL
- `ended_at` TIMESTAMPTZ NULL
- `operator_name` TEXT NULL
- `operator_user_id` TEXT NULL
- `event_phase_profile` TEXT NULL
- `expected_crowd_profile` TEXT NULL
- `staffing_summary` TEXT NULL
- `notes` TEXT NULL
- `status` TEXT NOT NULL DEFAULT 'open'
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Constraints:
- UNIQUE (`venue_id`, `session_number_for_venue`)

Why this matters:
- lets the venue build ordered learning over time
- avoids relying on date alone

Recommended `session_mode` values:
- `baseline`
- `engineered`
- `natural_followup`
- `test`

Recommended `status` values:
- `open`
- `closed`
- `validated`
- `archived`

---

## Raw Signal Layer

### 7. `signal_families`

Purpose:
- group raw measurable inputs by family
- distinguish operational facts from KPIs

Fields:
- `id` UUID PK
- `family_code` TEXT UNIQUE NOT NULL
- `display_name` TEXT NOT NULL
- `description` TEXT NULL

Recommended families:
- `flow_counts`
- `table_activity`
- `service_events`
- `complaints_incidents`
- `environmental_readings`
- `occupancy`
- `behavioral_counts`

---

### 8. `signal_definitions`

Purpose:
- define raw measurable inputs that must be logged
- support manual, sensor, POS, ticketing, counter, and derived source capture later

Fields:
- `id` UUID PK
- `signal_code` TEXT UNIQUE NOT NULL
- `display_name` TEXT NOT NULL
- `signal_family_id` UUID NOT NULL FK -> `signal_families.id`
- `description` TEXT NOT NULL
- `unit` TEXT NULL
- `value_type` TEXT NOT NULL
- `capture_mode` TEXT NOT NULL
- `supports_manual_entry` BOOLEAN NOT NULL DEFAULT TRUE
- `supports_system_entry` BOOLEAN NOT NULL DEFAULT TRUE
- `is_active` BOOLEAN NOT NULL DEFAULT TRUE
- `definition_version` INTEGER NOT NULL DEFAULT 1
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Recommended `value_type` values:
- `count`
- `numeric`
- `duration`
- `boolean`
- `text`

Recommended `capture_mode` values:
- `manual`
- `system`
- `hybrid`

Examples:
- `entry_count`
- `exit_count`
- `queue_count`
- `occupied_tables`
- `people_seated_count`
- `orders_created`
- `orders_completed`
- `complaint_count`
- `sound_level_db`
- `temperature_c`
- `co2_ppm`
- `quiet_zone_guest_count`

---

### 9. `signal_zone_assignments`

Purpose:
- assign raw signals to specific zones per venue
- support venue-specific tracking without redesign

Fields:
- `id` UUID PK
- `venue_id` UUID NOT NULL FK -> `venues.id`
- `zone_id` UUID NOT NULL FK -> `venue_zones.id`
- `signal_definition_id` UUID NOT NULL FK -> `signal_definitions.id`
- `display_order` INTEGER NOT NULL DEFAULT 0
- `is_required` BOOLEAN NOT NULL DEFAULT FALSE
- `is_active` BOOLEAN NOT NULL DEFAULT TRUE
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Constraints:
- UNIQUE (`zone_id`, `signal_definition_id`)

---

### 10. `raw_signal_observations`

Purpose:
- log raw measurable inputs directly against venue, session, and zone
- serve as the factual substrate for derived metrics and top-layer KPIs

Fields:
- `id` UUID PK
- `venue_id` UUID NOT NULL FK -> `venues.id`
- `session_id` UUID NOT NULL FK -> `venue_sessions.id`
- `zone_id` UUID NULL FK -> `venue_zones.id`
- `signal_definition_id` UUID NOT NULL FK -> `signal_definitions.id`
- `observed_at` TIMESTAMPTZ NOT NULL
- `source_type` TEXT NOT NULL
- `numeric_value` NUMERIC NULL
- `count_value` INTEGER NULL
- `text_value` TEXT NULL
- `boolean_value` BOOLEAN NULL
- `operator_name` TEXT NULL
- `operator_user_id` TEXT NULL
- `confidence_score` NUMERIC NULL
- `capture_method` TEXT NULL
- `note` TEXT NULL
- `definition_version` INTEGER NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Recommended `source_type` values:
- `manual`
- `counter`
- `ticketing`
- `pos`
- `environment_sensor`
- `camera`
- `derived_import`

Important:
- this is where counts like `people entering/exiting` and `people per table` belong
- these are not top-layer KPI cards by default, but they must be stored

---

## Derived Metric Layer

### 11. `derived_metric_families`

Purpose:
- group computed metrics that sit between raw signals and KPIs

Fields:
- `id` UUID PK
- `family_code` TEXT UNIQUE NOT NULL
- `display_name` TEXT NOT NULL
- `description` TEXT NULL

Examples:
- `flow_metrics`
- `service_metrics`
- `table_metrics`
- `environment_metrics`
- `complaint_metrics`
- `composite_metrics`

---

### 12. `derived_metric_definitions`

Purpose:
- define computed metrics derived from raw signals

Fields:
- `id` UUID PK
- `metric_code` TEXT UNIQUE NOT NULL
- `display_name` TEXT NOT NULL
- `metric_family_id` UUID NOT NULL FK -> `derived_metric_families.id`
- `description` TEXT NOT NULL
- `unit` TEXT NULL
- `formula_description` TEXT NOT NULL
- `calculation_mode` TEXT NOT NULL
- `is_active` BOOLEAN NOT NULL DEFAULT TRUE
- `definition_version` INTEGER NOT NULL DEFAULT 1
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Recommended `calculation_mode` values:
- `system`
- `hybrid`

Examples:
- `ingress_rate_per_5_min`
- `egress_rate_per_5_min`
- `net_occupancy_change`
- `queue_growth_rate`
- `table_occupancy_ratio`
- `avg_people_per_occupied_table`
- `service_throughput`
- `complaint_rate_per_100_guests`
- `density_estimate`
- `fatigue_risk_composite`

---

### 13. `derived_metric_inputs`

Purpose:
- define which raw signals feed which derived metrics

Fields:
- `id` UUID PK
- `derived_metric_definition_id` UUID NOT NULL FK -> `derived_metric_definitions.id`
- `signal_definition_id` UUID NOT NULL FK -> `signal_definitions.id`
- `input_role` TEXT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Example:
- `net_occupancy_change` depends on `entry_count` and `exit_count`

---

### 14. `derived_metric_observations`

Purpose:
- store calculated metric values by session, zone, and time

Fields:
- `id` UUID PK
- `venue_id` UUID NOT NULL FK -> `venues.id`
- `session_id` UUID NOT NULL FK -> `venue_sessions.id`
- `zone_id` UUID NULL FK -> `venue_zones.id`
- `derived_metric_definition_id` UUID NOT NULL FK -> `derived_metric_definitions.id`
- `observed_at` TIMESTAMPTZ NOT NULL
- `numeric_value` NUMERIC NULL
- `text_value` TEXT NULL
- `calculation_version` TEXT NULL
- `source_type` TEXT NOT NULL DEFAULT 'derived'
- `confidence_score` NUMERIC NULL
- `note` TEXT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Important:
- these are not top-layer KPIs either
- they are supporting metrics used to explain KPI state

---

## KPI Catalog Layer

### 15. `kpi_families`

Purpose:
- group KPIs by family for UI and analytics

Fields:
- `id` UUID PK
- `family_code` TEXT UNIQUE NOT NULL
- `display_name` TEXT NOT NULL
- `description` TEXT NULL

Recommended families:
- `flow`
- `service`
- `engagement`
- `overload_recovery`
- `complaints_risk`
- `commercial`
- `environment`

---

### 16. `kpi_definitions`

Purpose:
- canonical definition of each KPI
- supports broad coverage without redesigning the app
- sits above raw signals and derived metrics

Fields:
- `id` UUID PK
- `kpi_code` TEXT UNIQUE NOT NULL
- `display_name` TEXT NOT NULL
- `family_id` UUID NOT NULL FK -> `kpi_families.id`
- `description` TEXT NOT NULL
- `operator_friendly_description` TEXT NULL
- `measurement_mode` TEXT NOT NULL
- `score_type` TEXT NOT NULL
- `default_update_interval_minutes` INTEGER NULL
- `supports_manual_entry` BOOLEAN NOT NULL DEFAULT TRUE
- `supports_system_entry` BOOLEAN NOT NULL DEFAULT TRUE
- `is_active` BOOLEAN NOT NULL DEFAULT TRUE
- `definition_version` INTEGER NOT NULL DEFAULT 1
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Recommended `measurement_mode` values:
- `manual`
- `system`
- `hybrid`

Recommended `score_type` values:
- `rag`
- `numeric`
- `count`
- `duration`
- `composite`
- `rag_numeric`

Examples:
- `crowd_density_comfort`
- `queue_pressure`
- `service_speed`
- `engagement_level`
- `fatigue_overload_signals`
- `commercial_momentum`

---

### 17. `kpi_signal_mappings`

Purpose:
- map KPIs to the raw signals and derived metrics that support them

Fields:
- `id` UUID PK
- `kpi_definition_id` UUID NOT NULL FK -> `kpi_definitions.id`
- `signal_definition_id` UUID NULL FK -> `signal_definitions.id`
- `derived_metric_definition_id` UUID NULL FK -> `derived_metric_definitions.id`
- `mapping_role` TEXT NOT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Recommended `mapping_role` values:
- `primary_input`
- `supporting_input`
- `diagnostic_input`

Reason:
- preserves evidence lineage beneath each KPI

---

### 18. `kpi_zone_assignments`

Purpose:
- assign KPIs to specific zones per venue
- keeps the UI configurable

Fields:
- `id` UUID PK
- `venue_id` UUID NOT NULL FK -> `venues.id`
- `zone_id` UUID NOT NULL FK -> `venue_zones.id`
- `kpi_definition_id` UUID NOT NULL FK -> `kpi_definitions.id`
- `display_order` INTEGER NOT NULL DEFAULT 0
- `is_required` BOOLEAN NOT NULL DEFAULT FALSE
- `is_primary_card` BOOLEAN NOT NULL DEFAULT TRUE
- `is_active` BOOLEAN NOT NULL DEFAULT TRUE
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Constraints:
- UNIQUE (`zone_id`, `kpi_definition_id`)

Why this matters:
- different venues may expose different KPI sets by zone

---

## Layer 1 Observation Layer

### 19. `layer1_kpi_observations`

Purpose:
- store baseline / raw venue KPI observations

Fields:
- `id` UUID PK
- `venue_id` UUID NOT NULL FK -> `venues.id`
- `session_id` UUID NOT NULL FK -> `venue_sessions.id`
- `zone_id` UUID NOT NULL FK -> `venue_zones.id`
- `kpi_definition_id` UUID NOT NULL FK -> `kpi_definitions.id`
- `observed_at` TIMESTAMPTZ NOT NULL
- `source_type` TEXT NOT NULL
- `rag_status` TEXT NULL
- `numeric_value` NUMERIC NULL
- `value_band` TEXT NULL
- `note` TEXT NULL
- `operator_name` TEXT NULL
- `operator_user_id` TEXT NULL
- `event_phase` TEXT NULL
- `confidence_score` NUMERIC NULL
- `ontology_snapshot_version` TEXT NULL
- `kpi_definition_version` INTEGER NULL
- `capture_method` TEXT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Recommended `source_type` values:
- `manual`
- `pos`
- `ticketing`
- `environment_sensor`
- `counter`
- `derived`

Recommended `rag_status` values:
- `green`
- `amber`
- `red`

Important:
- this table must support both manual and automated inputs
- it is the raw baseline layer

---

### 20. `layer1_observation_context`

Purpose:
- attach structured detail without bloating the main observation row

Fields:
- `id` UUID PK
- `observation_id` UUID NOT NULL FK -> `layer1_kpi_observations.id`
- `context_key` TEXT NOT NULL
- `context_value` TEXT NOT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Examples:
- `crowd_profile = high_energy_young`
- `weather = rain`
- `special_condition = delayed_headliner`
- `phase = pre-peak`

Why:
- keeps the main observation table fast
- allows rich context later

---

### 21. `session_incident_logs`

Purpose:
- track complaints, welfare issues, friction, and non-KPI event logs

Fields:
- `id` UUID PK
- `venue_id` UUID NOT NULL FK -> `venues.id`
- `session_id` UUID NOT NULL FK -> `venue_sessions.id`
- `zone_id` UUID NULL FK -> `venue_zones.id`
- `logged_at` TIMESTAMPTZ NOT NULL
- `incident_type` TEXT NOT NULL
- `severity` TEXT NULL
- `description` TEXT NOT NULL
- `operator_name` TEXT NULL
- `source_type` TEXT NOT NULL DEFAULT 'manual'
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Examples:
- complaint
- safety
- queue_spillback
- welfare
- service_issue
- overload_signal

---

## Floor Logging Layer

These two tables are the primary data capture layer for the operator logging tool.
They sit at the same level as raw signal observations but carry structured, purpose-built schemas
that the logging UI writes to directly.

---

### 21a. `door_flow_intervals`

Purpose:
- store entry and exit counts per time interval as logged by the floor operator
- each row represents one submitted interval (e.g., every 15 or 30 minutes)
- this is the primary signal for crowd flow, ingress rate, and net occupancy change

Fields:
- `id` UUID PK
- `venue_id` UUID NOT NULL FK -> `venues.id`
- `session_id` UUID NOT NULL FK -> `venue_sessions.id`
- `interval_start` TIMESTAMPTZ NOT NULL
- `interval_end` TIMESTAMPTZ NOT NULL
- `interval_minutes` INTEGER NOT NULL
- `entry_count` INTEGER NOT NULL DEFAULT 0
- `exit_count` INTEGER NOT NULL DEFAULT 0
- `net_flow` INTEGER NOT NULL GENERATED ALWAYS AS (entry_count - exit_count) STORED
- `cumulative_entries_session` INTEGER NULL
- `cumulative_exits_session` INTEGER NULL
- `event_phase` TEXT NULL
- `operator_name` TEXT NULL
- `note` TEXT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Recommended `interval_minutes` values:
- `15`
- `30`

Notes:
- one row per submitted interval, not one row per person
- operator taps + for each entry and + for each exit during the interval, then hits Submit
- `cumulative_entries_session` and `cumulative_exits_session` are optional running totals the app can compute and store for fast session-level queries
- this replaces using two separate `raw_signal_observations` rows (one for entry_count, one for exit_count) for the door flow use case

---

### 21b. `table_session_observations`

Purpose:
- store the state of each physical table across a session
- captures when a table was seated, who was there, how long they stayed, and what segment they appeared to be
- this is the primary source of dwell time, segment distribution, and table utilization data
- feeds directly into Module 2 customer segment refinement over time

Fields:
- `id` UUID PK
- `venue_id` UUID NOT NULL FK -> `venues.id`
- `session_id` UUID NOT NULL FK -> `venue_sessions.id`
- `table_id` UUID NOT NULL FK -> `venue_tables.id`
- `observation_sequence` INTEGER NOT NULL
- `event_type` TEXT NOT NULL
- `people_count` INTEGER NULL
- `segment_primary` TEXT NULL
- `segment_secondary` TEXT NULL
- `segment_note` TEXT NULL
- `seated_at` TIMESTAMPTZ NULL
- `cleared_at` TIMESTAMPTZ NULL
- `dwell_duration_minutes` INTEGER NULL
- `spend_observed` BOOLEAN NULL
- `operator_name` TEXT NULL
- `note` TEXT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Recommended `event_type` values:
- `seated` — table newly occupied, headcount and segment set
- `updated` — headcount or segment revised mid-seating (e.g., more people joined)
- `cleared` — table vacated, dwell time recorded

Recommended `segment_primary` values:
- `couple`
- `social_group`
- `family`
- `college`
- `corporate`
- `solo`
- `mixed`
- `unknown`

Notes:
- `observation_sequence` orders events within a session (1, 2, 3...) for a given table
- `dwell_duration_minutes` is computed when `cleared` event is logged: `cleared_at - seated_at`
- `segment_secondary` is optional — for tables where two segments are clearly present (e.g., family + couple sharing a large table)
- `spend_observed` is a simple boolean flag: did the operator notice this table ordering, yes/no
- this data, accumulated across baseline sessions, becomes ground-truth customer segment observation data that feeds back into Module 2 segmentation — directly observed rather than inferred from reviews

Indices to add:
- `table_session_observations(session_id, table_id, observation_sequence)`
- `table_session_observations(venue_id, segment_primary, seated_at)`
- `door_flow_intervals(session_id, interval_start)`
- `door_flow_intervals(venue_id, interval_start)`
- `venue_tables(venue_id, is_active)`

---

## Recommendation Layer

### 22. `show_engineering_recommendations`

Purpose:
- one recommendation record per engineered session
- sits between Layer 1 and Layer 2

Fields:
- `id` UUID PK
- `venue_id` UUID NOT NULL FK -> `venues.id`
- `session_id` UUID NOT NULL FK -> `venue_sessions.id`
- `recommendation_version` INTEGER NOT NULL DEFAULT 1
- `recommendation_title` TEXT NOT NULL
- `summary` TEXT NOT NULL
- `recommendation_status` TEXT NOT NULL DEFAULT 'draft'
- `generated_from_module2` BOOLEAN NOT NULL DEFAULT FALSE
- `generated_from_layer1_history` BOOLEAN NOT NULL DEFAULT TRUE
- `generated_from_layer2_history` BOOLEAN NOT NULL DEFAULT TRUE
- `authoring_mode` TEXT NOT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Recommended `authoring_mode` values:
- `manual`
- `assisted`
- `system_generated`

Recommended `recommendation_status` values:
- `draft`
- `approved`
- `implemented`
- `superseded`

Constraint:
- UNIQUE (`session_id`)

Reason:
- one show/session should have one primary recommendation package

---

### 23. `recommendation_components`

Purpose:
- structured components of a recommendation
- keeps recommendation details queryable

Fields:
- `id` UUID PK
- `recommendation_id` UUID NOT NULL FK -> `show_engineering_recommendations.id`
- `component_type` TEXT NOT NULL
- `title` TEXT NOT NULL
- `description` TEXT NOT NULL
- `zone_id` UUID NULL FK -> `venue_zones.id`
- `sequence_order` INTEGER NOT NULL DEFAULT 0
- `expected_effect` TEXT NULL
- `risk_note` TEXT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Examples of `component_type`:
- pacing
- sound
- sequencing
- staff_action
- entry_control
- environment_adjustment
- crowd_flow_adjustment

---

## Layer 2 Observation Layer

### 24. `layer2_kpi_observations`

Purpose:
- store implementation / validation KPI data during engineered session

Fields:
- `id` UUID PK
- `venue_id` UUID NOT NULL FK -> `venues.id`
- `session_id` UUID NOT NULL FK -> `venue_sessions.id`
- `recommendation_id` UUID NOT NULL FK -> `show_engineering_recommendations.id`
- `zone_id` UUID NOT NULL FK -> `venue_zones.id`
- `kpi_definition_id` UUID NOT NULL FK -> `kpi_definitions.id`
- `observed_at` TIMESTAMPTZ NOT NULL
- `source_type` TEXT NOT NULL
- `rag_status` TEXT NULL
- `numeric_value` NUMERIC NULL
- `value_band` TEXT NULL
- `note` TEXT NULL
- `operator_name` TEXT NULL
- `operator_user_id` TEXT NULL
- `event_phase` TEXT NULL
- `confidence_score` NUMERIC NULL
- `capture_method` TEXT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Important:
- structure is similar to Layer 1
- but explicitly tied to recommendation/session implementation

---

## Outcomes, Validation, and Feedback

### 25. `validation_outcomes`

Purpose:
- summarize whether recommendation worked and how reality differed

Fields:
- `id` UUID PK
- `venue_id` UUID NOT NULL FK -> `venues.id`
- `session_id` UUID NOT NULL FK -> `venue_sessions.id`
- `recommendation_id` UUID NOT NULL FK -> `show_engineering_recommendations.id`
- `outcome_status` TEXT NOT NULL
- `summary` TEXT NOT NULL
- `prediction_vs_reality_gap` TEXT NULL
- `contradiction_note` TEXT NULL
- `success_factors` TEXT NULL
- `failure_factors` TEXT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Recommended `outcome_status` values:
- `successful`
- `partially_successful`
- `mixed`
- `unsuccessful`
- `inconclusive`

---

### 26. `session_feedback`

Purpose:
- store live customer feedback or staff-interpreted feedback entries

Fields:
- `id` UUID PK
- `venue_id` UUID NOT NULL FK -> `venues.id`
- `session_id` UUID NOT NULL FK -> `venue_sessions.id`
- `recommendation_id` UUID NULL FK -> `show_engineering_recommendations.id`
- `zone_id` UUID NULL FK -> `venue_zones.id`
- `recorded_at` TIMESTAMPTZ NOT NULL
- `feedback_type` TEXT NOT NULL
- `feedback_value` TEXT NULL
- `note` TEXT NULL
- `source_type` TEXT NOT NULL
- `operator_name` TEXT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Examples:
- emotional_resonance
- overstimulation
- comfort
- intent_to_stay
- intent_to_order

---

## Provenance, Audit, and Amendments

### 27. `audit_events`

Purpose:
- application-level audit trail for changes

Fields:
- `id` UUID PK
- `entity_type` TEXT NOT NULL
- `entity_id` UUID NOT NULL
- `event_type` TEXT NOT NULL
- `actor_name` TEXT NULL
- `actor_user_id` TEXT NULL
- `event_payload` JSONB NULL
- `recorded_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Examples:
- created
- updated
- deleted
- status_changed
- recommendation_approved
- observation_corrected

Why:
- do not rely only on `updated_at`

---

### 28. `schema_amendments`

Purpose:
- explicitly track business/schema amendments over time
- important because venues, KPIs, zones, and operating assumptions will keep increasing

Fields:
- `id` UUID PK
- `amendment_code` TEXT UNIQUE NOT NULL
- `amendment_title` TEXT NOT NULL
- `amendment_type` TEXT NOT NULL
- `description` TEXT NOT NULL
- `applies_to_table` TEXT NULL
- `schema_version_from` TEXT NULL
- `schema_version_to` TEXT NULL
- `effective_from` TIMESTAMPTZ NULL
- `status` TEXT NOT NULL DEFAULT 'planned'
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT now()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()

Recommended `amendment_type` values:
- schema
- data_model
- kpi_catalog
- zone_model
- recommendation_model
- audit_model

Recommended `status` values:
- planned
- approved
- applied
- retired

Reason:
- the system will evolve
- this gives a clean governance mechanism instead of ad-hoc schema drift

---

## Important Design Rules

### Rule 1: Never flatten repeated shows into venue columns

Bad:
- one venue row with repeated show1/show2/show3 fields

Correct:
- one `venue`
- many `venue_sessions`
- many observations and recommendations attached to sessions

---

### Rule 2: Keep Layer 1 and Layer 2 separate

They should not be merged into one table.

Why:
- baseline state and implementation validation are not the same thing
- future analytics will need this distinction clearly

---

### Rule 3: Use `venue_id` as the long-term anchor

This is non-negotiable.

As venues increase:
- all historical learning must still group cleanly by venue
- city grouping remains easy
- venue-specific recommendation improvement remains queryable

---

### Rule 4: Use `session_id` as the per-show anchor

This is how you preserve:
- ordering over time
- recommendation lineage
- show-by-show improvement
- correlation between Layer 1, recommendation, and Layer 2

---

### Rule 5: Treat recommendation as a first-class object

Do not store recommendation text only inside notes.

It needs its own table because:
- it is a decision artifact
- it will be compared over time
- it will later be generated using Module 2 + historical KPI data

---

### Rule 6: Build for manual now, system sources later

All raw signal, derived metric, and KPI observation tables must support:
- manual entry
- automated system inputs
- hybrid inputs

This prevents redesign when the dashboard later ingests sensors or operational feeds.

---

### Rule 7: Raw signals must be logged separately from KPIs

Examples:
- `entry_count`
- `exit_count`
- `occupied_tables`
- `people_seated_count`
- `queue_count`

These must be logged as raw signals, not flattened into KPI fields.

KPIs are the operator-facing interpretation layer.

---

### Rule 8: Derived metrics must be persisted when they matter operationally

Examples:
- ingress rate
- egress rate
- net occupancy change
- queue growth rate
- table occupancy ratio

These should not be recomputed ad hoc only in the UI.

Persisting them improves:
- auditability
- recommendation traceability
- historical learning
- contradiction analysis

---

## Suggested Indices

At minimum:

- `venues(city_id)`
- `venue_zones(venue_id, is_active)`
- `venue_sessions(venue_id, session_number_for_venue)`
- `venue_sessions(venue_id, session_date)`
- `raw_signal_observations(session_id, zone_id, observed_at)`
- `raw_signal_observations(venue_id, signal_definition_id, observed_at)`
- `derived_metric_observations(session_id, zone_id, observed_at)`
- `derived_metric_observations(venue_id, derived_metric_definition_id, observed_at)`
- `layer1_kpi_observations(session_id, zone_id, observed_at)`
- `layer1_kpi_observations(venue_id, kpi_definition_id, observed_at)`
- `layer2_kpi_observations(session_id, zone_id, observed_at)`
- `show_engineering_recommendations(session_id)`
- `validation_outcomes(session_id)`
- `audit_events(entity_type, entity_id, recorded_at)`

If using JSONB fields later, add GIN indexes selectively.

---

## Recommended ID Strategy

Use UUID primary keys throughout.

Also keep business-facing codes where useful:

- `city_code`
- `venue_code`
- `zone_code`
- `kpi_code`
- `session_type_code`
- `amendment_code`

This gives:
- stable technical IDs
- readable operational identifiers

---

## Suggested Versioning Strategy

At minimum version:

- KPI definitions
- ontology snapshot
- recommendation version
- schema amendment version

Later, also version:

- threshold profiles
- zone layouts
- recommendation templates

This matters because:
- venue operations change
- KPI wording changes
- dashboard logic changes
- recommendation logic evolves

Historical records must still remain interpretable.

---

## Recommended Rollout Sequence

### Phase 1: Foundation

Build first:

1. `cities`
2. `venues`
3. `venue_zone_templates`
4. `venue_zones`
5. `session_types`
6. `venue_sessions`
7. `signal_families`
8. `signal_definitions`
9. `signal_zone_assignments`
10. `raw_signal_observations`
11. `derived_metric_families`
12. `derived_metric_definitions`
13. `derived_metric_inputs`
14. `derived_metric_observations`
15. `kpi_families`
16. `kpi_definitions`
17. `kpi_signal_mappings`
18. `kpi_zone_assignments`
19. `layer1_kpi_observations`
20. `session_incident_logs`
21. `venue_tables`
22. `door_flow_intervals`
23. `table_session_observations`

Goal:
- make Layer 1 operational
- make the floor logging tool fully functional

---

### Phase 2: Recommendation and Layer 2

Build next:

24. `show_engineering_recommendations`
25. `recommendation_components`
26. `layer2_kpi_observations`
27. `validation_outcomes`
28. `session_feedback`

Goal:
- support engineered shows and validation loops

---

### Phase 3: Governance and durability

Build next:

29. `audit_events`
30. `schema_amendments`

Goal:
- support long-term operational change safely

---

## What The App Should Derive From This Schema

The future dashboard/app should be able to derive:

- available venues by city
- zones by venue
- table layout for a venue (from `venue_tables`)
- active sessions by venue
- door flow totals and interval history for a session (from `door_flow_intervals`)
- current table occupancy state for a session (from `table_session_observations`)
- segment distribution across tables for a session
- average dwell time by segment across baseline sessions
- raw signal capture requirements by zone
- supporting derived metrics by zone
- KPI cards by zone
- latest Layer 1 state for a session
- recommendation attached to a show
- Layer 2 validation records for that show
- historical session chains for the venue
- segment observation history per venue (for Module 2 feedback)

This is why the schema must stay relational and session-based.

---

## Final Recommendation

The Module 3 DB should be designed as:

- `venue-anchored`
- `session-driven`
- `layer-separated`
- `recommendation-aware`
- `future-amendable`

The correct long-term structure is:

`city`
-> `venue`
   -> `venue_tables` (configured once at onboarding)
-> `session`
   -> `door_flow_intervals` (operator-logged entry/exit per interval)
   -> `table_session_observations` (operator-logged per-table state: headcount, segment, dwell)
   -> `raw_signal_observations`
   -> `derived_metric_observations`
   -> `layer1_kpi_observations`
   -> `show_engineering_recommendation`
   -> `layer2_kpi_observations`
   -> `validation_outcomes`

That structure fully supports:

- first 5 natural baseline days
- unlimited implementation sessions afterward
- venue-specific learning
- future Module 2 integration
- future recommendation generation
- future dashboard and PostgreSQL wiring

---

## Next Step

After approval of this plan, the next implementation documents should be:

1. exact PostgreSQL DDL
2. seed data format for cities, venues, zones, signal definitions, derived metrics, KPI definitions
3. DB loader contract
4. app-to-DB API contract
5. recommendation linkage model
