from __future__ import annotations

import re
from dataclasses import dataclass

from research_extraction.confidence import infer_operational_relevance_score, with_confidence_updates
from research_extraction.registries import match_canonical_mechanism, match_canonical_state
from research_extraction.review import get_object_id
from research_extraction.schemas import (
    BehavioralState,
    ContradictionObject,
    EvidenceObject,
    Intervention,
    KPI,
    OntologyObject,
    RejectedEntity,
    Relationship,
    TemporalDynamic,
    ValidationReportEntry,
    ValidationResult,
    Variable,
)
from research_extraction.utils import normalize_whitespace
from research_extraction.validation.rules import (
    ACTION_VERBS,
    EVIDENCE_SOURCE_TYPES,
    FORBIDDEN_PATTERNS,
    GENERIC_SECTION_TITLES,
    MEASURABLE_TERMS,
    RELATIONSHIP_VOCAB,
    TEMPORAL_TERMS,
)


@dataclass
class ValidationOutcome:
    accepted: list[OntologyObject]
    report: list[ValidationReportEntry]
    rejected: list[RejectedEntity]


def validate_bundle(objects: list[OntologyObject]) -> ValidationOutcome:
    accepted: list[OntologyObject] = []
    report: list[ValidationReportEntry] = []
    rejected: list[RejectedEntity] = []

    for obj in objects:
        result = validate_object(obj)
        obj = obj.model_copy(update={"validation": result})
        obj = with_confidence_updates(
            obj,
            ontology_validity=result.validation_score,
            operational_relevance=infer_operational_relevance_score(obj),
        )
        object_id = get_object_id(obj)
        report.append(
            ValidationReportEntry(
                object_type=obj.__class__.__name__,
                object_id=object_id,
                source_file=obj.relative_source_file,
                section_id=obj.section_id,
                is_valid=result.is_valid,
                validation_score=result.validation_score,
                reasons=result.reasons,
                warnings=result.warnings,
                rejected_rules=result.rejected_rules,
            )
        )
        if result.is_valid:
            accepted.append(obj)
            continue
        rejected.append(
            RejectedEntity(
                object_type=obj.__class__.__name__,
                object_id=object_id,
                source_file=obj.relative_source_file,
                section_id=obj.section_id,
                rejected_at_stage="validation",
                reasons=result.reasons,
                rejected_rules=result.rejected_rules,
                payload=obj.model_dump(),
            )
        )

    return ValidationOutcome(accepted=accepted, report=report, rejected=rejected)


def validate_object(obj: OntologyObject) -> ValidationResult:
    if isinstance(obj, Variable):
        return _validate_variable(obj)
    if isinstance(obj, BehavioralState):
        return _validate_state(obj)
    if isinstance(obj, Relationship):
        return _validate_relationship(obj)
    if isinstance(obj, Intervention):
        return _validate_intervention(obj)
    if isinstance(obj, KPI):
        return _validate_kpi(obj)
    if isinstance(obj, TemporalDynamic):
        return _validate_temporal_dynamic(obj)
    if isinstance(obj, EvidenceObject):
        return _validate_evidence(obj)
    if isinstance(obj, ContradictionObject):
        return _validate_contradiction(obj)
    return ValidationResult(is_valid=False, validation_score=0.0, reasons=["Unsupported ontology object type."], rejected_rules=["unsupported_type"])


def _validate_variable(obj: Variable) -> ValidationResult:
    minimum_chars = 3 if obj.name.isupper() else 5
    reasons, warnings, rejected_rules = _base_entity_checks(obj, obj.name, minimum_chars=minimum_chars)
    label = normalize_whitespace(obj.name).lower()
    if not obj.unit and not any(term in label or term in obj.description.lower() or term in obj.measurement_method.lower() for term in MEASURABLE_TERMS):
        reasons.append("Variable lacks measurable or observable operational meaning.")
        rejected_rules.append("variable_not_measurable")
    if len(label.split()) > 12:
        reasons.append("Variable looks like prose rather than an entity label.")
        rejected_rules.append("variable_sentence_fragment")
    if label in GENERIC_SECTION_TITLES:
        reasons.append("Variable matches a generic section title.")
        rejected_rules.append("variable_section_title")
    if not obj.measurement_method:
        reasons.append("Variable is missing a measurement method.")
        rejected_rules.append("variable_missing_measurement")
    return _finalize(reasons, warnings, rejected_rules)


