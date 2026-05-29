from __future__ import annotations

import re
from typing import Any

from research_extraction.confidence import build_confidence_profile
from research_extraction.config import PipelineConfig
from research_extraction.ids import build_canonical_id
from research_extraction.registries import load_canonical_states, load_canonical_transitions, match_canonical_mechanism, match_canonical_state, match_canonical_transition
from research_extraction.schemas import BehavioralState, ContradictionObject, EvidenceObject, Intervention, KPI, Relationship, SemanticSection, TemporalDynamic
from research_extraction.utils import bullet_split, extract_minutes, normalize_whitespace, sentence_split


PRIVILEGED_TITLES = {
    "Trigger Conditions",
    "Contextual Modifiers",
    "Timing Dependencies and Escalation Window",
    "Lag Windows and Duration Effects",
    "Escalation Limits",
    "Fatigue / Recovery Characteristics",
    "Measurable Indicators (KPIs)",
    "Operational Interventions",
    "Contradiction Scenarios and State Dependencies",
    "Failure Conditions",
    "Measurement Framework",
    "Core Causal Chains",
}

TRANSITION_RE = re.compile(r"State\s+\d+:\s*(.+?)\s*(?:->|→)\s*(.+)$", re.IGNORECASE)
CONTRADICTION_HEAD_RE = re.compile(r"(.+?):\s*(.+?)\s+vs\.\s+(.+)$", re.IGNORECASE)


def extract_profile_overrides(section: SemanticSection, config: PipelineConfig) -> dict[str, list[Any]]:
    empty = {
        "variables": [],
        "states": [],
        "relationships": [],
        "interventions": [],
        "kpis": [],
        "temporal_dynamics": [],
        "evidence_objects": [],
        "contradiction_objects": [],
    }
    if section.source_role != "synthesis":
        return empty

    filename = section.filename
    if filename == "Behavioral State Transitions in Live Hospitality and Music Environments.md":
        return _state_transition_overrides(section, config)
    if filename == "behavioral_neuroscience_mechanisms.md":
        return _mechanism_overrides(section, config)
    if filename == "Contextual_Behavioral_Contradictions_Hospitality_Nightlife.md":
        return _contradiction_overrides(section, config)
    if filename == "Temporal Behavioral Dynamics and Sequencing Intelligence in Nightlife and Live Music.md":
        return _temporal_overrides(section, config)
    if filename == "operational_behavioral_intelligence_nightlife.md":
        return _operational_overrides(section, config)
    if filename == "deep-research-report (2).md":
        return _crowd_report_overrides(section, config)
    if filename == "Operational measurement framework for an ontology-first behavioral intelligence system.md":
        return _measurement_framework_overrides(section, config)
    return empty


def seed_profile_objects(sections: list[SemanticSection], config: PipelineConfig) -> dict[str, list[Any]]:
    bundle = _blank_bundle()
    source_sections = [section for section in sections if section.filename == "Behavioral State Transitions in Live Hospitality and Music Environments.md"]
    if not source_sections:
        return bundle
    anchor = source_sections[0]
    state_index = _state_transition_index(source_sections)
    for state_id, payload in load_canonical_states().items():
        bundle["states"].append(
            BehavioralState(
                state_id=build_canonical_id("behavioral_state", payload.get("label", state_id)),
                name=payload.get("label", state_id),
                description="Seeded canonical behavioral state from completed state-transition research.",
                observable_signals=[payload.get("label", state_id)],
                entry_conditions=[payload.get("label", state_id)],
                confidence_notes="Seeded canonical state.",
                confidence=build_confidence_profile(0.96, ontology_validity=0.96, operational_relevance=0.86),
                raw_text=anchor.raw_text,
                normalized_text=anchor.normalized_text,
                source_file=anchor.file,
                relative_source_file=anchor.relative_file,
                section_id=anchor.section_id,
                heading_path=anchor.heading_path,
                extractor_version=config.extractor_version,
                extractor_name="seeded_canonical_state_extractor",
                provenance_refs=[anchor.relative_file, "seeded_canonical_state_registry"],
                source_role=anchor.source_role,
                domain_tags=anchor.domain_tags,
                expected_coverage_tags=anchor.expected_coverage_tags,
                canonical_state_id=state_id,
                possible_next_states=state_index.get(state_id, []),
                applicable_contexts=["hospitality_live_environment"],
            )
        )
    for transition_id, payload in load_canonical_transitions().items():
        start_label = _state_label(payload.get("start_state_id", ""))
        end_label = _state_label(payload.get("end_state_id", ""))
        bundle["temporal_dynamics"].append(
            TemporalDynamic(
                dynamic_id=build_canonical_id("temporal_dynamic", transition_id),
                name=payload.get("label", transition_id),
                start_state=start_label,
                start_state_id=payload.get("start_state_id", ""),
                end_state=end_label,
                end_state_id=payload.get("end_state_id", ""),
                trigger_conditions=[],
                estimated_time_window=payload.get("transition_type", "seeded_transition"),
                recovery_characteristics=["seeded_recovery_edge"] if payload.get("recovery_edge") else [],
                transition_logic=payload.get("label", transition_id),
                sequence_dependencies=list(payload.get("allowed_contradiction_hooks", [])),
                state_progression=[start_label, end_label],
                confidence=build_confidence_profile(0.95, ontology_validity=0.95, operational_relevance=0.84),
                raw_text=anchor.raw_text,
                normalized_text=anchor.normalized_text,
                source_file=anchor.file,
                relative_source_file=anchor.relative_file,
                section_id=anchor.section_id,
                heading_path=anchor.heading_path,
                extractor_version=config.extractor_version,
                extractor_name="seeded_canonical_transition_extractor",
                provenance_refs=[anchor.relative_file, "seeded_canonical_transition_registry"],
                source_role=anchor.source_role,
                domain_tags=anchor.domain_tags,
                expected_coverage_tags=anchor.expected_coverage_tags,
                canonical_transition_id=transition_id,
                applicable_contexts=["hospitality_live_environment"],
                environment_dependencies=list(payload.get("allowed_contradiction_hooks", [])),
            )
        )
    return bundle


