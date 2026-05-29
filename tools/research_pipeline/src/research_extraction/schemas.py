from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class FileMetadata(BaseModel):
    file: str
    relative_file: str
    filename: str
    bytes_size: int
    modified_at: str


class SemanticSection(BaseModel):
    file: str
    relative_file: str
    filename: str
    heading_path: list[str]
    section_title: str
    raw_text: str
    normalized_text: str
    section_id: str
    level: int
    order_index: int
    metadata: dict[str, Any] = Field(default_factory=dict)
    source_role: str = "general"
    domain_tags: list[str] = Field(default_factory=list)
    expected_coverage_tags: list[str] = Field(default_factory=list)


class SectionClassification(BaseModel):
    section_id: str
    section_type: str
    confidence: float
    candidate_types: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)


class ConfidenceProfile(BaseModel):
    extraction_confidence: float = 0.0
    ontology_validity: float = 0.0
    cross_document_support: float = 0.0
    operational_relevance: float = 0.0
    final_confidence: float = 0.0


class ValidationResult(BaseModel):
    is_valid: bool = True
    validation_score: float = 0.0
    reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    rejected_rules: list[str] = Field(default_factory=list)


class BaseOntologyObject(BaseModel):
    confidence: ConfidenceProfile
    raw_text: str
    normalized_text: str
    source_file: str
    relative_source_file: str
    section_id: str
    heading_path: list[str]
    extraction_timestamp: str = Field(default_factory=utc_now_iso)
    extractor_version: str
    extractor_name: str
    aliases: list[str] = Field(default_factory=list)
    contextual_limitations: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    evidence_notes: list[str] = Field(default_factory=list)
    validation: ValidationResult = Field(default_factory=ValidationResult)
    original_language: str = "source"
    provenance_refs: list[str] = Field(default_factory=list)
    source_role: str = "general"
    domain_tags: list[str] = Field(default_factory=list)
    expected_coverage_tags: list[str] = Field(default_factory=list)
    canonical_mechanism_id: str | None = None
    canonical_mechanism_label: str | None = None
    canonical_state_id: str | None = None
    canonical_transition_id: str | None = None
    applicable_contexts: list[str] = Field(default_factory=list)
    invalid_contexts: list[str] = Field(default_factory=list)
    audience_dependencies: list[str] = Field(default_factory=list)
    environment_dependencies: list[str] = Field(default_factory=list)

    @property
    def confidence_score(self) -> float:
        return self.confidence.final_confidence


class Variable(BaseOntologyObject):
    variable_id: str
    name: str
    category: str
    description: str
    measurement_method: str
    unit: str
    real_time_capable: bool
    behavioral_relevance: list[str] = Field(default_factory=list)
    operational_relevance: list[str] = Field(default_factory=list)
    confidence_level: str


class BehavioralState(BaseOntologyObject):
    state_id: str
    name: str
    description: str
    observable_signals: list[str] = Field(default_factory=list)
    contributing_variables: list[str] = Field(default_factory=list)
    contributing_variable_ids: list[str] = Field(default_factory=list)
    possible_interventions: list[str] = Field(default_factory=list)
    possible_intervention_ids: list[str] = Field(default_factory=list)
    confidence_notes: str = ""
    entry_conditions: list[str] = Field(default_factory=list)
    exit_conditions: list[str] = Field(default_factory=list)
    possible_next_states: list[str] = Field(default_factory=list)
    possible_next_state_ids: list[str] = Field(default_factory=list)
    transition_triggers: list[str] = Field(default_factory=list)
    stability_score: float = 0.0
    fatigue_characteristics: list[str] = Field(default_factory=list)
    recovery_characteristics: list[str] = Field(default_factory=list)


class Relationship(BaseOntologyObject):
    relationship_id: str
    source_entity: str
    source_entity_id: str = ""
    target_entity: str
    target_entity_id: str = ""
    relationship_type: str
    effect_direction: str
    strength_estimate: str
    confidence_value: float = 0.0
    context_dependencies: list[str] = Field(default_factory=list)
    environmental_modifiers: list[str] = Field(default_factory=list)
    time_dependency: bool
    lag_window_minutes: float | None = None
    evidence_grade: str


class Intervention(BaseOntologyObject):
    intervention_id: str
    name: str
    trigger_conditions: list[str] = Field(default_factory=list)
    expected_effects: list[str] = Field(default_factory=list)
    affected_states: list[str] = Field(default_factory=list)
    affected_state_ids: list[str] = Field(default_factory=list)
    required_variables: list[str] = Field(default_factory=list)
    required_variable_ids: list[str] = Field(default_factory=list)
    lag_window_minutes: list[float] = Field(default_factory=list)
    risk_factors: list[str] = Field(default_factory=list)
    operational_complexity: str


