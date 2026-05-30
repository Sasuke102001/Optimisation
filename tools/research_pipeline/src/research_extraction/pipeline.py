from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
import re

from rapidfuzz import fuzz

from research_extraction.classification import classify_sections
from research_extraction.confidence import calibrate_cross_document_support
from research_extraction.config import PipelineConfig
from research_extraction.coverage import build_coverage_report
from research_extraction.extractors import extract_all
from research_extraction.graph_health import build_graph_health_report
from research_extraction.graph_builder import build_graph, export_graph
from research_extraction.ids import build_canonical_id
from research_extraction.ingestion import ingest_research_directory
from research_extraction.normalization import normalize_objects
from research_extraction.profile_extractors import seed_profile_objects
from research_extraction.registries import load_canonical_transitions
from research_extraction.rag import build_rag_chunks
from research_extraction.review import build_review_queue, promote_approved_objects
from research_extraction.schemas import (
    BehavioralState,
    ContradictionObject,
    EvidenceObject,
    Intervention,
    KPI,
    OntologyObject,
    PipelineOutputs,
    Relationship,
    TemporalDynamic,
    Variable,
)
from research_extraction.utils import ensure_dir, normalize_whitespace, write_json, write_jsonl
from research_extraction.validation import validate_bundle


def _default_research_dir() -> Path:
    # pipeline.py lives at tools/research_pipeline/src/research_extraction/
    # parents[4] = Module 3 - Optimisation/
    return Path(__file__).resolve().parents[4] / "backend" / "research"


def _default_output_dir() -> Path:
    # parents[4] = Module 3 - Optimisation/
    return Path(__file__).resolve().parents[4] / "backend" / "research_pipeline" / "output"


def _build_run_summary(outputs: PipelineOutputs, approved_objects: list[dict]) -> dict:
    return {
        "section_count": len(outputs.sections),
        "classification_count": len(outputs.classifications),
        "variable_count": len(outputs.variables),
        "state_count": len(outputs.states),
        "relationship_count": len(outputs.relationships),
        "intervention_count": len(outputs.interventions),
        "kpi_count": len(outputs.kpis),
        "temporal_dynamic_count": len(outputs.temporal_dynamics),
        "evidence_count": len(outputs.evidence_objects),
        "contradiction_count": len(outputs.contradiction_objects),
        "review_queue_count": len(outputs.review_queue),
        "rejected_entity_count": len(outputs.rejected_entities),
        "rag_chunk_count": len(outputs.rag_chunks),
        "approved_ontology_count": len(approved_objects),
        "missing_canonical_states": len(outputs.coverage_report.missing_canonical_states) if outputs.coverage_report else 0,
        "missing_canonical_transitions": len(outputs.coverage_report.missing_canonical_transitions) if outputs.coverage_report else 0,
        "missing_canonical_mechanisms": len(outputs.coverage_report.missing_canonical_mechanisms) if outputs.coverage_report else 0,
    }


