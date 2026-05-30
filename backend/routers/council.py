"""
routers/council.py — Polynovea Show Engineering Council

7-agent pipeline:
  Stage 1 (parallel)  — Agents 1–4: evidence sweep
  Stage 2 (sequential)— Agents 5–6: integration + prescription
  Stage 3 (on-demand) — Agent 7: conversational guide (not invoked here)

Model assignments (all via NVIDIA NIM):
  Agent 1  Behavioral KAG    Nemotron 120B
  Agent 2  Behavioral RAG    Llama 3.3 70B
  Agent 3  Neuroacoustic KAG DeepSeek Flash
  Agent 4  Neuroacoustic RAG Qwen 122B
  Agent 5  Integrator        DeepSeek Pro
  Agent 6  Prescriber        Mistral Large   (streams the final plan)
  Agent 7  Conversational    Nemotron 120B   (not invoked here)
"""

import asyncio
import glob as _glob
import json
import os
import re
import time
from decimal import Decimal
from typing import AsyncGenerator

from models import EvidencePackage
from routers.providers import (
    get_deepseek_pro_client,
    get_deepseek_r1_client,
    get_llama_client,
    get_mistral_client,
    get_nemotron_client,
    get_qwen_client,
)
from supabase_client import get_supabase

# ─── Sentinels ────────────────────────────────────────────────────────────────

COUNCIL_DELIBERATING = "[COUNCIL:DELIBERATING]"
COUNCIL_SYNTHESIS    = "[COUNCIL:SYNTHESIS]"

# ─── File loading ─────────────────────────────────────────────────────────────

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Module-level cache — loaded once per process
_BEHAVIORAL_PIPELINE_CACHE: str | None = None
_RESEARCH_CORPUS_CACHE: str | None = None
_SE_PIPELINE_CACHE: str | None = None
_RESEARCH_SE_CORPUS_CACHE: str | None = None


def _read_file(path: str, max_chars: int = 8000) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read(max_chars)
        if len(content) == max_chars:
            content += "\n…[truncated]"
        return content
    except FileNotFoundError:
        return "[not found]"
    except Exception as exc:
        return f"[read error: {exc}]"


def _load_behavioral_pipeline() -> str:
    global _BEHAVIORAL_PIPELINE_CACHE
    if _BEHAVIORAL_PIPELINE_CACHE is not None:
        return _BEHAVIORAL_PIPELINE_CACHE
    output_dir = os.path.join(_BACKEND_DIR, "research_pipeline", "output")
    targets = [
        ("BEHAVIORAL_STATES",    os.path.join(output_dir, "behavioral_states.json")),
        ("INTERVENTIONS",        os.path.join(output_dir, "interventions.json")),
        ("CAUSAL_RELATIONSHIPS", os.path.join(output_dir, "causal_relationships.json")),
        ("VARIABLES",            os.path.join(output_dir, "variables.json")),
        ("KPIS",                 os.path.join(output_dir, "kpis.json")),
    ]
    parts = [f"=== {label} ===\n{_read_file(path)}" for label, path in targets]
    _BEHAVIORAL_PIPELINE_CACHE = "\n\n".join(parts)
    return _BEHAVIORAL_PIPELINE_CACHE


def _load_research_corpus() -> str:
    global _RESEARCH_CORPUS_CACHE
    if _RESEARCH_CORPUS_CACHE is not None:
        return _RESEARCH_CORPUS_CACHE
    corpus_dir = os.path.join(_BACKEND_DIR, "research")
    files = sorted(_glob.glob(os.path.join(corpus_dir, "*.md")))
    parts = []
    for fp in files:
        label = os.path.basename(fp)
        try:
            with open(fp, encoding="utf-8") as f:
                text = f.read(2000)
            parts.append(f"--- {label} ---\n{text}")
        except Exception:
            continue
    _RESEARCH_CORPUS_CACHE = "\n\n".join(parts) if parts else "[no behavioral research files found]"
    return _RESEARCH_CORPUS_CACHE


