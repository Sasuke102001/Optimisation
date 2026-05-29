from __future__ import annotations

from collections import defaultdict

from research_extraction.schemas import SectionClassification, SemanticSection


SECTION_KEYWORDS = {
    "mechanism": ["mechanism", "how it works", "overview", "explanation", "pathway", "process", "model"],
    "variable": ["measurable indicator", "measurement", "signal", "feature", "variable", "parameter", "marker"],
    "behavioral_state": ["state", "engagement", "fatigue", "synchronization", "overload", "mood", "arousal", "attention"],
    "intervention": ["intervention", "operational implication", "action", "opportunity", "design", "use", "reduce", "increase", "recommendation", "adjust"],
    "causal_relationship": ["increases", "reduces", "leads to", "drives", "predicts", "correlates", "causes", "relationship", "influences", "associated with"],
    "evidence": ["evidence", "study", "citation", "replication", "consensus", "research shows", "findings", "observed"],
    "contradiction": ["contradiction", "failure", "however", "risk", "limitation", "depends", "may not", "trade-off", "caveat"],
    "temporal_dynamic": ["time", "phase", "window", "lag", "curve", "build", "recovery", "minutes", "hours", "duration", "sequence"],
    "KPI": ["kpi", "metric", "index", "rate", "score", "velocity", "time-to", "outcome", "benchmark"],
    "operational_implication": ["operational", "staff", "service", "venue", "workflow", "commercial", "deployment", "implementation"],
    "contextual_limitation": ["context", "limitation", "depends", "subculture", "audience", "environment", "setting", "boundary"],
}


def classify_section(section: SemanticSection) -> SectionClassification:
    haystack = f"{' '.join(section.heading_path)}\n{section.normalized_text}".lower()
    scores: dict[str, float] = defaultdict(float)
    reasons: list[str] = []

    for section_type, keywords in SECTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in haystack:
                scores[section_type] += 1.0

    if "kpi candidates" in haystack or "likely kpi" in haystack:
        scores["KPI"] += 3.0
        reasons.append("explicit KPI cue")
    if "possible intervention" in haystack or "intervention opportunities" in haystack:
        scores["intervention"] += 3.0
        reasons.append("explicit intervention cue")
    if "temporal dynamics" in haystack:
        scores["temporal_dynamic"] += 3.0
        reasons.append("explicit temporal cue")
    if "contradiction" in haystack or "failure and contradiction" in haystack:
        scores["contradiction"] += 3.0
        reasons.append("explicit contradiction cue")
    if "measurable indicators" in haystack or "measurable signals" in haystack:
        scores["variable"] += 2.5
        reasons.append("explicit variable cue")

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    if not ranked:
        return SectionClassification(
            section_id=section.section_id,
            section_type="mechanism",
            confidence=0.35,
            candidate_types=["mechanism"],
            reasons=["default fallback"],
        )

    top_type, top_score = ranked[0]
    total = max(sum(score for _, score in ranked), 1.0)
    confidence = min(0.99, max(0.35, top_score / total + 0.2))
    return SectionClassification(
        section_id=section.section_id,
        section_type=top_type,
        confidence=round(confidence, 3),
        candidate_types=[item[0] for item in ranked[:4]],
        reasons=reasons or [f"matched keywords for {top_type}"],
    )


def classify_sections(sections: list[SemanticSection]) -> list[SectionClassification]:
    return [classify_section(section) for section in sections]