def run_pipeline(config: PipelineConfig) -> PipelineOutputs:
    ensure_dir(config.output_dir)
    sections = ingest_research_directory(config)
    classifications = classify_sections(sections)
    classification_by_section = {item.section_id: item for item in classifications}

    variables: list[Variable] = []
    states: list[BehavioralState] = []
    relationships: list[Relationship] = []
    interventions: list[Intervention] = []
    kpis: list[KPI] = []
    temporal_dynamics: list[TemporalDynamic] = []
    evidence_objects: list[EvidenceObject] = []
    contradiction_objects: list[ContradictionObject] = []

    from concurrent.futures import ThreadPoolExecutor
    import threading

    total_sections = len(sections)
    counter = 0
    lock = threading.Lock()

    print(f"[research-extraction] extracting from {total_sections} sections using ThreadPoolExecutor(max_workers=10)...", flush=True)

    def process_section(section):
        nonlocal counter
        res = extract_all(section, classification_by_section[section.section_id], config)
        with lock:
            counter += 1
            if counter % 50 == 0 or counter == total_sections:
                print(f"[research-extraction] processed {counter}/{total_sections} sections...", flush=True)
        return res

    with ThreadPoolExecutor(max_workers=10) as executor:
        bundles = list(executor.map(process_section, sections))

    for bundle in bundles:
        variables.extend(bundle.variables)
        states.extend(bundle.states)
        relationships.extend(bundle.relationships)
        interventions.extend(bundle.interventions)
        kpis.extend(bundle.kpis)
        temporal_dynamics.extend(bundle.temporal_dynamics)
        evidence_objects.extend(bundle.evidence_objects)
        contradiction_objects.extend(bundle.contradiction_objects)

    seeded_bundle = seed_profile_objects(sections, config)
    variables.extend(seeded_bundle["variables"])
    states.extend(seeded_bundle["states"])
    relationships.extend(seeded_bundle["relationships"])
    interventions.extend(seeded_bundle["interventions"])
    kpis.extend(seeded_bundle["kpis"])
    temporal_dynamics.extend(seeded_bundle["temporal_dynamics"])
    evidence_objects.extend(seeded_bundle["evidence_objects"])
    contradiction_objects.extend(seeded_bundle["contradiction_objects"])

    raw_objects: list[OntologyObject] = [
        *variables,
        *states,
        *relationships,
        *interventions,
        *kpis,
        *temporal_dynamics,
        *evidence_objects,
        *contradiction_objects,
    ]
    raw_extraction_count = len(raw_objects)
    validation_outcome = validate_bundle(raw_objects)
    validated_objects = validation_outcome.accepted

    variables = [item for item in validated_objects if isinstance(item, Variable)]
    states = [item for item in validated_objects if isinstance(item, BehavioralState)]
    relationships = [item for item in validated_objects if isinstance(item, Relationship)]
    interventions = [item for item in validated_objects if isinstance(item, Intervention)]
    kpis = [item for item in validated_objects if isinstance(item, KPI)]
    temporal_dynamics = [item for item in validated_objects if isinstance(item, TemporalDynamic)]
    evidence_objects = [item for item in validated_objects if isinstance(item, EvidenceObject)]
    contradiction_objects = [item for item in validated_objects if isinstance(item, ContradictionObject)]

    normalization_decisions = []
    variables, decisions = normalize_objects("variable", variables, config, lambda item: item.name, lambda item: item.variable_id)
    normalization_decisions.extend(decisions)
    states, decisions = normalize_objects("behavioral_state", states, config, lambda item: item.name, lambda item: item.state_id)
    normalization_decisions.extend(decisions)
    interventions, decisions = normalize_objects("intervention", interventions, config, lambda item: item.name, lambda item: item.intervention_id)
    normalization_decisions.extend(decisions)
    kpis, decisions = normalize_objects("kpi", kpis, config, lambda item: item.operator_label, lambda item: item.kpi_id)
    normalization_decisions.extend(decisions)
    temporal_dynamics, decisions = normalize_objects("temporal_dynamic", temporal_dynamics, config, lambda item: item.name, lambda item: item.dynamic_id)
    normalization_decisions.extend(decisions)
    evidence_objects, decisions = normalize_objects("evidence", evidence_objects, config, lambda item: item.claim, lambda item: item.claim_id)
    normalization_decisions.extend(decisions)
    contradiction_objects, decisions = normalize_objects(
        "contradiction",
        contradiction_objects,
        config,
        lambda item: f"{item.claim} {item.contradiction_text}",
        lambda item: item.contradiction_id,
    )
    normalization_decisions.extend(decisions)

    variables, states, relationships, interventions, kpis, temporal_dynamics, evidence_objects, contradiction_objects = _wire_objects(
        variables,
        states,
        relationships,
        interventions,
        kpis,
        temporal_dynamics,
        evidence_objects,
        contradiction_objects,
    )

    entity_registry = _build_entity_registry(variables, states, interventions, kpis)
    states = _link_states(states, entity_registry)
    interventions = _link_interventions(interventions, entity_registry)
    kpis = _link_kpis(kpis, entity_registry)
    temporal_dynamics = _link_temporal_dynamics(temporal_dynamics, entity_registry)
    evidence_objects = _link_evidence(evidence_objects, entity_registry)
    contradiction_objects = _link_contradictions(contradiction_objects, entity_registry)
    relationships = _link_relationships(relationships, entity_registry)
    relationships = _dedupe_by_id(relationships, "relationship_id")

    all_objects: list[OntologyObject] = [
        *variables,
        *states,
        *relationships,
        *interventions,
        *kpis,
        *temporal_dynamics,
        *evidence_objects,
        *contradiction_objects,
    ]
    all_objects = calibrate_cross_document_support(all_objects)
    variables = [item for item in all_objects if isinstance(item, Variable)]
    states = [item for item in all_objects if isinstance(item, BehavioralState)]
    relationships = [item for item in all_objects if isinstance(item, Relationship)]
    interventions = [item for item in all_objects if isinstance(item, Intervention)]
    kpis = [item for item in all_objects if isinstance(item, KPI)]
    temporal_dynamics = [item for item in all_objects if isinstance(item, TemporalDynamic)]
    evidence_objects = [item for item in all_objects if isinstance(item, EvidenceObject)]
    contradiction_objects = [item for item in all_objects if isinstance(item, ContradictionObject)]

    review_queue = build_review_queue(all_objects, normalization_decisions, config)
    approved_objects, promotion_summary = promote_approved_objects(all_objects, review_queue, config.review_decisions_file)
    rag_chunks = build_rag_chunks(variables, states, relationships, interventions, kpis, temporal_dynamics, evidence_objects)
    normalized_count = len(all_objects)
    graph = build_graph(
        variables,
        states,
        relationships,
        interventions,
        kpis,
        temporal_dynamics,
        evidence_objects,
    )
    graph_health = build_graph_health_report(
        graph,
        all_objects,
        raw_extraction_count=raw_extraction_count,
        normalized_count=normalized_count,
        rejected_count=len(validation_outcome.rejected),
        section_count=len(sections),
    )
    coverage_report = build_coverage_report(all_objects)

    outputs = PipelineOutputs(
        sections=sections,
        classifications=classifications,
        variables=variables,
        states=states,
        relationships=relationships,
        interventions=interventions,
        kpis=kpis,
        temporal_dynamics=temporal_dynamics,
        evidence_objects=evidence_objects,
        contradiction_objects=contradiction_objects,
        review_queue=review_queue,
        normalization_decisions=normalization_decisions,
        rag_chunks=rag_chunks,
        validation_report=validation_outcome.report,
        rejected_entities=validation_outcome.rejected,
        graph_health=graph_health,
        coverage_report=coverage_report,
    )
    write_outputs(config, outputs, approved_objects, promotion_summary, graph)
    return outputs


