# Module 3 — Folder Reorganisation Brief
**For: Antigravity**
**Date: 2026-05-28**

This brief covers a full folder reorganisation of the Module 3 project folder.
No code changes. No HTML/CSS changes. File moves and folder creation only.

Base path for everything below:
`D:\PolyNovea\PolyNovea\Docx\Company Docx\Module 3 - Optimisation\`

---

## Step 1 — Create the new folder structure

Create these folders (they don't exist yet):

```
backend\
backend\routers\
backend\research\
backend\research_pipeline\
backend\research_pipeline\output\       ← runtime: backend reads from here at startup
tools\
tools\research_pipeline\                ← dev tool: pipeline scripts that generate the output
tools\research_pipeline\scripts\
tools\research_pipeline\src\
tools\research_pipeline\src\research_extraction\
tools\research_pipeline\src\research_extraction\validation\
tools\research_pipeline\data\
tools\research_pipeline\tests\
db\
docs\
show-engineering\
```

**Why this split:**
- `backend\research_pipeline\output\` — what the M3 backend loads at startup (rag_chunks.jsonl, canonical_knowledge_store.json, interventions.json, etc.). This is what the AI and show engineering engine actually pull from.
- `tools\research_pipeline\` — the Python scripts that generate those outputs. Run once when research files change. Not loaded by the backend at runtime.

`dashboard\` already exists — leave it as-is.

---

## Step 2 — Move research .md files → `backend\research\`

Flatten all research files into `backend\research\`. Remove sub-folders after moving.

**From `Module 3 research\` (root level files):**

| From | To (rename if shown) |
|------|----------------------|
| `Module 3 research\Behavioral State Transitions in Live Hospitality and Music Environments.md` | `backend\research\behavioral_state_transitions.md` |
| `Module 3 research\Contextual_Behavioral_Contradictions_Hospitality_Nightlife.md` | `backend\research\contextual_behavioral_contradictions.md` |
| `Module 3 research\Temporal Behavioral Dynamics and Sequencing Intelligence in Nightlife and Live Music.md` | `backend\research\temporal_behavioral_dynamics.md` |
| `Module 3 research\behavioral_neuroscience_mechanisms.md` | `backend\research\behavioral_neuroscience_mechanisms.md` |
| `Module 3 research\Operational measurement framework for an ontology-first behavioral intelligence system.md` | `backend\research\operational_measurement_framework.md` |
| `Module 3 research\operational_behavioral_intelligence_nightlife.md` | `backend\research\operational_behavioral_intelligence_nightlife.md` |
| `Module 3 research\deep-research-report (2).md` | `backend\research\deep_research_report.md` |

**From `Module 3 research\Music implementation\`:**

| From | To (rename) |
|------|-------------|
| `Music, Behavior, and Synchronization Research.md` | `backend\research\music_behavior_synchronization.md` |
| `Operational_Economics_of_Auditory_Environments.md` | `backend\research\operational_economics_auditory_environments.md` |
| `Research_Prompt_6_Auditory_Fatigue_Sensory_Load_Long_Duration_Exposure.md` | `backend\research\auditory_fatigue_sensory_load.md` |
| `Research_Prompt_7_Crowd_State_Estimation.md` | `backend\research\crowd_state_estimation.md` |
| `Scientific_Validity_Review_Frequency_Claims.md` | `backend\research\frequency_claims_validity_review.md` |
| `computational_audio_features_behavioral_intelligence.md` | `backend\research\computational_audio_features.md` |
| `psychoacoustic_foundations_behavioral_environment_systems.md` | `backend\research\psychoacoustic_foundations.md` |
| `behavioral_pipeline_refactor_brief.md` | `docs\behavioral_pipeline_refactor_brief.md` |

**From `Module 3 research\bheavioural research\` (note: typo in folder name — that's correct, it's named wrong):**

| From | To (rename) |
|------|-------------|
| `Behavioral Sequencing and Emotional Pacing in Live Hospitality Environments.md` | `backend\research\behavioral_sequencing_emotional_pacing.md` |
| `Cultural & Demographic Effects on Hospitality Behavior.md` | `backend\research\cultural_demographic_effects.md` |
| `Emotional Memory and Loyalty Mechanisms in Live Hospitality Experiences.md` | `backend\research\emotional_memory_loyalty_mechanisms.md` |
| `Environmental & Operational Factors in Hospitality.md` | `backend\research\environmental_operational_factors.md` |
| `Hospitality Spending & Behavioral Triggers.md` | `backend\research\hospitality_spending_behavioral_triggers.md` |
| `Identity Signaling and Social-Status Dynamics in Hospitality Environments.md` | `backend\research\identity_signaling_social_status.md` |
| `Operational Music Mechanisms in Hospitality Environments.md` | `backend\research\operational_music_mechanisms.md` |
| `Social Sharing, Virality, and Amplification in Live Hospitality Environments.md` | `backend\research\social_sharing_virality_amplification.md` |
| `behavioral_intervention_system_attention_mechanisms.md` | `backend\research\behavioral_intervention_attention_mechanisms.md` |
| `polynovea-live-behavioral-experimentation-framework.md` | `backend\research\live_behavioral_experimentation_framework.md` |

After all files are moved, **delete these now-empty folders:**
- `Module 3 research\Music implementation\`
- `Module 3 research\bheavioural research\`
- `Module 3 research\`

---

## Step 3 — Split Research Extraction Pipeline into two destinations

The pipeline has two parts with different purposes. They go to different places.

---

### 3A — Output files → `backend\research_pipeline\output\`
*(This is what the M3 backend and show engineering engine actually read at runtime)*

Move the entire contents of `Research Extraction Pipeline\output\` into `backend\research_pipeline\output\`:

| From | To |
|------|----|
| `Research Extraction Pipeline\output\` (entire folder — all files and subfolders) | `backend\research_pipeline\output\` |

Key files the backend will load: `rag_chunks.jsonl`, `canonical_knowledge_store.json`, `interventions.json`, `behavioral_states.json`, `causal_relationships.json`, `temporal_dynamics.json`, `variables.json`, `kpis.json`.

---

### 3B — Pipeline source code → `tools\research_pipeline\`
*(Dev tool — run this when research .md files change to regenerate the output above)*

**Scripts:**

| From | To |
|------|----|
| `Research Extraction Pipeline\scripts\run_pipeline.py` | `tools\research_pipeline\scripts\run_pipeline.py` |
| `Research Extraction Pipeline\scripts\build_review_decisions_template.py` | `tools\research_pipeline\scripts\build_review_decisions_template.py` |

**Source package — move entire `src\research_extraction\` including all subfolders:**

| From | To |
|------|----|
| `Research Extraction Pipeline\src\research_extraction\` (all files) | `tools\research_pipeline\src\research_extraction\` |

Files inside: `__init__.py`, `classification.py`, `confidence.py`, `config.py`, `coverage.py`, `extractors.py`, `graph_builder.py`, `graph_health.py`, `ids.py`, `ingestion.py`, `llm.py`, `normalization.py`, `pipeline.py`, `profile_extractors.py`, `rag.py`, `registries.py`, `research_profiles.py`, `review.py`, `schemas.py`, `utils.py`, and the `validation\` subfolder (`__init__.py`, `rules.py`, `service.py`).

**Data:**

| From | To |
|------|----|
| `Research Extraction Pipeline\data\canonical_mechanisms.json` | `tools\research_pipeline\data\canonical_mechanisms.json` |
| `Research Extraction Pipeline\data\canonical_states.json` | `tools\research_pipeline\data\canonical_states.json` |
| `Research Extraction Pipeline\data\canonical_transitions.json` | `tools\research_pipeline\data\canonical_transitions.json` |

**Tests:**

| From | To |
|------|----|
| `Research Extraction Pipeline\tests\test_gold_coverage.py` | `tools\research_pipeline\tests\test_gold_coverage.py` |

**Config files:**

| From | To |
|------|----|
| `Research Extraction Pipeline\requirements.txt` | `tools\research_pipeline\requirements.txt` |
| `Research Extraction Pipeline\.env.example` | `tools\research_pipeline\.env.example` |
| `Research Extraction Pipeline\.env` | `tools\research_pipeline\.env` |
| `Research Extraction Pipeline\README.md` | `tools\research_pipeline\README.md` |

**Do NOT move `.vendor\`** — leave it inside `Research Extraction Pipeline\`. Claude will clean it up after.

---

## Step 4 — Move DB and SQL files → `db\`

| From | To |
|------|----|
| `supabase_module3_tables.sql` | `db\supabase_module3_tables.sql` |

---

## Step 5 — Move architecture and planning docs → `docs\`

| From | To |
|------|----|
| `Module 3 DB\module_3_db_plan.md` | `docs\module_3_db_plan.md` |
| `Module 3 DB\module_3_refined_architecture.md` | `docs\module_3_refined_architecture.md` |
| `session_retrospective_2026_05_28.json` | `docs\session_retrospective_2026_05_28.json` |

After moving, **delete the now-empty folder:**
- `Module 3 DB\`

---

## Step 6 — Move dashboard stitch files

The `dashboard\Stitch files\` folder (contains `code.html` + `screen.png`) — move up into `docs\stitch\`:

| From | To |
|------|----|
| `dashboard\Stitch files\code.html` | `docs\stitch\code.html` |
| `dashboard\Stitch files\screen.png` | `docs\stitch\screen.png` |

Then **delete:**
- `dashboard\Stitch files\`

---

## Step 7 — Delete the old prototype UI

**Delete this entire folder and all its contents:**
- `module3-live-ops-ui\`

It contains `app.js`, `index.html`, `styles.css` — this was an early prototype, fully superseded by `dashboard\index.html`. Nothing in it is needed.

---

## Step 8 — Create placeholder .gitkeep files

These folders need to exist in the repo but have no files yet. Create an empty `.gitkeep` file inside each:

- `backend\routers\.gitkeep`
- `show-engineering\.gitkeep`

---

## Final state after reorganisation

```
Module 3 - Optimisation\
│
├── backend\
│   ├── routers\                     ← empty, Claude fills this in Phase 2
│   ├── research\                    ← 23 .md research files, flat, clean names
│   └── research_pipeline\
│       └── output\                  ← rag_chunks.jsonl, canonical_knowledge_store.json,
│                                       interventions.json, behavioral_states.json, etc.
│                                       (this is what the AI engine reads at runtime)
│
├── tools\
│   └── research_pipeline\           ← dev tool to regenerate the output above
│       ├── scripts\
│       ├── src\research_extraction\
│       ├── data\
│       ├── tests\
│       ├── requirements.txt
│       ├── .env
│       ├── .env.example
│       └── README.md
│
├── dashboard\
│   ├── index.html
│   ├── antigravity_todo.md
│   └── dashboard_redesign_brief.md
│
├── db\
│   └── supabase_module3_tables.sql
│
├── docs\
│   ├── module_3_db_plan.md
│   ├── module_3_refined_architecture.md
│   ├── session_retrospective_2026_05_28.json
│   ├── behavioral_pipeline_refactor_brief.md
│   └── stitch\
│       ├── code.html
│       └── screen.png
│
└── show-engineering\                ← empty placeholder
```

---

## What Antigravity does NOT touch

- No changes to `dashboard\index.html` content
- No changes to any `.py` files
- No changes to any `.json` output files
- No changes to `dashboard\antigravity_todo.md` (that's a separate work list)
- The `.vendor\` folder inside `Research Extraction Pipeline\` — leave it, Claude handles deletion

---

## After Antigravity is done

Confirm by listing the top-level folders so Claude can verify the structure is correct before proceeding to Phase 2 (GitHub repo creation + M3 FastAPI skeleton).