def _load_se_pipeline() -> str:
    global _SE_PIPELINE_CACHE
    if _SE_PIPELINE_CACHE is not None:
        return _SE_PIPELINE_CACHE
    output_dir = os.path.join(_BACKEND_DIR, "output_se")
    if not os.path.isdir(output_dir):
        _SE_PIPELINE_CACHE = (
            "Neuroacoustic prescription database not yet built (output_se/ does not exist). "
            "Derive best prescription from the evidence package and neuroacoustic research corpus."
        )
        return _SE_PIPELINE_CACHE
    files = _glob.glob(os.path.join(output_dir, "*.json"))
    if not files:
        _SE_PIPELINE_CACHE = "output_se/ directory exists but is empty."
        return _SE_PIPELINE_CACHE
    parts = [f"=== {os.path.basename(fp)} ===\n{_read_file(fp)}" for fp in sorted(files)]
    _SE_PIPELINE_CACHE = "\n\n".join(parts)
    return _SE_PIPELINE_CACHE


def _load_research_se_corpus() -> str:
    global _RESEARCH_SE_CORPUS_CACHE
    if _RESEARCH_SE_CORPUS_CACHE is not None:
        return _RESEARCH_SE_CORPUS_CACHE
    corpus_dir = os.path.join(_BACKEND_DIR, "research_se")
    files = sorted(_glob.glob(os.path.join(corpus_dir, "*.md")))
    parts = []
    for fp in files:
        label = os.path.basename(fp)
        try:
            with open(fp, encoding="utf-8") as f:
                text = f.read(2000)
            parts.append(f"--- {label} ---\n{text}")
        except Exception:
            continue
    _RESEARCH_SE_CORPUS_CACHE = "\n\n".join(parts) if parts else "[no neuroacoustic research files found]"
    return _RESEARCH_SE_CORPUS_CACHE


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _json_default(o):
    if isinstance(o, Decimal):
        return float(o)
    if hasattr(o, "isoformat"):
        return o.isoformat()
    raise TypeError(f"Not serializable: {type(o)}")


def _strip_thinking(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"<think>.*$", "", text, flags=re.DOTALL)
    return text.strip()


def _extract_json(text: str) -> dict | None:
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return None


async def _call_nonstream(
    client_fn, messages: list, max_tokens: int = 600, thinking: bool = False
) -> tuple[str, str, str | None]:
    """Returns (response_text, reasoning_content, error_message)."""
    ac = client_fn()
    if ac is None:
        return "", "", f"[{client_fn.__name__} unavailable — API key not set]"
    try:
        kwargs: dict = dict(
            model=ac.model,
            messages=messages,
            temperature=0.30,
            max_tokens=max_tokens,
        )
        if thinking:
            kwargs["extra_body"] = {
                "chat_template_kwargs": {"enable_thinking": True},
                "reasoning_budget": 8192,
            }
        resp = await ac.client.chat.completions.create(**kwargs)
        raw = resp.choices[0].message.content or ""
        reasoning = getattr(resp.choices[0].message, "reasoning_content", "") or ""
        return _strip_thinking(raw), reasoning, None
    except Exception as exc:
        return "", "", str(exc)


# ─── Evidence package → prompt ────────────────────────────────────────────────

def _format_evidence(package: EvidencePackage) -> str:
    se = package.structured_evidence
    np = package.neuroacoustic_prescription

    passages = (
        "\n".join(f"  - {p}" for p in package.theory_passages)
        if package.theory_passages
        else "  Not yet available"
    )
    neuro = (
        json.dumps(np.model_dump(), indent=2)
        if np else "Not yet available — SE pipeline not yet built"
    )
    se_block = (
        f"Canonical crowd state: {se.canonical_state}\n"
        f"Mechanism chains: {json.dumps(se.mechanism_chains, indent=2, default=_json_default)}\n"
        f"Intervention candidates: {json.dumps(se.intervention_candidates, indent=2, default=_json_default)}\n"
        f"KPI linkages: {', '.join(se.kpi_linkages)}"
        if se else
        "Stage 1 pipeline not yet built — canonical state and mechanism chains unavailable"
    )
    history_block = (
        json.dumps(package.session_history[-3:], indent=2, default=_json_default)
        if package.session_history else "No prior sessions at this venue"
    )
    return f"""\
=== EVIDENCE PACKAGE ===

CURRENT SHOW CONTEXT:
{json.dumps(package.session_state, indent=2, default=_json_default)}

VENUE BEHAVIORAL PROFILE (M2):
{json.dumps(package.venue_profile, indent=2, default=_json_default)}

BEHAVIORAL SCIENCE EVIDENCE:
{se_block}

Theory passages from research corpus:
{passages}

NEUROACOUSTIC PRESCRIPTION:
{neuro}

SESSION HISTORY AT THIS VENUE:
{history_block}"""