def _state_transition_overrides(section: SemanticSection, config: PipelineConfig) -> dict[str, list[Any]]:
    bundle = _blank_bundle()
    transition_heading = next((part for part in section.heading_path if TRANSITION_RE.match(part)), "")
    if not transition_heading:
        return bundle
    match = TRANSITION_RE.match(transition_heading)
    if not match:
        return bundle
    start_label = normalize_whitespace(match.group(1))
    end_label = normalize_whitespace(match.group(2))
    start_id, canonical_start = match_canonical_state(start_label)
    end_id, canonical_end = match_canonical_state(end_label)
    transition_id, transition_payload = match_canonical_transition(start_label, end_label)

    for state_label, state_id, canonical_label in (
        (start_label, start_id, canonical_start),
        (end_label, end_id, canonical_end),
    ):
        if not state_id:
            continue
        bundle["states"].append(
            BehavioralState(
                state_id=build_canonical_id("behavioral_state", canonical_label or state_label),
                name=canonical_label or state_label,
                description=f"Canonical state seeded from transition '{transition_heading}'.",
                observable_signals=bullet_split(section.normalized_text)[:3] or sentence_split(section.normalized_text)[:2],
                entry_conditions=bullet_split(section.normalized_text)[:3] or sentence_split(section.normalized_text)[:2],
                exit_conditions=[line for line in bullet_split(section.normalized_text) if any(token in line.lower() for token in ("exit", "leave", "decline"))][:3],
                possible_next_states=[canonical_end] if canonical_label == canonical_start and canonical_end else [],
                transition_triggers=bullet_split(section.normalized_text)[:4] if section.section_title == "Trigger Conditions" else [],
                stability_score=0.7 if canonical_label == canonical_end else 0.55,
                fatigue_characteristics=bullet_split(section.normalized_text)[:3] if "Fatigue" in (canonical_label or "") or "fatigue" in section.normalized_text.lower() else [],
                recovery_characteristics=bullet_split(section.normalized_text)[:3] if "Recovery" in (canonical_label or "") or "recover" in section.normalized_text.lower() else [],
                confidence_notes="Seeded from explicit state transition research structure.",
                confidence=build_confidence_profile(0.91, ontology_validity=0.92, operational_relevance=0.82),
                raw_text=section.raw_text,
                normalized_text=section.normalized_text,
                source_file=section.file,
                relative_source_file=section.relative_file,
                section_id=section.section_id,
                heading_path=section.heading_path,
                extractor_version=config.extractor_version,
                extractor_name="profile_state_transition_extractor",
                provenance_refs=[section.relative_file, transition_heading, section.section_title],
                source_role=section.source_role,
                domain_tags=section.domain_tags,
                expected_coverage_tags=section.expected_coverage_tags,
                canonical_state_id=state_id,
                applicable_contexts=["hospitality_live_environment"],
            )
        )

    if section.section_title in {"Core Description", "Trigger Conditions", "Timing Dependencies and Escalation Window", "Lag Windows and Duration Effects"}:
        bundle["temporal_dynamics"].append(
            TemporalDynamic(
                dynamic_id=build_canonical_id("temporal_dynamic", f"{start_label}_{end_label}_{section.section_title}"),
                name=transition_heading,
                start_state=canonical_start or start_label,
                start_state_id=start_id or "",
                end_state=canonical_end or end_label,
                end_state_id=end_id or "",
                trigger_conditions=bullet_split(section.normalized_text)[:5],
                estimated_time_window=", ".join(str(value) for value in extract_minutes(section.normalized_text)) or section.section_title,
                recovery_characteristics=[line for line in bullet_split(section.normalized_text) if "recover" in line.lower()][:3],
                transition_logic=sentence_split(section.normalized_text)[0][:220] if sentence_split(section.normalized_text) else transition_heading,
                duration_minutes=extract_minutes(section.normalized_text),
                sequence_dependencies=bullet_split(section.normalized_text)[:4],
                state_progression=[canonical_start or start_label, canonical_end or end_label],
                confidence=build_confidence_profile(0.89, ontology_validity=0.9, operational_relevance=0.8),
                raw_text=section.raw_text,
                normalized_text=section.normalized_text,
                source_file=section.file,
                relative_source_file=section.relative_file,
                section_id=section.section_id,
                heading_path=section.heading_path,
                extractor_version=config.extractor_version,
                extractor_name="profile_transition_temporal_extractor",
                provenance_refs=[section.relative_file, transition_heading, section.section_title],
                source_role=section.source_role,
                domain_tags=section.domain_tags,
                expected_coverage_tags=section.expected_coverage_tags,
                canonical_transition_id=transition_id,
                applicable_contexts=["hospitality_live_environment"],
                environment_dependencies=["crowd_density", "sensory_load"],
            )
        )

    if section.section_title == "Measurable Indicators (KPIs)":
        for item in bullet_split(section.normalized_text)[:6]:
            bundle["kpis"].append(
                KPI(
                    kpi_id=build_canonical_id("kpi", item),
                    operator_label=item[:120],
                    technical_definition=f"KPI for transition {transition_heading}.",
                    category="behavioral",
                    human_interpretation=f"Use this KPI to monitor the transition from {start_label} to {end_label}.",
                    complexity_level="medium",
                    confidence=build_confidence_profile(0.88, ontology_validity=0.9, operational_relevance=0.85),
                    raw_text=section.raw_text,
                    normalized_text=section.normalized_text,
                    source_file=section.file,
                    relative_source_file=section.relative_file,
                    section_id=section.section_id,
                    heading_path=section.heading_path,
                    extractor_version=config.extractor_version,
                    extractor_name="profile_transition_kpi_extractor",
                    provenance_refs=[section.relative_file, transition_heading, "kpi"],
                    source_role=section.source_role,
                    domain_tags=section.domain_tags,
                    expected_coverage_tags=section.expected_coverage_tags,
                    applicable_contexts=["transition_monitoring"],
                )
            )

    if section.section_title == "Operational Interventions":
        for item in _list_like_candidates(section.normalized_text)[:6]:
            action_text = _intervention_text(item)
            bundle["interventions"].append(
                Intervention(
                    intervention_id=build_canonical_id("intervention", action_text),
                    name=action_text[:160],
                    trigger_conditions=[transition_heading],
                    expected_effects=[f"Support transition from {start_label} to {end_label}"],
                    affected_states=[canonical_end or end_label],
                    affected_state_ids=[end_id] if end_id else [],
                    lag_window_minutes=extract_minutes(action_text),
                    operational_complexity="medium",
                    confidence=build_confidence_profile(0.87, ontology_validity=0.88, operational_relevance=0.9),
                    raw_text=section.raw_text,
                    normalized_text=section.normalized_text,
                    source_file=section.file,
                    relative_source_file=section.relative_file,
                    section_id=section.section_id,
                    heading_path=section.heading_path,
                    extractor_version=config.extractor_version,
                    extractor_name="profile_transition_intervention_extractor",
                    provenance_refs=[section.relative_file, transition_heading, "intervention"],
                    source_role=section.source_role,
                    domain_tags=section.domain_tags,
                    expected_coverage_tags=section.expected_coverage_tags,
                    canonical_transition_id=transition_id,
                    applicable_contexts=["hospitality_live_environment"],
                )
            )

    if section.section_title == "Contradiction Scenarios and State Dependencies":
        contradiction_text = " ".join(bullet_split(section.normalized_text)[:4]) or section.normalized_text[:240]
        bundle["contradiction_objects"].append(
            ContradictionObject(
                contradiction_id=build_canonical_id("contradiction", f"{transition_heading}_{section.section_title}"),
                claim=transition_heading,
                contradiction_text=contradiction_text[:240],
                uncertainty_level="medium",
                confidence=build_confidence_profile(0.86, ontology_validity=0.9, operational_relevance=0.84),
                raw_text=section.raw_text,
                normalized_text=section.normalized_text,
                source_file=section.file,
                relative_source_file=section.relative_file,
                section_id=section.section_id,
                heading_path=section.heading_path,
                extractor_version=config.extractor_version,
                extractor_name="profile_transition_contradiction_extractor",
                provenance_refs=[section.relative_file, transition_heading, "contradiction"],
                source_role=section.source_role,
                domain_tags=section.domain_tags,
                expected_coverage_tags=section.expected_coverage_tags,
                canonical_transition_id=transition_id,
                applicable_contexts=["contextual_state_transition"],
                invalid_contexts=["universal_claim"],
                audience_dependencies=["group_identity", "cultural_norms"],
                environment_dependencies=["density", "safety", "experience_quality"],
            )
        )

    return bundle