def write_outputs(
    config: PipelineConfig,
    outputs: PipelineOutputs,
    approved_objects: list[dict],
    promotion_summary: dict,
    graph,
) -> None:
    base = config.output_dir
    ensure_dir(base)

    write_json(base / "sections.json", [item.model_dump() for item in outputs.sections])
    write_json(base / "section_classifications.json", [item.model_dump() for item in outputs.classifications])
    write_json(base / "variables" / "variables.json", [item.model_dump() for item in outputs.variables])
    write_json(base / "variables.json", [item.model_dump() for item in outputs.variables])
    write_json(base / "states" / "behavioral_states.json", [item.model_dump() for item in outputs.states])
    write_json(base / "behavioral_states.json", [item.model_dump() for item in outputs.states])
    write_json(base / "relationships" / "causal_relationships.json", [item.model_dump() for item in outputs.relationships])
    write_json(base / "causal_relationships.json", [item.model_dump() for item in outputs.relationships])
    write_json(base / "interventions" / "interventions.json", [item.model_dump() for item in outputs.interventions])
    write_json(base / "interventions.json", [item.model_dump() for item in outputs.interventions])
    write_json(base / "kpis" / "kpis.json", [item.model_dump() for item in outputs.kpis])
    write_json(base / "kpis.json", [item.model_dump() for item in outputs.kpis])
    write_json(base / "evidence" / "evidence_registry.json", [item.model_dump() for item in outputs.evidence_objects])
    write_json(base / "evidence_registry.json", [item.model_dump() for item in outputs.evidence_objects])
    write_json(base / "temporal_dynamics" / "temporal_dynamics.json", [item.model_dump() for item in outputs.temporal_dynamics])
    write_json(base / "temporal_dynamics.json", [item.model_dump() for item in outputs.temporal_dynamics])
    write_json(base / "contradictions" / "contradictions.json", [item.model_dump() for item in outputs.contradiction_objects])
    write_json(base / "contradictions.json", [item.model_dump() for item in outputs.contradiction_objects])
    review_grouped = _group_review_queue(outputs.review_queue, outputs.rejected_entities)
    write_json(base / "review_queue" / "review_queue.json", review_grouped)
    write_json(base / "review_queue.json", review_grouped)
    write_json(base / "review_queue" / "approved_ontology.json", approved_objects)
    write_json(base / "approved_ontology.json", approved_objects)
    write_json(base / "review_queue" / "promotion_summary.json", promotion_summary)
    write_json(base / "promotion_summary.json", promotion_summary)
    write_json(base / "normalization_decisions.json", [item.model_dump() for item in outputs.normalization_decisions])
    write_json(base / "rag_chunks.json", [item.model_dump() for item in outputs.rag_chunks])
    write_jsonl(base / "rag_chunks.jsonl", [item.model_dump() for item in outputs.rag_chunks])
    write_json(base / "validation_report.json", [item.model_dump() for item in outputs.validation_report])
    write_json(base / "rejected_entities.json", [item.model_dump() for item in outputs.rejected_entities])
    if outputs.graph_health is not None:
        write_json(base / "graph_health.json", outputs.graph_health.model_dump())
    if outputs.coverage_report is not None:
        write_json(base / "coverage_report.json", outputs.coverage_report.model_dump())
    write_json(
        base / "canonical_knowledge_store.json",
        {
            "variables": [item.model_dump() for item in outputs.variables],
            "states": [item.model_dump() for item in outputs.states],
            "relationships": [item.model_dump() for item in outputs.relationships],
            "interventions": [item.model_dump() for item in outputs.interventions],
            "kpis": [item.model_dump() for item in outputs.kpis],
            "temporal_dynamics": [item.model_dump() for item in outputs.temporal_dynamics],
            "evidence": [item.model_dump() for item in outputs.evidence_objects],
            "contradictions": [item.model_dump() for item in outputs.contradiction_objects],
        },
    )

    export_graph(graph, base)

    summary = _build_run_summary(outputs, approved_objects)
    write_json(base / "run_summary.json", summary)