# ─── System prompts ───────────────────────────────────────────────────────────

_COUNCIL_BASE = """\
You are part of the Polynovea Show Engineering Council — an AI system that produces \
actionable, evidence-grounded show plans for live venue operators.
The output must be specific enough that the performer can walk in with it and run the night \
without consulting the app again. Use BPM ranges, chord structures, and frequency prescriptions \
by name. Do not hedge with "consider" or "might".\
"""

_AGENT1_SYSTEM = _COUNCIL_BASE + """

ROLE — Agent 1: Behavioral KAG (Knowledge-Augmented Generation)
You query the structured behavioral knowledge graph provided below.
Given the venue context and session parameters, return:

CANONICAL_STATE: the most likely crowd behavioral state at this venue tonight
MECHANISM_CHAINS: 2–3 mechanism chains from the knowledge graph most relevant to this context
INTERVENTION_CANDIDATES: 2–3 specific interventions from the knowledge graph that fit
KPI_LINKAGES: which KPIs to watch for each intervention (reference KPI IDs where available)
CONFIDENCE: HIGH / MEDIUM / LOW"""

_AGENT2_SYSTEM = _COUNCIL_BASE + """

ROLE — Agent 2: Behavioral RAG (Retrieval-Augmented Generation)
You search the behavioral research corpus provided below.
Extract the 3–5 most relevant verbatim passages that explain:
  — Why this type of crowd behaves the way it does
  — What drives dwell time, social contagion, floor activation, or spend at this venue type
  — Which behavioral mechanisms govern intervention effectiveness here

Quote passages verbatim. Label each with the source filename. Do not summarise — extract."""

_AGENT3_SYSTEM = _COUNCIL_BASE + """

ROLE — Agent 3: Neuroacoustic KAG (Knowledge-Augmented Generation)
You query the neuroacoustic prescription database provided below.
Given the venue context and crowd state, return a specific neuroacoustic prescription:

BPM_PRESCRIPTION: exact BPM range per show phase
CHORD_PRESCRIPTION: chord structures per phase with behavioral rationale
FREQUENCY_PRESCRIPTION: bass/mid/high emphasis per phase in Hz with dB adjustments
BRAINWAVE_TARGET: target brainwave state per phase (alpha/beta) with Hz range
PHRASE_ARCHITECTURE: bar structure and phrase length per phase

If the prescription database is not yet built, derive the best prescription from the evidence package and the corpus."""

_AGENT4_SYSTEM = _COUNCIL_BASE + """

ROLE — Agent 4: Neuroacoustic RAG (Retrieval-Augmented Generation)
You search the neuroacoustic and music psychology research corpus provided below.
Extract the 3–5 most relevant verbatim passages explaining the WHY behind the prescription:
  — Why specific BPM ranges affect this crowd's brainwave state
  — Why specific chord structures produce specific behavioral responses
  — Why specific frequency emphases affect physical engagement
  — The neurological mechanism — not just that it works, but how

Quote passages verbatim. Label each with the source filename."""