def _mechanism_overrides(section: SemanticSection, config: PipelineConfig) -> dict[str, list[Any]]:
    bundle = _blank_bundle()
    mechanism_heading = next((part for part in section.heading_path if re.match(r"^\d+\.\s+", part)), "")
    mechanism_id, mechanism_label = match_canonical_mechanism(mechanism_heading)
    if not mechanism_id:
        mechanism_id, mechanism_label = match_canonical_mechanism(section.section_title)
    if not mechanism_id:
        return bundle

    if section.section_title in {"Temporal Characteristics", "Fatigue / Recovery Characteristics", "Escalation Limits"}:
        bundle["temporal_dynamics"].append(
            TemporalDynamic(
                dynamic_id=build_canonical_id("temporal_dynamic", f"{mechanism_id}_{section.section_title}"),
                name=mechanism_label or mechanism_heading,
                start_state="unknown",
                end_state="unknown",
                trigger_conditions=bullet_split(section.normalized_text)[:5],
                estimated_time_window=", ".join(str(value) for value in extract_minutes(section.normalized_text)) or section.section_title,
                recovery_characteristics=bullet_split(section.normalized_text)[:4],
                transition_logic=sentence_split(section.normalized_text)[0][:220] if sentence_split(section.normalized_text) else mechanism_label or mechanism_heading,
                duration_minutes=extract_minutes(section.normalized_text),
                sequence_dependencies=bullet_split(section.normalized_text)[:4],
                state_progression=[],
                confidence=build_confidence_profile(0.9, ontology_validity=0.91, operational_relevance=0.83),
                raw_text=section.raw_text,
                normalized_text=section.normalized_text,
                source_file=section.file,
                relative_source_file=section.relative_file,
                section_id=section.section_id,
                heading_path=section.heading_path,
                extractor_version=config.extractor_version,
                extractor_name="profile_mechanism_temporal_extractor",
                provenance_refs=[section.relative_file, mechanism_heading, section.section_title],
                source_role=section.source_role,
                domain_tags=section.domain_tags,
                expected_coverage_tags=section.expected_coverage_tags,
                canonical_mechanism_id=mechanism_id,
                canonical_mechanism_label=mechanism_label,
            )
        )
    if section.section_title == "Intervention Opportunities":
        for item in _list_like_candidates(section.normalized_text)[:6]:
            action_text = _intervention_text(item)
            bundle["interventions"].append(
                Intervention(
                    intervention_id=build_canonical_id("intervention", f"{mechanism_id}_{action_text}"),
                    name=action_text[:160],
                    trigger_conditions=[mechanism_label or mechanism_heading],
                    expected_effects=[f"Operationalize {mechanism_label or mechanism_heading}"],
                    lag_window_minutes=extract_minutes(action_text),
                    operational_complexity="medium",
                    confidence=build_confidence_profile(0.9, ontology_validity=0.9, operational_relevance=0.9),
                    raw_text=section.raw_text,
                    normalized_text=section.normalized_text,
                    source_file=section.file,
                    relative_source_file=section.relative_file,
                    section_id=section.section_id,
                    heading_path=section.heading_path,
                    extractor_version=config.extractor_version,
                    extractor_name="profile_mechanism_intervention_extractor",
                    provenance_refs=[section.relative_file, mechanism_heading, "intervention"],
                    source_role=section.source_role,
                    domain_tags=section.domain_tags,
                    expected_coverage_tags=section.expected_coverage_tags,
                    canonical_mechanism_id=mechanism_id,
                    canonical_mechanism_label=mechanism_label,
                )
            )
    return bundle