class KPI(BaseOntologyObject):
    kpi_id: str
    operator_label: str
    technical_definition: str
    category: str
    leading_indicators: list[str] = Field(default_factory=list)
    leading_indicator_ids: list[str] = Field(default_factory=list)
    lagging_indicators: list[str] = Field(default_factory=list)
    lagging_indicator_ids: list[str] = Field(default_factory=list)
    possible_interventions: list[str] = Field(default_factory=list)
    possible_intervention_ids: list[str] = Field(default_factory=list)
    human_interpretation: str
    complexity_level: str


class TemporalDynamic(BaseOntologyObject):
    dynamic_id: str
    name: str
    start_state: str
    start_state_id: str = ""
    end_state: str
    end_state_id: str = ""
    trigger_conditions: list[str] = Field(default_factory=list)
    estimated_time_window: str
    recovery_characteristics: list[str] = Field(default_factory=list)
    transition_logic: str = ""
    duration_minutes: list[float] = Field(default_factory=list)
    sequence_dependencies: list[str] = Field(default_factory=list)
    state_progression: list[str] = Field(default_factory=list)


class EvidenceObject(BaseOntologyObject):
    claim_id: str
    claim: str
    evidence_strength: str
    replication_quality: str
    scientific_consensus: str
    operational_relevance: str
    source_type: str = "speculative"
    recommended_weight: float
    linked_entity_ids: list[str] = Field(default_factory=list)
    notes: str


class ContradictionObject(BaseOntologyObject):
    contradiction_id: str
    claim: str
    contradiction_text: str
    affected_entities: list[str] = Field(default_factory=list)
    affected_entity_ids: list[str] = Field(default_factory=list)
    uncertainty_level: str


class ReviewQueueItem(BaseModel):
    review_id: str
    review_target_id: str
    object_type: str
    review_bucket: Literal[
        "auto_rejected",
        "low_confidence",
        "ontology_conflict",
        "contradiction_review",
        "merge_review",
        "promotion_review",
    ]
    proposed_object: dict[str, Any]
    raw_text: str
    confidence: float
    review_status: Literal["pending", "approved", "rejected", "modified"] = "pending"
    review_reason: str
    created_at: str = Field(default_factory=utc_now_iso)


class NormalizationDecision(BaseModel):
    entity_type: str
    canonical_id: str
    candidate_id: str
    canonical_name: str
    candidate_name: str
    similarity_score: float
    merge_action: Literal["merged", "flagged_for_review", "kept_distinct"]
    rationale: str


class RagChunk(BaseModel):
    chunk_id: str
    chunk_type: str
    concept: str
    source: str
    section_id: str
    heading_path: list[str]
    evidence_quality: str
    operational_relevance: list[str] = Field(default_factory=list)
    linked_entities: list[str] = Field(default_factory=list)
    state_relevance: list[str] = Field(default_factory=list)
    intervention_relevance: list[str] = Field(default_factory=list)
    provenance_text: str
    text: str


class RejectedEntity(BaseModel):
    object_type: str
    object_id: str
    source_file: str
    section_id: str
    rejected_at_stage: str
    reasons: list[str] = Field(default_factory=list)
    rejected_rules: list[str] = Field(default_factory=list)
    payload: dict[str, Any]


class ValidationReportEntry(BaseModel):
    object_type: str
    object_id: str
    source_file: str
    section_id: str
    is_valid: bool
    validation_score: float
    reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    rejected_rules: list[str] = Field(default_factory=list)


class GraphHealthReport(BaseModel):
    duplicate_density: float
    orphan_node_count: int
    low_confidence_ratio: float
    contradiction_density: float
    ontology_growth_rate: float
    normalization_compression_ratio: float
    invalid_extraction_rejection_rate: float


class CoverageReport(BaseModel):
    missing_canonical_states: list[str] = Field(default_factory=list)
    missing_canonical_transitions: list[str] = Field(default_factory=list)
    missing_canonical_mechanisms: list[str] = Field(default_factory=list)
    contradiction_extraction_coverage: dict[str, int] = Field(default_factory=dict)
    temporal_kernel_coverage: dict[str, int] = Field(default_factory=dict)
    source_file_coverage: dict[str, dict[str, Any]] = Field(default_factory=dict)


class PipelineOutputs(BaseModel):
    sections: list[SemanticSection]
    classifications: list[SectionClassification]
    variables: list[Variable]
    states: list[BehavioralState]
    relationships: list[Relationship]
    interventions: list[Intervention]
    kpis: list[KPI]
    temporal_dynamics: list[TemporalDynamic]
    evidence_objects: list[EvidenceObject]
    contradiction_objects: list[ContradictionObject]
    review_queue: list[ReviewQueueItem]
    normalization_decisions: list[NormalizationDecision]
    rag_chunks: list[RagChunk]
    validation_report: list[ValidationReportEntry]
    rejected_entities: list[RejectedEntity]
    graph_health: GraphHealthReport | None = None
    coverage_report: CoverageReport | None = None


OntologyObject = (
    Variable
    | BehavioralState
    | Relationship
    | Intervention
    | KPI
    | TemporalDynamic
    | EvidenceObject
    | ContradictionObject
)