_AGENT5_SYSTEM = _COUNCIL_BASE + """

ROLE — Agent 5: Integrator
You receive Stage 1 findings from 4 parallel agents and synthesise them into a unified show picture.
Do NOT produce a show plan yet. Produce coherent integration:

CROWD_PICTURE: synthesised portrait of tonight's crowd behavioral baseline
DOMINANT_DRIVERS: the 2–3 behavioral mechanisms that govern tonight's arc
NEUROACOUSTIC_CHAIN: the BPM → chord → frequency → brainwave prescription chain for the full night
PRIOR_SESSION_PATTERN: what worked and what did not at this venue (from session history)
RISK_FACTORS: anything in Stage 1 that suggests deviation from defaults
POSITION: one sentence — the single most important insight for tonight's plan
CONFIDENCE: HIGH / MEDIUM / LOW"""

_PRESCRIBER_SYSTEM = """\
You are Agent 6 of the Polynovea Show Engineering Council — the Prescriber.
You receive an integrated show picture from Agent 5 and produce the complete show plan.

Output ONLY a JSON object in this exact shape — no other text before or after:

{
  "council_brief": {
    "state": "one sentence — what the room is doing tonight",
    "mechanism": "one or two sentences — behavioral science reasoning",
    "lever": "the specific controllable variable",
    "action": "the exact instruction the operator executes — cite BPM, chord, frequency by name",
    "signal": "what to watch for in the next 5–10 minutes to confirm it worked"
  },
  "phase_arc": [
    {
      "phase_name": "Opening",
      "bpm": "105–112",
      "chord": "I–IV–V",
      "key": "F major — Ionian",
      "bass": "55–70Hz · nominal",
      "watch_for": ["...", "...", "..."],
      "action_line": "Hold energy low. Let room fill naturally.",
      "reference_tracks": [
        {
          "bpm": 108,
          "key": "F",
          "chords": ["F-Bb-C"],
          "energy_score": 55,
          "why": "Specific neurological or behavioural mechanism — not generic"
        }
      ]
    }
  ]
}

Rules:
- phase_arc must have exactly {phase_count} items in show order
- Each phase must include 3–4 reference_tracks showing range — not 3 identical chord structures
- The `why` field must state the specific neural or behavioral mechanism
- chords is an array — multi-section tracks get multiple entries
- Do NOT use dance floor language for non-nightclub venues
- cite BPM numbers, chord structures, frequency ranges from the integrated evidence
"""


# ─── Stage 1 agents ───────────────────────────────────────────────────────────

async def _agent1(evidence_text: str) -> tuple[str, str, str | None]:
    pipeline_data = _load_behavioral_pipeline()
    messages = [
        {"role": "system", "content": _AGENT1_SYSTEM},
        {"role": "user",   "content": f"BEHAVIORAL KNOWLEDGE GRAPH:\n{pipeline_data}\n\n{evidence_text}"},
    ]
    return await _call_nonstream(get_nemotron_client, messages, max_tokens=700, thinking=True)


async def _agent2(evidence_text: str) -> tuple[str, str, str | None]:
    corpus = _load_research_corpus()
    messages = [
        {"role": "system", "content": _AGENT2_SYSTEM},
        {"role": "user",   "content": f"BEHAVIORAL RESEARCH CORPUS:\n{corpus}\n\n{evidence_text}"},
    ]
    return await _call_nonstream(get_llama_client, messages, max_tokens=800)


async def _agent3(evidence_text: str) -> tuple[str, str, str | None]:
    se_data = _load_se_pipeline()
    messages = [
        {"role": "system", "content": _AGENT3_SYSTEM},
        {"role": "user",   "content": f"NEUROACOUSTIC PRESCRIPTION DATABASE:\n{se_data}\n\n{evidence_text}"},
    ]
    return await _call_nonstream(get_deepseek_r1_client, messages, max_tokens=800, thinking=True)


async def _agent4(evidence_text: str) -> tuple[str, str, str | None]:
    corpus = _load_research_se_corpus()
    messages = [
        {"role": "system", "content": _AGENT4_SYSTEM},
        {"role": "user",   "content": f"NEUROACOUSTIC RESEARCH CORPUS:\n{corpus}\n\n{evidence_text}"},
    ]
    return await _call_nonstream(get_qwen_client, messages, max_tokens=800)


# ─── Stage 2 agents ───────────────────────────────────────────────────────────

