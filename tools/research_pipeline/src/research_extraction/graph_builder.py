from __future__ import annotations

from pathlib import Path

import networkx as nx

from research_extraction.ids import build_canonical_id
from research_extraction.schemas import (
    BehavioralState,
    EvidenceObject,
    Intervention,
    KPI,
    Relationship,
    TemporalDynamic,
    Variable,
)
from research_extraction.utils import ensure_dir, write_json


def build_graph(
    variables: list[Variable],
    states: list[BehavioralState],
    relationships: list[Relationship],
    interventions: list[Intervention],
    kpis: list[KPI],
    temporal_dynamics: list[TemporalDynamic],
    evidence_objects: list[EvidenceObject],
) -> nx.DiGraph:
    graph = nx.DiGraph()

    for obj in [*variables, *states, *interventions, *kpis, *temporal_dynamics, *evidence_objects]:
        node_id, label, node_type = _node_parts(obj)
        graph.add_node(node_id, label=label, node_type=node_type, source_file=obj.relative_source_file)

    for rel in relationships:
        source_id = rel.source_entity_id or _unresolved_reference_id(rel.source_entity)
        target_id = rel.target_entity_id or _unresolved_reference_id(rel.target_entity)
        _ensure_reference_node(graph, source_id, rel.source_entity, rel.relative_source_file, rel.source_entity_id != "")
        _ensure_reference_node(graph, target_id, rel.target_entity, rel.relative_source_file, rel.target_entity_id != "")
        graph.add_edge(
            source_id,
            target_id,
            relationship_id=rel.relationship_id,
            relationship_type=rel.relationship_type,
            effect_direction=rel.effect_direction,
            confidence=rel.confidence_value,
            context_dependencies=rel.context_dependencies,
            environmental_modifiers=rel.environmental_modifiers,
            time_dependency=rel.time_dependency,
            lag_window_minutes=rel.lag_window_minutes,
            evidence_grade=rel.evidence_grade,
            section_id=rel.section_id,
        )

    for intervention in interventions:
        for state_id in intervention.affected_state_ids:
            graph.add_edge(intervention.intervention_id, state_id, relationship_type="affects_state")
        for variable_id in intervention.required_variable_ids:
            graph.add_edge(variable_id, intervention.intervention_id, relationship_type="required_for")

    for state in states:
        for variable_id in state.contributing_variable_ids:
            graph.add_edge(variable_id, state.state_id, relationship_type="contributes_to")
        for intervention_id in state.possible_intervention_ids:
            graph.add_edge(intervention_id, state.state_id, relationship_type="can_shift_state")
        for next_state_id in state.possible_next_state_ids:
            graph.add_edge(state.state_id, next_state_id, relationship_type="possible_state_transition", stability_score=state.stability_score)

    for kpi in kpis:
        for leading_id in kpi.leading_indicator_ids:
            graph.add_edge(leading_id, kpi.kpi_id, relationship_type="leading_indicator_for")
        for lagging_id in kpi.lagging_indicator_ids:
            graph.add_edge(lagging_id, kpi.kpi_id, relationship_type="lagging_indicator_for")
        for intervention_id in kpi.possible_intervention_ids:
            graph.add_edge(intervention_id, kpi.kpi_id, relationship_type="improves_kpi")

    for dynamic in temporal_dynamics:
        if dynamic.start_state_id and dynamic.end_state_id:
            graph.add_edge(
                dynamic.start_state_id,
                dynamic.dynamic_id,
                relationship_type="starts_transition",
                dynamic_id=dynamic.dynamic_id,
            )
            graph.add_edge(
                dynamic.dynamic_id,
                dynamic.end_state_id,
                relationship_type="ends_transition",
                dynamic_id=dynamic.dynamic_id,
            )
            graph.add_edge(
                dynamic.start_state_id,
                dynamic.end_state_id,
                relationship_type="temporal_transition",
                dynamic_id=dynamic.dynamic_id,
                transition_logic=dynamic.transition_logic,
                duration_minutes=",".join(str(value) for value in dynamic.duration_minutes),
            )

    for evidence in evidence_objects:
        for entity_id in evidence.linked_entity_ids:
            graph.add_edge(evidence.claim_id, entity_id, relationship_type="supports_entity")

    return graph


def export_graph(graph: nx.DiGraph, output_dir: Path) -> None:
    ensure_dir(output_dir)
    graph_json = nx.node_link_data(graph, edges="edges")
    write_json(output_dir / "ontology_graph.json", graph_json)
    nx.write_graphml(_graphml_safe_graph(graph), output_dir / "ontology_graph.graphml")


def _ensure_reference_node(graph: nx.DiGraph, node_id: str, label: str, source_file: str, resolved: bool) -> None:
    if graph.has_node(node_id):
        return
    graph.add_node(
        node_id,
        label=label,
        node_type="resolved_reference" if resolved else "unresolved_reference",
        source_file=source_file,
    )


def _unresolved_reference_id(label: str) -> str:
    return build_canonical_id("section", f"UNRESOLVED_{label}")


def _node_parts(obj) -> tuple[str, str, str]:
    if hasattr(obj, "variable_id"):
        return obj.variable_id, obj.name, "variable"
    if hasattr(obj, "state_id"):
        return obj.state_id, obj.name, "behavioral_state"
    if hasattr(obj, "intervention_id"):
        return obj.intervention_id, obj.name, "intervention"
    if hasattr(obj, "kpi_id"):
        return obj.kpi_id, obj.operator_label, "kpi"
    if hasattr(obj, "dynamic_id"):
        return obj.dynamic_id, obj.name, "temporal_dynamic"
    return obj.claim_id, obj.claim[:120], "evidence"


def _graphml_safe_graph(graph: nx.DiGraph) -> nx.DiGraph:
    safe = nx.DiGraph()
    for node_id, attrs in graph.nodes(data=True):
        safe.add_node(node_id, **{key: _graphml_safe_value(value) for key, value in attrs.items()})
    for source, target, attrs in graph.edges(data=True):
        safe.add_edge(source, target, **{key: _graphml_safe_value(value) for key, value in attrs.items()})
    return safe


def _graphml_safe_value(value):
    if isinstance(value, list):
        return " | ".join(str(item) for item in value)
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value).lower()
    return value
