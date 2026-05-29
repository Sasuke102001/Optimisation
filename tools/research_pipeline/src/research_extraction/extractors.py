from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field

from research_extraction.confidence import build_confidence_profile
from research_extraction.config import PipelineConfig
from research_extraction.ids import build_canonical_id
from research_extraction.llm import build_structured_extractor
from research_extraction.profile_extractors import PRIVILEGED_TITLES, extract_profile_overrides
from research_extraction.registries import match_canonical_mechanism, match_canonical_state
from research_extraction.schemas import (
    BehavioralState,
    ContradictionObject,
    EvidenceObject,
    Intervention,
    KPI,
    Relationship,
    SectionClassification,
    SemanticSection,
    TemporalDynamic,
    Variable,
)
from research_extraction.utils import bullet_split, extract_minutes, normalize_whitespace, sentence_split
from research_extraction.validation.rules import ACTION_VERBS


VARIABLE_PATTERNS = {
    "acoustic": [
        ("SPL", "dBA", "ambient sound pressure level"),
        ("BPM", "bpm", "music tempo"),
        ("spectral centroid", "Hz", "spectral brightness"),
        ("spectral flux", "delta", "spectral change rate"),
        ("RMS energy", "relative", "average acoustic power"),
        ("noise level", "dB", "ambient noise intensity"),
        ("volume", "dB", "playback level"),
        ("temperature", "C", "ambient thermal level"),
        ("crowd density", "persons_per_m2", "people per square meter"),
    ],
    "behavioral": [
        ("dwell time", "minutes", "visit duration"),
        ("movement intensity", "relative", "aggregate body motion level"),
        ("movement entropy", "score", "diversity of movement trajectories"),
        ("dance floor occupancy", "percent", "occupied dance floor share"),
        ("phone-check frequency", "checks_per_hour", "rate of device attention switching"),
        ("exit velocity", "guests_per_minute", "departure rate"),
        ("ordering velocity", "orders_per_minute", "ordering pace"),
        ("drink consumption velocity", "drinks_per_hour", "consumption rate"),
        ("conversation pause patterns", "count", "conversation interruption signal"),
        ("gaze direction frequency", "count", "visual attention allocation"),
    ],
    "operational": [
        ("bar queue length", "people", "queue load at ordering point"),
        ("service time", "seconds", "time to complete service interaction"),
        ("complaint rate", "count", "incident or complaint frequency"),
        ("tip percentage", "percent", "tip share of spend"),
        ("return visit intent", "score", "stated revisit probability"),
        ("social media posting density", "posts_per_hour", "posting activity around moments"),
    ],
}

STATE_TERMS = [
    "passive observation",
    "engaged",
    "engagement",
    "participation",
    "euphoria",
    "fatigued",
    "fatigue",
    "overstimulated",
    "overstimulation",
    "synchronized",
    "synchronized behavior",
    "conversational",
    "disengagement",
    "disengaging",
    "reactivation",
    "anticipatory",
    "immersive",
    "chaotic",
    "socially active",
    "recovery",
    "peak",
    "warm-up",
    "flow",
    "resolution",
    "calibration",
]

INTERVENTION_PREFIXES = tuple(f"{verb} " for verb in ACTION_VERBS)

KPI_METRIC_TERMS = (
    "rate",
    "score",
    "index",
    "time-to",
    "time to",
    "velocity",
    "lift",
    "retention",
    "intent",
    "ratio",
    "rebound",
    "drop-off",
    "drop off",
    "frequency",
    "occupancy",
    "density",
    "satisfaction",
    "conversion",
    "spend",
    "sales",
    "revenue",
    "complaint",
    "incident",
    "dwell",
    "engagement",
    "fatigue",
    "exit",
)

KPI_ACTION_TERMS = ("track ", "measure ", "monitor ", "correlate ", "compare ")
KPI_METRIC_PATTERNS = [re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE) for term in KPI_METRIC_TERMS]

RELATIONSHIP_PATTERNS = [
    (re.compile(r"(.+?)\s+increases?\s+(.+?)(?:[.;]|$)", re.IGNORECASE), "increases", "positive"),
    (re.compile(r"(.+?)\s+reduces?\s+(.+?)(?:[.;]|$)", re.IGNORECASE), "decreases", "negative"),
    (re.compile(r"(.+?)\s+leads to\s+(.+?)(?:[.;]|$)", re.IGNORECASE), "leads_to", "positive"),
    (re.compile(r"(.+?)\s+drives?\s+(.+?)(?:[.;]|$)", re.IGNORECASE), "drives", "positive"),
    (re.compile(r"(.+?)\s+correlates?\s+with\s+(.+?)(?:[.;]|$)", re.IGNORECASE), "correlates_with", "mixed"),
    (re.compile(r"(.+?)\s+predicts?\s+(.+?)(?:[.;]|$)", re.IGNORECASE), "predicts", "positive"),
    (re.compile(r"(.+?)\s+amplifies?\s+(.+?)(?:[.;]|$)", re.IGNORECASE), "amplifies", "positive"),
    (re.compile(r"(.+?)\s+suppresses?\s+(.+?)(?:[.;]|$)", re.IGNORECASE), "suppresses", "negative"),
    (re.compile(r"(.+?)\s+accelerates?\s+(.+?)(?:[.;]|$)", re.IGNORECASE), "accelerates", "positive"),
    (re.compile(r"(.+?)\s+delays?\s+(.+?)(?:[.;]|$)", re.IGNORECASE), "delays", "negative"),
    (re.compile(r"(.+?)\s+destabilizes?\s+(.+?)(?:[.;]|$)", re.IGNORECASE), "destabilizes", "negative"),
    (re.compile(r"(.+?)\s+stabilizes?\s+(.+?)(?:[.;]|$)", re.IGNORECASE), "stabilizes", "positive"),
    (re.compile(r"(.+?)\s+buffers?\s+(.+?)(?:[.;]|$)", re.IGNORECASE), "buffers", "negative"),
    (re.compile(r"(.+?)\s+primes?\s+(.+?)(?:[.;]|$)", re.IGNORECASE), "primes", "positive"),
    (re.compile(r"(.+?)\s+fatigues?\s+(.+?)(?:[.;]|$)", re.IGNORECASE), "fatigues", "negative"),
    (re.compile(r"(.+?)\s+restores?\s+(.+?)(?:[.;]|$)", re.IGNORECASE), "restores", "positive"),
    (re.compile(r"(.+?)\s+reinforces?\s+(.+?)(?:[.;]|$)", re.IGNORECASE), "reinforces", "positive"),
    (re.compile(r"(.+?)\s+disrupts?\s+(.+?)(?:[.;]|$)", re.IGNORECASE), "disrupts", "negative"),
]

SECTION_TYPE_TO_FAMILIES = {
    "mechanism": {"variables", "states", "relationships", "evidence_objects", "temporal_dynamics"},
    "variable": {"variables", "relationships", "evidence_objects"},
    "behavioral_state": {"states", "relationships", "evidence_objects", "contradiction_objects"},
    "intervention": {"interventions", "relationships", "kpis", "temporal_dynamics"},
    "causal_relationship": {"relationships", "evidence_objects", "contradiction_objects"},
    "evidence": {"evidence_objects", "relationships", "contradiction_objects"},
    "contradiction": {"contradiction_objects", "evidence_objects", "relationships"},
    "temporal_dynamic": {"temporal_dynamics", "relationships", "evidence_objects"},
    "KPI": {"kpis", "relationships", "interventions", "evidence_objects"},
    "operational_implication": {"interventions", "kpis", "relationships", "evidence_objects"},
    "contextual_limitation": {"contradiction_objects", "evidence_objects", "relationships", "temporal_dynamics"},
}

