from __future__ import annotations

from pathlib import Path
from pydantic import BaseModel, Field


class PipelineConfig(BaseModel):
    research_dir: Path
    output_dir: Path
    review_decisions_file: Path | None = None
    llm_provider: str = "none"
    llm_model: str = ""
    llm_base_url: str = ""
    extractor_version: str = "0.1.0"
    review_confidence_threshold: float = 0.7
    merge_confidence_threshold: float = 0.93
    fuzzy_merge_threshold: float = 0.84
    enable_embeddings: bool = False
    embedding_model_name: str = "all-MiniLM-L6-v2"
    max_chunk_chars: int = 1800
    corpus: str = "core"  # "core" or "se" — set by runner, tags output
    graph_name: str = "module3_research_ontology"
    write_debug_artifacts: bool = True
    section_min_text_length: int = 40
    section_types: tuple[str, ...] = Field(
        default=(
            "mechanism",
            "variable",
            "behavioral_state",
            "intervention",
            "causal_relationship",
            "evidence",
            "contradiction",
            "temporal_dynamic",
            "KPI",
            "operational_implication",
            "contextual_limitation",
        )
    )
