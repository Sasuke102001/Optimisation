"""
POST /api/session/brief
Generates a pre/mid/post-session AI brief using M2 behavioral context + M3 session history.
Council mode streams R1 → R2 → synthesis. Fast mode returns a single response.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from database import fetch_m2_venue_context, get_m3_pool
from models import SessionBriefRequest, SessionBriefResponse

router = APIRouter()


def _build_brief_prompt(
    body: SessionBriefRequest,
    m2_context: dict,
    m3_history: list[dict],
) -> str:
    venue = m2_context.get("venue", {})
    fitness = m2_context.get("fitness", {})
    segments = m2_context.get("segments", [])
    primitives = m2_context.get("primitives", [])

    seg_lines = "\n".join(
        f"  - {s['segment_id']}: {round(s['alignment_score'] * 100)}% alignment"
        for s in segments[:3]
    )
    prim_line = ", ".join(p["primitive_id"] for p in primitives[:10])
    history_note = (
        f"Prior sessions at this venue: {len(m3_history)}. "
        f"Most recent: {m3_history[0].get('opened_at', 'unknown') if m3_history else 'none'}"
        if m3_history else "No prior M3 session history for this venue."
    )

    return f"""
=== SESSION BRIEF REQUEST ===
Venue: {venue.get('name', f'ID {body.venue_id}')} — {venue.get('area', '')}, {venue.get('city', '')}
Mode: {body.session_mode} | Session #{body.session_number}

=== LAYER A — M2 BEHAVIORAL PROFILE ===
Top segments:
{seg_lines if seg_lines else '  Not available'}

Fitness dimensions:
  Social dwell: {fitness.get('fitness_for_social_dwell', 'N/A')}
  Group energy: {fitness.get('fitness_for_group_energy', 'N/A')}
  Repeat habit: {fitness.get('fitness_for_repeat_habit', 'N/A')}
  Operational quality: {fitness.get('operational_quality', 'N/A')}
  Retention strength: {fitness.get('retention_strength', 'N/A')}

Top behavioral primitives: {prim_line if prim_line else 'Not available'}

=== LAYER B — M3 SESSION HISTORY ===
{history_note}

=== LIVE STATE ===
{str(body.live_state) if body.live_state else 'No live state provided (pre-session).'}

Generate a concise, actionable {body.session_mode.replace('_', ' ')} brief for the show engineer.
""".strip()


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
            ORDER BY opened_at DESC
            LIMIT 10
            """,
            body.venue_id,
        )
    m3_history = [dict(r) for r in history]

    prompt = _build_brief_prompt(body, m2_context, m3_history)

    # TODO: wire Council here (Phase 6).
    # Placeholder response until council.py is built.
    brief_text = (
        f"[Brief placeholder — Council not yet wired]\n\n"
        f"Prompt assembled for venue {body.venue_id}, session #{body.session_number}, "
        f"mode: {body.session_mode}.\n"
        f"M2 context: {'available' if m2_context else 'not available'}. "
        f"Prior sessions: {len(m3_history)}."
    )

    return SessionBriefResponse(
        brief=brief_text,
        session_number=body.session_number,
        venue_id=body.venue_id,
        generated_at=datetime.now(timezone.utc),
    )
