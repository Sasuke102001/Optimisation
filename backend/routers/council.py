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
from typing import AsyncGenerator

from models import EvidencePackage
from routers.providers import get_nemotron_client, get_deepseek_r1_client

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

_SYNTHESIS_SYSTEM = """\
You are the final synthesiser for the Polynovea Show Engineering Council.

Two expert agents (R1 Proposer and R2 Challenger) have analysed the evidence package and debated.
Your task: produce the single best 5-part operator suggestion, resolving any tension between them.

Output exactly this format — no other text:
State: [one sentence]
Mechanism: [one or two sentences — behavioral science reasoning]
Lever: [the specific controllable variable]
Action: [the exact instruction the operator executes — BPM, chord, frequency, staff move, etc.]
Signal: [what to watch for in the next 5–10 minutes to confirm it worked]

Do not mention the council, the debate, or the agents. Just the suggestion.\
"""

# ─── Evidence package → prompt text ──────────────────────────────────────────

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
        f"Mechanism chains: {json.dumps(se.mechanism_chains, indent=2)}\n"
        f"Intervention candidates: {json.dumps(se.intervention_candidates, indent=2)}\n"
        f"KPI linkages: {', '.join(se.kpi_linkages)}"
        if se else
        "Stage 1 pipeline not yet built — canonical state and mechanism chains unavailable"
    )

    history_block = (
        json.dumps(package.session_history[-3:], indent=2)
        if package.session_history else "No prior sessions"
    )

    return f"""\
=== EVIDENCE PACKAGE ===

CURRENT CROWD STATE:
{json.dumps(package.session_state, indent=2)}

VENUE BEHAVIORAL PROFILE (M2):
{json.dumps(package.venue_profile, indent=2)}

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


async def _call_nonstream(client_fn, messages: list, max_tokens: int = 600, thinking: bool = False) -> str:
    """Non-streaming call to one agent. Returns full response text."""
    ac = client_fn()
    if ac is None:
        return f"[{client_fn.__name__} unavailable — API key not set]"
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
        return _strip_thinking(raw)
    except Exception as exc:
        return f"[error: {exc}]"


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


async def _round1(evidence_text: str) -> str:
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


async def _round2(r1_response: str, evidence_text: str) -> str:
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
    evidence_text: str, r1: str, r2: str
) -> AsyncGenerator[str, None]:
    """Stream the Nemotron synthesis as the final output."""
    ac = get_nemotron_client()
    if ac is None:
        yield "[Council synthesis unavailable — NVIDIA_API_KEY_NEMOTRON_120B not set]"
        return
    try:
        stream = await ac.client.chat.completions.create(
            model=ac.model,
            messages=[
                {"role": "system", "content": _SYNTHESIS_SYSTEM},
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
            # Forward final content only (not reasoning_content chain-of-thought)
            text = getattr(delta, "content", None) or ""
            if text:
                yield text
    except Exception as exc:
        yield f"\n\n[Synthesis error: {exc}]"


# ─── Public interface ─────────────────────────────────────────────────────────

async def run_council(package: EvidencePackage) -> AsyncGenerator[str, None]:
    """
    Stage 2: receives assembled evidence package, runs R1→R2→synthesis debate.

    Yields streamed text. Protocol:
      1. COUNCIL_DELIBERATING sentinel
      2. [COUNCIL:PHASE:r1:{confidence}]{position}\\n  — after Round 1 completes
      3. [COUNCIL:PHASE:r2:{change}]{challenge}\\n     — after Round 2 completes
      4. COUNCIL_SYNTHESIS sentinel
      5. Final 5-part suggestion chunks streamed live from Nemotron
    """
    yield COUNCIL_DELIBERATING

    evidence_text = _format_evidence(package)

    # R1 and R2 run sequentially (R2 needs R1's output)
    r1 = await _round1(evidence_text)

    # Extract position line for the phase sentinel
    position = ""
    confidence = "MEDIUM"
    for line in r1.split("\n"):
        stripped = line.strip()
        if stripped.startswith("POSITION:"):
            position = stripped[9:].strip()
        elif stripped.startswith("CONFIDENCE:"):
            confidence = stripped[11:].strip()
    if position:
        yield f"[COUNCIL:PHASE:r1:{confidence}]{position}\n"

    r2 = await _round2(r1, evidence_text)

    # Extract change indicator for the phase sentinel
    change = "MINOR"
    challenge = ""
    for line in r2.split("\n"):
        stripped = line.strip()
        if stripped.startswith("CHANGE_FROM_R1:"):
            change = stripped[15:].strip()
        elif stripped.startswith("CHALLENGE:") and not challenge:
            challenge = stripped[10:].strip()
    if challenge:
        yield f"[COUNCIL:PHASE:r2:{change}]{challenge}\n"

    yield f"{COUNCIL_SYNTHESIS}\n"

    async for chunk in _stream_synthesis(evidence_text, r1, r2):
        yield chunk


async def run_council_fast(package: EvidencePackage) -> str:
    """
    Single-model fast path — Nemotron only, no R2 debate.
    Used when mode='fast'. Returns full 5-part suggestion as string.
    """
    ac = get_nemotron_client()
    if ac is None:
        return "[Council fast mode unavailable — NVIDIA_API_KEY_NEMOTRON_120B not set]"

    evidence_text = _format_evidence(package)
    messages = [
        {"role": "system", "content": _COUNCIL_SYSTEM},
        {"role": "user",   "content": evidence_text + "\n\nGenerate the 5-part suggestion now. Be direct and specific."},
    ]
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
        return _strip_thinking(raw)
    except Exception as exc:
        return f"[Council fast error: {exc}]"
