"""
routers/council.py
The M3 Show Engineering Council — 2-round debate engine.

Architecture (from Step 5 locked decisions):
  R1  — Nemotron 120B proposes a 5-part suggestion from the evidence package
  R2  — DeepSeek Flash challenges R1 (alternative lever or interpretation)
  R3  — Nemotron 120B synthesises final 5-part output (streamed live)

The Council receives a pre-assembled EvidencePackage (Stage 1 output).
It does NOT do retrieval — that is Stage 1's job.

5-part output format (mandatory):
  State:     What the room is doing right now
  Mechanism: The behavioral science WHY
  Lever:     Which variable to change — music / volume / lighting / staff / layout
  Action:    The specific instruction the operator executes right now
  Signal:    What to watch for to confirm it worked
"""

import asyncio
import json
import re
import time
from decimal import Decimal
from typing import AsyncGenerator

from models import EvidencePackage
from routers.providers import get_nemotron_client, get_deepseek_r1_client
from supabase_client import get_supabase

# ─── Sentinels (forwarded to frontend) ───────────────────────────────────────

COUNCIL_DELIBERATING = "[COUNCIL:DELIBERATING]"
COUNCIL_SYNTHESIS    = "[COUNCIL:SYNTHESIS]"

# ─── System prompt ────────────────────────────────────────────────────────────

_COUNCIL_SYSTEM = """\
You are part of the Polynovea Show Engineering Council — a deliberative AI system that generates \
actionable behavioral engineering suggestions for live venue operators.

You receive a pre-assembled evidence package containing:
- Current crowd state (KPI pattern across zones)
- M2 venue behavioral profile (who comes here, how they behave)
- Behavioral science evidence (mechanisms, theory passages from research corpus)
- Neuroacoustic prescriptions (specific music parameters mapped to this crowd state)
- Prior session history at this venue

Your output must be a 5-part suggestion:
State: [what the room is doing right now]
Mechanism: [the behavioral science WHY]
Lever: [which variable to change — music / volume / lighting / staff / layout]
Action: [the specific instruction the operator can execute right now]
Signal: [what to watch for to confirm it worked]

Be specific. Use the neuroacoustic prescription when available — cite BPM ranges, chord structures, \
frequency emphases by name. Do not hedge with "consider" or "might" — give the operator a clear call.\
"""

_SYNTHESIS_SYSTEM = """
You are the final synthesiser for the Polynovea Show Engineering Council.

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
          "bpm": 124,
          "key": "Am",
          "chords": ["Am-F-C-G"],
          "energy_score": 72,
          "why": "Familiar tonic resolution — low cognitive load, sustains alpha state, lowers approach inhibition"
        },
        {
          "bpm": 128,
          "key": "Em",
          "chords": ["Em-C-G-D", "Am-F-C-G"],
          "energy_score": 84,
          "why": "Minor-to-relative-major shift creates emotional uplift — beta priming begins, contagion onset"
        },
        {
          "bpm": 132,
          "key": "Gm",
          "chords": ["Gm-Eb-Bb-F"],
          "energy_score": 91,
          "why": "Dorian groove with raised 6th — urgency without aggression, sustained motor activation"
        }
      ]
    }
  ]
}

The phase_arc array must have exactly {phase_count} items in show order.
Each phase must include 3–4 reference_tracks that embody the phase prescription.
reference_tracks must show range — not 3 profiles with the same chord structure.
The `why` field must state the neurological or behavioural mechanism specifically — not generic ("good energy") but mechanistic ("raised 6th in Dorian suppresses aggression while sustaining motor activation").
chords is an array — a track with multiple distinct sections (verse, chorus, drop) gets multiple entries.
Use the venue type, crowd type, and show type from the evidence package to calibrate language.
Do NOT use dance floor language for venues that are not night clubs or dance venues —
use crowd density, bar queue length, table fill rate, standing cluster formation instead.
Do NOT use "first floor movers" for non-nightclub venues.
Be specific about BPM numbers, chord structures, frequency ranges — draw from the evidence package.
"""

# ─── Evidence package → prompt text ──────────────────────────────────────────