def _contradiction_overrides(section: SemanticSection, config: PipelineConfig) -> dict[str, list[Any]]:
    bundle = _blank_bundle()
    contradiction_heading = next((part for part in section.heading_path if CONTRADICTION_HEAD_RE.match(part)), "")
    if not contradiction_heading:
        return bundle
    match = CONTRADICTION_HEAD_RE.match(contradiction_heading)
    if not match:
        return bundle
    stimulus = normalize_whitespace(match.group(1))
    positive = normalize_whitespace(match.group(2))
    negative = normalize_whitespace(match.group(3))
    context_lines = [line for line in bullet_split(section.normalized_text) if ":" in line or "context" in line.lower() or "time of night" in line.lower()]
    contradiction_text = f"{stimulus} can drive {positive} or {negative} depending on context."
    bundle["contradiction_objects"].append(
        ContradictionObject(
            contradiction_id=build_canonical_id("contradiction", contradiction_heading),
            claim=stimulus,
            contradiction_text=contradiction_text,
            affected_entities=[positive, negative],
            uncertainty_level="medium",
            confidence=build_confidence_profile(0.91, ontology_validity=0.93, operational_relevance=0.89),
            raw_text=section.raw_text,
            normalized_text=section.normalized_text,
            source_file=section.file,
            relative_source_file=section.relative_file,
            section_id=section.section_id,
            heading_path=section.heading_path,
            extractor_version=config.extractor_version,
            extractor_name="profile_contradiction_extractor",
            provenance_refs=[section.relative_file, contradiction_heading, section.section_title],
            source_role=section.source_role,
            domain_tags=section.domain_tags,
            expected_coverage_tags=section.expected_coverage_tags,
            applicable_contexts=context_lines[:5],
            invalid_contexts=["universal_behavioral_claim"],
            audience_dependencies=[line for line in context_lines if any(token in line.lower() for token in ("age", "gender", "introvert", "extrovert", "demographic"))][:4],
            environment_dependencies=[line for line in context_lines if any(token in line.lower() for token in ("time", "density", "culture", "intensity", "night"))][:5],
        )
    )
    return bundle


