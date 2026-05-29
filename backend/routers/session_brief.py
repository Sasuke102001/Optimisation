"""
POST /api/session/brief
Generates a pre/mid/post-session AI brief using the M3 Council.

Stage 1 (evidence assembly) — builds EvidencePackage from:
  - M2 venue behavioral context (venue profile, fitness, segments, primitives)
  - M3 session history (prior closed sessions for this venue)
  - Live state from POST body (KPI readings, if mid-session)
  Agents 1–4 will be inserted here when se_pipeline is built (Steps 3–4).

Stage 2 (Council) — debate + synthesis:
  - run_council(package) → streams R1→R2→synthesis
  - run_council_fast(package) → single Nemotron call, returns string
"""
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from database import fetch_m2_venue_context, get_m3_pool
from models import (
    EvidencePackage,
    SessionBriefRequest,
    SessionBriefResponse,
)
from routers.council import run_council, run_council_fast

router = APIRouter()


async def _assemble_evidence_package(
    body: SessionBriefRequest,
    m2_context: dict,
    m3_history: list[dict],
) -> EvidencePackage:
    """
    Stage 1 evidence sweep.
    Agents 1–4 will be inserted here when se_pipeline is built (Steps 3–4).
    For now: builds package from available data (venue profile + session history).
    """
    return EvidencePackage(
        session_state=body.live_state or {},
        venue_profile=m2_context,
        structured_evidence=None,    # TODO Step 3: Pipeline Agent fills this
        theory_passages=[],          # TODO Step 4: Research Agent fills this
        neuroacoustic_prescription=None,  # TODO Step 4: Neuroacoustic Agents fill this
        session_history=m3_history,
    )


@router.post("/brief", response_model=SessionBriefResponse)
async def generate_session_brief(body: SessionBriefRequest):
    pool = get_m3_pool()

    # Fetch M2 context (returns {} if M2 not available)
    m2_context = await fetch_m2_venue_context(body.venue_id)

    # Fetch M3 session history for this venue
    async with pool.acquire() as conn:
        history = await conn.fetch(
            """
            SELECT id, session_number, session_mode, opened_at, closed_at
            FROM m3_sessions
            WHERE venue_id = $1 AND closed_at IS NOT NULL
            ORDER BY opened_at DESC LIMIT 10
            """,
            body.venue_id,
        )
    m3_history = [dict(r) for r in history]

    package = await _assemble_evidence_package(body, m2_context, m3_history)

    if body.mode == "fast":
        brief_text = await run_council_fast(package)
    else:
        # Council streams — collect for non-streaming response
        chunks: list[str] = []
        async for chunk in run_council(package):
            chunks.append(chunk)
        brief_text = "".join(chunks)

    return SessionBriefResponse(
        brief=brief_text,
        session_number=body.session_number,
        venue_id=body.venue_id,
        generated_at=datetime.now(timezone.utc),
    )
