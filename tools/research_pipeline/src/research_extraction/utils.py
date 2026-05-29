from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Iterable


SLUG_RE = re.compile(r"[^A-Z0-9]+")
SPACE_RE = re.compile(r"\s+")
MOJIBAKE_MARKERS = ("â€", "â€“", "â€”", "â€˜", "â€™", "â€œ", "â€\x9d", "â†", "Ã", "�")
MOJIBAKE_REPLACEMENTS = {
    "â€˜": "'",
    "â€™": "'",
    "â€œ": '"',
    "â€\x9d": '"',
    "â€“": "-",
    "â€”": "-",
    "â€‘": "-",
    "â€": '"',
    "â†’": "->",
    "â†": "<-",
    "â‰¥": ">=",
    "â‰¤": "<=",
    "Ã—": "x",
    "\ufeff": "",
}


def normalize_whitespace(text: str) -> str:
    return SPACE_RE.sub(" ", text).strip()


def normalize_mojibake(text: str) -> str:
    normalized = text
    if any(marker in normalized for marker in MOJIBAKE_MARKERS):
        try:
            repaired = normalized.encode("latin-1", errors="ignore").decode("utf-8", errors="ignore")
            if repaired and repaired.count("�") <= normalized.count("�"):
                normalized = repaired
        except Exception:
            pass
    for broken, fixed in MOJIBAKE_REPLACEMENTS.items():
        normalized = normalized.replace(broken, fixed)
    return normalized


def slugify_upper(text: str) -> str:
    normalized = normalize_whitespace(text).upper()
    return SLUG_RE.sub("_", normalized).strip("_") or "UNKNOWN"


def stable_hash(text: str, length: int = 12) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:length]


def sentence_split(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])", text.strip())
    return [part.strip() for part in parts if normalize_whitespace(part)]


def bullet_split(text: str) -> list[str]:
    lines = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(("- ", "* ", "+ ")):
            lines.append(line[2:].strip())
        elif re.match(r"^\d+\.\s+", line):
            lines.append(re.sub(r"^\d+\.\s+", "", line).strip())
    return lines


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data: object) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def extract_minutes(text: str) -> list[float]:
    values: list[float] = []
    for match in re.finditer(r"(\d+(?:\.\d+)?)\s*(?:-|to)?\s*(\d+(?:\.\d+)?)?\s*(minutes?|mins?|hours?|hrs?)", text, re.IGNORECASE):
        first = float(match.group(1))
        second = float(match.group(2)) if match.group(2) else None
        unit = match.group(3).lower()
        multiplier = 60.0 if unit.startswith("hour") or unit.startswith("hr") else 1.0
        values.append(first * multiplier)
        if second is not None:
            values.append(second * multiplier)
    return sorted(set(values))