def _build_entity_registry(
    variables: list[Variable],
    states: list[BehavioralState],
    interventions: list[Intervention],
    kpis: list[KPI],
) -> dict[str, tuple[str, str]]:
    registry: dict[str, tuple[str, str]] = {}
    for item, object_id, label, aliases in (
        *((variable, variable.variable_id, variable.name, variable.aliases) for variable in variables),
        *((state, state.state_id, state.name, state.aliases) for state in states),
        *((intervention, intervention.intervention_id, intervention.name, intervention.aliases) for intervention in interventions),
        *((kpi, kpi.kpi_id, kpi.operator_label, kpi.aliases) for kpi in kpis),
    ):
        del item
        for value in {label, *aliases}:
            normalized = normalize_whitespace(value).lower()
            if normalized:
                registry[normalized] = (object_id, label)
    return registry


def _link_states(states: list[BehavioralState], registry: dict[str, tuple[str, str]]) -> list[BehavioralState]:
    linked: list[BehavioralState] = []
    for state in states:
        linked.append(
            state.model_copy(
                update={
                    "contributing_variable_ids": _resolve_entity_ids(state.contributing_variables, registry, prefixes=("VAR_",)),
                    "possible_intervention_ids": _resolve_entity_ids(state.possible_interventions, registry, prefixes=("INT_",)),
                    "possible_next_state_ids": _resolve_entity_ids(state.possible_next_states, registry, prefixes=("ST_",)),
                }
            )
        )
    return linked


