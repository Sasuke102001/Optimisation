# Module 3 — Master Todo
**Last updated: 2026-05-29**

---

## 🔴 Step 1 — Unblock M2 RDS (immediate)

### S1-1 — Run M2 RDS DDL
Script is ready at `backend/db/run_m2_rds.py`. Blocked — dev machine not in AWS security group.

**Two options:**
- SSH into M2 EC2 (43.205.229.130) and run from there — EC2 is already whitelisted
- OR add dev machine public IP to M2 RDS inbound rules in AWS console

Creates on M2 RDS:
- `m3_segment_validation_feedback`
- `m3_venue_behavioral_outcomes`
- `m3_kpi_observations`
- `m3_dwell_observations`
- `m3_segment_table_log`
- `m3_app_user` role (password: `M3app_PNv2026!` — in `backend/.env`)

---

## 🔴 Step 2 — Complete SE Research (Perplexity)

### S2-1 — Run Prompts 1 & 5 (not yet done)
- Prompt 1 — BPM, Neural Entrainment and Behavioral State Mapping
- Prompt 5 — Groove, Syncopation and the Neurological Urge to Move

Save outputs as `.md` files to `backend/research/`.

### S2-2 — Run Prompts 6–12 (High Value)
- Prompt 6 — Lighting Psychology
- Prompt 7 — Crowd Synchrony and Social Contagion
- Prompt 8 — Temporal Dynamics: Full Night Arc
- Prompt 9 — Indian Cultural Context ⚠️ especially important
- Prompt 10 — Novelty vs Familiarity
- Prompt 11 — Volume, SPL and Disinhibition
- Prompt 12 — Staff Choreography as Behavioral Engineering Tool

### S2-3 — Run Prompts 13–16 (Good to Have)
- Prompt 13 — Temperature, Air Quality, Physical Comfort
- Prompt 14 — Alcohol, Pharmacology and Music Interaction
- Prompt 15 — Peak-End Rule and Emotional Memory
- Prompt 16 — Silence, Space and Dynamic Contrast

**All prompts are at `backend/research/prompts/se_research_prompts.md`**
**Already done: Prompts 2, 3, 4 (harmonic, frequency, transition architecture)**

---

## 🔴 Step 3 — Deploy FastAPI to Azure VM

### S3-1 — SSH into VM and set up environment
```
ssh -i keys/polynovea-m3-key.pem subrojitroy@20.219.216.138
```
- Install Python 3.11, pip, virtualenv
- Copy `backend/` to VM
- Install requirements: `pip install -r requirements.txt`
- Create `.env` on VM (same as local `backend/.env`)

### S3-2 — Run as systemd service on port 8001
- Create `/etc/systemd/system/m3-api.service`
- `uvicorn main:app --host 0.0.0.0 --port 8001`
- Enable and start: `systemctl enable m3-api && systemctl start m3-api`

### S3-3 — Confirm health check
`curl http://20.219.216.138:8001/health` → `{"status": "ok"}`

---

## 🟡 Step 4 — Re-run Extraction Pipeline

### S4-1 — Re-run pipeline after new SE research files added
After Steps S2-1 through S2-3 are done, re-run the extraction pipeline:
```
python tools/research_pipeline/scripts/run_pipeline.py
```
Expected: ~400–500 new entities from SE research files.

### S4-2 — Review 9 missing canonical transitions
`run_summary.json` shows `missing_canonical_transitions: 9`.
Add valid ones to `data/canonical_transitions.json`.

---

## 🟡 Step 5 — Design SE Extraction Pipeline (Architecture Session)

This is a **Claude + team design session** before any code is written.

### S5-1 — Define SE entity schema
The SE research is prescriptive (WHAT TO DO), not mechanistic (WHY).
New entity types needed:
- `Prescription` — {state, bpm_range, chord, mode, frequency_emphasis, timing}
- `Threshold` — {parameter, value, effect, crowd_type}
- `ParameterMapping` — {crowd_state → music_parameters}
- `TransitionRule` — {from_state, to_state, bpm_path, harmonic_path, risk_level}
- `GrooveProfile` — {syncopation_level, microtiming, density, repetition}
- `CrowdStateArc` — {time_index, bpm_target, energy_level, action}

### S5-2 — Define vector store approach
Options:
- `pgvector` extension on Azure PostgreSQL (already provisioned — simplest)
- `ChromaDB` on Azure VM (lightweight, no DB extension needed)

Decision needed before building.

### S5-3 — Define KAG graph structure
How state→prescription→signal chains are stored and traversed by Agent 3.
Simple JSON graph vs full graph DB (Neo4j).

---

## 🟡 Step 6 — Build SE Extraction Pipeline (Codex)

### S6-1 — Build `backend/se_pipeline/`
Separate from existing `tools/research_pipeline/`.
- New extractor for SE entity types
- Builds `se_prescriptions.json`, `se_thresholds.json`, `se_transitions.json`
- Builds `se_rag_chunks.json` + vector embeddings → vector store
- Builds KAG graph from state→prescription→signal relationships

**Blocked on: S2 (research files) + S5 (schema design)**

---

## 🟡 Step 7 — Build 6-Agent Evidence System (Codex)