def _json_default(o):
    """JSON encoder fallback: handles Decimal and datetime from asyncpg rows."""
    if isinstance(o, Decimal):
        return float(o)
    if hasattr(o, "isoformat"):
        return o.isoformat()
    raise TypeError(f"Not serializable: {type(o)}")


def _format_evidence(package: EvidencePackage) -> str:
    se = package.structured_evidence
    np = package.neuroacoustic_prescription

    passages = (
        "\n".join(f"  - {p}" for p in package.theory_passages)
        if package.theory_passages
        else "  Not available — run evidence sweep first"
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
        if package.session_history else "No prior sessions"
    )

    return f"""\
=== EVIDENCE PACKAGE ===

CURRENT CROWD STATE:
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


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _strip_thinking(text: str) -> str:
    """Remove <think>...</think> blocks (DeepSeek / Qwen thinking mode)."""
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


async def _call_nonstream(client_fn, messages: list, max_tokens: int = 600, thinking: bool = False) -> tuple[str, str, str | None]:
    """Non-streaming call to one agent. Returns (response_text, reasoning_content, error_message)."""
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


def _extract_turn_fields(turn_label: str, text: str) -> dict:
    fields = {}
    lines = text.split("\n")

    def find(prefix: str) -> str | None:
        for line in lines:
            stripped = line.strip()
            if stripped.upper().startswith(prefix.upper() + ":"):
                return stripped[len(prefix)+1:].strip()
        return None

    if turn_label == "r1_propose":
        fields["extracted_position"]   = find("POSITION")
        fields["extracted_confidence"] = find("CONFIDENCE")
    elif turn_label == "r2_challenge":
        fields["extracted_challenge"]  = find("CHALLENGE")
        fields["extracted_change"]     = find("CHANGE_FROM_R1")
    elif turn_label == "synthesis":
        # First try to load as JSON to see if we can get fields
        parsed = _extract_json(text)
        if parsed and "council_brief" in parsed and parsed["council_brief"]:
            cb = parsed["council_brief"]
            fields["extracted_state"]      = cb.get("state")
            fields["extracted_mechanism"]  = cb.get("mechanism")
            fields["extracted_lever"]      = cb.get("lever")
            fields["extracted_action"]     = cb.get("action")
            fields["extracted_signal"]     = cb.get("signal")
        else:
            fields["extracted_state"]      = find("State")
            fields["extracted_mechanism"]  = find("Mechanism")
            fields["extracted_lever"]      = find("Lever")
            fields["extracted_action"]     = find("Action")
            fields["extracted_signal"]     = find("Signal")
    return fields


async def _log_turn(
    run_id: int,
    venue_id: int,
    show_date: str,
    turn_index: int,
    turn_label: str,      # "r1_propose" | "r2_challenge" | "synthesis"
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
        # Extract structured fields from raw_response based on turn_label
        extracted = _extract_turn_fields(turn_label, raw_response)
        sb.table("m3_council_turns").insert({
            "run_id":              run_id,
            "venue_id":            venue_id,
            "show_date":           show_date,
            "turn_index":          turn_index,
            "turn_label":          turn_label,
            "model_id":            model_id,
            "model_alias":         model_alias,
            "system_prompt":       system_prompt,
            "user_prompt":         user_prompt,
            "raw_response":        raw_response,
            "reasoning_content":   reasoning_content,
            "latency_ms":          latency_ms,
            "errored":             errored,
            "error_message":       error_message,
            **extracted,
        }).execute()
    except Exception as exc:
        print(f"[supabase] _log_turn failed: {exc}")


async def _log_run_start(
    venue_id: int,
    venue_name: str,
    area: str | None,
    city: str | None,
    primary_type: str | None,
    cascade_types: list[str],
    show_date: str,
    start_time: str | None,
    end_time: str | None,
    phase_count: int,
    crowd_size: str | None,
    crowd_type: str | None,
    show_type: str | None,
    notes: str | None,
    venue_profile: dict,
    mode: str,
) -> int | None:
    """Creates the run row. Returns run_id or None if Supabase unavailable."""
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
    run_id: int,
    final_output: str,
    models_errored: list[str],
    total_latency_ms: int,
    status: str = "complete",
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


# ─── R1 instruction ───────────────────────────────────────────────────────────

_R1_INSTRUCTION = """