def _temporal_overrides(section: SemanticSection, config: PipelineConfig) -> dict[str, list[Any]]:
    bundle = _blank_bundle()
    parent = section.heading_path[1] if len(section.heading_path) > 1 else section.section_title
    mechanism_id, mechanism_label = match_canonical_mechanism(parent)
    if section.section_title in {"Sequence Dependencies", "Lag Windows and Duration Effects", "Timing Thresholds and Failure Conditions", "Intervention Timing Opportunities"}:
        bundle["temporal_dynamics"].append(
            TemporalDynamic(
                dynamic_id=build_canonical_id("temporal_dynamic", f"{parent}_{section.section_title}"),
                name=parent,
                start_state="unknown",
                end_state="unknown",
                trigger_conditions=bullet_split(section.normalized_text)[:5],
                estimated_time_window=", ".join(str(value) for value in extract_minutes(section.normalized_text)) or section.section_title,
                recovery_characteristics=[line for line in bullet_split(section.normalized_text) if "recover" in line.lower()][:4],
                transition_logic=sentence_split(section.normalized_text)[0][:220] if sentence_split(section.normalized_text) else parent,
                duration_minutes=extract_minutes(section.normalized_text),
                sequence_dependencies=bullet_split(section.normalized_text)[:5],
                state_progression=[part.strip() for part in re.split(r"->|→", parent) if normalize_whitespace(part)][:4],
                confidence=build_confidence_profile(0.9, ontology_validity=0.92, operational_relevance=0.87),
                raw_text=section.raw_text,
                normalized_text=section.normalized_text,
                source_file=section.file,
                relative_source_file=section.relative_file,
                section_id=section.section_id,
                heading_path=section.heading_path,
                extractor_version=config.extractor_version,
                extractor_name="profile_temporal_kernel_extractor",
                provenance_refs=[section.relative_file, parent, section.section_title],
                source_role=section.source_role,
                domain_tags=section.domain_tags,
                expected_coverage_tags=section.expected_coverage_tags,
                canonical_mechanism_id=mechanism_id,
                canonical_mechanism_label=mechanism_label,
            )
        )
    return bundle


def _operational_overrides(section: SemanticSection, config: PipelineConfig) -> dict[str, list[Any]]:
    bundle = _blank_bundle()
    heading_text = " > ".join(section.heading_path)
    if "Core Causal Chains" in heading_text or "Failure Mode Matrix" in heading_text:
        for sentence in sentence_split(section.normalized_text):
            if "->" in sentence or "→" in sentence:
                parts = [normalize_whitespace(part) for part in re.split(r"->|→", sentence) if normalize_whitespace(part)]
                for left, right in zip(parts, parts[1:]):
                    bundle["relationships"].append(
                        Relationship(
                            relationship_id=build_canonical_id("relationship", f"{left}_leads_to_{right}"),
                            source_entity=left[:120],
                            target_entity=right[:120],
                            relationship_type="leads_to",
                            effect_direction="positive",
                            strength_estimate="operational_chain",
                            confidence_value=0.86,
                            context_dependencies=["venue_operations"],
                            environmental_modifiers=[],
                            time_dependency=False,
                            evidence_grade="moderate",
                            confidence=build_confidence_profile(0.88, ontology_validity=0.9, operational_relevance=0.92),
                            raw_text=section.raw_text,
                            normalized_text=section.normalized_text,
                            source_file=section.file,
                            relative_source_file=section.relative_file,
                            section_id=section.section_id,
                            heading_path=section.heading_path,
                            extractor_version=config.extractor_version,
                            extractor_name="profile_operational_chain_extractor",
                            provenance_refs=[section.relative_file, section.section_title, "causal_chain"],
                            source_role=section.source_role,
                            domain_tags=section.domain_tags,
                            expected_coverage_tags=section.expected_coverage_tags,
                        )
                    )
    if any(key in heading_text for key in ("Leading Indicators", "Lagging Indicators", "Operational Signals Dashboard")):
        for item in _list_like_candidates(section.normalized_text)[:8]:
            bundle["kpis"].append(
                KPI(
                    kpi_id=build_canonical_id("kpi", item),
                    operator_label=item[:120],
                    technical_definition=f"Operational KPI from section '{section.section_title}'.",
                    category="operational",
                    human_interpretation="Operational indicator from the nightlife operations synthesis.",
                    complexity_level="medium",
                    confidence=build_confidence_profile(0.89, ontology_validity=0.89, operational_relevance=0.94),
                    raw_text=section.raw_text,
                    normalized_text=section.normalized_text,
                    source_file=section.file,
                    relative_source_file=section.relative_file,
                    section_id=section.section_id,
                    heading_path=section.heading_path,
                    extractor_version=config.extractor_version,
                    extractor_name="profile_operational_kpi_extractor",
                    provenance_refs=[section.relative_file, section.section_title, "kpi"],
                    source_role=section.source_role,
                    domain_tags=section.domain_tags,
                    expected_coverage_tags=section.expected_coverage_tags,
                )
            )
    if any(key in heading_text for key in ("Intervention Points", "Implementation Protocol", "De-escalation Mechanics")):
        for item in _list_like_candidates(section.normalized_text)[:8]:
            action_text = _intervention_text(item)
            bundle["interventions"].append(
                Intervention(
                    intervention_id=build_canonical_id("intervention", action_text),
                    name=action_text[:160],
                    trigger_conditions=[section.section_title],
                    expected_effects=["Operational behavior change"],
                    lag_window_minutes=extract_minutes(action_text),
                    operational_complexity="medium",
                    confidence=build_confidence_profile(0.88, ontology_validity=0.88, operational_relevance=0.95),
                    raw_text=section.raw_text,
                    normalized_text=section.normalized_text,
                    source_file=section.file,
                    relative_source_file=section.relative_file,
                    section_id=section.section_id,
                    heading_path=section.heading_path,
                    extractor_version=config.extractor_version,
                    extractor_name="profile_operational_intervention_extractor",
                    provenance_refs=[section.relative_file, section.section_title, "intervention"],
                    source_role=section.source_role,
                    domain_tags=section.domain_tags,
                    expected_coverage_tags=section.expected_coverage_tags,
                )
            )
    return bundle


