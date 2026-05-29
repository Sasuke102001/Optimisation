from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from research_extraction.utils import normalize_whitespace


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"


@lru_cache(maxsize=1)
def load_canonical_states() -> dict[str, dict]:
    return _load_json(DATA_DIR / "canonical_states.json")


@lru_cache(maxsize=1)
def load_canonical_transitions() -> dict[str, dict]:
    return _load_json(DATA_DIR / "canonical_transitions.json")


@lru_cache(maxsize=1)
def load_canonical_mechanisms() -> dict[str, dict]:
    return _load_json(DATA_DIR / "canonical_mechanisms.json")


def match_canonical_state(name: str) -> tuple[str | None, str | None]:
    normalized_name = normalize_whitespace(name).lower()
    if not normalized_name:
        return None, None
    fallback: tuple[str | None, str | None] = (None, None)
    for state_id, payload in load_canonical_states().items():
        labels = {payload.get("label", ""), *payload.get("aliases", [])}
        normalized_labels = {normalize_whitespace(label).lower() for label in labels if normalize_whitespace(label)}
        if normalized_name in normalized_labels:
            return state_id, str(payload.get("label", state_id))
        if any(_token_safe_match(normalized_name, label) for label in normalized_labels):
            fallback = (state_id, str(payload.get("label", state_id)))
    return fallback


def match_canonical_transition(start_state: str, end_state: str) -> tuple[str | None, dict | None]:
    start_id, _ = match_canonical_state(start_state)
    end_id, _ = match_canonical_state(end_state)
    for transition_id, payload in load_canonical_transitions().items():
        if payload.get("start_state_id") == start_id and payload.get("end_state_id") == end_id:
            return transition_id, payload
    return None, None


def match_canonical_mechanism(name: str) -> tuple[str | None, str | None]:
    normalized_name = normalize_whitespace(name).lower()
    if not normalized_name:
        return None, None
    fallback: tuple[str | None, str | None] = (None, None)
    for mechanism_id, payload in load_canonical_mechanisms().items():
        labels = {payload.get("label", ""), *payload.get("aliases", [])}
        normalized_labels = {normalize_whitespace(label).lower() for label in labels if normalize_whitespace(label)}
        if normalized_name in normalized_labels:
            return mechanism_id, str(payload.get("label", mechanism_id))
        if any(_token_safe_match(normalized_name, label) for label in normalized_labels):
            fallback = (mechanism_id, str(payload.get("label", mechanism_id)))
    return fallback


def _load_json(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _token_safe_match(left: str, right: str) -> bool:
    if left == right:
        return True
    return bool(re.search(rf"(?<![a-z0-9]){re.escape(right)}(?![a-z0-9])", left) or re.search(rf"(?<![a-z0-9]){re.escape(left)}(?![a-z0-9])", right))