Based on the evidence package above, produce a 5-part suggestion:

POSITION: [one sentence — your core recommended action]
State: [what the room is doing right now]
Mechanism: [the behavioral science WHY]
Lever: [which variable — music / volume / lighting / staff / layout]
Action: [specific instruction — include BPM, chord structure, frequency if available]
Signal: [what to watch for in 5–10 min to confirm it worked]
CONFIDENCE: [HIGH / MEDIUM / LOW]"""


async def _round1(evidence_text: str) -> tuple[str, str, str | None]:
    """R1: Nemotron proposes a 5-part suggestion from the evidence."""
    messages = [
        {"role": "system", "content": _COUNCIL_SYSTEM + _R1_INSTRUCTION},
        {"role": "user",   "content": evidence_text},
    ]
    return await _call_nonstream(get_nemotron_client, messages, max_tokens=500, thinking=True)


# ─── R2 instruction ───────────────────────────────────────────────────────────

def _r2_user_message(r1_response: str, evidence_text: str) -> str:
    return f"""\
The evidence package is above. Agent R1 (Nemotron) proposed this suggestion:

R1 PROPOSAL:
{r1_response}

Your task: challenge this proposal. Consider:
- Is R1 using the right lever? Would a different variable be more effective right now?
- Is the BPM / chord / frequency prescription correct for this crowd state?
- Is the crowd state diagnosis accurate, or is R1 missing something?

Respond:
CHALLENGE: [what R1 got wrong or missed]
ALTERNATIVE_LEVER: [your preferred lever, if different]
REFINED_ACTION: [your alternative or refined specific instruction]
AGREE_ON: [what R1 got right that should be kept]
CHANGE_FROM_R1: [MAJOR / MINOR / NONE]"""


async def _round2(r1_response: str, evidence_text: str) -> tuple[str, str, str | None]:
    """R2: DeepSeek challenges R1's proposal."""
    messages = [
        {"role": "system", "content": _COUNCIL_SYSTEM},
        {"role": "user",   "content": evidence_text},
        {"role": "user",   "content": _r2_user_message(r1_response, evidence_text)},
    ]
    return await _call_nonstream(get_deepseek_r1_client, messages, max_tokens=400, thinking=True)


# ─── R3 synthesis (streamed) ─────────────────────────────────────────────────

def _synthesis_user_message(evidence_text: str, r1: str, r2: str) -> str:
    return f"""\
{evidence_text}

---

AGENT R1 PROPOSAL (Nemotron):
{r1}

AGENT R2 CHALLENGE (DeepSeek):
{r2}

Synthesise the single best 5-part operator suggestion now. Resolve any tension between R1 and R2. \
Prefer specificity — cite BPM, chord structure, frequency by name when available in the evidence."""


async def _stream_synthesis(
    evidence_text: str, r1: str, r2: str, phase_count: int, collector: dict
) -> AsyncGenerator[str, None]:
    """Stream the Nemotron synthesis as the final output."""
    ac = get_nemotron_client()
    if ac is None:
        yield "[Council synthesis unavailable — NVIDIA_API_KEY_NEMOTRON_120B not set]"
        return
    try:
        sys_prompt = _SYNTHESIS_SYSTEM.replace("{phase_count}", str(phase_count))
        stream = await ac.client.chat.completions.create(
            model=ac.model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user",   "content": _synthesis_user_message(evidence_text, r1, r2)},
            ],
            temperature=0.25,
            max_tokens=512,
            stream=True,
            extra_body={
                "chat_template_kwargs": {"enable_thinking": True},
                "reasoning_budget": 4096,
            },
        )
        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            text = getattr(delta, "content", None) or ""
            reasoning = getattr(delta, "reasoning_content", None) or ""
            if text:
                collector["content"] += text
                yield text
            if reasoning:
                collector["reasoning"] += reasoning
    except Exception as exc:
        yield f"\n\n[Synthesis error: {exc}]"


# ─── Public interface ─────────────────────────────────────────────────────────