def _crowd_report_overrides(section: SemanticSection, config: PipelineConfig) -> dict[str, list[Any]]:
    bundle = _blank_bundle()
    text = section.normalized_text.lower()
    if "arrival/search" in text or "collective effervescence" in text or "recovery or exhaustion" in text:
        hidden_states = ["arrival/search", "alignment", "collective effervescence", "cascade", "compression/instability", "recovery or exhaustion"]
        for state_name in hidden_states:
            bundle["states"].append(
                BehavioralState(
                    state_id=build_canonical_id("behavioral_state", state_name),
                    name=state_name.title(),
                    description="Crowd-state mode extracted from ontology-ready modeling architecture.",
                    observable_signals=[],
                    confidence_notes="Composite crowd-state mode from deep research report.",
                    confidence=build_confidence_profile(0.84, ontology_validity=0.85, operational_relevance=0.82),
                    raw_text=section.raw_text,
                    normalized_text=section.normalized_text,
                    source_file=section.file,
                    relative_source_file=section.relative_file,
                    section_id=section.section_id,
                    heading_path=section.heading_path,
                    extractor_version=config.extractor_version,
                    extractor_name="profile_crowd_state_extractor",
                    provenance_refs=[section.relative_file, section.section_title, "crowd_state"],
                    source_role=section.source_role,
                    domain_tags=section.domain_tags,
                    expected_coverage_tags=section.expected_coverage_tags,
                    invalid_contexts=["single_metric_crowd_model"],
                )
            )
    if "tipping point" in text or "cascade" in text or "coupled transitions" in text:
        lines = bullet_split(section.normalized_text) or sentence_split(section.normalized_text)
        for item in lines[:6]:
            bundle["relationships"].append(
                Relationship(
                    relationship_id=build_canonical_id("relationship", item[:80]),
                    source_entity=section.section_title[:120],
                    target_entity=item[:120],
                    relationship_type="destabilizes" if "risk" in item.lower() or "collapse" in item.lower() else "reinforces",
                    effect_direction="mixed",
                    strength_estimate="crowd_dynamics",
                    confidence_value=0.8,
                    context_dependencies=["coupled_transition_model"],
                    environmental_modifiers=[],
                    time_dependency=True,
                    evidence_grade="moderate",
                    confidence=build_confidence_profile(0.82, ontology_validity=0.84, operational_relevance=0.82),
                    raw_text=section.raw_text,
                    normalized_text=section.normalized_text,
                    source_file=section.file,
                    relative_source_file=section.relative_file,
                    section_id=section.section_id,
                    heading_path=section.heading_path,
                    extractor_version=config.extractor_version,
                    extractor_name="profile_cascade_relationship_extractor",
                    provenance_refs=[section.relative_file, section.section_title, "cascade"],
                    source_role=section.source_role,
                    domain_tags=section.domain_tags,
                    expected_coverage_tags=section.expected_coverage_tags,
                    canonical_mechanism_id="MECH_ATTENTION_SYNC" if "attention" in item.lower() or "attention alignment" in text else None,
                    canonical_mechanism_label="Attention Synchronization" if "attention" in item.lower() or "attention alignment" in text else None,
                    invalid_contexts=["single_variable_explanation"],
                )
            )
    return bundle


