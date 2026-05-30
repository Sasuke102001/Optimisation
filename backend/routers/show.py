"""
POST /api/show/brief     — generate show engineering brief
GET  /api/show/history/{venue_id} — prior show outcomes for a venue
POST /api/show/outcome   — log what happened after a show
"""
from datetime import date, datetime, timezone

from fastapi import APIRouter, HTTPException

from database import fetch_m2_venue_context, get_m3_pool
from models import EvidencePackage, ShowBriefRequest, ShowBriefResponse, ShowOutcomeRequest
from routers.council import run_council, run_council_fast, _extract_json

router = APIRouter()


async def _assemble_show_evidence(
    body: ShowBriefRequest,
    m2_context: dict,
    prior_shows: list[dict],
) -> EvidencePackage:
    """
    Stage 1 evidence sweep for show brief.
    Agents 1–4 will be inserted here when se_pipeline is built (Steps 3–4).
    """
    session_state = (body.live_state or {}).copy()
    session_state.update({
        "show_date": body.show_date,
        "start_time": body.start_time,
        "end_time": body.end_time,
        "phase_count": body.phase_count,
        "crowd_size": body.crowd_size,
        "crowd_type": body.crowd_type,
        "show_type": body.show_type,
        "notes": body.notes,
    })

    venue_profile = (m2_context or {}).copy()
    venue_profile.update({
        "venue_name": body.venue_name,
        "area": body.area,
        "city": body.city,
        "primary_type": body.primary_type,
        "cascade_types": body.cascade_types,
    })

    return EvidencePackage(
        session_state=session_state,
        venue_profile=venue_profile,
        structured_evidence=None,         # TODO Step 3: Pipeline Agent fills this
        theory_passages=[],               # TODO Step 4: Research Agent fills this
        neuroacoustic_prescription=None,  # TODO Step 4: Neuroacoustic Agents fill this
        session_history=prior_shows,
    )


@router.post("/brief", response_model=ShowBriefResponse)
async def generate_show_brief(body: ShowBriefRequest):
    pool = get_m3_pool()

    m2_context = await fetch_m2_venue_context(body.venue_id)

    # Prior show sessions — includes mode and timestamps for session history
    async with pool.acquire() as conn:
        history = await conn.fetch(
            """
            SELECT session_number, opened_at, closed_at, session_mode
            FROM m3_sessions
            WHERE venue_id = $1
            ORDER BY opened_at DESC
            LIMIT 5
            """,
            body.venue_id,
        )
    prior_shows = [dict(r) for r in history]

    package = await _assemble_show_evidence(body, m2_context, prior_shows)

    log_context = {
        "venue_id":      body.venue_id,
        "venue_name":    body.venue_name,
        "area":          body.area,
        "city":          body.city,
        "primary_type":  body.primary_type,
        "cascade_types": body.cascade_types,
        "show_date":     body.show_date,
        "start_time":    body.start_time,
        "end_time":      body.end_time,
        "phase_count":   body.phase_count,
        "crowd_size":    body.crowd_size,
        "crowd_type":    body.crowd_type,
        "show_type":     body.show_type,
        "notes":         body.notes,
        "venue_profile": m2_context,
        "mode":          body.mode,
    }

    if body.mode == "fast":
        brief_text = await run_council_fast(package, log_context)
    else:
        chunks: list[str] = []
        async for chunk in run_council(package, log_context):
            chunks.append(chunk)
        brief_text = "".join(chunks)

    # Parse JSON out of synthesis stream
    parsed = _extract_json(brief_text)
    council_brief = None
    phase_arc = []
    if parsed:
        try:
            if "council_brief" in parsed and parsed["council_brief"] is not None:
                cb = parsed["council_brief"]
                from models import CouncilBrief
                council_brief = CouncilBrief(
                    state=cb.get("state", ""),
                    mechanism=cb.get("mechanism", ""),
                    lever=cb.get("lever", ""),
                    action=cb.get("action", ""),
                    signal=cb.get("signal", "")
                )
            if "phase_arc" in parsed and parsed["phase_arc"] is not None:
                from models import PhaseArcItem, ReferenceTrack
                phase_arc = [
                    PhaseArcItem(
                        phase_name=item.get("phase_name", ""),
                        start_time=item.get("start_time", ""),
                        end_time=item.get("end_time", ""),
                        bpm=item.get("bpm", ""),
                        chord=item.get("chord", ""),
                        key=item.get("key", ""),
                        bass=item.get("bass", ""),
                        watch_for=item.get("watch_for") or [],
                        action_line=item.get("action_line", ""),
                        reference_tracks=[
                            ReferenceTrack(
                                bpm=int(rt.get("bpm", 0)),
                                key=str(rt.get("key", "")),
                                chords=rt.get("chords") or [],
                                energy_score=int(rt.get("energy_score", 0)),
                                why=str(rt.get("why", "")),
                            )
                            for rt in (item.get("reference_tracks") or [])
                            if isinstance(rt, dict)
                        ],
                    )
                    for item in parsed["phase_arc"]
                ]
        except Exception:
            pass

    return ShowBriefResponse(
        brief=brief_text,
        council_brief=council_brief,
        phase_arc=phase_arc,
        venue_id=body.venue_id,
        session_number=body.session_number,
        generated_at=datetime.now(timezone.utc),
    )


@router.get("/history/{venue_id}")
async def get_show_history(venue_id: int, limit: int = 10):
    pool = get_m3_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT s.id, s.session_number, s.opened_at, s.closed_at,
                   s.session_mode, s.notes
            FROM m3_sessions s
            WHERE s.venue_id = $1
            ORDER BY s.opened_at DESC
            LIMIT $2
            """,
            venue_id, limit,
        )
    return [dict(r) for r in rows]


@router.post("/outcome")
async def log_show_outcome(body: ShowOutcomeRequest):
    """
    Writes a completed session outcome to M2 RDS (m3_venue_behavioral_outcomes).
    Falls back gracefully if M2 pool is unavailable.
    """
    from database import get_m2_pool

    pool = get_m2_pool()
    if pool is None:
        return {"logged": False, "reason": "M2 pool not available"}

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT venue_id, opened_at FROM m3_sessions WHERE id = $1",
            body.session_id,
        )
    if row is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    venue_id = row["venue_id"]
    session_date = row["opened_at"].date()

    async with pool.acquire() as conn:
        outcome_id = await conn.fetchval(
            """
            INSERT INTO m3_venue_behavioral_outcomes
                (venue_id, session_date, session_number,
                 avg_dwell_min, peak_crowd_energy, peak_occupancy_pct,
                 primary_segment_confirmed,
                 intervention_deployed, intervention_worked, intervention_type,
                 notes, data_quality)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)
            RETURNING id
            """,
            venue_id, session_date, body.session_number,
            body.avg_dwell_min, body.peak_crowd_energy, body.peak_occupancy_pct,
            body.primary_segment_confirmed,
            body.intervention_deployed, body.intervention_worked, body.intervention_type,
            body.notes, body.data_quality,
        )

    return {"logged": True, "outcome_id": outcome_id}