async def run_council(
    package: EvidencePackage,
    log_context: dict | None = None,
) -> AsyncGenerator[str, None]:
    """
    Stage 2: receives assembled evidence package, runs R1→R2→synthesis debate.

    Yields streamed text. Protocol:
      1. COUNCIL_DELIBERATING sentinel
      2. [COUNCIL:PHASE:r1:{confidence}]{position}\n  — after Round 1 completes
      3. [COUNCIL:PHASE:r2:{change}]{challenge}\n     — after Round 2 completes
      4. COUNCIL_SYNTHESIS sentinel
      5. Final 5-part suggestion chunks streamed live from Nemotron
    """
    yield COUNCIL_DELIBERATING

    run_id = None
    models_errored = []
    t_start = time.time()

    if log_context:
        # 1. Log Run Start
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

    # --- R1 Proposer ---
    t0 = time.time()
    r1, r1_reasoning, r1_error = await _round1(evidence_text)
    r1_latency = int((time.time() - t0) * 1000)

    if r1_error:
        models_errored.append("r1_propose")

    # Extract position line for the phase sentinel
    position = ""
    confidence = "MEDIUM"
    for line in r1.split("\n"):
        stripped = line.strip()
        if stripped.upper().startswith("POSITION:"):
            position = stripped[9:].strip()
        elif stripped.upper().startswith("CONFIDENCE:"):
            confidence = stripped[11:].strip()
    if position:
        yield f"[COUNCIL:PHASE:r1:{confidence}]{position}\n"

    if log_context and run_id:
        ac = get_nemotron_client()
        await _log_turn(
            run_id=run_id,
            venue_id=log_context["venue_id"],
            show_date=log_context["show_date"],
            turn_index=0,
            turn_label="r1_propose",
            model_id=ac.model if ac else "nvidia/nemotron-3-super-120b-a12b",
            model_alias=ac.name if ac else "nemotron",
            system_prompt=_COUNCIL_SYSTEM + _R1_INSTRUCTION,
            user_prompt=evidence_text,
            raw_response=r1 if not r1_error else f"[error: {r1_error}]",
            reasoning_content=r1_reasoning,
            latency_ms=r1_latency,
            errored=r1_error is not None,
            error_message=r1_error,
        )

    # --- R2 Challenger ---
    t0 = time.time()
    r2, r2_reasoning, r2_error = await _round2(r1, evidence_text)
    r2_latency = int((time.time() - t0) * 1000)

    if r2_error:
        models_errored.append("r2_challenge")

    # Extract change indicator for the phase sentinel
    change = "MINOR"
    challenge = ""
    for line in r2.split("\n"):
        stripped = line.strip()
        if stripped.upper().startswith("CHANGE_FROM_R1:"):
            change = stripped[15:].strip()
        elif stripped.upper().startswith("CHALLENGE:") and not challenge:
            challenge = stripped[10:].strip()
    if challenge:
        yield f"[COUNCIL:PHASE:r2:{change}]{challenge}\n"

    if log_context and run_id:
        ac = get_deepseek_r1_client()
        user_prompt = evidence_text + "\n\n" + _r2_user_message(r1, evidence_text)
        await _log_turn(
            run_id=run_id,
            venue_id=log_context["venue_id"],
            show_date=log_context["show_date"],
            turn_index=1,
            turn_label="r2_challenge",
            model_id=ac.model if ac else "deepseek-ai/deepseek-v4-flash",
            model_alias=ac.name if ac else "deepseek_flash",
            system_prompt=_COUNCIL_SYSTEM,
            user_prompt=user_prompt,
            raw_response=r2 if not r2_error else f"[error: {r2_error}]",
            reasoning_content=r2_reasoning,
            latency_ms=r2_latency,
            errored=r2_error is not None,
            error_message=r2_error,
        )

    yield f"{COUNCIL_SYNTHESIS}\n"

    # --- R3 Synthesiser (streamed) ---
    phase_count = package.session_state.get("phase_count", 4)
    t0 = time.time()
    collector = {"content": "", "reasoning": ""}
    synthesis_error = None

    try:
        async for chunk in _stream_synthesis(evidence_text, r1, r2, phase_count, collector):
            yield chunk
    except Exception as exc:
        synthesis_error = str(exc)
        yield f"\n\n[Synthesis error: {exc}]"

    synth_latency = int((time.time() - t0) * 1000)

    # Check if synthesis stream failed/errored internally
    if "[Synthesis error:" in collector["content"] and not synthesis_error:
        synthesis_error = collector["content"]

    if synthesis_error:
        models_errored.append("synthesis")

    if log_context and run_id:
        ac = get_nemotron_client()
        sys_prompt = _SYNTHESIS_SYSTEM.replace("{phase_count}", str(phase_count))
        user_prompt = _synthesis_user_message(evidence_text, r1, r2)
        await _log_turn(
            run_id=run_id,
            venue_id=log_context["venue_id"],
            show_date=log_context["show_date"],
            turn_index=2,
            turn_label="synthesis",
            model_id=ac.model if ac else "nvidia/nemotron-3-super-120b-a12b",
            model_alias=ac.name if ac else "nemotron",
            system_prompt=sys_prompt,
            user_prompt=user_prompt,
            raw_response=collector["content"],
            reasoning_content=collector["reasoning"],
            latency_ms=synth_latency,
            errored=synthesis_error is not None,
            error_message=synthesis_error,
        )

    total_latency_ms = int((time.time() - t_start) * 1000)

    if log_context and run_id:
        status = "error" if models_errored else "complete"
        await _log_run_complete(
            run_id=run_id,
            final_output=collector["content"],
            models_errored=models_errored,
            total_latency_ms=total_latency_ms,
            status=status,
        )


