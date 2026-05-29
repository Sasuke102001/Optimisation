# Antigravity — Research Extraction Pipeline Upgrade

**Project:** Module 3 - Optimisation  
**Root:** `D:\PolyNovea\PolyNovea\Docx\Company Docx\Module 3 - Optimisation\`  
**Scope:** Python only — no frontend work in this task.

---

## Context

The research extraction pipeline lives in `tools/research_pipeline/`. It ingests a flat folder of `.md` research files and produces structured JSON output (variables, states, relationships, interventions, KPIs, RAG chunks, etc.) into `backend/research_pipeline/output/`.

The pipeline already works and has been run once on the existing 28 research files in `backend/research/`. We now have a second corpus of SE (Show Engineering) research files in `backend/research_se/` — and we need to be able to run the pipeline against either folder on demand.

The pipeline entry point: `tools/research_pipeline/scripts/run_pipeline.py`  
The pipeline core: `tools/research_pipeline/src/research_extraction/pipeline.py`  
Config model: `tools/research_pipeline/src/research_extraction/config.py`  
Extractors: `tools/research_pipeline/src/research_extraction/extractors.py`

The pipeline's `main()` function already accepts `--research-dir` and `--output-dir` CLI args — use those, don't rewrite the pipeline.

---

## Task 1 — Runner Script

**File to create:** `tools/research_pipeline/scripts/runner.py`

A convenience CLI wrapper around the existing `run_pipeline.py`. Maps named sources to the correct paths so you never have to type full paths manually.

### Interface

```
python tools/research_pipeline/scripts/runner.py --source research
python tools/research_pipeline/scripts/runner.py --source research_se
python tools/research_pipeline/scripts/runner.py --source all
python tools/research_pipeline/scripts/runner.py --source research --incremental
python tools/research_pipeline/scripts/runner.py --source research_se --llm-provider openai --llm-model gpt-4o
```

### Path mappings (hardcoded relative to repo root)

| `--source` | Research dir | Output dir |
|---|---|---|
| `research` | `backend/research/` | `backend/research_pipeline/output/` |
| `research_se` | `backend/research_se/` | `backend/research_pipeline/output_se/` |
| `all` | runs `research` then `research_se` sequentially | respective output dirs |

### `--incremental` flag

When passed, the runner checks a manifest file (`backend/research_pipeline/.manifest_{source}.json`) that stores `{filename: mtime}` for files processed in the last run. Only passes files whose mtime has changed to the pipeline. On completion, updates the manifest.

**Important:** The pipeline's `ingest_research_directory` in `ingestion.py` reads all `.md` files from the given dir. For incremental mode, write a pre-filter: copy only changed files to a temp dir, run the pipeline against that temp dir, then merge the output with the existing output JSON (append-only into the arrays). Keep it simple — if merge gets complicated, just re-run full and skip the merge step for now.

### Pass-through args

Any extra args passed to the runner (`--llm-provider`, `--llm-model`, `--llm-base-url`, `--enable-embeddings`, `--review-decisions-file`) should be forwarded to `run_pipeline.py` as-is. Use `argparse` with `parse_known_args` to capture them.

### Source corpus tag

When the runner invokes the pipeline for `research_se`, it should pass `--extractor-version 0.1.0-se` so outputs are tagged distinctly in `run_summary.json`.

---

## Task 2 — Three SE-Specific Extractors

The current `extractors.py` has rule-based extractors for variables, states, interventions, relationships, etc. These are built for descriptive science ("noise above 85 dB activates HPA axis"). The SE research corpus contains prescriptive operational content — intervention recipes, parameter thresholds, decision rules — that the existing extractors miss or partially capture.

Add three new extractors. They slot into the existing `extract_all()` function in `extractors.py` which is called per section. Each extractor returns objects that map to existing schema types — no new schemas needed.

### Extractor 1 — SE Intervention Recipe Extractor

**What it finds:** Full operational intervention recipes with trigger, action, parameter delta, timing, and expected outcome in one coherent object.

**Target schema:** `Intervention` (already exists in `schemas.py`)

**What to populate beyond the existing fields:**
- `trigger_conditions` — the specific measurable condition that fires the intervention (e.g., "BPM drops below 118 AND dance floor occupancy < 40%")
- `expected_effects` — quantified expected outcome (e.g., "dance floor occupancy increase 15–25% within 4 minutes")
- `timing_constraints` — timing window as a string (e.g., "apply over 3–4 minutes, not abrupt")
- `required_variables` — the parameters being acted on (e.g., "BPM", "SPL")
- `affected_states` — the behavioral state being targeted (e.g., "disengagement", "reactivation")

**Detection patterns to look for in section text:**
- Sentences containing `"when"` + a measurable condition + `"increase"/"decrease"/"shift"/"raise"/"lower"` + a parameter
- Bullet patterns: `"Trigger:"`, `"Action:"`, `"Expected:"`, `"Duration:"`, `"Timing:"`
- Sentences with BPM/SPL/lux/temperature values followed by directional verbs
- Numbered step patterns: `"1. ... 2. ... 3. ..."`

**Classification filter:** Only run this extractor on sections classified as `intervention` or `operational_implication`. Check `classification.section_type` before running.

---

### Extractor 2 — Parameter Range Extractor

**What it finds:** Concrete numeric thresholds and ranges for operational parameters.

**Target schema:** `Variable` (already exists) — populate the `contextual_limitations` and `evidence_notes` fields with range data, or if a cleaner approach exists in the schema, use it.

**What to extract per range found:**
- Parameter name (e.g., "BPM", "SPL", "lux", "temperature", "crowd density")
- Min value, max value, unit
- Context/condition it applies to (e.g., "euphoric state", "post-midnight", "late-night venue")
- Source sentence

**Detection patterns:**
- Regex for numeric ranges: `\d+[\–\-]\d+\s*(BPM|bpm|dB|dBA|lux|°C|%)`
- Patterns like `"between X and Y"`, `"X to Y BPM"`, `"above X dB"`, `"below X lux"`
- Tables in markdown with parameter/value columns

**Where to store:** Extend the matched `Variable` object's `evidence_notes` with a structured string: `"Range: {min}–{max} {unit} | Context: {context}"`. If no matching Variable exists in the registry yet, create a new `Variable` with the range as `raw_text`.

**Classification filter:** Run on all section types — ranges appear everywhere.

---

### Extractor 3 — Agent Decision Rule Extractor

**What it finds:** If/then decision logic that maps directly to agent reasoning. SE agents need these as their rule base.

**Target schema:** `Relationship` (already exists) — a decision rule is a directed causal relationship with a condition and an action.

**What to populate:**
- `source_entity` — the condition/trigger state
- `target_entity` — the outcome/action
- `relationship_type` — set to `"decision_rule"` (new value, valid as a string)
- `mechanism` — the reasoning behind the rule
- `effect_size` — confidence/effect size if stated
- `evidence_notes` — the raw if/then text

**Detection patterns:**
- `"if ... then ..."` sentence structures
- `"when X, apply Y"` patterns
- `"X indicates Y should be triggered"`
- Operator guidance bullets: `"Signal: ... Response: ..."`, `"Cue: ... Action: ..."`
- Decision tree language: `"in the case of"`, `"provided that"`, `"as long as"`

**Classification filter:** `intervention`, `operational_implication`, `mechanism` sections.

---

## Task 3 — Wire New Extractors into `extract_all()`

In `extractors.py`, the `extract_all(section, classification, config)` function calls individual extractors and returns an `ExtractionBundle`. Add calls to the three new extractors here.

The SE extractors should only run when the source file is from `research_se/` — check `section.relative_source_file` or pass a flag through `PipelineConfig`. Simplest approach: add `corpus: str = "core"` to `PipelineConfig`, set it to `"se"` when runner passes `--extractor-version 0.1.0-se`, and gate the new extractors on `config.corpus == "se"`.

Actually — run the SE extractors on both corpora. The parameter range extractor especially will find useful data in the existing 28 files too. Only gate if you find noise issues after testing.

---

## Task 4 — Config Addition

In `config.py`, add one field to `PipelineConfig`:

```python
corpus: str = "core"  # "core" or "se" — set by runner, tags output
```

No other config changes needed.

---

## Task 5 — Smoke Test

After implementation, run both:

```bash
cd "D:\PolyNovea\PolyNovea\Docx\Company Docx\Module 3 - Optimisation"