ALL_FAMILIES = (
    "variables",
    "states",
    "relationships",
    "interventions",
    "kpis",
    "temporal_dynamics",
    "evidence_objects",
    "contradiction_objects",
)


@dataclass
class ExtractionBundle:
    variables: list[Variable]
    states: list[BehavioralState]
    relationships: list[Relationship]
    interventions: list[Intervention]
    kpis: list[KPI]
    temporal_dynamics: list[TemporalDynamic]
    evidence_objects: list[EvidenceObject]
    contradiction_objects: list[ContradictionObject]


class LLMVariable(BaseModel):
    name: str
    category: str = "behavioral"
    description: str = ""
    measurement_method: str = "llm_inferred"
    unit: str = "unspecified"
    real_time_capable: bool = True
    confidence_level: str = "medium"
    aliases: list[str] = Field(default_factory=list)


class LLMState(BaseModel):
    name: str
    description: str = ""
    observable_signals: list[str] = Field(default_factory=list)
    contributing_variables: list[str] = Field(default_factory=list)
    possible_interventions: list[str] = Field(default_factory=list)
    confidence_notes: str = "LLM structured extraction."
    aliases: list[str] = Field(default_factory=list)
    entry_conditions: list[str] = Field(default_factory=list)
    exit_conditions: list[str] = Field(default_factory=list)
    possible_next_states: list[str] = Field(default_factory=list)
    transition_triggers: list[str] = Field(default_factory=list)
    stability_score: float = 0.0
    fatigue_characteristics: list[str] = Field(default_factory=list)
    recovery_characteristics: list[str] = Field(default_factory=list)


class LLMRelationship(BaseModel):
    source_entity: str
    target_entity: str
    relationship_type: str = "influences"
    effect_direction: str = "mixed"
    strength_estimate: str = "unspecified"
    confidence_value: float = 0.75
    context_dependencies: list[str] = Field(default_factory=list)
    environmental_modifiers: list[str] = Field(default_factory=list)
    time_dependency: bool = False
    lag_window_minutes: float | None = None
    evidence_grade: str = "unclear"


class LLMIntervention(BaseModel):
    name: str
    trigger_conditions: list[str] = Field(default_factory=list)
    expected_effects: list[str] = Field(default_factory=list)
    affected_states: list[str] = Field(default_factory=list)
    required_variables: list[str] = Field(default_factory=list)
    lag_window_minutes: list[float] = Field(default_factory=list)
    risk_factors: list[str] = Field(default_factory=list)
    operational_complexity: str = "medium"


class LLMKPI(BaseModel):
    operator_label: str
    technical_definition: str = ""
    category: str = "operational"
    leading_indicators: list[str] = Field(default_factory=list)
    lagging_indicators: list[str] = Field(default_factory=list)
    possible_interventions: list[str] = Field(default_factory=list)
    human_interpretation: str = ""
    complexity_level: str = "medium"


class LLMTemporalDynamic(BaseModel):
    name: str
    start_state: str = "unknown"
    end_state: str = "unknown"
    trigger_conditions: list[str] = Field(default_factory=list)
    estimated_time_window: str = "unspecified"
    recovery_characteristics: list[str] = Field(default_factory=list)
    transition_logic: str = ""
    duration_minutes: list[float] = Field(default_factory=list)
    sequence_dependencies: list[str] = Field(default_factory=list)
    state_progression: list[str] = Field(default_factory=list)


class LLMEvidence(BaseModel):
    claim: str
    evidence_strength: str = "unclear"
    replication_quality: str = "unknown"
    scientific_consensus: str = "mixed"
    operational_relevance: str = "medium"
    source_type: str = "speculative"
    recommended_weight: float = 0.5
    linked_entities: list[str] = Field(default_factory=list)
    notes: str = ""


class LLMContradiction(BaseModel):
    claim: str
    contradiction_text: str
    affected_entities: list[str] = Field(default_factory=list)
    uncertainty_level: str = "medium"


class VariableExtractionResponse(BaseModel):
    variables: list[LLMVariable] = Field(default_factory=list)


class StateExtractionResponse(BaseModel):
    states: list[LLMState] = Field(default_factory=list)


class RelationshipExtractionResponse(BaseModel):
    relationships: list[LLMRelationship] = Field(default_factory=list)


class InterventionExtractionResponse(BaseModel):
    interventions: list[LLMIntervention] = Field(default_factory=list)


class KPIExtractionResponse(BaseModel):
    kpis: list[LLMKPI] = Field(default_factory=list)


class TemporalDynamicExtractionResponse(BaseModel):
    temporal_dynamics: list[LLMTemporalDynamic] = Field(default_factory=list)


class EvidenceExtractionResponse(BaseModel):
    evidence_objects: list[LLMEvidence] = Field(default_factory=list)


class ContradictionExtractionResponse(BaseModel):
    contradiction_objects: list[LLMContradiction] = Field(default_factory=list)


LLM_RESPONSE_SCHEMAS = {
    "variables": VariableExtractionResponse,
    "states": StateExtractionResponse,
    "relationships": RelationshipExtractionResponse,
    "interventions": InterventionExtractionResponse,
    "kpis": KPIExtractionResponse,
    "temporal_dynamics": TemporalDynamicExtractionResponse,
    "evidence_objects": EvidenceExtractionResponse,
    "contradiction_objects": ContradictionExtractionResponse,
}


def _base_kwargs(section: SemanticSection, config: PipelineConfig, extractor_name: str, confidence: float) -> dict[str, Any]:
    return {
        "confidence": build_confidence_profile(confidence, operational_relevance=0.55),
        "raw_text": section.raw_text,
        "normalized_text": section.normalized_text,
        "source_file": section.file,
        "relative_source_file": section.relative_file,
        "section_id": section.section_id,
        "heading_path": section.heading_path,
        "extractor_version": config.extractor_version,
        "extractor_name": extractor_name,
        "provenance_refs": [section.relative_file, section.section_id, "semantic_section_extraction"],
        "source_role": section.source_role,
        "domain_tags": section.domain_tags,
        "expected_coverage_tags": section.expected_coverage_tags,
        **_context_kwargs(section),
    }


def _context_kwargs(section: SemanticSection) -> dict[str, Any]:
    heading_text = " ".join(section.heading_path).lower()
    applicable_contexts: list[str] = []
    invalid_contexts: list[str] = []
    audience_dependencies: list[str] = []
    environment_dependencies: list[str] = []
    if "nightlife" in heading_text or "venue" in heading_text:
        applicable_contexts.append("hospitality_live_environment")
        environment_dependencies.append("venue_layout")
    if "crowd" in heading_text:
        applicable_contexts.append("high_density_social_context")
        audience_dependencies.append("group_behavior")
    if "limitation" in heading_text or "boundary" in heading_text:
        invalid_contexts.append("universal_claim")
    if section.section_title in PRIVILEGED_TITLES:
        applicable_contexts.append("privileged_research_structure")
    return {
        "applicable_contexts": applicable_contexts,
        "invalid_contexts": invalid_contexts,
        "audience_dependencies": audience_dependencies,
        "environment_dependencies": environment_dependencies,
    }


