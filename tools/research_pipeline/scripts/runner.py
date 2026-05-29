"""
runner.py — Convenience CLI wrapper for the research extraction pipeline.

Usage:
    python tools/research_pipeline/scripts/runner.py --source research
    python tools/research_pipeline/scripts/runner.py --source research_se
    python tools/research_pipeline/scripts/runner.py --source all
    python tools/research_pipeline/scripts/runner.py --source research --incremental
    python tools/research_pipeline/scripts/runner.py --source research_se --llm-provider openai --llm-model gpt-4o
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path


# ---------------------------------------------------------------------------
# Resolve repo root (Module 3 - Optimisation/)
# ---------------------------------------------------------------------------
# runner.py lives at:  tools/research_pipeline/scripts/runner.py
# parents[3]        =  Module 3 - Optimisation/
_RUNNER_DIR = Path(__file__).resolve().parent
ROOT = _RUNNER_DIR.parents[2]  # Module 3 - Optimisation/
_RUN_PIPELINE_SCRIPT = _RUNNER_DIR / "run_pipeline.py"

# ---------------------------------------------------------------------------
# Source → (research_dir, output_dir, extractor_version_tag) mappings
# ---------------------------------------------------------------------------
_SOURCES: dict[str, tuple[Path, Path, str]] = {
    "research": (
        ROOT / "backend" / "research",
        ROOT / "backend" / "research_pipeline" / "output",
        "0.1.0",
    ),
    "research_se": (
        ROOT / "backend" / "research_se",
        ROOT / "backend" / "research_pipeline" / "output_se",
        "0.1.0-se",
    ),
}

_MANIFEST_DIR = ROOT / "backend" / "research_pipeline"


# ---------------------------------------------------------------------------
# Incremental helpers
# ---------------------------------------------------------------------------

def _manifest_path(source: str) -> Path:
    return _MANIFEST_DIR / f".manifest_{source}.json"


def _load_manifest(source: str) -> dict[str, float]:
    path = _manifest_path(source)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_manifest(source: str, research_dir: Path) -> None:
    manifest: dict[str, float] = {}
    for md_file in sorted(research_dir.glob("*.md")):
        try:
            manifest[md_file.name] = md_file.stat().st_mtime
        except OSError:
            pass
    _MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    _manifest_path(source).write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _changed_files(source: str, research_dir: Path) -> list[Path]:
    """Return .md files whose mtime has changed since the last manifest."""
    manifest = _load_manifest(source)
    changed: list[Path] = []
    for md_file in sorted(research_dir.glob("*.md")):
        last_mtime = manifest.get(md_file.name)
        try:
            current_mtime = md_file.stat().st_mtime
        except OSError:
            continue
        if last_mtime is None or abs(current_mtime - last_mtime) > 0.01:
            changed.append(md_file)
    return changed


# ---------------------------------------------------------------------------
# Core run helper
# ---------------------------------------------------------------------------

def _run_source(
    source: str,
    incremental: bool,
    passthrough_args: list[str],
) -> int:
    research_dir, output_dir, extractor_version = _SOURCES[source]

    if not research_dir.exists():
        print(f"[runner] ERROR: research dir does not exist: {research_dir}", file=sys.stderr)
        return 1

    effective_research_dir = research_dir
    tmp_dir: str | None = None

    if incremental:
        changed = _changed_files(source, research_dir)
        if not changed:
            print(f"[runner] incremental: no changed files for '{source}' — skipping.")
            return 0
        print(f"[runner] incremental: {len(changed)} changed file(s) detected for '{source}'.")
        # Copy only changed files to a temp dir; pipeline ingests from there.
        tmp_dir = tempfile.mkdtemp(prefix="runner_incremental_")
        for f in changed:
            shutil.copy2(f, Path(tmp_dir) / f.name)
        effective_research_dir = Path(tmp_dir)

    print(f"[runner] source={source}  research_dir={effective_research_dir}  output_dir={output_dir}")

    cmd = [
        sys.executable,
        str(_RUN_PIPELINE_SCRIPT),
        "--research-dir", str(effective_research_dir),
        "--output-dir", str(output_dir),
        "--extractor-version", extractor_version,
        *passthrough_args,
    ]

    import subprocess
    result = subprocess.run(cmd)
    returncode: int = result.returncode

    if tmp_dir:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    if returncode == 0:
        _save_manifest(source, research_dir)
        print(f"[runner] manifest updated for '{source}'.")

    return returncode


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Runner wrapper for the research extraction pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--source",
        required=True,
        choices=list(_SOURCES.keys()) + ["all"],
        help="Which research corpus to process. 'all' runs research then research_se.",
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        default=False,
        help=(
            "Only process files that have changed since the last run. "
            "Tracked via backend/research_pipeline/.manifest_{source}.json"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    # parse_known_args lets any extra flags pass through to run_pipeline.py
    args, passthrough = parser.parse_known_args(argv)

    sources_to_run = list(_SOURCES.keys()) if args.source == "all" else [args.source]

    overall_rc = 0
    for source in sources_to_run:
        rc = _run_source(source, incremental=args.incremental, passthrough_args=passthrough)
        if rc != 0:
            overall_rc = rc
            print(f"[runner] WARNING: pipeline exited with code {rc} for source='{source}'")

    return overall_rc


if __name__ == "__main__":
    raise SystemExit(main())
