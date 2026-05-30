"""
POST /api/show/brief     — generate show engineering brief (SSE stream)
GET  /api/show/history/{venue_id} — prior show outcomes for a venue
POST /api/show/outcome   — log what happened after a show
"""
import json as _json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from database import fetch_m2_venue_context, get_m3_pool
from models import ConversationRequest, EvidencePackage, ShowBriefRequest, ShowOutcomeRequest
from routers.council import (
    COUNCIL_DELIBERATING, COUNCIL_SYNTHESIS,
    run_council, run_council_fast, run_agent7, _extract_json,
)

router = APIRouter()


def _sse(event: dict) -> str:
    return "data: " + _json.dumps(event) + "\n\n"


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


@router.post("/brief")
async def generate_show_brief(body: ShowBriefRequest):
    """
    Streams Council deliberation as Server-Sent Events so the frontend can
    render live progress. Event types:
      status   — plain-text status line (model starting, waiting, etc.)
      r1       — R1 position + confidence after Round 1 completes
      r2       — R2 challenge + change level after Round 2 completes
      chunk    — raw synthesis text chunk as it streams
      complete — final parsed output (council_brief, phase_arc, raw_brief)
      error    — something went wrong
    """
    pool = get_m3_pool()
    m2_context = await fetch_m2_venue_context(body.venue_id)

    async with pool.acquire() as conn:
        history = await conn.fetch(
            """
            SELECT session_number, opened_at, closed_at, session_mode
            FROM m3_sessions WHERE venue_id = $1
            ORDER BY opened_at DESC LIMIT 5
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

    async def _stream():
        all_chunks: list[str] = []
        try:
            if body.mode == "fast":
                yield _sse({"type": "status", "msg": "Running fast mode synthesis…"})
                brief_text = await run_council_fast(package, log_context)
                all_chunks.append(brief_text)
                yield _sse({"type": "chunk", "text": brief_text})
            else:
                yield _sse({"type": "status", "msg": "Assembling evidence package…"})
                async for chunk in run_council(package, log_context):
                    all_chunks.append(chunk)

                    if chunk.startswith("[COUNCIL:PHASE:r1:"):
                        # [COUNCIL:PHASE:r1:HIGH]position text
                        inner = chunk[len("[COUNCIL:PHASE:r1:"):]
                        confidence, _, position = inner.partition("]")
                        yield _sse({
                            "type": "r1",
                            "confidence": confidence.strip(),
                            "position": position.strip(),
                        })

                    elif chunk.startswith("[COUNCIL:PHASE:r2:"):
                        inner = chunk[len("[COUNCIL:PHASE:r2:"):]
                        change, _, challenge = inner.partition("]")
                        yield _sse({
                            "type": "r2",
                            "change": change.strip(),
                            "challenge": challenge.strip(),
                        })

                    elif COUNCIL_SYNTHESIS in chunk:
                        yield _sse({"type": "synthesis_start", "text": "Prescribing show plan…"})

                    elif COUNCIL_DELIBERATING in chunk:
                        yield _sse({"type": "status", "msg": "Stage 1 — 4 agents reading evidence in parallel…"})

                    elif chunk and not chunk.startswith("[COUNCIL:"):
                        yield _sse({"type": "chunk", "text": chunk})

        except Exception as exc:
            yield _sse({"type": "error", "msg": str(exc)})
            return

        # Parse final output
        brief_text = "".join(all_chunks)
        synthesis_only = "".join(
            c for c in all_chunks
            if not c.startswith("[COUNCIL:") and COUNCIL_DELIBERATING not in c
        )
        parsed = _extract_json(synthesis_only)

        council_brief_dict = None
        phase_arc_list = []
        if parsed:
            try:
                if parsed.get("council_brief"):
                    council_brief_dict = parsed["council_brief"]
                if parsed.get("phase_arc"):
                    phase_arc_list = parsed["phase_arc"]
            except Exception:
                pass

        yield _sse({
            "type":          "complete",
            "raw_brief":     brief_text,
            "council_brief": council_brief_dict,
            "phase_arc":     phase_arc_list,
            "venue_id":      body.venue_id,
            "session_number": body.session_number,
            "generated_at":  datetime.now(timezone.utc).isoformat(),
        })

    return StreamingResponse(_stream(), media_type="text/event-stream")


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


@router.get("/runs")
async def get_all_show_runs(limit: int = 20):
    """
    Returns recent show plans across all venues, newest first.
    Used by ShowHistory screen in the SE app.
    """
    pool = get_m3_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT sp.id, sp.venue_id, sp.plan_date, sp.version, sp.phase_count,
                   sp.start_time, sp.end_time, sp.generated_at, sp.finalized,
                   sp.m2_context_snapshot,
                   v.venue_name, v.area, v.city
            FROM m3_show_plans sp
            LEFT JOIN m3_venues v ON sp.venue_id = v.venue_id
            ORDER BY sp.generated_at DESC
            LIMIT $1
            """,
            limit,
        )

    results = []
    for r in rows:
        row = dict(r)
        ctx = row.get("m2_context_snapshot") or {}
        show_type = ctx.get("show_type") if isinstance(ctx, dict) else None
        plan_date = row["plan_date"]
        generated_at = row["generated_at"]
        results.append({
            "id":          row["id"],
            "venue_id":    row["venue_id"],
            "venue_name":  row.get("venue_name") or f"Venue {row['venue_id']}",
            "area":        row.get("area") or "",
            "city":        row.get("city") or "",
            "plan_date":   plan_date.isoformat() if plan_date else None,
            "version":     row["version"],
            "phase_count": row["phase_count"],
            "start_time":  row["start_time"],
            "end_time":    row["end_time"],
            "show_type":   show_type,
            "generated_at": generated_at.isoformat() if generated_at else None,
            "finalized":   row["finalized"],
            "outcome":     "no_review",
        })
    return results


@router.post("/converse")
async def converse_with_agent7(body: ConversationRequest):
    """
    Agent 7 — Conversational Guide (Nemotron 120B).
    Interprets the operator's natural language refinement and returns a structured
    response: what was heard, a summary, and a parameter_patch to apply before
    regenerating.
    """
    result = await run_agent7(
        operator_input=body.operator_input,
        venue_name=body.venue_name,
        current_context=body.current_context,
        current_plan=body.current_plan,
    )
    return result