def extract_variables(section: SemanticSection, config: PipelineConfig) -> list[Variable]:
    haystack = section.normalized_text.lower()
    variables: list[Variable] = []
    for category, patterns in VARIABLE_PATTERNS.items():
        for name, unit, description in patterns:
            if name.lower() in haystack:
                variable_id = build_canonical_id("variable", name if unit == "" else f"{name}_{unit}")
                variables.append(
                    Variable(
                        variable_id=variable_id,
                        name=name,
                        category=category,
                        description=description,
                        measurement_method="inferred from section text; requires domain-specific instrumentation mapping",
                        unit=unit,
                        real_time_capable=category != "operational" or "intent" not in name.lower(),
                        behavioral_relevance=[section.section_title],
                        operational_relevance=bullet_split(section.normalized_text)[:4],
                        confidence_level="medium" if "measurable" in haystack else "low",
                        canonical_mechanism_id=match_canonical_mechanism(name)[0],
                        canonical_mechanism_label=match_canonical_mechanism(name)[1],
                        **_base_kwargs(section, config, "rule_variable_extractor", 0.68 if "measurable" in haystack else 0.58),
                    )
                )
    return _dedupe_models(variables, "variable_id")


def extract_states(section: SemanticSection, config: PipelineConfig) -> list[BehavioralState]:
    haystack = section.normalized_text.lower()
    states: list[BehavioralState] = []
    signal_candidates = bullet_split(section.normalized_text) or sentence_split(section.normalized_text)[:5]
    for term in STATE_TERMS:
        if term.lower() in haystack or term.lower() in section.section_title.lower():
            state_id = build_canonical_id("behavioral_state", term)
            states.append(
                BehavioralState(
                    state_id=state_id,
                    name=term.title(),
                    description=f"Behavioral or environmental state referenced in section '{section.section_title}'.",
                    observable_signals=signal_candidates[:5],
                    contributing_variables=[],
                    contributing_variable_ids=[],
                    possible_interventions=[],
                    possible_intervention_ids=[],
                    confidence_notes="Rule-based detection from heading and section text.",
                    entry_conditions=signal_candidates[:3],
                    exit_conditions=[line for line in signal_candidates if any(token in line.lower() for token in ("leave", "exit", "fade", "drop"))][:3],
                    possible_next_states=[next_term.title() for next_term in STATE_TERMS if next_term != term and next_term.lower() in haystack][:3],
                    transition_triggers=[line for line in signal_candidates if any(token in line.lower() for token in ("trigger", "when", "after", "before"))][:3],
                    stability_score=0.58,
                    fatigue_characteristics=[line for line in signal_candidates if "fatigue" in line.lower()][:3],
                    recovery_characteristics=[line for line in signal_candidates if "recover" in line.lower() or "reset" in line.lower()][:3],
                    canonical_state_id=match_canonical_state(term.title())[0],
                    **_base_kwargs(section, config, "rule_state_extractor", 0.62),
                )
            )
    return _dedupe_models(states, "state_id")


def extract_relationships(section: SemanticSection, config: PipelineConfig) -> list[Relationship]:
    relationships: list[Relationship] = []
    for sentence in sentence_split(section.normalized_text):
        for pattern, relationship_type, direction in RELATIONSHIP_PATTERNS:
            match = pattern.search(sentence)
            if not match:
                continue
            source = normalize_whitespace(match.group(1))[:120]
            target = normalize_whitespace(match.group(2))[:120]
            relationship_id = build_canonical_id("relationship", f"{source}_{relationship_type}_{target}")
            relationships.append(
                Relationship(
                    relationship_id=relationship_id,
                    source_entity=source,
                    target_entity=target,
                    relationship_type=relationship_type,
                    effect_direction=direction,
                    strength_estimate="unspecified",
                    confidence_value=0.64,
                    context_dependencies=[],
                    time_dependency=bool(extract_minutes(sentence)) or "time" in sentence.lower(),
                    environmental_modifiers=[line for line in bullet_split(section.normalized_text) if any(token in line.lower() for token in ("environment", "layout", "crowd", "venue"))][:3],
                    lag_window_minutes=min(extract_minutes(sentence), default=None),
                    evidence_grade=_evidence_grade_from_text(sentence),
                    **_base_kwargs(section, config, "rule_relationship_extractor", 0.64),
                )
            )
    return _dedupe_models(relationships, "relationship_id")


def extract_interventions(section: SemanticSection, config: PipelineConfig) -> list[Intervention]:
    interventions: list[Intervention] = []
    for candidate in bullet_split(section.normalized_text) + sentence_split(section.normalized_text):
        lowered = candidate.lower()
        if len(candidate.split()) > 18:
            continue
        if not lowered.startswith(INTERVENTION_PREFIXES) and " should " not in f" {lowered} " and "recommend" not in lowered:
            continue
        name = normalize_whitespace(candidate).rstrip(".")
        intervention_id = build_canonical_id("intervention", name[:80])
        interventions.append(
            Intervention(
                intervention_id=intervention_id,
                name=name[:160],
                trigger_conditions=[],
                expected_effects=[],
                affected_states=[],
                affected_state_ids=[],
                required_variables=[],
                required_variable_ids=[],
                lag_window_minutes=extract_minutes(candidate),
                risk_factors=[],
                operational_complexity="medium",
                **_base_kwargs(section, config, "rule_intervention_extractor", 0.66),
            )
        )
    return _dedupe_models(interventions, "intervention_id")


def extract_kpis(section: SemanticSection, config: PipelineConfig) -> list[KPI]:
    kpis: list[KPI] = []
    title_has_kpi = "kpi" in section.section_title.lower() or "metric" in section.section_title.lower()
    candidates = []
    candidates.extend(bullet_split(section.normalized_text))
    candidates.extend([line.strip() for line in section.normalized_text.splitlines() if line.strip()])
    seen_candidates: set[str] = set()

    for candidate in candidates:
        normalized = normalize_whitespace(candidate)
        if normalized in seen_candidates:
            continue
        seen_candidates.add(normalized)
        lowered = normalized.lower()
        has_metric_term = any(pattern.search(normalized) for pattern in KPI_METRIC_PATTERNS)
        has_action_term = lowered.startswith(KPI_ACTION_TERMS)
        if not has_metric_term:
            continue
        if not title_has_kpi and not has_action_term:
            continue
        if len(normalized) < 8 or len(normalized) > 180:
            continue
        kpi_id = build_canonical_id("kpi", normalized)
        kpis.append(
            KPI(
                kpi_id=kpi_id,
                operator_label=normalized[:120],
                technical_definition=f"Operator-facing KPI derived from section '{section.section_title}'.",
                category="behavioral" if "engagement" in lowered or "fatigue" in lowered else "operational",
                leading_indicators=[],
                leading_indicator_ids=[],
                lagging_indicators=[],
                lagging_indicator_ids=[],
                possible_interventions=[],
                possible_intervention_ids=[],
                human_interpretation="Monitor this KPI as a simplified operator-facing signal rather than a raw technical metric.",
                complexity_level="medium",
                **_base_kwargs(section, config, "rule_kpi_extractor", 0.72),
            )
        )
    return _dedupe_models(kpis, "kpi_id")