async def _agent5(evidence_text: str, a1: str, a2: str, a3: str, a4: str) -> tuple[str, str, str | None]:
    stage1_block = f"""\
AGENT 1 — BEHAVIORAL KAG:
{a1 or '[Agent 1 returned no results]'}

AGENT 2 — BEHAVIORAL THEORY PASSAGES:
{a2 or '[Agent 2 returned no results]'}

AGENT 3 — NEUROACOUSTIC PRESCRIPTION:
{a3 or '[Agent 3 returned no results]'}

AGENT 4 — NEUROACOUSTIC THEORY PASSAGES:
{a4 or '[Agent 4 returned no results]'}"""

    messages = [
        {"role": "system", "content": _AGENT5_SYSTEM},
        {"role": "user",   "content": f"{evidence_text}\n\n---\n\nSTAGE 1 FINDINGS:\n{stage1_block}"},
    ]
    return await _call_nonstream(get_deepseek_pro_client, messages, max_tokens=1000, thinking=True)


async def _agent6_stream(
    evidence_text: str,
    integrated_picture: str,
    phase_count: int,
    collector: dict,
) -> AsyncGenerator[str, None]:
    """Agent 6 — Mistral Large: streams the final show plan JSON."""
    ac = get_mistral_client()
    if ac is None:
        # Fallback to Nemotron if Mistral key not set
        ac = get_nemotron_client()
    if ac is None:
        yield "[Prescriber unavailable — NVIDIA_API_KEY_MISTRAL_LARGE and NVIDIA_API_KEY_NEMOTRON_120B not set]"
        return

    sys_prompt = _PRESCRIBER_SYSTEM.replace("{phase_count}", str(phase_count))
    user_prompt = f"""\
{evidence_text}

---

AGENT 5 — INTEGRATED SHOW PICTURE:
{integrated_picture}

Produce the complete show plan JSON now."""

    try:
        stream = await ac.client.chat.completions.create(
            model=ac.model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0.25,
            max_tokens=4096,
            stream=True,
        )
        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            text = getattr(delta, "content", None) or ""
            if text:
                collector["content"] += text
                yield text
    except Exception as exc:
        yield f"\n\n[Prescriber error: {exc}]"


# ─── Supabase logging ─────────────────────────────────────────────────────────

def _extract_turn_fields(turn_label: str, text: str) -> dict:
    fields: dict = {}
    lines = text.split("\n")

    def find(prefix: str) -> str | None:
        for line in lines:
            stripped = line.strip()
            if stripped.upper().startswith(prefix.upper() + ":"):
                return stripped[len(prefix) + 1:].strip()
        return None

    if turn_label in ("behavioral_kag", "neuro_kag", "integration"):
        fields["extracted_position"]   = find("POSITION") or find("CANONICAL_STATE")
        fields["extracted_confidence"] = find("CONFIDENCE")
    elif turn_label == "prescription":
        parsed = _extract_json(text)
        if parsed and "council_brief" in parsed and parsed["council_brief"]:
            cb = parsed["council_brief"]
            fields["extracted_state"]     = cb.get("state")
            fields["extracted_mechanism"] = cb.get("mechanism")
            fields["extracted_lever"]     = cb.get("lever")
            fields["extracted_action"]    = cb.get("action")
            fields["extracted_signal"]    = cb.get("signal")
    return fields


async def _log_turn(
    run_id: int,
    venue_id: int,
    show_date: str,
    turn_index: int,
    turn_label: str,
    model_id: str,
    model_alias: str,
    system_prompt: str,
    user_prompt: str,
    raw_response: str,
    reasoning_content: str,
    latency_ms: int,
    errored: bool = False,
    error_message: str | None = None,
) -> None:
    sb = get_supabase()
    if sb is None:
        return
    try:
        extracted = _extract_turn_fields(turn_label, raw_response)
        sb.table("m3_council_turns").insert({
            "run_id":            run_id,
            "venue_id":          venue_id,
            "show_date":         show_date,
            "turn_index":        turn_index,
            "turn_label":        turn_label,
            "model_id":          model_id,
            "model_alias":       model_alias,
            "system_prompt":     system_prompt,
            "user_prompt":       user_prompt[:8000],   # cap to avoid Supabase row size limits
            "raw_response":      raw_response,
            "reasoning_content": reasoning_content,
            "latency_ms":        latency_ms,
            "errored":           errored,
            "error_message":     error_message,
            **extracted,
        }).execute()
    except Exception as exc:
        print(f"[supabase] _log_turn failed: {exc}")