# Existing corpus
python tools/research_pipeline/scripts/runner.py --source research

# SE corpus
python tools/research_pipeline/scripts/runner.py --source research_se
```

Verify:
- `backend/research_pipeline/output/run_summary.json` — counts roughly match previous run (986 sections, ~24 variables, etc.)
- `backend/research_pipeline/output_se/run_summary.json` — exists and has non-zero section/intervention/relationship counts
- `output_se/interventions.json` — contains objects with populated `trigger_conditions` and `expected_effects` (from Extractor 1)
- `output_se/causal_relationships.json` — contains objects with `relationship_type: "decision_rule"` (from Extractor 3)

---

## What NOT to change

- Do not modify `backend/research_pipeline/output/` contents — the existing output stays as-is until a deliberate re-run
- Do not change the schema classes in `schemas.py` — work within existing types
- Do not change `run_pipeline.py` — the runner wraps it, doesn't replace it
- Do not add new dependencies — use what's already in `tools/research_pipeline/requirements.txt` and `.vendor/`

---

## File Summary

| File | Action |
|------|--------|
| `tools/research_pipeline/scripts/runner.py` | **Create** |
| `tools/research_pipeline/src/research_extraction/extractors.py` | **Modify** — add 3 extractors, wire into `extract_all()` |
| `tools/research_pipeline/src/research_extraction/config.py` | **Modify** — add `corpus` field |
| `backend/research_pipeline/output_se/` | **Created automatically** by runner on first SE run |
