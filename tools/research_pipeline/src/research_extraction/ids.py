from __future__ import annotations

from research_extraction.utils import slugify_upper


ID_PREFIXES = {
    "variable": "VAR",
    "behavioral_state": "ST",
    "relationship": "REL",
    "intervention": "INT",
    "kpi": "KPI",
    "temporal_dynamic": "DYN",
    "transition": "TRN",
    "evidence": "EVD",
    "contradiction": "CON",
    "section": "SEC",
    "review": "REV",
    "chunk": "CHK",
}


def build_canonical_id(entity_type: str, label: str) -> str:
    prefix = ID_PREFIXES[entity_type]
    slug = slugify_upper(label)
    return f"{prefix}_{slug}"
