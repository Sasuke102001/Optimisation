from __future__ import annotations

from research_extraction.ids import build_canonical_id
from research_extraction.schemas import (
    BehavioralState,
    EvidenceObject,
    Intervention,
    KPI,
    RagChunk,
    Relationship,
    TemporalDynamic,
    Variable,
)


def build_rag_chunks(
    variables: list[Variable],
    states: list[BehavioralState],
    relationships: list[Relationship],
    interventions: list[Intervention],
    kpis: list[KPI],
    temporal_dynamics: list[TemporalDynamic],
    evidence_objects: list[EvidenceObject],
) -> list[RagChunk]:
    chunks: list[RagChunk] = []
    for variable in variables:
        chunks.append(
            RagChunk(
                chunk_id=build_canonical_id("chunk", variable.variable_id),
                chunk_type="variable",
                concept=variable.name,
                source=variable.relative_source_file,
                section_id=variable.section_id,
                heading_path=variable.heading_path,
                evidence_quality=variable.confidence_level,
                operational_relevance=variable.operational_relevance,
                linked_entities=[variable.variable_id],
                provenance_text=variable.raw_text,
                text=f"Variable: {variable.name}. Description: {variable.description}. Measurement: {variable.measurement_method}.",
            )
        )
    for state in states:
        chunks.append(
            RagChunk(
                chunk_id=build_canonical_id("chunk", state.state_id),
                chunk_type="behavioral_state",
                concept=state.name,
                source=state.relative_source_file,
                section_id=state.section_id,
                heading_path=state.heading_path,
                evidence_quality="medium",
                operational_relevance=state.possible_interventions,
                linked_entities=[state.state_id, *state.contributing_variable_ids],
                state_relevance=[state.state_id],
                provenance_text=state.raw_text,
                text=f"State: {state.name}. Signals: {', '.join(state.observable_signals[:5])}.",
            )
        )
    for rel in relationships:
        chunks.append(
            RagChunk(
                chunk_id=build_canonical_id("chunk", rel.relationship_id),
                chunk_type="relationship",
                concept=rel.relationship_type,
                source=rel.relative_source_file,
                section_id=rel.section_id,
                heading_path=rel.heading_path,
                evidence_quality=rel.evidence_grade,
                linked_entities=[item for item in [rel.source_entity_id, rel.target_entity_id] if item] or [rel.source_entity, rel.target_entity],
                provenance_text=rel.raw_text,
                text=f"Relationship: {rel.source_entity} {rel.relationship_type} {rel.target_entity}. Direction: {rel.effect_direction}.",
            )
        )
    for intervention in interventions:
        chunks.append(
            RagChunk(
                chunk_id=build_canonical_id("chunk", intervention.intervention_id),
                chunk_type="intervention",
                concept=intervention.name,
                source=intervention.relative_source_file,
                section_id=intervention.section_id,
                heading_path=intervention.heading_path,
                evidence_quality="medium",
                operational_relevance=intervention.expected_effects,
                linked_entities=[intervention.intervention_id, *intervention.required_variable_ids],
                intervention_relevance=[intervention.intervention_id],
                provenance_text=intervention.raw_text,
                text=f"Intervention: {intervention.name}. Lag window: {intervention.lag_window_minutes}. Risks: {', '.join(intervention.risk_factors[:4])}.",
            )
        )
    for kpi in kpis:
        chunks.append(
            RagChunk(
                chunk_id=build_canonical_id("chunk", kpi.kpi_id),
                chunk_type="kpi",
                concept=kpi.operator_label,
                source=kpi.relative_source_file,
                section_id=kpi.section_id,
                heading_path=kpi.heading_path,
                evidence_quality="medium",
                operational_relevance=kpi.possible_interventions,
                linked_entities=[kpi.kpi_id, *kpi.leading_indicator_ids, *kpi.lagging_indicator_ids],
                provenance_text=kpi.raw_text,
                text=f"KPI: {kpi.operator_label}. Definition: {kpi.technical_definition}.",
            )
        )
    for dynamic in temporal_dynamics:
        chunks.append(
            RagChunk(
                chunk_id=build_canonical_id("chunk", dynamic.dynamic_id),
                chunk_type="temporal_dynamic",
                concept=dynamic.name,
                source=dynamic.relative_source_file,
                section_id=dynamic.section_id,
                heading_path=dynamic.heading_path,
                evidence_quality="medium",
                operational_relevance=dynamic.trigger_conditions,
                linked_entities=[item for item in [dynamic.dynamic_id, dynamic.start_state_id, dynamic.end_state_id] if item],
                provenance_text=dynamic.raw_text,
                text=f"Temporal dynamic: {dynamic.name}. Window: {dynamic.estimated_time_window}.",
            )
        )
    for evidence in evidence_objects:
        chunks.append(
            RagChunk(
                chunk_id=build_canonical_id("chunk", evidence.claim_id),
                chunk_type="evidence",
                concept=evidence.claim[:80],
                source=evidence.relative_source_file,
                section_id=evidence.section_id,
                heading_path=evidence.heading_path,
                evidence_quality=evidence.evidence_strength,
                operational_relevance=[evidence.operational_relevance],
                linked_entities=[evidence.claim_id],
                provenance_text=evidence.raw_text,
                text=f"Evidence claim: {evidence.claim}. Strength: {evidence.evidence_strength}. Consensus: {evidence.scientific_consensus}.",
            )
        )
    return chunks