def _measurement_framework_overrides(section: SemanticSection, config: PipelineConfig) -> dict[str, list[Any]]:
    bundle = _blank_bundle()

    if section.section_title == "KPI-to-signal mapping table":
        for row in _markdown_table_rows(section.raw_text):
            kpi_name = row.get("KPI name", "")
            if not kpi_name:
                continue
            target_states = _csv_like_split(row.get("Target state(s)", ""))
            leading = _csv_like_split(row.get("Leading indicators", ""))
            lagging = _csv_like_split(row.get("Lagging indicators", ""))
            interventions = _csv_like_split(row.get("Intervention linkage", ""))
            data_sources = row.get("Recommended data source(s)", "")
            collection_method = row.get("Collection method", "")
            cadence = row.get("Cadence", "")
            window = row.get("Aggregation window", "")
            threshold = row.get("Threshold guidance", "")
            privacy = row.get("Privacy/compliance notes", "")
            validity = row.get("Confidence in measurement validity", "")
            category = row.get("Ontology category", "operational")
            technical_definition = normalize_whitespace(
                f"Measurement architecture for {kpi_name}. Sources: {data_sources}. "
                f"Method: {collection_method}. Cadence: {cadence}. Window: {window}. "
                f"Thresholds: {threshold}. Validity: {validity}."
            )
            bundle["kpis"].append(
                KPI(
                    kpi_id=build_canonical_id("kpi", kpi_name),
                    operator_label=kpi_name[:120],
                    technical_definition=technical_definition[:400],
                    category=category[:60] or "operational",
                    leading_indicators=leading[:5],
                    lagging_indicators=lagging[:5],
                    possible_interventions=interventions[:5],
                    human_interpretation=f"Target states: {', '.join(target_states[:4])}. Privacy profile: {privacy[:120]}",
                    complexity_level="high" if "hybrid" in data_sources.lower() or "composite" in technical_definition.lower() else "medium",
                    confidence=build_confidence_profile(0.92, ontology_validity=0.93, operational_relevance=0.96),
                    raw_text=section.raw_text,
                    normalized_text=section.normalized_text,
                    source_file=section.file,
                    relative_source_file=section.relative_file,
                    section_id=section.section_id,
                    heading_path=section.heading_path,
                    extractor_version=config.extractor_version,
                    extractor_name="profile_measurement_kpi_extractor",
                    provenance_refs=[section.relative_file, section.section_title, kpi_name],
                    source_role=section.source_role,
                    domain_tags=section.domain_tags,
                    expected_coverage_tags=section.expected_coverage_tags,
                    applicable_contexts=target_states[:4],
                    invalid_contexts=["universal_threshold"] if "not universal" in threshold.lower() or "baseline" in threshold.lower() else [],
                    environment_dependencies=_csv_like_split(data_sources)[:4],
                )
            )
            bundle["evidence_objects"].append(
                EvidenceObject(
                    claim_id=build_canonical_id("evidence", f"{kpi_name}_measurement_validity"),
                    claim=f"{kpi_name} measurement design should use {data_sources}",
                    evidence_strength="moderate",
                    replication_quality="unknown",
                    scientific_consensus="mixed",
                    operational_relevance="high",
                    source_type="hospitality_operational",
                    recommended_weight=0.72,
                    notes=f"Thresholds: {threshold[:220]}",
                    confidence=build_confidence_profile(0.84, ontology_validity=0.88, operational_relevance=0.95),
                    raw_text=section.raw_text,
                    normalized_text=section.normalized_text,
                    source_file=section.file,
                    relative_source_file=section.relative_file,
                    section_id=section.section_id,
                    heading_path=section.heading_path,
                    extractor_version=config.extractor_version,
                    extractor_name="profile_measurement_evidence_extractor",
                    provenance_refs=[section.relative_file, section.section_title, kpi_name],
                    source_role=section.source_role,
                    domain_tags=section.domain_tags,
                    expected_coverage_tags=section.expected_coverage_tags,
                    evidence_notes=[collection_method[:120], privacy[:120], validity[:120]],
                )
            )

    if section.section_title == "Measurement architecture":
        architecture_actions = {
            "edge collection layer": "Deploy edge collection publishing normalized observation events by zone.",
            "event normalization layer": "Normalize measurement events with provenance, confidence, device, and calibration metadata.",
            "KPI computation layer": "Compute direct and composite KPIs with graceful degradation and provenance bundles.",
            "alerting and intervention trigger layer": "Use advisory, alert, escalation, and recovery trigger states rather than one-off threshold trips.",
            "validation and recalibration loop": "Review comparable events and recalibrate thresholds after layout, staffing, programming, or ventilation changes.",
        }
        lowered = section.normalized_text.lower()
        for label, action_text in architecture_actions.items():
            if label in lowered:
                bundle["interventions"].append(
                    Intervention(
                        intervention_id=build_canonical_id("intervention", action_text),
                        name=action_text[:160],
                        trigger_conditions=[label],
                        expected_effects=["measurement_system_hardening"],
                        operational_complexity="high",
                        confidence=build_confidence_profile(0.9, ontology_validity=0.92, operational_relevance=0.97),
                        raw_text=section.raw_text,
                        normalized_text=section.normalized_text,
                        source_file=section.file,
                        relative_source_file=section.relative_file,
                        section_id=section.section_id,
                        heading_path=section.heading_path,
                        extractor_version=config.extractor_version,
                        extractor_name="profile_measurement_architecture_extractor",
                        provenance_refs=[section.relative_file, section.section_title, label],
                        source_role=section.source_role,
                        domain_tags=section.domain_tags,
                        expected_coverage_tags=section.expected_coverage_tags,
                        applicable_contexts=["measurement_architecture"],
                    )
                )

    if section.section_title == "Venue deployment tiers":
        for sentence in sentence_split(section.normalized_text):
            lowered = sentence.lower()
            if "low-instrumentation venue" in lowered or "medium-instrumentation venue" in lowered or "high-instrumentation venue" in lowered:
                tier_name = sentence.split(" is ")[0].replace("A ", "").strip()
                bundle["interventions"].append(
                    Intervention(
                        intervention_id=build_canonical_id("intervention", tier_name),
                        name=f"Deploy {tier_name.lower()} measurement stack"[:160],
                        trigger_conditions=[tier_name],
                        expected_effects=["deployment_tier_selection"],
                        operational_complexity="medium" if "low-" in lowered else "high",
                        confidence=build_confidence_profile(0.88, ontology_validity=0.9, operational_relevance=0.94),
                        raw_text=section.raw_text,
                        normalized_text=section.normalized_text,
                        source_file=section.file,
                        relative_source_file=section.relative_file,
                        section_id=section.section_id,
                        heading_path=section.heading_path,
                        extractor_version=config.extractor_version,
                        extractor_name="profile_measurement_deployment_tier_extractor",
                        provenance_refs=[section.relative_file, section.section_title, tier_name],
                        source_role=section.source_role,
                        domain_tags=section.domain_tags,
                        expected_coverage_tags=section.expected_coverage_tags,
                        applicable_contexts=[tier_name],
                    )
                )

    if section.section_title == "Recommended MVP measurement stack":
        for sentence in sentence_split(section.normalized_text):
            lowered = sentence.lower()
            if "first part is" in lowered or "second part is" in lowered or "third part is" in lowered or "fourth part is" in lowered or "fifth part is" in lowered or "sixth part is" in lowered:
                stack_item = normalize_whitespace(sentence.split(" is ", 1)[1] if " is " in sentence else sentence)
                action_text = f"Implement {stack_item}"
                bundle["interventions"].append(
                    Intervention(
                        intervention_id=build_canonical_id("intervention", action_text),
                        name=action_text[:160],
                        trigger_conditions=["MVP measurement rollout"],
                        expected_effects=["mvp_stack_deployment"],
                        operational_complexity="medium",
                        confidence=build_confidence_profile(0.9, ontology_validity=0.91, operational_relevance=0.98),
                        raw_text=section.raw_text,
                        normalized_text=section.normalized_text,
                        source_file=section.file,
                        relative_source_file=section.relative_file,
                        section_id=section.section_id,
                        heading_path=section.heading_path,
                        extractor_version=config.extractor_version,
                        extractor_name="profile_measurement_mvp_stack_extractor",
                        provenance_refs=[section.relative_file, section.section_title, stack_item[:80]],
                        source_role=section.source_role,
                        domain_tags=section.domain_tags,
                        expected_coverage_tags=section.expected_coverage_tags,
                        applicable_contexts=["mvp_stack"],
                    )
                )

    if section.section_title == "Explicit no-go claims":
        for sentence in sentence_split(section.normalized_text):
            lowered = sentence.lower()
            if "should not" not in lowered:
                continue
            claim_text = normalize_whitespace(sentence)
            bundle["contradiction_objects"].append(
                ContradictionObject(
                    contradiction_id=build_canonical_id("contradiction", claim_text[:120]),
                    claim="measurement_system_no_go_claim",
                    contradiction_text=claim_text[:240],
                    uncertainty_level="low",
                    confidence=build_confidence_profile(0.93, ontology_validity=0.95, operational_relevance=0.95),
                    raw_text=section.raw_text,
                    normalized_text=section.normalized_text,
                    source_file=section.file,
                    relative_source_file=section.relative_file,
                    section_id=section.section_id,
                    heading_path=section.heading_path,
                    extractor_version=config.extractor_version,
                    extractor_name="profile_measurement_no_go_extractor",
                    provenance_refs=[section.relative_file, section.section_title, claim_text[:80]],
                    source_role=section.source_role,
                    domain_tags=section.domain_tags,
                    expected_coverage_tags=section.expected_coverage_tags,
                    invalid_contexts=["unsafe_measurement_claim", "person_level_surveillance"],
                    applicable_contexts=["measurement_governance"],
                    environment_dependencies=["privacy_law", "proxy_validity"],
                )
            )

    return bundle


