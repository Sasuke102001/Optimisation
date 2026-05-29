from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from rapidfuzz import fuzz

from research_extraction.config import PipelineConfig
from research_extraction.registries import match_canonical_mechanism, match_canonical_state, match_canonical_transition
from research_extraction.schemas import NormalizationDecision, OntologyObject
from research_extraction.utils import normalize_whitespace


ALIAS_REGISTRY = {
    "auditory fatigue": ["listener fatigue", "attention fatigue", "sensory fatigue"],
    "cognitive overload": ["decision overload", "information overload"],
    "crowd density": ["occupancy density", "people per square meter"],
    "spectral centroid": ["spectral brightness", "brightness intensity"],
}

ROOT = Path(__file__).resolve().parents[2]
CANONICAL_MECHANISM_PATH = ROOT / "data" / "canonical_mechanisms.json"
_CANONICAL_MECHANISMS_CACHE: dict[str, dict[str, list[str]]] | None = None

_EMBED_MODEL = None
_EMBED_CACHE: dict[str, object] = {}
_EMBEDDINGS_AVAILABLE: bool | None = None


def _ensure_embeddings_loaded(config: PipelineConfig) -> bool:
    if not config.enable_embeddings:
        return False

    global _EMBED_MODEL, _EMBEDDINGS_AVAILABLE
    if _EMBEDDINGS_AVAILABLE is False:
        return False
    if _EMBED_MODEL is not None:
        return True

    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
    except Exception:
        _EMBEDDINGS_AVAILABLE = False
        return False

    _EMBED_MODEL = SentenceTransformer(config.embedding_model_name)
    _EMBEDDINGS_AVAILABLE = True
    return True


def _embedding_similarity(left: str, right: str, config: PipelineConfig) -> float | None:
    if not _ensure_embeddings_loaded(config):
        return None
    try:
        from sentence_transformers import util  # type: ignore

        left_vec = _EMBED_CACHE.get(left)
        if left_vec is None:
            left_vec = _EMBED_MODEL.encode(left, convert_to_tensor=True)
            _EMBED_CACHE[left] = left_vec
        right_vec = _EMBED_CACHE.get(right)
        if right_vec is None:
            right_vec = _EMBED_MODEL.encode(right, convert_to_tensor=True)
            _EMBED_CACHE[right] = right_vec
        return float(util.cos_sim(left_vec, right_vec).item())
    except Exception:
        return None


def normalize_objects(
    entity_type: str,
    objects: list[OntologyObject],
    config: PipelineConfig,
    name_getter: Callable[[OntologyObject], str],
    id_getter: Callable[[OntologyObject], str],
) -> tuple[list[OntologyObject], list[NormalizationDecision]]:
    normalized: list[OntologyObject] = []
    decisions: list[NormalizationDecision] = []
    grouped: dict[str, OntologyObject] = {}

    for raw_obj in objects:
        obj = _assign_canonical_ids(raw_obj, name_getter(raw_obj))
        candidate_name = normalize_whitespace(name_getter(obj)).lower()
        merged = False
        for canonical_name, canonical_obj in grouped.items():
            if not _anchors_are_compatible(obj, canonical_obj):
                continue
            fuzzy_score = fuzz.ratio(candidate_name, canonical_name) / 100.0
            embed_score = _embedding_similarity(candidate_name, canonical_name, config)
            alias_score = _alias_score(candidate_name, canonical_name)
            mechanism_bonus = _mechanism_score(obj, canonical_obj)
            state_bonus = _state_score(obj, canonical_obj)
            transition_bonus = _transition_score(obj, canonical_obj)
            score = max(fuzzy_score, embed_score or 0.0, alias_score, mechanism_bonus, state_bonus, transition_bonus)
            auto_merge_allowed = min(obj.confidence_score, canonical_obj.confidence_score) >= config.review_confidence_threshold
            if min(obj.confidence_score, canonical_obj.confidence_score) < config.review_confidence_threshold:
                if not _shares_any_canonical_anchor(obj, canonical_obj):
                    auto_merge_allowed = False
            if score >= config.merge_confidence_threshold and auto_merge_allowed:
                merged = True
                decisions.append(
                    NormalizationDecision(
                        entity_type=entity_type,
                        canonical_id=id_getter(canonical_obj),
                        candidate_id=id_getter(obj),
                        canonical_name=name_getter(canonical_obj),
                        candidate_name=name_getter(obj),
                        similarity_score=round(score, 3),
                        merge_action="merged",
                        rationale="High lexical, alias, or canonical-mechanism similarity.",
                    )
                )
                _merge_aliases(canonical_obj, obj)
                break
            if score >= config.fuzzy_merge_threshold:
                decisions.append(
                    NormalizationDecision(
                        entity_type=entity_type,
                        canonical_id=id_getter(canonical_obj),
                        candidate_id=id_getter(obj),
                        canonical_name=name_getter(canonical_obj),
                        candidate_name=name_getter(obj),
                        similarity_score=round(score, 3),
                        merge_action="flagged_for_review",
                        rationale="Similarity is material but below safe auto-merge confidence.",
                    )
                )
        if not merged:
            grouped[candidate_name] = obj
            normalized.append(obj)
    return normalized, decisions