def _link_interventions(interventions: list[Intervention], registry: dict[str, tuple[str, str]]) -> list[Intervention]:
    linked: list[Intervention] = []
    for intervention in interventions:
        linked.append(
            intervention.model_copy(
                update={
                    "affected_state_ids": _resolve_entity_ids(intervention.affected_states, registry, prefixes=("ST_",)),
                    "required_variable_ids": _resolve_entity_ids(intervention.required_variables, registry, prefixes=("VAR_",)),
                }
            )
        )
    return linked


def _link_kpis(kpis: list[KPI], registry: dict[str, tuple[str, str]]) -> list[KPI]:
    linked: list[KPI] = []
    for kpi in kpis:
        linked.append(
            kpi.model_copy(
                update={
                    "leading_indicator_ids": _resolve_entity_ids(kpi.leading_indicators, registry),
                    "lagging_indicator_ids": _resolve_entity_ids(kpi.lagging_indicators, registry),
                    "possible_intervention_ids": _resolve_entity_ids(kpi.possible_interventions, registry, prefixes=("INT_",)),
                }
            )
        )
    return linked


def _link_temporal_dynamics(
    temporal_dynamics: list[TemporalDynamic],
    registry: dict[str, tuple[str, str]],
) -> list[TemporalDynamic]:
    linked: list[TemporalDynamic] = []
    canonical_transitions = load_canonical_transitions()
    for dynamic in temporal_dynamics:
        start_state_id = _resolve_entity_id(dynamic.start_state, registry, prefixes=("ST_",))
        end_state_id = _resolve_entity_id(dynamic.end_state, registry, prefixes=("ST_",))
        if dynamic.canonical_transition_id and dynamic.canonical_transition_id in canonical_transitions:
            payload = canonical_transitions[dynamic.canonical_transition_id]
            start_state_id = start_state_id or str(payload.get("start_state_id", ""))
            end_state_id = end_state_id or str(payload.get("end_state_id", ""))
        if not start_state_id and dynamic.state_progression:
            start_state_id = _resolve_entity_id(dynamic.state_progression[0], registry, prefixes=("ST_",))
        if not end_state_id and len(dynamic.state_progression) > 1:
            end_state_id = _resolve_entity_id(dynamic.state_progression[-1], registry, prefixes=("ST_",))
        if not start_state_id:
            start_state_id = _resolve_entity_id(" ".join(dynamic.heading_path), registry, prefixes=("ST_",))
        if not end_state_id:
            end_state_id = _resolve_entity_id(" ".join(reversed(dynamic.heading_path)), registry, prefixes=("ST_",))
        linked.append(dynamic.model_copy(update={"start_state_id": start_state_id, "end_state_id": end_state_id}))
    return linked


def _link_evidence(evidence_objects: list[EvidenceObject], registry: dict[str, tuple[str, str]]) -> list[EvidenceObject]:
    linked: list[EvidenceObject] = []
    for evidence in evidence_objects:
        candidates = [evidence.claim, *evidence.evidence_notes]
        inferred_ids = _resolve_entity_ids_from_text(" ".join(candidates + evidence.heading_path), registry)
        section_context_ids = _resolve_entity_ids_from_text(" ".join(evidence.heading_path), registry)
        combined_ids = _dedupe_strings([*_resolve_entity_ids(candidates, registry), *inferred_ids, *section_context_ids])
        linked.append(
            evidence.model_copy(
                update={
                    "linked_entity_ids": combined_ids[:6],
                }
            )
        )
    return linked


def _link_contradictions(
    contradiction_objects: list[ContradictionObject],
    registry: dict[str, tuple[str, str]],
) -> list[ContradictionObject]:
    linked: list[ContradictionObject] = []
    for contradiction in contradiction_objects:
        linked.append(
            contradiction.model_copy(
                update={
                    "affected_entity_ids": _resolve_entity_ids(contradiction.affected_entities, registry),
                }
            )
        )
    return linked