def extract_temporal_dynamics(section: SemanticSection, config: PipelineConfig) -> list[TemporalDynamic]:
    dynamics: list[TemporalDynamic] = []
    lowered = section.normalized_text.lower()
    temporal_hits = sum(1 for token in ("time", "phase", "window", "lag", "sequence", "recovery", "duration", "transition") if token in lowered)
    minutes = extract_minutes(section.normalized_text)
    if temporal_hits < 2 and not minutes:
        return dynamics
    title = normalize_whitespace(section.section_title)
    dynamic_id = build_canonical_id("temporal_dynamic", title)
    dynamics.append(
        TemporalDynamic(
            dynamic_id=dynamic_id,
            name=title,
            start_state=section.heading_path[-2] if len(section.heading_path) > 1 else "unknown",
            end_state=title,
            trigger_conditions=bullet_split(section.normalized_text)[:3],
            estimated_time_window=", ".join(str(value) for value in minutes) or "unspecified",
            recovery_characteristics=[line for line in bullet_split(section.normalized_text) if "recover" in line.lower()][:3],
            transition_logic=sentence_split(section.normalized_text)[0][:200] if sentence_split(section.normalized_text) else "",
            duration_minutes=minutes,
            sequence_dependencies=[line for line in bullet_split(section.normalized_text) if any(token in line.lower() for token in ("before", "after", "sequence", "then"))][:3],
            state_progression=[part.strip() for part in re.split(r"->|→| to ", title) if normalize_whitespace(part)][:4],
            **_base_kwargs(section, config, "rule_temporal_extractor", 0.61),
        )
    )
    return dynamics


def extract_evidence(section: SemanticSection, config: PipelineConfig) -> list[EvidenceObject]:
    evidence_objects: list[EvidenceObject] = []
    for sentence in sentence_split(section.normalized_text):
        lowered = sentence.lower()
        if not any(marker in lowered for marker in ("research", "study", "evidence", "shows", "suggests", "correlate", "citation", "[^")):
            continue
        claim_id = build_canonical_id("evidence", sentence[:80])
        grade = _evidence_grade_from_text(sentence)
        evidence_objects.append(
            EvidenceObject(
                claim_id=claim_id,
                claim=sentence[:240],
                evidence_strength=grade,
                replication_quality="unknown",
                scientific_consensus="mixed" if "may" in lowered or "suggest" in lowered else "unclear",
                operational_relevance="high" if any(word in lowered for word in ("spend", "dwell", "fatigue", "exit", "engagement")) else "medium",
                source_type=_evidence_source_type_from_text(sentence),
                recommended_weight=_weight_from_grade(grade),
                linked_entity_ids=[],
                notes="Rule-based evidence capture from section sentence.",
                **_base_kwargs(section, config, "rule_evidence_extractor", 0.6),
            )
        )
    return _dedupe_models(evidence_objects, "claim_id")


# ---------------------------------------------------------------------------
# SE Extractor 1 — Intervention Recipe Extractor
# ---------------------------------------------------------------------------

_SE_TRIGGER_WORDS = re.compile(
    r"\b(when|if|once|as soon as|upon|after|during)\b",
    re.IGNORECASE,
)
_SE_ACTION_WORDS = re.compile(
    r"\b(increase|decrease|raise|lower|shift|reduce|boost|cut|drop|add|remove|apply|trigger|activate|play|set)\b",
    re.IGNORECASE,
)
_SE_BULLET_LABELS = re.compile(
    r"^\s*(Trigger|Action|Expected|Duration|Timing|Response|Effect|Outcome)\s*:\s*",
    re.IGNORECASE | re.MULTILINE,
)
_SE_PARAM_VALUES = re.compile(
    r"\b(\d+(?:[\.,]\d+)?\s*(?:BPM|bpm|dB|dBA|lux|°C|%|percent|beats per minute))\b",
    re.IGNORECASE,
)
_SE_NUMBERED_STEPS = re.compile(r"^\s*\d+\.\s+.+", re.MULTILINE)
_SE_OPERATIONAL_TYPES = frozenset({"intervention", "operational_implication"})


def extract_se_intervention_recipe(
    section: SemanticSection,
    classification: SectionClassification,
    config: PipelineConfig,
) -> list[Intervention]:
    """SE Extractor 1: pulls structured intervention recipes from SE-style operational sections."""
    if classification.section_type not in _SE_OPERATIONAL_TYPES:
        return []

    text = section.normalized_text
    interventions: list[Intervention] = []

    # Strategy A — Bullet-labelled recipes (Trigger: / Action: / Expected: etc.)
    bullet_blocks: list[dict[str, str]] = []
    current_block: dict[str, str] = {}
    for line in text.splitlines():
        m = _SE_BULLET_LABELS.match(line)
        if m:
            label = m.group(1).lower()
            value = line[m.end():].strip()
            current_block[label] = value
        else:
            if len(current_block) >= 2:
                bullet_blocks.append(current_block)
                current_block = {}
    if len(current_block) >= 2:
        bullet_blocks.append(current_block)

    for block in bullet_blocks:
        trigger = block.get("trigger", "")
        action = block.get("action", "")
        expected = block.get("expected", block.get("effect", block.get("outcome", "")))
        timing = block.get("timing", block.get("duration", ""))
        name = normalize_whitespace(action or trigger)[:160] or section.section_title[:160]
        if not name:
            continue
        params = [m.group() for m in _SE_PARAM_VALUES.finditer(f"{trigger} {action} {expected}")]
        state_hits = [t for t in STATE_TERMS if t in f"{trigger} {expected}".lower()]
        intervention_id = build_canonical_id("intervention", name[:80])
        interventions.append(
            Intervention(
                intervention_id=intervention_id,
                name=name,
                trigger_conditions=[trigger] if trigger else [],
                expected_effects=[expected] if expected else [],
                required_variables=params,
                required_variable_ids=[],
                affected_states=state_hits,
                affected_state_ids=[],
                lag_window_minutes=extract_minutes(timing or expected),
                risk_factors=[],
                operational_complexity="medium",
                contextual_limitations=[f"Timing: {timing}"] if timing else [],
                **_base_kwargs(section, config, "se_recipe_extractor", 0.74),
            )
        )

    # Strategy B — Sentence-level "when X, [verb] Y" patterns
    for sentence in sentence_split(text):
        if not (_SE_TRIGGER_WORDS.search(sentence) and _SE_ACTION_WORDS.search(sentence)):
            continue
        if not _SE_PARAM_VALUES.search(sentence):
            continue
        full_sentence = normalize_whitespace(sentence).rstrip(".")
        # Extract the action clause after a comma as the name (starts with an action verb)
        # e.g. "When BPM drops below 118, increase tempo to 128 BPM" → "increase tempo to 128 BPM"
        action_clause = full_sentence
        if "," in full_sentence:
            parts = full_sentence.split(",", 1)
            candidate = parts[1].strip()
            # Only use the action clause as name if it starts with an action-like word
            if candidate and _SE_ACTION_WORDS.match(candidate):
                action_clause = candidate
        # Truncate name to 24 words to pass intervention_explanatory_prose validation
        name = " ".join(action_clause.split()[:24])
        if not name or len(name.split()) < 2:
            name = " ".join(full_sentence.split()[:12])
        intervention_id = build_canonical_id("intervention", name[:80])
        params = [m.group() for m in _SE_PARAM_VALUES.finditer(sentence)]
        state_hits = [t for t in STATE_TERMS if t in sentence.lower()]
        interventions.append(
            Intervention(
                intervention_id=intervention_id,
                name=name,
                trigger_conditions=[full_sentence],
                expected_effects=[],
                required_variables=params,
                required_variable_ids=[],
                affected_states=state_hits,
                affected_state_ids=[],
                lag_window_minutes=extract_minutes(sentence),
                risk_factors=[],
                operational_complexity="medium",
                **_base_kwargs(section, config, "se_recipe_extractor", 0.67),
            )
        )

    # Strategy C — Numbered step blocks  ("1. ... 2. ... 3. ...")
    steps = _SE_NUMBERED_STEPS.findall(text)
    if len(steps) >= 2:
        joined = " ".join(s.strip() for s in steps)
        name = normalize_whitespace(section.section_title)[:160]
        intervention_id = build_canonical_id("intervention", f"steps_{name[:60]}")
        params = [m.group() for m in _SE_PARAM_VALUES.finditer(joined)]
        state_hits = [t for t in STATE_TERMS if t in joined.lower()]
        interventions.append(
            Intervention(
                intervention_id=intervention_id,
                name=name,
                trigger_conditions=steps[:2],
                expected_effects=steps[-1:],
                required_variables=params,
                required_variable_ids=[],
                affected_states=state_hits,
                affected_state_ids=[],
                lag_window_minutes=extract_minutes(joined),
                risk_factors=[],
                operational_complexity="medium",
                **_base_kwargs(section, config, "se_recipe_extractor", 0.65),
            )
        )

    return _dedupe_models(interventions, "intervention_id")