async def _log_run_start(
    venue_id: int, venue_name: str, area: str | None, city: str | None,
    primary_type: str | None, cascade_types: list[str], show_date: str,
    start_time: str | None, end_time: str | None, phase_count: int,
    crowd_size: str | None, crowd_type: str | None, show_type: str | None,
    notes: str | None, venue_profile: dict, mode: str,
) -> int | None:
    sb = get_supabase()
    if sb is None:
        return None
    try:
        result = sb.table("m3_council_runs").insert({
            "venue_id":      venue_id,
            "venue_name":    venue_name,
            "area":          area,
            "city":          city,
            "primary_type":  primary_type,
            "cascade_types": cascade_types,
            "show_date":     show_date,
            "start_time":    start_time,
            "end_time":      end_time,
            "phase_count":   phase_count,
            "crowd_size":    crowd_size,
            "crowd_type":    crowd_type,
            "show_type":     show_type,
            "notes":         notes,
            "venue_profile": venue_profile,
            "mode":          mode,
            "status":        "running",
        }).execute()
        return result.data[0]["id"] if result.data else None
    except Exception as exc:
        print(f"[supabase] _log_run_start failed: {exc}")
        return None


async def _log_run_complete(
    run_id: int, final_output: str, models_errored: list[str], total_latency_ms: int, status: str = "complete",
) -> None:
    sb = get_supabase()
    if sb is None:
        return
    try:
        sb.table("m3_council_runs").update({
            "final_output":     final_output,
            "models_errored":   models_errored,
            "total_latency_ms": total_latency_ms,
            "status":           status,
        }).eq("id", run_id).execute()
    except Exception as exc:
        print(f"[supabase] _log_run_complete failed: {exc}")


# ─── Public interface ─────────────────────────────────────────────────────────