def _link_relationships(
    relationships: list[Relationship],
    registry: dict[str, tuple[str, str]],
) -> list[Relationship]:
    linked: list[Relationship] = []
    for relationship in relationships:
        source_entity_id = _resolve_entity_id(relationship.source_entity, registry)
        target_entity_id = _resolve_entity_id(relationship.target_entity, registry)
        relationship_id = build_canonical_id(
            "relationship",
            f"{source_entity_id or relationship.source_entity}_{relationship.relationship_type}_{target_entity_id or relationship.target_entity}",
        )
        linked.append(
            relationship.model_copy(
                update={
                    "relationship_id": relationship_id,
                    "source_entity_id": source_entity_id,
                    "target_entity_id": target_entity_id,
                }
            )
        )
    return linked


def _resolve_entity_ids(
    values: list[str],
    registry: dict[str, tuple[str, str]],
    prefixes: tuple[str, ...] | None = None,
) -> list[str]:
    resolved: list[str] = []
    for value in values:
        entity_id = _resolve_entity_id(value, registry, prefixes=prefixes)
        if entity_id and entity_id not in resolved:
            resolved.append(entity_id)
    return resolved


def _resolve_entity_id(
    value: str,
    registry: dict[str, tuple[str, str]],
    prefixes: tuple[str, ...] | None = None,
) -> str:
    normalized = normalize_whitespace(value).lower()
    if not normalized:
        return ""
    exact = registry.get(normalized)
    if exact and _prefix_allowed(exact[0], prefixes):
        return exact[0]

    best_id = ""
    best_score = 0.0
    for alias, (candidate_id, _) in registry.items():
        if not _prefix_allowed(candidate_id, prefixes):
            continue
        if alias in normalized or normalized in alias:
            score = 0.96
        else:
            score = fuzz.partial_ratio(normalized, alias) / 100.0
        if score > best_score:
            best_score = score
            best_id = candidate_id
    return best_id if best_score >= 0.9 else ""


def _prefix_allowed(candidate_id: str, prefixes: tuple[str, ...] | None) -> bool:
    if prefixes is None:
        return True
    return candidate_id.startswith(prefixes)


def _dedupe_by_id(items: list[OntologyObject], field_name: str) -> list[OntologyObject]:
    seen: set[str] = set()
    deduped: list[OntologyObject] = []
    for item in items:
        object_id = getattr(item, field_name)
        if object_id in seen:
            continue
        seen.add(object_id)
        deduped.append(item)
    return deduped


def _group_review_queue(review_queue, rejected_entities):
    grouped = {
        "auto_rejected": [item.model_dump() for item in rejected_entities],
        "low_confidence": [],
        "ontology_conflict": [],
        "contradiction_review": [],
        "merge_review": [],
        "promotion_review": [],
    }
    for item in review_queue:
        grouped[item.review_bucket].append(item.model_dump())
    return grouped