# ---------------------------------------------------------------------------
# SE Extractor 2 — Parameter Range Extractor
# ---------------------------------------------------------------------------

_SE_RANGE_PATTERN = re.compile(
    r"(\d+(?:[\.,]\d+)?)[\s]*[–\-\–\—]([\s]*(\d+(?:[\.,]\d+)?))[\s]*(BPM|bpm|dB|dBA|lux|°C|%|percent|beats per minute)",
    re.IGNORECASE,
)
_SE_ABOVE_BELOW = re.compile(
    r"(above|below|over|under|at least|at most|more than|less than)[\s]+(\d+(?:[\.,]\d+)?)[\s]*(BPM|bpm|dB|dBA|lux|°C|%|percent)?",
    re.IGNORECASE,
)
_SE_BETWEEN = re.compile(
    r"between[\s]+(\d+(?:[\.,]\d+)?)[\s]+and[\s]+(\d+(?:[\.,]\d+)?)[\s]*(BPM|bpm|dB|dBA|lux|°C|%|percent)?",
    re.IGNORECASE,
)
_SE_X_TO_Y = re.compile(
    r"(\d+(?:[\.,]\d+)?)[\s]+to[\s]+(\d+(?:[\.,]\d+)?)[\s]*(BPM|bpm|dB|dBA|lux|°C|%|percent)",
    re.IGNORECASE,
)
# Maps detected keyword to a (canonical_name, canonical_unit) pair
_SE_PARAM_CANONICAL: list[tuple[str, str, str]] = [
    ("beats per minute", "Music Tempo", "bpm"),
    ("bpm", "Music Tempo", "bpm"),
    ("BPM", "Music Tempo", "bpm"),
    ("SPL", "Sound Pressure Level", "dBA"),
    ("dBA", "Sound Pressure Level", "dBA"),
    ("dB", "Sound Pressure Level", "dBA"),
    ("lux", "Ambient Illuminance", "lux"),
    ("temperature", "Ambient Temperature", "°C"),
    ("crowd density", "Crowd Density", "percent"),
    ("occupancy", "Dance Floor Occupancy", "percent"),
]


def _detect_param_name(context: str) -> tuple[str, str]:
    """Returns (canonical_name, canonical_unit) for the first matching parameter keyword."""
    lowered = context.lower()
    for keyword, name, unit in _SE_PARAM_CANONICAL:
        if keyword.lower() in lowered:
            return name, unit
    return "Operational Parameter", "unspecified"


def extract_se_parameter_ranges(
    section: SemanticSection,
    config: PipelineConfig,
) -> list[Variable]:
    """SE Extractor 2: finds concrete numeric ranges for operational parameters."""
    text = section.normalized_text
    variables: list[Variable] = []

    def _make_variable(param_name: str, min_val: str, max_val: str, unit: str, context_sentence: str) -> Variable:
        range_note = f"Range: {min_val}\u2013{max_val} {unit} | Context: {context_sentence[:120]}"
        category = "acoustic" if unit.lower() in ("bpm", "dba", "db", "lux") else "behavioral"
        variable_id = build_canonical_id("variable", f"{param_name}_{unit}_range")
        return Variable(
            variable_id=variable_id,
            name=param_name,
            category=category,
            description=f"Operational parameter range extracted from SE research: {range_note}",
            measurement_method="se_range_extraction",
            unit=unit,
            real_time_capable=True,
            behavioral_relevance=[section.section_title],
            operational_relevance=[range_note],
            confidence_level="medium",
            evidence_notes=[range_note],
            **_base_kwargs(section, config, "se_range_extractor", 0.72),
        )

    for sentence in sentence_split(text):
        # Explicit X-Y unit pattern
        for m in _SE_RANGE_PATTERN.finditer(sentence):
            min_val, _, max_val, unit = m.group(1), m.group(2), m.group(3), m.group(4)
            param, detected_unit = _detect_param_name(sentence)
            variables.append(_make_variable(param, min_val, max_val, detected_unit or unit, sentence))

        # "between X and Y [unit]"
        for m in _SE_BETWEEN.finditer(sentence):
            min_val, max_val, unit = m.group(1), m.group(2), m.group(3) or "unspecified"
            param, detected_unit = _detect_param_name(sentence)
            variables.append(_make_variable(param, min_val, max_val, detected_unit or unit, sentence))

        # "X to Y unit"
        for m in _SE_X_TO_Y.finditer(sentence):
            min_val, max_val, unit = m.group(1), m.group(2), m.group(3)
            param, detected_unit = _detect_param_name(sentence)
            variables.append(_make_variable(param, min_val, max_val, detected_unit or unit, sentence))

    return _dedupe_models(variables, "variable_id")


# ---------------------------------------------------------------------------
# SE Extractor 3 — Agent Decision Rule Extractor
# ---------------------------------------------------------------------------

