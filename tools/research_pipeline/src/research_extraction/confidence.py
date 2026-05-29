from __future__ import annotations

from collections import Counter, defaultdict

from research_extraction.schemas import ConfidenceProfile, OntologyObject
from research_extraction.utils import normalize_whitespace


CONFIDENCE_WEIGHTS = {
    "extraction_confidence": 0.35,
    "ontology_validity": 0.3,
    "cross_document_support": 0.15,
    "operational_relevance": 0.2,
}
BASE_CONFIDENCE_PRIOR = 0.12


def build_confidence_profile(
    extraction_confidence: float,
    ontology_validity: float = 0.5,
    cross_document_support: float = 0.0,
    operational_relevance: float = 0.5,
) -> ConfidenceProfile:
    extraction_confidence = _clamp(extraction_confidence)
    ontology_validity = _clamp(ontology_validity)
    cross_document_support = _clamp(cross_document_support)
    operational_relevance = _clamp(operational_relevance)
    final_confidence = (
        BASE_CONFIDENCE_PRIOR
        +
        extraction_confidence * CONFIDENCE_WEIGHTS["extraction_confidence"]
        + ontology_validity * CONFIDENCE_WEIGHTS["ontology_validity"]
        + cross_document_support * CONFIDENCE_WEIGHTS["cross_document_support"]
        + operational_relevance * CONFIDENCE_WEIGHTS["operational_relevance"]
    )
    return ConfidenceProfile(
        extraction_confidence=round(extraction_confidence, 3),
        ontology_validity=round(ontology_validity, 3),
        cross_document_support=round(cross_document_support, 3),
        operational_relevance=round(operational_relevance, 3),
        final_confidence=round(final_confidence, 3),
    )


def with_confidence_updates(
    obj: OntologyObject,
    *,
    extraction_confidence: float | None = None,
    ontology_validity: float | None = None,
    cross_document_support: float | None = None,
    operational_relevance: float | None = None,
) -> OntologyObject:
    profile = build_confidence_profile(
        extraction_confidence=obj.confidence.extraction_confidence if extraction_confidence is None else extraction_confidence,
        ontology_validity=obj.confidence.ontology_validity if ontology_validity is None else ontology_validity,
        cross_document_support=obj.confidence.cross_document_support if cross_document_support is None else cross_document_support,
        operational_relevance=obj.confidence.operational_relevance if operational_relevance is None else operational_relevance,
    )
    return obj.model_copy(update={"confidence": profile})


def calibrate_cross_document_support(objects: list[OntologyObject]) -> list[OntologyObject]:
    label_to_files: dict[str, set[str]] = defaultdict(set)
    for obj in objects:
        label = object_display_name(obj)
        key = normalize_whitespace(label).lower()
        if key:
            label_to_files[key].add(obj.relative_source_file)

    updated: list[OntologyObject] = []
    for obj in objects:
        label = normalize_whitespace(object_display_name(obj)).lower()
        doc_count = len(label_to_files.get(label, set()))
        cross_support = min(1.0, 0.25 + (doc_count * 0.25)) if label else 0.0
        updated.append(with_confidence_updates(obj, cross_document_support=cross_support))
    return updated


def infer_operational_relevance_score(obj: OntologyObject) -> float:
    signals: list[str] = []
    if hasattr(obj, "operational_relevance"):
        value = getattr(obj, "operational_relevance")
        if isinstance(value, list):
            signals.extend(value)
        elif isinstance(value, str):
            signals.append(value)
    if hasattr(obj, "behavioral_relevance"):
        signals.extend(getattr(obj, "behavioral_relevance", []))
    if hasattr(obj, "possible_interventions"):
        signals.extend(getattr(obj, "possible_interventions", []))
    if hasattr(obj, "expected_effects"):
        signals.extend(getattr(obj, "expected_effects", []))
    distinct = len({normalize_whitespace(item).lower() for item in signals if normalize_whitespace(item)})
    return round(min(1.0, 0.45 + distinct * 0.1), 3) if distinct else 0.45


def object_display_name(obj: OntologyObject) -> str:
    for field_name in ("name", "operator_label", "claim", "contradiction_text"):
        value = getattr(obj, field_name, "")
        if isinstance(value, str) and normalize_whitespace(value):
            return value
    return ""


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