def _validate_state(obj: BehavioralState) -> ValidationResult:
    reasons, warnings, rejected_rules = _base_entity_checks(obj, obj.name, minimum_chars=4)
    if not obj.entry_conditions and not obj.observable_signals and not obj.transition_triggers and not obj.possible_next_states:
        reasons.append("State needs observable signals or entry conditions.")
        rejected_rules.append("state_missing_entry_signal")
    if obj.stability_score and not 0.0 <= obj.stability_score <= 1.0:
        reasons.append("State stability score must be between 0 and 1.")
        rejected_rules.append("state_invalid_stability")
    if obj.source_role == "synthesis" and obj.confidence.extraction_confidence >= 0.8 and not (obj.canonical_state_id or match_canonical_state(obj.name)[0]):
        reasons.append("High-confidence synthesis state must map to the canonical state registry.")
        rejected_rules.append("state_missing_canonical_mapping")
    return _finalize(reasons, warnings, rejected_rules)


def _validate_relationship(obj: Relationship) -> ValidationResult:
    reasons, warnings, rejected_rules = _base_entity_checks(obj, f"{obj.source_entity} {obj.relationship_type} {obj.target_entity}", minimum_chars=8)
    if obj.relationship_type not in RELATIONSHIP_VOCAB:
        reasons.append("Relationship type is outside the ontology vocabulary.")
        rejected_rules.append("relationship_unknown_type")
    if not obj.source_entity or not obj.target_entity:
        reasons.append("Relationship requires both source and target entities.")
        rejected_rules.append("relationship_missing_endpoint")
    if not obj.effect_direction:
        reasons.append("Relationship requires directional semantics.")
        rejected_rules.append("relationship_missing_direction")
    if len(obj.target_entity.split()) > 20 or _looks_like_sentence_chunk(obj.target_entity):
        reasons.append("Relationship target is malformed or sentence-like.")
        rejected_rules.append("relationship_malformed_target")
    if "state_transitions" in obj.domain_tags and not obj.target_entity_id:
        warnings.append("Transition-linked relationship target is unresolved and may need merge review.")
    return _finalize(reasons, warnings, rejected_rules)


def _validate_intervention(obj: Intervention) -> ValidationResult:
    reasons, warnings, rejected_rules = _base_entity_checks(obj, obj.name, minimum_chars=8)
    lowered = normalize_whitespace(obj.name).lower()
    if not any(re.match(rf"^{verb}\b", lowered) for verb in ACTION_VERBS):
        reasons.append("Intervention must describe an actionable environmental or behavioral modification.")
        rejected_rules.append("intervention_missing_action_verb")
    if len(lowered.split()) > 24:
        reasons.append("Intervention looks like generic explanatory prose.")
        rejected_rules.append("intervention_explanatory_prose")
    return _finalize(reasons, warnings, rejected_rules)


def _validate_kpi(obj: KPI) -> ValidationResult:
    reasons, warnings, rejected_rules = _base_entity_checks(obj, obj.operator_label, minimum_chars=5)
    haystack = f"{obj.operator_label} {obj.technical_definition} {obj.human_interpretation}".lower()
    if not any(term in haystack for term in MEASURABLE_TERMS):
        reasons.append("KPI lacks measurable evaluation intent.")
        rejected_rules.append("kpi_not_measurable")
    if "monitor" not in haystack and "measure" not in haystack and "track" not in haystack:
        warnings.append("KPI does not explicitly state monitoring intent.")
    return _finalize(reasons, warnings, rejected_rules)


def _validate_temporal_dynamic(obj: TemporalDynamic) -> ValidationResult:
    reasons, warnings, rejected_rules = _base_entity_checks(obj, obj.name, minimum_chars=4)
    combined = " ".join(
        [
            obj.transition_logic,
            obj.estimated_time_window,
            " ".join(obj.sequence_dependencies),
            " ".join(obj.state_progression),
            " ".join(obj.trigger_conditions),
        ]
    ).lower()
    has_transition_anchor = bool(
        (obj.canonical_transition_id and (obj.start_state_id or obj.start_state) and (obj.end_state_id or obj.end_state))
        or (obj.start_state and obj.end_state and len(obj.state_progression) >= 2)
    )
    if not has_transition_anchor and not any(term in combined for term in TEMPORAL_TERMS) and not obj.duration_minutes:
        reasons.append("Temporal dynamic must encode transition logic, duration, sequence dependency, or state progression.")
        rejected_rules.append("temporal_missing_transition_logic")
    if obj.source_role == "synthesis" and "state_transitions" in obj.domain_tags:
        if not obj.start_state_id or not obj.end_state_id:
            reasons.append("Transition dynamic must resolve known start and end states.")
            rejected_rules.append("transition_unresolved_states")
        if not obj.canonical_transition_id:
            warnings.append("Transition dynamic is unresolved against the canonical transition registry.")
    return _finalize(reasons, warnings, rejected_rules)