_SE_IF_THEN = re.compile(
    r"if\s+(.+?)\s*,?\s*then\s+(.+?)(?:[.;]|$)",
    re.IGNORECASE,
)
_SE_WHEN_APPLY = re.compile(
    r"when\s+(.+?),\s+(apply|use|increase|decrease|trigger|activate|raise|lower|shift)\s+(.+?)(?:[.;]|$)",
    re.IGNORECASE,
)
_SE_INDICATES = re.compile(
    r"(.+?)\s+indicates?\s+(?:that\s+)?(.+?)\s+should\s+(?:be\s+)?(triggered|applied|activated|used|increased|decreased)(?:[.;]|$)",
    re.IGNORECASE,
)
_SE_SIGNAL_RESPONSE = re.compile(
    r"(?:Signal|Cue):\s*(.+?)\s*(?:\n|;)\s*(?:Response|Action):\s*(.+?)(?:[\n;]|$)",
    re.IGNORECASE | re.MULTILINE,
)
_SE_DECISION_TREE_MARKERS = re.compile(
    r"\b(in the case of|provided that|as long as|given that)\b",
    re.IGNORECASE,
)
# Matches "**If X:**" or "**If X is Y:**" followed (within a few lines) by
# "**Intervention:**" or "**Diagnosis:**" or "**Response:**" blocks.
_SE_BOLD_IF_BLOCK = re.compile(
    r"\*{1,2}[Ii]f\s+(.+?)\*{0,2}:?\*{0,2}[\s\n]+"
    r"(?:[^\n]*\n)*?"
    r"[-–]?\s*\*{1,2}(?:Intervention|Response|Action|Diagnosis)\*{0,2}:\s*(.+?)(?:\n|$)",
    re.IGNORECASE | re.MULTILINE,
)
# Matches "-  **Intervention:** X" standalone bullets
_SE_INTERVENTION_BULLET = re.compile(
    r"^[-–*]?\s*\*{1,2}(Intervention|Response|Action|Next step)\*{0,2}:\s*(.+?)$",
    re.IGNORECASE | re.MULTILINE,
)
_SE_DECISION_TYPES = frozenset({"intervention", "operational_implication", "mechanism"})


def extract_se_decision_rules(
    section: SemanticSection,
    classification: SectionClassification,
    config: PipelineConfig,
) -> list[Relationship]:
    """SE Extractor 3: maps if/then decision logic to Relationship objects with type 'decision_rule'."""
    if classification.section_type not in _SE_DECISION_TYPES:
        return []

    text = section.normalized_text
    relationships: list[Relationship] = []

    def _make_rule(condition: str, action: str, mechanism: str = "", evidence_raw: str = "") -> Relationship:
        # Truncate to 20 words max to pass relationship_malformed_target validation
        condition = " ".join(normalize_whitespace(condition).split()[:20])
        action = " ".join(normalize_whitespace(action).split()[:20])
        if not condition or not action:
            # Return a dummy that will be deduped away rather than crashing
            condition = condition or "unknown condition"
            action = action or "unknown action"
        relationship_id = build_canonical_id("relationship", f"{condition}_decision_rule_{action}")
        rule_evidence_notes = []
        if mechanism:
            rule_evidence_notes.append(f"Mechanism: {mechanism[:200]}")
        if evidence_raw:
            rule_evidence_notes.append(evidence_raw[:240])
        return Relationship(
            relationship_id=relationship_id,
            source_entity=condition,
            target_entity=action,
            relationship_type="decision_rule",
            effect_direction="positive",
            strength_estimate="unspecified",
            confidence_value=0.71,
            context_dependencies=[],
            time_dependency=bool(extract_minutes(evidence_raw or action)),
            environmental_modifiers=[],
            lag_window_minutes=min(extract_minutes(evidence_raw or action), default=None),
            evidence_grade=_evidence_grade_from_text(evidence_raw or action),
            evidence_notes=rule_evidence_notes,
            **_base_kwargs(section, config, "se_decision_rule_extractor", 0.71),
        )

    for sentence in sentence_split(text):
        # if ... then ...
        for m in _SE_IF_THEN.finditer(sentence):
            relationships.append(_make_rule(m.group(1), m.group(2), evidence_raw=sentence))

        # when X, apply/do Y
        for m in _SE_WHEN_APPLY.finditer(sentence):
            relationships.append(_make_rule(m.group(1), f"{m.group(2)} {m.group(3)}", evidence_raw=sentence))

        # X indicates Y should be triggered
        for m in _SE_INDICATES.finditer(sentence):
            relationships.append(_make_rule(m.group(1), f"{m.group(2)} {m.group(3)}", evidence_raw=sentence))

        # Decision-tree language ("in the case of X, Y")
        if _SE_DECISION_TREE_MARKERS.search(sentence) and "," in sentence:
            parts = sentence.split(",", 1)
            if len(parts) == 2 and len(parts[0].split()) >= 3:
                relationships.append(_make_rule(parts[0].strip(), parts[1].strip(), evidence_raw=sentence))

    # Signal/Cue: ... Response/Action: ... patterns (multi-line bullets)
    for m in _SE_SIGNAL_RESPONSE.finditer(text):
        relationships.append(_make_rule(m.group(1), m.group(2), evidence_raw=m.group(0)))

    # **If condition:** ... **Intervention:** action  (markdown bold blocks)
    for m in _SE_BOLD_IF_BLOCK.finditer(text):
        condition = re.sub(r"\*+", "", m.group(1)).strip()
        action = re.sub(r"\*+", "", m.group(2)).strip()
        if condition and action:
            relationships.append(_make_rule(condition, action, evidence_raw=m.group(0)[:300]))

    # Standalone **Intervention:** bullet lines — pair with the nearest preceding "If" heading
    prev_condition = ""
    for line in text.splitlines():
        if_match = re.match(r"\*{0,2}[Ii]f\s+(.+?)\*{0,2}:?\s*$", line.strip())
        if if_match:
            prev_condition = re.sub(r"\*+", "", if_match.group(1)).strip()
        int_match = _SE_INTERVENTION_BULLET.match(line)
        if int_match and prev_condition:
            action = re.sub(r"\*+", "", int_match.group(2)).strip()
            if action:
                relationships.append(_make_rule(prev_condition, action, evidence_raw=line.strip()[:240]))

    return _dedupe_models(relationships, "relationship_id")


def extract_contradictions(section: SemanticSection, config: PipelineConfig) -> list[ContradictionObject]:
    contradictions: list[ContradictionObject] = []
    for sentence in sentence_split(section.normalized_text):
        lowered = sentence.lower()
        if not any(keyword in lowered for keyword in ("however", "but", "may", "depends", "risk", "contradiction", "failure", "not always")):
            continue
        contradiction_id = build_canonical_id("contradiction", sentence[:80])
        contradictions.append(
            ContradictionObject(
                contradiction_id=contradiction_id,
                claim=section.section_title,
                contradiction_text=sentence[:240],
                affected_entities=[],
                affected_entity_ids=[],
                uncertainty_level="medium" if "may" in lowered or "depends" in lowered else "high",
                **_base_kwargs(section, config, "rule_contradiction_extractor", 0.63),
            )
        )
    return _dedupe_models(contradictions, "contradiction_id")