def _assign_canonical_ids(obj: OntologyObject, name: str) -> OntologyObject:
    updates: dict[str, object] = {}
    mechanism_id, mechanism_label = match_canonical_mechanism(name)
    if mechanism_id and not obj.canonical_mechanism_id:
        updates["canonical_mechanism_id"] = mechanism_id
        updates["canonical_mechanism_label"] = mechanism_label
    state_id, _ = match_canonical_state(name)
    if state_id and not getattr(obj, "canonical_state_id", None):
        updates["canonical_state_id"] = state_id
    start_state = getattr(obj, "start_state", "")
    end_state = getattr(obj, "end_state", "")
    if start_state and end_state and not getattr(obj, "canonical_transition_id", None):
        transition_id, _ = match_canonical_transition(start_state, end_state)
        if transition_id:
            updates["canonical_transition_id"] = transition_id
    return obj.model_copy(update=updates) if updates else obj


def _load_canonical_mechanisms() -> dict[str, dict[str, list[str]]]:
    global _CANONICAL_MECHANISMS_CACHE
    if _CANONICAL_MECHANISMS_CACHE is not None:
        return _CANONICAL_MECHANISMS_CACHE
    if not CANONICAL_MECHANISM_PATH.exists():
        _CANONICAL_MECHANISMS_CACHE = {}
        return _CANONICAL_MECHANISMS_CACHE
    payload = json.loads(CANONICAL_MECHANISM_PATH.read_text(encoding="utf-8"))
    _CANONICAL_MECHANISMS_CACHE = payload if isinstance(payload, dict) else {}
    return _CANONICAL_MECHANISMS_CACHE


def _merge_aliases(canonical_obj: OntologyObject, candidate_obj: OntologyObject) -> None:
    aliases = set(canonical_obj.aliases)
    aliases.add(_object_display_name(candidate_obj))
    aliases.update(candidate_obj.aliases)
    canonical_obj.aliases = sorted(alias for alias in aliases if alias)
    canonical_obj.provenance_refs = sorted(set([*canonical_obj.provenance_refs, *candidate_obj.provenance_refs]))
    if not canonical_obj.canonical_mechanism_id and candidate_obj.canonical_mechanism_id:
        canonical_obj.canonical_mechanism_id = candidate_obj.canonical_mechanism_id
        canonical_obj.canonical_mechanism_label = candidate_obj.canonical_mechanism_label
    if not getattr(canonical_obj, "canonical_state_id", None) and getattr(candidate_obj, "canonical_state_id", None):
        canonical_obj.canonical_state_id = candidate_obj.canonical_state_id
    if not getattr(canonical_obj, "canonical_transition_id", None) and getattr(candidate_obj, "canonical_transition_id", None):
        canonical_obj.canonical_transition_id = candidate_obj.canonical_transition_id


def _alias_score(candidate_name: str, canonical_name: str) -> float:
    for root, aliases in ALIAS_REGISTRY.items():
        names = {root, *aliases}
        if candidate_name in names and canonical_name in names:
            return 0.96
    return 0.0


def _mechanism_score(candidate_obj: OntologyObject, canonical_obj: OntologyObject) -> float:
    if candidate_obj.canonical_mechanism_id and candidate_obj.canonical_mechanism_id == canonical_obj.canonical_mechanism_id:
        return 0.97
    return 0.0


def _state_score(candidate_obj: OntologyObject, canonical_obj: OntologyObject) -> float:
    if getattr(candidate_obj, "canonical_state_id", None) and getattr(candidate_obj, "canonical_state_id", None) == getattr(canonical_obj, "canonical_state_id", None):
        return 0.98
    return 0.0


def _transition_score(candidate_obj: OntologyObject, canonical_obj: OntologyObject) -> float:
    if getattr(candidate_obj, "canonical_transition_id", None) and getattr(candidate_obj, "canonical_transition_id", None) == getattr(canonical_obj, "canonical_transition_id", None):
        return 0.985
    return 0.0


def _shares_any_canonical_anchor(candidate_obj: OntologyObject, canonical_obj: OntologyObject) -> bool:
    for field_name in ("canonical_mechanism_id", "canonical_state_id", "canonical_transition_id"):
        left = getattr(candidate_obj, field_name, None)
        right = getattr(canonical_obj, field_name, None)
        if left and right and left == right:
            return True
    return False


def _anchors_are_compatible(candidate_obj: OntologyObject, canonical_obj: OntologyObject) -> bool:
    for field_name in ("canonical_state_id", "canonical_transition_id", "canonical_mechanism_id"):
        left = getattr(candidate_obj, field_name, None)
        right = getattr(canonical_obj, field_name, None)
        if left and right and left != right:
            return False
    return True


def _object_display_name(obj: OntologyObject) -> str:
    for field in ("name", "operator_label", "claim"):
        if hasattr(obj, field):
            return getattr(obj, field)
    return ""