async def run_council(
    package: EvidencePackage,
    log_context: dict | None = None,
) -> AsyncGenerator[str, None]:
    """
    Full 7-agent council run. Yields streamed text with sentinel protocol:
      1. COUNCIL_DELIBERATING
      2. [COUNCIL:PHASE:r1:{confidence}]{integration_summary}  — Agent 5 complete
      3. COUNCIL_SYNTHESIS
      4. Show plan JSON chunks streamed from Agent 6 (Mistral)
    """
    yield COUNCIL_DELIBERATING

    t_start = time.time()
    run_id = None
    models_errored: list[str] = []

    if log_context:
        run_id = await _log_run_start(
            venue_id=log_context.get("venue_id"),
            venue_name=log_context.get("venue_name"),
            area=log_context.get("area"),
            city=log_context.get("city"),
            primary_type=log_context.get("primary_type"),
            cascade_types=log_context.get("cascade_types") or [],
            show_date=log_context.get("show_date"),
            start_time=log_context.get("start_time"),
            end_time=log_context.get("end_time"),
            phase_count=log_context.get("phase_count", 4),
            crowd_size=log_context.get("crowd_size"),
            crowd_type=log_context.get("crowd_type"),
            show_type=log_context.get("show_type"),
            notes=log_context.get("notes"),
            venue_profile=log_context.get("venue_profile") or {},
            mode=log_context.get("mode", "council"),
        )

    evidence_text = _format_evidence(package)

    # ── Stage 1: Agents 1–4 in parallel ──────────────────────────────────────
    t1 = time.time()
    results = await asyncio.gather(
        _agent1(evidence_text),
        _agent2(evidence_text),
        _agent3(evidence_text),
        _agent4(evidence_text),
        return_exceptions=True,
    )
    stage1_ms = int((time.time() - t1) * 1000)

    def _unpack(r, label: str) -> tuple[str, str, str | None]:
        if isinstance(r, Exception):
            models_errored.append(label)
            return "", "", str(r)
        txt, reasoning, err = r
        if err:
            models_errored.append(label)
        return txt, reasoning, err

    a1_txt, a1_rsn, a1_err = _unpack(results[0], "behavioral_kag")
    a2_txt, a2_rsn, a2_err = _unpack(results[1], "behavioral_rag")
    a3_txt, a3_rsn, a3_err = _unpack(results[2], "neuro_kag")
    a4_txt, a4_rsn, a4_err = _unpack(results[3], "neuro_rag")

    # ── Stage 2: Agent 5 — Integrator ────────────────────────────────────────
    t5 = time.time()
    a5_txt, a5_rsn, a5_err = await _agent5(evidence_text, a1_txt, a2_txt, a3_txt, a4_txt)
    a5_ms = int((time.time() - t5) * 1000)
    if a5_err:
        models_errored.append("integration")

    # Emit integration summary using the r1 sentinel so the frontend transitions stages
    position = ""
    confidence = "MEDIUM"
    for line in a5_txt.split("\n"):
        stripped = line.strip()
        if stripped.upper().startswith("POSITION:"):
            position = stripped[9:].strip()
        elif stripped.upper().startswith("CONFIDENCE:"):
            confidence = stripped[11:].strip()
    if position:
        yield f"[COUNCIL:PHASE:r1:{confidence}]{position}\n"

    yield f"{COUNCIL_SYNTHESIS}\n"

    # ── Stage 2: Agent 6 — Prescriber (streamed) ─────────────────────────────
    phase_count = package.session_state.get("phase_count", 4)
    t6 = time.time()
    collector: dict = {"content": "", "reasoning": ""}
    synth_error: str | None = None

    try:
        async for chunk in _agent6_stream(evidence_text, a5_txt, phase_count, collector):
            yield chunk
    except Exception as exc:
        synth_error = str(exc)
        yield f"\n\n[Prescriber error: {exc}]"

    a6_ms = int((time.time() - t6) * 1000)
    if synth_error or "[Prescriber error:" in collector["content"]:
        models_errored.append("prescription")

    total_ms = int((time.time() - t_start) * 1000)

    # ── Supabase logging (fire-and-forget) ───────────────────────────────────
    if log_context and run_id:
        venue_id   = log_context["venue_id"]
        show_date  = log_context["show_date"]
        a1c = get_nemotron_client()
        a2c = get_llama_client()
        a3c = get_deepseek_r1_client()
        a4c = get_qwen_client()
        a5c = get_deepseek_pro_client()
        a6c = get_mistral_client() or get_nemotron_client()

        await asyncio.gather(
            _log_turn(run_id, venue_id, show_date, 0, "behavioral_kag",
                      a1c.model if a1c else "nemotron", a1c.name if a1c else "nemotron",
                      _AGENT1_SYSTEM, evidence_text,
                      a1_txt or f"[error: {a1_err}]", a1_rsn, stage1_ms,
                      a1_err is not None, a1_err),
            _log_turn(run_id, venue_id, show_date, 1, "behavioral_rag",
                      a2c.model if a2c else "llama_70b", a2c.name if a2c else "llama_70b",
                      _AGENT2_SYSTEM, evidence_text,
                      a2_txt or f"[error: {a2_err}]", a2_rsn, stage1_ms,
                      a2_err is not None, a2_err),
            _log_turn(run_id, venue_id, show_date, 2, "neuro_kag",
                      a3c.model if a3c else "deepseek_flash", a3c.name if a3c else "deepseek_flash",
                      _AGENT3_SYSTEM, evidence_text,
                      a3_txt or f"[error: {a3_err}]", a3_rsn, stage1_ms,
                      a3_err is not None, a3_err),
            _log_turn(run_id, venue_id, show_date, 3, "neuro_rag",
                      a4c.model if a4c else "qwen_122b", a4c.name if a4c else "qwen_122b",
                      _AGENT4_SYSTEM, evidence_text,
                      a4_txt or f"[error: {a4_err}]", a4_rsn, stage1_ms,
                      a4_err is not None, a4_err),
            _log_turn(run_id, venue_id, show_date, 4, "integration",
                      a5c.model if a5c else "deepseek_pro", a5c.name if a5c else "deepseek_pro",
                      _AGENT5_SYSTEM, evidence_text,
                      a5_txt or f"[error: {a5_err}]", a5_rsn, a5_ms,
                      a5_err is not None, a5_err),
            _log_turn(run_id, venue_id, show_date, 5, "prescription",
                      a6c.model if a6c else "mistral_large", a6c.name if a6c else "mistral_large",
                      _PRESCRIBER_SYSTEM, evidence_text,
                      collector["content"], collector["reasoning"], a6_ms,
                      synth_error is not None, synth_error),
            return_exceptions=True,
        )

        status = "error" if models_errored else "complete"
        await _log_run_complete(run_id, collector["content"], models_errored, total_ms, status)


