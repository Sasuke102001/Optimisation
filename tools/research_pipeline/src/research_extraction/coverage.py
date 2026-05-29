from __future__ import annotations

from collections import defaultdict

from research_extraction.registries import load_canonical_mechanisms, load_canonical_states, load_canonical_transitions
from research_extraction.research_profiles import RESEARCH_SOURCE_PROFILES
from research_extraction.schemas import BehavioralState, ContradictionObject, CoverageReport, OntologyObject, TemporalDynamic


def build_coverage_report(objects: list[OntologyObject]) -> CoverageReport:
    state_hits = {obj.canonical_state_id for obj in objects if getattr(obj, "canonical_state_id", None)}
    transition_hits = {obj.canonical_transition_id for obj in objects if getattr(obj, "canonical_transition_id", None)}
    mechanism_hits = {obj.canonical_mechanism_id for obj in objects if getattr(obj, "canonical_mechanism_id", None)}

    contradiction_counts: dict[str, int] = defaultdict(int)
    temporal_counts: dict[str, int] = defaultdict(int)
    source_file_coverage: dict[str, dict] = defaultdict(lambda: {"states": 0, "transitions": 0, "mechanisms": 0, "contradictions": 0, "temporal_dynamics": 0})

    for obj in objects:
        file_key = obj.relative_source_file
        if isinstance(obj, BehavioralState):
            source_file_coverage[file_key]["states"] += 1
        if isinstance(obj, TemporalDynamic):
            source_file_coverage[file_key]["temporal_dynamics"] += 1
            if obj.canonical_transition_id:
                source_file_coverage[file_key]["transitions"] += 1
            for tag in obj.expected_coverage_tags:
                if "temporal" in tag or "recovery" in tag or "peak_end" in tag or "wave" in tag:
                    temporal_counts[tag] += 1
        if isinstance(obj, ContradictionObject):
            source_file_coverage[file_key]["contradictions"] += 1
            for tag in obj.expected_coverage_tags:
                if "contradiction" in tag or "reversal" in tag:
                    contradiction_counts[tag] += 1
        if getattr(obj, "canonical_mechanism_id", None):
            source_file_coverage[file_key]["mechanisms"] += 1
        if getattr(obj, "canonical_state_id", None):
            source_file_coverage[file_key]["states"] += 0

    for relative_file, profile in RESEARCH_SOURCE_PROFILES.items():
        source_file_coverage.setdefault(relative_file, {"states": 0, "transitions": 0, "mechanisms": 0, "contradictions": 0, "temporal_dynamics": 0})
        source_file_coverage[relative_file]["expected_coverage_tags"] = list(profile["expected_coverage_tags"])

    return CoverageReport(
        missing_canonical_states=sorted(set(load_canonical_states()) - state_hits),
        missing_canonical_transitions=sorted(set(load_canonical_transitions()) - transition_hits),
        missing_canonical_mechanisms=sorted(set(load_canonical_mechanisms()) - mechanism_hits),
        contradiction_extraction_coverage=dict(sorted(contradiction_counts.items())),
        temporal_kernel_coverage=dict(sorted(temporal_counts.items())),
        source_file_coverage=dict(sorted(source_file_coverage.items())),
    )