One step at a time. Do not start next agent until current one is tested.

### S7-1 — Build Agent 1: Behavioral KAG
- Input: session state (current KPI RAG pattern + zone + time in session)
- Queries: `m3_mechanisms.json`, `m3_states.json`, `m3_relationships.json`, `m3_interventions.json`
- Output: canonical state match + mechanism chains + intervention candidates
- Model: Nemotron 70B via Key 1

### S7-2 — Build Agent 2: Behavioral RAG
- Input: same session state
- Queries: vector store over raw behavioral research `.md` files (24 existing files)
- Output: top-K verbatim theory passages most relevant to current state
- Model: Nemotron 70B via Key 1

### S7-3 — Build Agent 3: Neuroacoustic KAG
- Input: session state + canonical state from Agent 1
- Queries: SE pipeline outputs (`se_prescriptions.json`, `se_transitions.json`, `se_thresholds.json`)
- Output: specific music parameters — BPM range, chord, mode, frequency emphasis, transition path
- Model: Nemotron 70B via Key 2
- **Blocked on: S6**

### S7-4 — Build Agent 4: Neuroacoustic RAG
- Input: same session state + canonical state
- Queries: vector store over raw SE research `.md` files
- Output: verbatim neuroacoustic theory passages — the mechanistic why behind each prescription
- Model: Nemotron 70B via Key 2
- **Blocked on: S6**

### S7-5 — Build evidence package assembler
- Waits for Agents 1–4 to complete (parallel async)
- Assembles: structured evidence (Agents 1 & 3) + theory passages (Agents 2 & 4) + M3 session history + M2 venue profile
- Passes full package to Agent 5

### S7-6 — Build Agent 5: Integrator
- Input: full evidence package from S7-5
- Produces: unified session picture — current state + behavioral mechanism + neuroacoustic prescription
- No suggestion output — coherence synthesis only
- Model: Nemotron 70B via Key 3

### S7-7 — Build Agent 6: Prescriber
- Input: Agent 5 integrated picture + M3/M2 data
- Produces: final 5-part suggestion (State → Mechanism → Lever → Action → Signal)
- Model: DeepSeek R1 via Key 3

### S7-8 — Wire into API endpoints
- `POST /api/session/brief` → triggers full 6-agent sweep
- `POST /api/show/brief` → same sweep with show engineering context
- Replace TODO placeholders in `backend/routers/session_brief.py` and `backend/routers/show.py`

---

## 🟢 Dashboard — Antigravity Remaining

### D-1 — Fix QuickEnvCheck: dropdowns → segmented buttons
4 quick-env selectors (`sound / temp / energy / queue`) are `<select>` dropdowns.
Must match the Environment tab segmented button style. No dropdowns anywhere.

### D-3 — Verify remaining brief items
- [ ] Table detail modal bottom sheet works on mobile
- [ ] Countdown bar warning/danger states trigger correctly at <2min and 0
- [ ] Unlogged KPI card pulse animation fires
- [ ] All 6 toast triggers fire correctly
- [ ] Open Session button disabled state when venue empty or 0 tables
- [ ] Stepper flash-green animation on venue recall

---

## ✅ Done

- [x] M2 schema confirmed (all 5 tables, column structures)
- [x] fetch_m2_venue_context() 5-query pattern designed
- [x] M2 cleanup — module3.py removed, prompts.py reverted, main.py reverted
- [x] Folder reorganisation (Antigravity)
- [x] research_profiles.py rewritten — all 24 files profiled
- [x] Pipeline run with LLM enabled — full extraction complete (1318 chunks, 87 interventions, 20 states)
- [x] M3↔M2 integration pattern agreed (push model, Bayesian blend, no overrides)
- [x] session_mode semantics agreed (row-level: observation_only / engineering_active / post_intervention)
- [x] Azure PostgreSQL provisioned — polynovea-m3.postgres.database.azure.com, database: polynovea_m3
- [x] Azure VM provisioned — polynovea-m3-api, IP: 20.219.216.138
- [x] M3 schema applied — 15 tables live in polynovea_m3
- [x] M2 RDS DDL written — run_m2_rds.py ready (not yet executed)
- [x] FastAPI skeleton complete — main.py, database.py, models.py, 3 routers, requirements.txt
- [x] Dashboard React migration complete (Antigravity — React + Vite + TypeScript + Zustand)
- [x] Dashboard visual check — all screens verified, 0 build errors
- [x] SE research prompts written — 16 prompts in backend/research/prompts/se_research_prompts.md
- [x] SE research Prompt 2 done — harmonic_psychology_chord_behavioral_response.md
- [x] SE research Prompt 3 done — frequency_psychology_behavioral_prescriptions.md
- [x] SE research Prompt 4 done — musical_transition_architecture.md
- [x] Zone tab status dots fixed — auto-derived signals now surface without manual logging (Antigravity verified)
- [x] 6-agent Council architecture decided — 2 behavioral agents, 2 neuroacoustic agents, 2 synthesis agents
- [x] Model assignment decided — Nemotron 70B at all stages, 3 NIM keys across 3 cofounders
- [x] D-2 zone tab dots — DONE