def _blank_bundle() -> dict[str, list[Any]]:
    return {
        "variables": [],
        "states": [],
        "relationships": [],
        "interventions": [],
        "kpis": [],
        "temporal_dynamics": [],
        "evidence_objects": [],
        "contradiction_objects": [],
    }


def _list_like_candidates(text: str) -> list[str]:
    candidates = bullet_split(text)
    for raw_line in text.splitlines():
        line = normalize_whitespace(re.sub(r"^\d+\.\s*", "", raw_line.strip()))
        if line and line not in candidates and len(line.split()) <= 32:
            candidates.append(line)
    if candidates:
        return candidates
    return [sentence for sentence in sentence_split(text) if len(sentence.split()) <= 32]


def _intervention_text(text: str) -> str:
    cleaned = normalize_whitespace(re.sub(r"^\*\*(.+?)\*\*:\s*", "", text.strip()))
    if ":" in cleaned:
        prefix, suffix = cleaned.split(":", 1)
        suffix = normalize_whitespace(suffix)
        if suffix:
            cleaned = suffix
    return cleaned or normalize_whitespace(text)


def _state_transition_index(source_sections: list[SemanticSection]) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for section in source_sections:
        transition_heading = next((part for part in section.heading_path if TRANSITION_RE.match(part)), "")
        if not transition_heading:
            continue
        match = TRANSITION_RE.match(transition_heading)
        if not match:
            continue
        start_id, _ = match_canonical_state(match.group(1))
        end_id, end_label = match_canonical_state(match.group(2))
        if start_id and end_id:
            mapping.setdefault(start_id, [])
            if end_label and end_label not in mapping[start_id]:
                mapping[start_id].append(end_label)
    return mapping


def _state_label(state_id: str) -> str:
    payload = load_canonical_states().get(state_id, {})
    return str(payload.get("label", state_id))


def _markdown_table_rows(raw_text: str) -> list[dict[str, str]]:
    lines = [line.strip() for line in raw_text.splitlines() if line.strip().startswith("|") and line.strip().endswith("|")]
    if len(lines) < 3:
        return []
    headers = [cell.strip() for cell in lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(headers):
            continue
        rows.append({header: value for header, value in zip(headers, cells)})
    return rows


def _csv_like_split(text: str) -> list[str]:
    normalized = normalize_whitespace(re.sub(r"îˆ€cite.*?îˆ", "", text))
    normalized = normalized.replace(";", ",")
    parts = [normalize_whitespace(part) for part in normalized.split(",")]
    return [part for part in parts if part and part not in {"-", "—", "–"}][:8]