async def run_council_fast(
    package: EvidencePackage,
    log_context: dict | None = None,
) -> str:
    """
    Fast path — Nemotron only, no multi-agent debate.
    Used when mode='fast'. Returns the full plan as a string.
    """
    t_start = time.time()
    run_id = None

    if log_context:
        run_id = await _log_run_start(
            venue_id=log_context.get("venue_id"),
            venue_name=log_context.get("venue_name"),
            area=log_context.get("area"),
            city=log_context.get("city"),
            primary_type=log_context.get("primary_type"),
            cascade_types=log_context.get("cascade_types") or [],
            show_date=log_context.get("show_date"),
            start_time=log_context.get("start_time"),
            end_time=log_context.get("end_time"),
            phase_count=log_context.get("phase_count", 4),
            crowd_size=log_context.get("crowd_size"),
            crowd_type=log_context.get("crowd_type"),
            show_type=log_context.get("show_type"),
            notes=log_context.get("notes"),
            venue_profile=log_context.get("venue_profile") or {},
            mode="fast",
        )

    ac = get_nemotron_client()
    if ac is None:
        err = "[Fast mode unavailable — NVIDIA_API_KEY_NEMOTRON_120B not set]"
        if log_context and run_id:
            await _log_run_complete(run_id, "", ["prescription"],
                                    int((time.time() - t_start) * 1000), "error")
        return err

    phase_count = package.session_state.get("phase_count", 4)
    sys_prompt  = _PRESCRIBER_SYSTEM.replace("{phase_count}", str(phase_count))
    evidence_text = _format_evidence(package)

    t0 = time.time()
    try:
        resp = await ac.client.chat.completions.create(
            model=ac.model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user",   "content": evidence_text + "\n\nGenerate the show plan now."},
            ],
            temperature=0.28,
            max_tokens=4096,
            extra_body={
                "chat_template_kwargs": {"enable_thinking": True},
                "reasoning_budget": 4096,
            },
        )
        raw      = resp.choices[0].message.content or ""
        reasoning = getattr(resp.choices[0].message, "reasoning_content", "") or ""
        output   = _strip_thinking(raw)
        errored  = False
        error_msg: str | None = None
    except Exception as exc:
        output    = ""
        reasoning = ""
        errored   = True
        error_msg = str(exc)

    latency_ms = int((time.time() - t0) * 1000)

    if log_context and run_id:
        await _log_turn(
            run_id=run_id, venue_id=log_context["venue_id"], show_date=log_context["show_date"],
            turn_index=0, turn_label="prescription",
            model_id=ac.model, model_alias=ac.name,
            system_prompt=sys_prompt,
            user_prompt=evidence_text + "\n\nGenerate the show plan now.",
            raw_response=output if not errored else f"[error: {error_msg}]",
            reasoning_content=reasoning, latency_ms=latency_ms,
            errored=errored, error_message=error_msg,
        )
        await _log_run_complete(
            run_id=run_id,
            final_output=output if not errored else "",
            models_errored=["prescription"] if errored else [],
            total_latency_ms=int((time.time() - t_start) * 1000),
            status="error" if errored else "complete",
        )

    return output if not errored else f"[Fast mode error: {error_msg}]"