def _wire_objects(
    variables: list[Variable],
    states: list[BehavioralState],
    relationships: list[Relationship],
    interventions: list[Intervention],
    kpis: list[KPI],
    temporal_dynamics: list[TemporalDynamic],
    evidence_objects: list[EvidenceObject],
    contradiction_objects: list[ContradictionObject],
) -> tuple[
    list[Variable],
    list[BehavioralState],
    list[Relationship],
    list[Intervention],
    list[KPI],
    list[TemporalDynamic],
    list[EvidenceObject],
    list[ContradictionObject],
]:
    context_states = _objects_by_context(states, "name")
    context_variables = _objects_by_context(variables, "name")
    context_interventions = _objects_by_context(interventions, "name")
    context_kpis = _objects_by_context(kpis, "operator_label")

    wired_interventions: list[Intervention] = []
    for intervention in interventions:
        context_key = _context_key(intervention.relative_source_file, intervention.heading_path)
        related_states = context_states.get(context_key, [])
        related_variables = context_variables.get(context_key, [])
        state_candidates = _infer_context_labels(
            intervention.name,
            intervention.expected_effects + intervention.trigger_conditions + intervention.affected_states,
            related_states,
        )
        variable_candidates = _infer_context_labels(
            intervention.name,
            intervention.expected_effects + intervention.trigger_conditions + intervention.required_variables,
            related_variables,
        )
        wired_interventions.append(
            intervention.model_copy(
                update={
                    "affected_states": _prefer_existing_or_inferred(intervention.affected_states, state_candidates),
                    "required_variables": _prefer_existing_or_inferred(intervention.required_variables, variable_candidates),
                }
            )
        )

    wired_kpis: list[KPI] = []
    for kpi in kpis:
        context_key = _context_key(kpi.relative_source_file, kpi.heading_path)
        related_states = context_states.get(context_key, [])
        related_variables = context_variables.get(context_key, [])
        related_interventions = context_interventions.get(context_key, [])
        related_kpis = [item for item in context_kpis.get(context_key, []) if item != kpi.operator_label]
        transition_states = _transition_states_from_heading(kpi.heading_path)
        leading_candidates = _infer_context_labels(
            kpi.operator_label,
            kpi.leading_indicators + transition_states,
            related_variables + related_states,
        )
        if not leading_candidates and transition_states:
            leading_candidates = transition_states[:1]
        if not leading_candidates and related_variables:
            leading_candidates = related_variables[:2]
        if not leading_candidates and related_states:
            leading_candidates = related_states[:1]
        lagging_candidates = _infer_context_labels(
            kpi.operator_label,
            kpi.lagging_indicators + transition_states,
            related_states + related_kpis,
        )
        if len(transition_states) >= 2 and not lagging_candidates:
            lagging_candidates = transition_states[1:2]
        if not lagging_candidates and related_states:
            lagging_candidates = related_states[-1:]
        if not lagging_candidates and related_kpis:
            lagging_candidates = related_kpis[:1]
        intervention_candidates = _infer_context_labels(
            kpi.operator_label,
            kpi.possible_interventions + transition_states,
            related_interventions,
        )
        if not intervention_candidates and related_interventions:
            intervention_candidates = related_interventions[:3]
        wired_kpis.append(
            kpi.model_copy(
                update={
                    "leading_indicators": _prefer_existing_or_inferred(kpi.leading_indicators, leading_candidates),
                    "lagging_indicators": _prefer_existing_or_inferred(kpi.lagging_indicators, lagging_candidates),
                    "possible_interventions": _prefer_existing_or_inferred(kpi.possible_interventions, intervention_candidates),
                }
            )
        )

    wired_evidence: list[EvidenceObject] = []
    for evidence in evidence_objects:
        context_key = _context_key(evidence.relative_source_file, evidence.heading_path)
        related_labels = [
            *context_states.get(context_key, []),
            *context_variables.get(context_key, []),
            *context_interventions.get(context_key, []),
            *context_kpis.get(context_key, []),
        ]
        inferred_notes = _infer_context_labels(evidence.claim, evidence.evidence_notes, related_labels)
        if not inferred_notes:
            inferred_notes = related_labels[:3]
        wired_evidence.append(
            evidence.model_copy(
                update={
                    "evidence_notes": _prefer_existing_or_inferred(evidence.evidence_notes, inferred_notes, limit=6),
                }
            )
        )

    return variables, states, relationships, wired_interventions, wired_kpis, temporal_dynamics, wired_evidence, contradiction_objects


def _objects_by_context(objects: list[OntologyObject], label_field: str) -> dict[tuple[str, tuple[str, ...]], list[str]]:
    grouped: dict[tuple[str, tuple[str, ...]], list[str]] = defaultdict(list)
    for obj in objects:
        key = _context_key(obj.relative_source_file, obj.heading_path)
        label = normalize_whitespace(str(getattr(obj, label_field, "")))
        if label and label not in grouped[key]:
            grouped[key].append(label)
    return grouped


def _context_key(relative_source_file: str, heading_path: list[str]) -> tuple[str, tuple[str, ...]]:
    if len(heading_path) > 1:
        return relative_source_file, tuple(heading_path[:-1])
    return relative_source_file, tuple(heading_path)


