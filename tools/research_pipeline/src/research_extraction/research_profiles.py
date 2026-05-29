from __future__ import annotations

from pathlib import Path


RESEARCH_SOURCE_PROFILES = {
    # ── Core / root-level research files ─────────────────────────────────────
    "behavioral_state_transitions.md": {
        "source_role": "synthesis",
        "domain_tags": ["state_transitions", "crowd_states", "recovery", "kpis", "interventions"],
        "expected_coverage_tags": ["canonical_states", "canonical_transitions", "transition_kpis", "transition_interventions"],
    },
    "behavioral_neuroscience_mechanisms.md": {
        "source_role": "synthesis",
        "domain_tags": ["mechanisms", "neuroscience", "timing", "recovery", "interventions"],
        "expected_coverage_tags": ["canonical_mechanisms", "temporal_kernels", "mechanism_interventions"],
    },
    "contextual_behavioral_contradictions.md": {
        "source_role": "synthesis",
        "domain_tags": ["contradictions", "context_boundaries", "audience_dependencies", "environmental_dependencies"],
        "expected_coverage_tags": ["contradiction_patterns", "context_reversals"],
    },
    "deep_research_report.md": {
        "source_role": "synthesis",
        "domain_tags": ["crowd_intelligence", "cascade_dynamics", "tipping_points", "coupled_transitions"],
        "expected_coverage_tags": ["crowd_state_variables", "cascade_relations", "coupled_transition_logic"],
    },
    "operational_behavioral_intelligence_nightlife.md": {
        "source_role": "synthesis",
        "domain_tags": ["operations", "causal_chains", "kpis", "interventions", "failure_modes"],
        "expected_coverage_tags": ["operational_chains", "queue_psychology", "closing_sequence", "conflict_pathways"],
    },
    "temporal_behavioral_dynamics.md": {
        "source_role": "synthesis",
        "domain_tags": ["temporal_dynamics", "sequencing", "anticipation", "habituation", "recovery"],
        "expected_coverage_tags": ["temporal_kernels", "peak_end", "recovery_windows", "wave_structures"],
    },
    "operational_measurement_framework.md": {
        "source_role": "synthesis",
        "domain_tags": ["measurement", "kpi_instrumentation", "deployment_tiers", "privacy_constraints", "mvp_stack"],
        "expected_coverage_tags": ["kpi_signal_mappings", "deployment_tiers", "privacy_constraints", "no_go_claims", "mvp_stack"],
    },

    # ── Music implementation files ────────────────────────────────────────────
    "music_behavior_synchronization.md": {
        "source_role": "synthesis",
        "domain_tags": ["music", "behavioral_sync", "entrainment", "tempo", "crowd_response"],
        "expected_coverage_tags": ["music_state_coupling", "tempo_interventions", "synchronization_mechanisms"],
    },
    "operational_economics_auditory_environments.md": {
        "source_role": "synthesis",
        "domain_tags": ["music", "economics", "spend_uplift", "dwell_time", "operational_levers"],
        "expected_coverage_tags": ["music_revenue_relations", "dwell_spend_dynamics", "auditory_kpis"],
    },
    "auditory_fatigue_sensory_load.md": {
        "source_role": "synthesis",
        "domain_tags": ["auditory_fatigue", "sensory_load", "long_duration", "recovery", "thresholds"],
        "expected_coverage_tags": ["fatigue_thresholds", "recovery_windows", "sensory_overload_states"],
    },
    "crowd_state_estimation.md": {
        "source_role": "synthesis",
        "domain_tags": ["crowd_states", "estimation", "proxy_signals", "observable_indicators", "measurement"],
        "expected_coverage_tags": ["crowd_state_variables", "proxy_signal_mappings", "estimation_heuristics"],
    },
    "frequency_claims_validity_review.md": {
        "source_role": "review",
        "domain_tags": ["frequency", "scientific_validity", "evidence_quality", "claim_review"],
        "expected_coverage_tags": ["validated_claims", "contested_claims", "evidence_grades"],
    },
    "computational_audio_features.md": {
        "source_role": "synthesis",
        "domain_tags": ["audio_features", "computational", "behavioral_intelligence", "signal_processing"],
        "expected_coverage_tags": ["audio_feature_variables", "behavioral_signal_mappings", "feature_extraction_methods"],
    },
    "psychoacoustic_foundations.md": {
        "source_role": "synthesis",
        "domain_tags": ["psychoacoustics", "perception", "loudness", "frequency_response", "behavioral_effects"],
        "expected_coverage_tags": ["psychoacoustic_mechanisms", "perception_thresholds", "frequency_behavior_relations"],
    },

    # ── Behavioural research files ────────────────────────────────────────────
    "behavioral_sequencing_emotional_pacing.md": {
        "source_role": "synthesis",
        "domain_tags": ["behavioral_sequencing", "emotional_pacing", "arc_design", "hospitality", "live_events"],
        "expected_coverage_tags": ["sequence_patterns", "emotional_arc_logic", "pacing_interventions"],
    },
    "cultural_demographic_effects.md": {
        "source_role": "synthesis",
        "domain_tags": ["culture", "demographics", "behavioral_modifiers", "segment_effects", "hospitality"],
        "expected_coverage_tags": ["demographic_modifiers", "cultural_context_factors", "segment_behavioral_profiles"],
    },
    "emotional_memory_loyalty_mechanisms.md": {
        "source_role": "synthesis",
        "domain_tags": ["emotional_memory", "loyalty", "peak_end", "retention", "experiential_encoding"],
        "expected_coverage_tags": ["memory_encoding_mechanisms", "loyalty_drivers", "peak_end_relations"],
    },
    "environmental_operational_factors.md": {
        "source_role": "synthesis",
        "domain_tags": ["environment", "operations", "physical_factors", "temperature", "lighting", "density"],
        "expected_coverage_tags": ["environmental_variables", "operational_levers", "environmental_state_relations"],
    },
    "hospitality_spending_behavioral_triggers.md": {
        "source_role": "synthesis",
        "domain_tags": ["spending", "behavioral_triggers", "hospitality", "revenue", "purchase_drivers"],
        "expected_coverage_tags": ["spend_triggers", "purchase_behavior_relations", "revenue_kpis"],
    },
    "identity_signaling_social_status.md": {
        "source_role": "synthesis",
        "domain_tags": ["identity", "social_status", "signaling", "group_dynamics", "prestige"],
        "expected_coverage_tags": ["social_status_mechanisms", "identity_signaling_patterns", "group_behavior_relations"],
    },
    "operational_music_mechanisms.md": {
        "source_role": "synthesis",
        "domain_tags": ["music", "operations", "mechanisms", "hospitality", "volume", "tempo", "genre"],
        "expected_coverage_tags": ["music_operational_levers", "music_behavior_mechanisms", "dj_interventions"],
    },
    "social_sharing_virality_amplification.md": {
        "source_role": "synthesis",
        "domain_tags": ["social_sharing", "virality", "amplification", "hospitality", "live_events", "ug_content"],
        "expected_coverage_tags": ["sharing_trigger_mechanisms", "virality_conditions", "amplification_interventions"],
    },
    "behavioral_intervention_attention_mechanisms.md": {
        "source_role": "synthesis",
        "domain_tags": ["interventions", "attention", "mechanisms", "behavioral_design", "cognitive_load"],
        "expected_coverage_tags": ["attention_mechanisms", "intervention_effectiveness", "cognitive_load_factors"],
    },
    "live_behavioral_experimentation_framework.md": {
        "source_role": "synthesis",
        "domain_tags": ["experimentation", "live_testing", "behavioral_measurement", "framework", "methodology"],
        "expected_coverage_tags": ["experiment_design_patterns", "measurement_methodology", "live_testing_constraints"],
    },
}


def get_research_source_profile(relative_file: str) -> dict[str, object]:
    filename = Path(relative_file).name
    profile = RESEARCH_SOURCE_PROFILES.get(filename)
    if profile is None:
        return {
            "source_role": "general",
            "domain_tags": [],
            "expected_coverage_tags": [],
        }
    return {
        "source_role": str(profile["source_role"]),
        "domain_tags": list(profile["domain_tags"]),
        "expected_coverage_tags": list(profile["expected_coverage_tags"]),
    }
