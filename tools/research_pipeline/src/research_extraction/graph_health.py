from __future__ import annotations

from collections import Counter

import networkx as nx

from research_extraction.schemas import GraphHealthReport, OntologyObject
from research_extraction.utils import normalize_whitespace


def build_graph_health_report(
    graph: nx.DiGraph,
    objects: list[OntologyObject],
    *,
    raw_extraction_count: int,
    normalized_count: int,
    rejected_count: int,
    section_count: int,
) -> GraphHealthReport:
    labels = [normalize_whitespace(_object_label(obj)).lower() for obj in objects if normalize_whitespace(_object_label(obj))]
    label_counts = Counter(labels)
    duplicate_count = sum(count - 1 for count in label_counts.values() if count > 1)
    duplicate_density = duplicate_count / max(len(objects), 1)
    orphan_node_count = sum(1 for node in graph.nodes if graph.degree(node) == 0)
    low_confidence_ratio = sum(1 for obj in objects if obj.confidence_score < 0.7) / max(len(objects), 1)
    contradiction_density = sum(1 for obj in objects if getattr(obj, "contradictions", [])) / max(len(objects), 1)
    ontology_growth_rate = normalized_count / max(section_count, 1)
    normalization_compression_ratio = 1.0 - (normalized_count / max(raw_extraction_count, 1))
    invalid_extraction_rejection_rate = rejected_count / max(raw_extraction_count, 1)
    return GraphHealthReport(
        duplicate_density=round(duplicate_density, 3),
        orphan_node_count=orphan_node_count,
        low_confidence_ratio=round(low_confidence_ratio, 3),
        contradiction_density=round(contradiction_density, 3),
        ontology_growth_rate=round(ontology_growth_rate, 3),
        normalization_compression_ratio=round(normalization_compression_ratio, 3),
        invalid_extraction_rejection_rate=round(invalid_extraction_rejection_rate, 3),
    )


def _object_label(obj: OntologyObject) -> str:
    for field_name in ("name", "operator_label", "claim", "contradiction_text"):
        value = getattr(obj, field_name, "")
        if isinstance(value, str) and value:
            return value
    return ""