def _validate_evidence(obj: EvidenceObject) -> ValidationResult:
    reasons, warnings, rejected_rules = _base_entity_checks(obj, obj.claim, minimum_chars=12)
    if obj.source_type not in EVIDENCE_SOURCE_TYPES:
        reasons.append("Evidence source type is outside the supported evidence ontology.")
        rejected_rules.append("evidence_invalid_source_type")
    if not 0.0 <= obj.recommended_weight <= 1.0:
        reasons.append("Evidence recommended weight must be between 0 and 1.")
        rejected_rules.append("evidence_invalid_weight")
    if obj.source_role == "synthesis" and "mechanisms" in obj.domain_tags:
        if not (obj.canonical_mechanism_id or match_canonical_mechanism(obj.claim)[0]):
            warnings.append("Mechanism evidence did not map to a canonical mechanism.")
    return _finalize(reasons, warnings, rejected_rules)


def _validate_contradiction(obj: ContradictionObject) -> ValidationResult:
    reasons, warnings, rejected_rules = _base_entity_checks(obj, obj.contradiction_text, minimum_chars=12)
    if not obj.claim:
        reasons.append("Contradiction must preserve the originating claim.")
        rejected_rules.append("contradiction_missing_claim")
    if not obj.uncertainty_level:
        warnings.append("Contradiction is missing uncertainty calibration.")
    if obj.source_role == "synthesis" and "contradictions" in obj.domain_tags:
        if not (obj.applicable_contexts or obj.invalid_contexts or obj.audience_dependencies or obj.environment_dependencies):
            reasons.append("Contradiction must carry explicit reversal conditions or context boundaries.")
            rejected_rules.append("contradiction_missing_reversal_context")
    return _finalize(reasons, warnings, rejected_rules)


def _base_entity_checks(obj: OntologyObject, primary_text: str, *, minimum_chars: int) -> tuple[list[str], list[str], list[str]]:
    reasons: list[str] = []
    warnings: list[str] = []
    rejected_rules: list[str] = []
    text = normalize_whitespace(primary_text)

    if not text or len(text) < minimum_chars:
        reasons.append("Entity does not meet minimum content requirements.")
        rejected_rules.append("minimum_content")
    forbidden_hits = _forbidden_pattern_hits(f"{obj.raw_text}\n{text}\n{obj.normalized_text}")
    if forbidden_hits:
        reasons.append("Entity contains forbidden bibliography or link patterns.")
        rejected_rules.append("forbidden_patterns")
        warnings.append(f"Matched forbidden patterns: {', '.join(forbidden_hits[:4])}")
    if len(text.split()) <= 1:
        warnings.append("Entity is extremely short and may need manual review.")
    return reasons, warnings, rejected_rules


def _forbidden_pattern_hits(text: str) -> list[str]:
    lowered = text.lower()
    return [pattern for pattern in FORBIDDEN_PATTERNS if pattern in lowered]


def _looks_like_sentence_chunk(text: str) -> bool:
    lowered = text.lower()
    return len(text.split()) > 14 or any(token in lowered for token in (" because ", " which ", " therefore ", " however "))


def _finalize(reasons: list[str], warnings: list[str], rejected_rules: list[str]) -> ValidationResult:
    unique_reasons = list(dict.fromkeys(reasons))
    unique_warnings = list(dict.fromkeys(warnings))
    unique_rules = list(dict.fromkeys(rejected_rules))
    penalty = min(1.0, len(unique_reasons) * 0.22 + len(unique_warnings) * 0.06)
    score = max(0.0, round(1.0 - penalty, 3))
    return ValidationResult(
        is_valid=not unique_reasons,
        validation_score=score,
        reasons=unique_reasons,
        warnings=unique_warnings,
        rejected_rules=unique_rules,
    )