async def run_council_fast(
    package: EvidencePackage,
    log_context: dict | None = None,
) -> str:
    """
    Single-model fast path — Nemotron only, no R2 debate.
    Used when mode='fast'. Returns full 5-part suggestion as string.
    """
    t_start = time.time()
    run_id = None
    models_errored = []

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
            mode=log_context.get("mode", "fast"),
        )

    ac = get_nemotron_client()
    if ac is None:
        err_msg = "[Council fast mode unavailable — NVIDIA_API_KEY_NEMOTRON_120B not set]"
        if log_context and run_id:
            await _log_run_complete(
                run_id=run_id,
                final_output="",
                models_errored=["synthesis"],
                total_latency_ms=int((time.time() - t_start) * 1000),
                status="error",
            )
        return err_msg

    phase_count = package.session_state.get("phase_count", 4)
    sys_prompt = _SYNTHESIS_SYSTEM.replace("{phase_count}", str(phase_count))

    evidence_text = _format_evidence(package)
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user",   "content": evidence_text + "\n\nGenerate the 5-part suggestion now. Be direct and specific."},
    ]

    t0 = time.time()
    try:
        resp = await ac.client.chat.completions.create(
            model=ac.model,
            messages=messages,
            temperature=0.28,
            max_tokens=512,
            extra_body={
                "chat_template_kwargs": {"enable_thinking": True},
                "reasoning_budget": 4096,
            },
        )
        raw = resp.choices[0].message.content or ""
        reasoning = getattr(resp.choices[0].message, "reasoning_content", "") or ""
        final_output = _strip_thinking(raw)
        errored = False
        error_message = None
    except Exception as exc:
        final_output = ""
        reasoning = ""
        errored = True
        error_message = str(exc)
        models_errored.append("synthesis")

    latency_ms = int((time.time() - t0) * 1000)

    if log_context and run_id:
        await _log_turn(
            run_id=run_id,
            venue_id=log_context["venue_id"],
            show_date=log_context["show_date"],
            turn_index=0,
            turn_label="synthesis",
            model_id=ac.model,
            model_alias=ac.name,
            system_prompt=sys_prompt,
            user_prompt=evidence_text + "\n\nGenerate the 5-part suggestion now. Be direct and specific.",
            raw_response=final_output if not errored else f"[Council fast error: {error_message}]",
            reasoning_content=reasoning,
            latency_ms=latency_ms,
            errored=errored,
            error_message=error_message,
        )

        status = "error" if models_errored else "complete"
        await _log_run_complete(
            run_id=run_id,
            final_output=final_output if not errored else f"[Council fast error: {error_message}]",
            models_errored=models_errored,
            total_latency_ms=int((time.time() - t_start) * 1000),
            status=status,
        )

    if errored:
        return f"[Council fast error: {error_message}]"
    return final_output