def extract_all(section: SemanticSection, classification: SectionClassification, config: PipelineConfig) -> ExtractionBundle:
    families = _route_extractor_families(classification)
    rule_bundle = ExtractionBundle(
        variables=extract_variables(section, config) if "variables" in families else [],
        states=extract_states(section, config) if "states" in families else [],
        relationships=extract_relationships(section, config) if "relationships" in families else [],
        interventions=extract_interventions(section, config) if "interventions" in families else [],
        kpis=extract_kpis(section, config) if "kpis" in families else [],
        temporal_dynamics=extract_temporal_dynamics(section, config) if "temporal_dynamics" in families else [],
        evidence_objects=extract_evidence(section, config) if "evidence_objects" in families else [],
        contradiction_objects=extract_contradictions(section, config) if "contradiction_objects" in families else [],
    )
    # SE extractors — run on both corpora (parameter ranges are universally useful)
    se_interventions = extract_se_intervention_recipe(section, classification, config)
    se_variables = extract_se_parameter_ranges(section, config)
    se_relationships = extract_se_decision_rules(section, classification, config)

    profile_bundle = extract_profile_overrides(section, config)
    llm_bundle = _extract_with_llm(section, classification, config, families)
    return ExtractionBundle(
        variables=_dedupe_models([*profile_bundle["variables"], *llm_bundle.variables, *rule_bundle.variables, *se_variables], "variable_id"),
        states=_dedupe_models([*profile_bundle["states"], *llm_bundle.states, *rule_bundle.states], "state_id"),
        relationships=_dedupe_models([*profile_bundle["relationships"], *llm_bundle.relationships, *rule_bundle.relationships, *se_relationships], "relationship_id"),
        interventions=_dedupe_models([*profile_bundle["interventions"], *llm_bundle.interventions, *rule_bundle.interventions, *se_interventions], "intervention_id"),
        kpis=_dedupe_models([*profile_bundle["kpis"], *llm_bundle.kpis, *rule_bundle.kpis], "kpi_id"),
        temporal_dynamics=_dedupe_models([*profile_bundle["temporal_dynamics"], *llm_bundle.temporal_dynamics, *rule_bundle.temporal_dynamics], "dynamic_id"),
        evidence_objects=_dedupe_models([*profile_bundle["evidence_objects"], *llm_bundle.evidence_objects, *rule_bundle.evidence_objects], "claim_id"),
        contradiction_objects=_dedupe_models([*profile_bundle["contradiction_objects"], *llm_bundle.contradiction_objects, *rule_bundle.contradiction_objects], "contradiction_id"),
    )


def _route_extractor_families(classification: SectionClassification) -> set[str]:
    families = set(SECTION_TYPE_TO_FAMILIES.get(classification.section_type, SECTION_TYPE_TO_FAMILIES["mechanism"]))
    candidate_types = classification.candidate_types[:2] if classification.confidence >= 0.6 else classification.candidate_types[:4]
    for candidate_type in candidate_types:
        families.update(SECTION_TYPE_TO_FAMILIES.get(candidate_type, set()))
    if classification.confidence < 0.45:
        families.update(ALL_FAMILIES)
    families.add("evidence_objects")
    return families


def _extract_with_llm(
    section: SemanticSection,
    classification: SectionClassification,
    config: PipelineConfig,
    families: set[str],
) -> ExtractionBundle:
    empty = ExtractionBundle([], [], [], [], [], [], [], [])
    if config.llm_provider == "none":
        return empty

    extractor = build_structured_extractor(config.llm_provider, config.llm_model, config.llm_base_url)
    if extractor is None:
        return empty

    responses: dict[str, BaseModel] = {}
    for family in ALL_FAMILIES:
        if family not in families:
            continue
        schema = LLM_RESPONSE_SCHEMAS[family]
        prompt = _build_llm_prompt(section, classification, family)
        try:
            responses[family] = extractor.extract(prompt, schema)
        except Exception:
            continue

    return ExtractionBundle(
        variables=_convert_llm_variables(responses.get("variables"), section, config),
        states=_convert_llm_states(responses.get("states"), section, config),
        relationships=_convert_llm_relationships(responses.get("relationships"), section, config),
        interventions=_convert_llm_interventions(responses.get("interventions"), section, config),
        kpis=_convert_llm_kpis(responses.get("kpis"), section, config),
        temporal_dynamics=_convert_llm_temporal_dynamics(responses.get("temporal_dynamics"), section, config),
        evidence_objects=_convert_llm_evidence(responses.get("evidence_objects"), section, config),
        contradiction_objects=_convert_llm_contradictions(responses.get("contradiction_objects"), section, config),
    )


def _build_llm_prompt(section: SemanticSection, classification: SectionClassification, family: str) -> str:
    directives = {
        "variables": "Extract measurable or controllable variables only.",
        "states": "Extract behavioral or environmental states only.",
        "relationships": "Extract causal or correlational relationships only.",
        "interventions": "Extract operational or experimental interventions only.",
        "kpis": "Extract KPI-grade operator-facing metrics only.",
        "temporal_dynamics": "Extract temporal windows, phase shifts, and recovery patterns only.",
        "evidence_objects": "Extract evidence claims and evidence quality only.",
        "contradiction_objects": "Extract contradictions, caveats, and context dependence only.",
    }
    return (
        "You are performing ontology-first section extraction. "
        "Do not summarize the document. "
        "Return only schema-valid objects grounded in the provided section text.\n\n"
        f"Target object family: {family}\n"
        f"Section classifier primary type: {classification.section_type}\n"
        f"Section classifier candidate types: {', '.join(classification.candidate_types)}\n"
        f"Directive: {directives[family]}\n\n"
        f"Section title: {section.section_title}\n"
        f"Heading path: {' > '.join(section.heading_path)}\n"
        f"Normalized source text:\n{section.normalized_text}\n"
    )


def _convert_llm_variables(payload: BaseModel | None, section: SemanticSection, config: PipelineConfig) -> list[Variable]:
    if not isinstance(payload, VariableExtractionResponse):
        return []
    base_conf = 0.83
    return _dedupe_models(
        [
            Variable(
                variable_id=build_canonical_id("variable", f"{item.name}_{item.unit}"),
                name=item.name[:120],
                category=item.category,
                description=item.description or "LLM-derived variable.",
                measurement_method=item.measurement_method,
                unit=item.unit,
                real_time_capable=item.real_time_capable,
                behavioral_relevance=[section.section_title],
                operational_relevance=[],
                confidence_level=item.confidence_level,
                aliases=item.aliases,
                **_base_kwargs(section, config, "llm_variable_extractor", base_conf),
            )
            for item in payload.variables
        ],
        "variable_id",
    )


def _convert_llm_states(payload: BaseModel | None, section: SemanticSection, config: PipelineConfig) -> list[BehavioralState]:
    if not isinstance(payload, StateExtractionResponse):
        return []
    base_conf = 0.83
    return _dedupe_models(
        [
            BehavioralState(
                state_id=build_canonical_id("behavioral_state", item.name),
                name=item.name[:120],
                description=item.description or "LLM-derived state.",
                observable_signals=item.observable_signals,
                contributing_variables=item.contributing_variables,
                contributing_variable_ids=[],
                possible_interventions=item.possible_interventions,
                possible_intervention_ids=[],
                confidence_notes=item.confidence_notes,
                aliases=item.aliases,
                entry_conditions=item.entry_conditions,
                exit_conditions=item.exit_conditions,
                possible_next_states=item.possible_next_states,
                transition_triggers=item.transition_triggers,
                stability_score=item.stability_score,
                fatigue_characteristics=item.fatigue_characteristics,
                recovery_characteristics=item.recovery_characteristics,
                **_base_kwargs(section, config, "llm_state_extractor", base_conf),
            )
            for item in payload.states
        ],
        "state_id",
    )