def _infer_context_labels(primary_text: str, seed_texts: list[str], candidates: list[str]) -> list[str]:
    joined = " ".join([primary_text, *seed_texts])
    normalized = normalize_whitespace(joined).lower()
    matched: list[str] = []
    for candidate in candidates:
        normalized_candidate = normalize_whitespace(candidate).lower()
        if not normalized_candidate:
            continue
        if _text_contains_label(normalized, normalized_candidate):
            matched.append(candidate)
    return _dedupe_strings(matched)[:4]


def _text_contains_label(text: str, label: str) -> bool:
    if len(label) <= 4 and label.isalpha():
        return bool(re.search(rf"\b{re.escape(label)}\b", text))
    return label in text


def _prefer_existing_or_inferred(existing: list[str], inferred: list[str], *, limit: int = 4) -> list[str]:
    return _dedupe_strings([*existing, *inferred])[:limit]


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        normalized = normalize_whitespace(value)
        if not normalized:
            continue
        lowered = normalized.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        deduped.append(normalized)
    return deduped


def _transition_states_from_heading(heading_path: list[str]) -> list[str]:
    for part in heading_path:
        if "->" in part or "â†’" in part:
            states = [normalize_whitespace(piece) for piece in re.split(r"->|â†’", part) if normalize_whitespace(piece)]
            if states:
                cleaned = [re.sub(r"^State\s+\d+:\s*", "", value, flags=re.IGNORECASE) for value in states]
                return [normalize_whitespace(value) for value in cleaned if normalize_whitespace(value)]
    return []


def _resolve_entity_ids_from_text(
    text: str,
    registry: dict[str, tuple[str, str]],
    prefixes: tuple[str, ...] | None = None,
) -> list[str]:
    normalized = normalize_whitespace(text).lower()
    if not normalized:
        return []
    matches: list[str] = []
    for alias, (candidate_id, _) in registry.items():
        if not _prefix_allowed(candidate_id, prefixes):
            continue
        if _text_contains_label(normalized, alias):
            matches.append(candidate_id)
    return _dedupe_strings(matches)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Research extraction pipeline")
    parser.add_argument(
        "--research-dir",
        type=Path,
        default=_default_research_dir(),
        help="Research directory to ingest. Defaults to the workspace's Module 3 research folder.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=_default_output_dir(),
        help="Output directory for generated artifacts. Defaults to Research Extraction Pipeline/output.",
    )
    parser.add_argument("--llm-provider", default="none", choices=["none", "openai", "nvidia"])
    parser.add_argument("--llm-model", default="")
    parser.add_argument("--llm-base-url", default="")
    parser.add_argument("--review-decisions-file", type=Path, default=None)
    parser.add_argument("--enable-embeddings", action="store_true")
    parser.add_argument("--extractor-version", default="0.1.0")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    config = PipelineConfig(
        research_dir=args.research_dir,
        output_dir=args.output_dir,
        review_decisions_file=args.review_decisions_file,
        llm_provider=args.llm_provider,
        llm_model=args.llm_model,
        llm_base_url=args.llm_base_url,
        enable_embeddings=args.enable_embeddings,
        extractor_version=args.extractor_version,
    )
    print(f"[research-extraction] ingesting: {config.research_dir}")
    print(f"[research-extraction] writing to: {config.output_dir}")
    print(
        "[research-extraction] llm provider: "
        f"{config.llm_provider}"
        + (" with embeddings" if config.enable_embeddings else "")
    )
    outputs = run_pipeline(config)
    print(
        "[research-extraction] complete: "
        f"sections={len(outputs.sections)}, "
        f"variables={len(outputs.variables)}, "
        f"states={len(outputs.states)}, "
        f"relationships={len(outputs.relationships)}, "
        f"interventions={len(outputs.interventions)}, "
        f"kpis={len(outputs.kpis)}, "
        f"review_queue={len(outputs.review_queue)}"
    )
    print(f"[research-extraction] summary: {config.output_dir / 'run_summary.json'}")
    return 0