def _convert_llm_relationships(payload: BaseModel | None, section: SemanticSection, config: PipelineConfig) -> list[Relationship]:
    if not isinstance(payload, RelationshipExtractionResponse):
        return []
    base_conf = 0.83
    return _dedupe_models(
        [
            Relationship(
                relationship_id=build_canonical_id("relationship", f"{item.source_entity}_{item.relationship_type}_{item.target_entity}"),
                source_entity=item.source_entity[:120],
                target_entity=item.target_entity[:120],
                relationship_type=item.relationship_type,
                effect_direction=item.effect_direction,
                strength_estimate=item.strength_estimate,
                confidence_value=max(0.0, min(1.0, item.confidence_value)),
                context_dependencies=item.context_dependencies,
                time_dependency=item.time_dependency,
                environmental_modifiers=item.environmental_modifiers,
                lag_window_minutes=item.lag_window_minutes,
                evidence_grade=item.evidence_grade,
                **_base_kwargs(section, config, "llm_relationship_extractor", base_conf),
            )
            for item in payload.relationships
        ],
        "relationship_id",
    )


def _convert_llm_interventions(payload: BaseModel | None, section: SemanticSection, config: PipelineConfig) -> list[Intervention]:
    if not isinstance(payload, InterventionExtractionResponse):
        return []
    base_conf = 0.83
    return _dedupe_models(
        [
            Intervention(
                intervention_id=build_canonical_id("intervention", item.name),
                name=item.name[:160],
                trigger_conditions=item.trigger_conditions,
                expected_effects=item.expected_effects,
                affected_states=item.affected_states,
                affected_state_ids=[],
                required_variables=item.required_variables,
                required_variable_ids=[],
                lag_window_minutes=item.lag_window_minutes,
                risk_factors=item.risk_factors,
                operational_complexity=item.operational_complexity,
                **_base_kwargs(section, config, "llm_intervention_extractor", base_conf),
            )
            for item in payload.interventions
        ],
        "intervention_id",
    )


def _convert_llm_kpis(payload: BaseModel | None, section: SemanticSection, config: PipelineConfig) -> list[KPI]:
    if not isinstance(payload, KPIExtractionResponse):
        return []
    base_conf = 0.83
    return _dedupe_models(
        [
            KPI(
                kpi_id=build_canonical_id("kpi", item.operator_label),
                operator_label=item.operator_label[:120],
                technical_definition=item.technical_definition,
                category=item.category,
                leading_indicators=item.leading_indicators,
                leading_indicator_ids=[],
                lagging_indicators=item.lagging_indicators,
                lagging_indicator_ids=[],
                possible_interventions=item.possible_interventions,
                possible_intervention_ids=[],
                human_interpretation=item.human_interpretation or "LLM-derived KPI summary.",
                complexity_level=item.complexity_level,
                **_base_kwargs(section, config, "llm_kpi_extractor", base_conf),
            )
            for item in payload.kpis
        ],
        "kpi_id",
    )


def _convert_llm_temporal_dynamics(payload: BaseModel | None, section: SemanticSection, config: PipelineConfig) -> list[TemporalDynamic]:
    if not isinstance(payload, TemporalDynamicExtractionResponse):
        return []
    base_conf = 0.83
    return _dedupe_models(
        [
            TemporalDynamic(
                dynamic_id=build_canonical_id("temporal_dynamic", item.name),
                name=item.name[:120],
                start_state=item.start_state,
                end_state=item.end_state,
                trigger_conditions=item.trigger_conditions,
                estimated_time_window=item.estimated_time_window,
                recovery_characteristics=item.recovery_characteristics,
                transition_logic=item.transition_logic,
                duration_minutes=item.duration_minutes,
                sequence_dependencies=item.sequence_dependencies,
                state_progression=item.state_progression,
                **_base_kwargs(section, config, "llm_temporal_extractor", base_conf),
            )
            for item in payload.temporal_dynamics
        ],
        "dynamic_id",
    )


def _convert_llm_evidence(payload: BaseModel | None, section: SemanticSection, config: PipelineConfig) -> list[EvidenceObject]:
    if not isinstance(payload, EvidenceExtractionResponse):
        return []
    base_conf = 0.83
    return _dedupe_models(
        [
            EvidenceObject(
                claim_id=build_canonical_id("evidence", item.claim),
                claim=item.claim[:240],
                evidence_strength=item.evidence_strength,
                replication_quality=item.replication_quality,
                scientific_consensus=item.scientific_consensus,
                operational_relevance=item.operational_relevance,
                source_type=item.source_type,
                recommended_weight=max(0.0, min(1.0, item.recommended_weight)),
                linked_entity_ids=[],
                evidence_notes=item.linked_entities,
                notes=item.notes,
                **_base_kwargs(section, config, "llm_evidence_extractor", base_conf),
            )
            for item in payload.evidence_objects
        ],
        "claim_id",
    )


def _convert_llm_contradictions(payload: BaseModel | None, section: SemanticSection, config: PipelineConfig) -> list[ContradictionObject]:
    if not isinstance(payload, ContradictionExtractionResponse):
        return []
    base_conf = 0.83
    return _dedupe_models(
        [
            ContradictionObject(
                contradiction_id=build_canonical_id("contradiction", f"{item.claim}_{item.contradiction_text}"),
                claim=item.claim[:120],
                contradiction_text=item.contradiction_text[:240],
                affected_entities=item.affected_entities,
                affected_entity_ids=[],
                uncertainty_level=item.uncertainty_level,
                **_base_kwargs(section, config, "llm_contradiction_extractor", base_conf),
            )
            for item in payload.contradiction_objects
        ],
        "contradiction_id",
    )


def _dedupe_models(models: list[Any], field_name: str) -> list[Any]:
    seen: set[str] = set()
    deduped: list[Any] = []
    for model in models:
        key = getattr(model, field_name)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(model)
    return deduped


def _evidence_grade_from_text(text: str) -> str:
    lowered = text.lower()
    if "[^" in lowered or "study" in lowered or "research" in lowered:
        return "moderate"
    if "may" in lowered or "could" in lowered or "suggest" in lowered:
        return "weak"
    return "unclear"


def _weight_from_grade(grade: str) -> float:
    return {
        "strong": 0.9,
        "moderate": 0.7,
        "weak": 0.4,
        "unclear": 0.25,
        "unsupported": 0.1,
    }.get(grade, 0.25)


def _evidence_source_type_from_text(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ("randomized", "experiment", "controlled trial")):
        return "peer_reviewed_experimental"
    if any(token in lowered for token in ("observational", "survey", "cohort")):
        return "peer_reviewed_observational"
    if any(token in lowered for token in ("neural", "brain", "neuroscience", "dopamine")):
        return "neuroscience"
    if any(token in lowered for token in ("operator", "venue", "hospitality", "service")):
        return "hospitality_operational"
    if any(token in lowered for token in ("social media", "platform", "online")):
        return "online_behavioral"
    if any(token in lowered for token in ("social proof", "crowd")):
        return "social_proof"
    if any(token in lowered for token in ("anecdote", "operator said", "observed in practice")):
        return "anecdotal_operator"
    return "speculative"
