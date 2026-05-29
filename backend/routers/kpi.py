from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from database import get_m2_pool, get_m3_pool
from models import (
    EnvironmentLogRequest,
    InterventionEndRequest,
    InterventionStartRequest,
    KpiAssessmentRequest,
    SessionEndRequest,
    SessionStartRequest,
    SessionStartResponse,
)

_RAG_SCORE = {"green": 0.85, "amber": 0.55, "red": 0.20}


def _compute_feed_values(rag_status: str, readings: list) -> tuple[float, int, str | None]:
    """
    Returns (score, signal_count, dominant_signal) for the M2 feed row.
    score      — RAG bracket midpoint until per-signal ranges are stored in m3_kpi_signals.
    signal_count — number of readings that carried a numeric value.
    dominant_signal — label of the reading with the largest absolute numeric value.
    """
    numeric = [(r.signal_label, r.value_numeric) for r in readings if r.value_numeric is not None]
    signal_count = len(numeric)
    dominant_signal = None
    if numeric:
        dominant_signal = max(numeric, key=lambda x: abs(x[1]))[0]
    score = _RAG_SCORE.get(rag_status, 0.55)
    return score, signal_count, dominant_signal


async def _push_kpi_observation_to_m2(
    venue_id: int,
    session_number: int,
    session_mode: str,
    day_of_week: int,
    session_start_hour: int,
    zone: str | None,
    kpi_family_slug: str,
    rag_status: str,
    score: float,
    signal_count: int,
    dominant_signal: str | None,
    notes: str | None,
) -> None:
    """Fire-and-forget push to M2 RDS. Silently skips if M2 pool is unavailable."""
    pool = get_m2_pool()
    if pool is None:
        return
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO m3_kpi_observations
                    (venue_id, session_number, session_mode, day_of_week, session_start_hour,
                     zone, kpi_family_slug, rag_status, score, signal_count, dominant_signal, notes)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)
                """,
                venue_id, session_number, session_mode, day_of_week, session_start_hour,
                zone, kpi_family_slug, rag_status, score, signal_count, dominant_signal, notes,
            )
    except Exception as exc:
        # M2 feed failure must never break the M3 response.
        print(f"[m2-feed] kpi_observation push failed: {exc}")

router = APIRouter()


# ─── Session lifecycle ────────────────────────────────────────────────────────

@router.post("/session/start", response_model=SessionStartResponse)
async def start_session(body: SessionStartRequest):
    pool = get_m3_pool()
    now = datetime.now(timezone.utc)
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO m3_sessions
                (venue_id, session_number, session_mode, table_config,
                 opened_at, day_of_week, session_start_hour, notes)
            VALUES ($1, $2, $3, $4::jsonb, $5, $6, $7, $8)
            ON CONFLICT (venue_id, session_number) DO NOTHING
            RETURNING id, venue_id, session_number, opened_at
            """,
            body.venue_id,
            body.session_number,
            body.session_mode,
            str(body.table_config) if body.table_config else None,
            now,
            now.isoweekday(),   # 1=Mon 7=Sun
            now.hour,
            body.notes,
        )
        if row is None:
            raise HTTPException(
                status_code=409,
                detail=f"Session {body.session_number} for venue {body.venue_id} already exists.",
            )
    return SessionStartResponse(**dict(row))


@router.post("/session/{session_id}/end")
async def end_session(session_id: int, body: SessionEndRequest):
    pool = get_m3_pool()
    async with pool.acquire() as conn:
        updated = await conn.fetchval(
            """
            UPDATE m3_sessions
            SET closed_at = NOW(), notes = COALESCE($2, notes)
            WHERE id = $1 AND closed_at IS NULL
            RETURNING id
            """,
            session_id,
            body.notes,
        )
    if updated is None:
        raise HTTPException(status_code=404, detail="Session not found or already closed.")
    return {"session_id": session_id, "closed": True}


@router.get("/session/{session_id}")
async def get_session(session_id: int):
    pool = get_m3_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM m3_sessions WHERE id = $1",
            session_id,
        )
    if row is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return dict(row)


# ─── KPI assessments ──────────────────────────────────────────────────────────

@router.post("/session/{session_id}/assessment")
async def submit_assessment(session_id: int, body: KpiAssessmentRequest):
    pool = get_m3_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            assessment_id = await conn.fetchval(
                """
                INSERT INTO m3_kpi_assessments
                    (session_id, family_id, zone, rag_status, notes)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
                """,
                session_id, body.family_id, body.zone, body.rag_status, body.notes,
            )
            for r in body.readings:
                await conn.execute(
                    """
                    INSERT INTO m3_kpi_signal_readings
                        (assessment_id, signal_id, signal_label, value_numeric, value_text)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    assessment_id, r.signal_id, r.signal_label, r.value_numeric, r.value_text,
                )

        # Fetch session anchor fields needed for M2 feed row.
        session_row = await conn.fetchrow(
            """
            SELECT s.venue_id, s.session_number, s.session_mode,
                   s.day_of_week, s.session_start_hour,
                   f.slug AS family_slug
            FROM m3_sessions s
            JOIN m3_kpi_families f ON f.id = $2
            WHERE s.id = $1
            """,
            session_id, body.family_id,
        )

    if session_row:
        score, signal_count, dominant_signal = _compute_feed_values(body.rag_status, body.readings)
        await _push_kpi_observation_to_m2(
            venue_id=session_row["venue_id"],
            session_number=session_row["session_number"],
            session_mode=session_row["session_mode"],
            day_of_week=session_row["day_of_week"],
            session_start_hour=session_row["session_start_hour"],
            zone=body.zone,
            kpi_family_slug=session_row["family_slug"],
            rag_status=body.rag_status,
            score=score,
            signal_count=signal_count,
            dominant_signal=dominant_signal,
            notes=body.notes,
        )

    return {"assessment_id": assessment_id}


# ─── Intervention tracking ────────────────────────────────────────────────────

@router.post("/session/{session_id}/intervention/start")
async def start_intervention(session_id: int, body: InterventionStartRequest):
    pool = get_m3_pool()
    async with pool.acquire() as conn:
        log_id = await conn.fetchval(
            """
            INSERT INTO m3_intervention_log
                (session_id, intervention_id, intervention_label, operator_notes)
            VALUES ($1, $2, $3, $4)
            RETURNING id
            """,
            session_id, body.intervention_id, body.intervention_label, body.operator_notes,
        )
    return {"intervention_log_id": log_id, "started": True}


@router.post("/session/{session_id}/intervention/end")
async def end_intervention(session_id: int, body: InterventionEndRequest):
    pool = get_m3_pool()
    async with pool.acquire() as conn:
        updated = await conn.fetchval(
            """
            UPDATE m3_intervention_log
            SET ended_at = NOW(),
                operator_notes = COALESCE($3, operator_notes)
            WHERE id = $1 AND session_id = $2 AND ended_at IS NULL
            RETURNING id
            """,
            body.intervention_log_id, session_id, body.operator_notes,
        )
    if updated is None:
        raise HTTPException(status_code=404, detail="Intervention log not found or already ended.")
    return {"intervention_log_id": body.intervention_log_id, "ended": True}


# ─── Environment log ──────────────────────────────────────────────────────────

@router.post("/session/{session_id}/environment")
async def log_environment(session_id: int, body: EnvironmentLogRequest):
    """Logs environment-tab readings as a KPI assessment against a synthetic family."""
    pool = get_m3_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            # Upsert an env-type assessment (zone=body.zone, family slug='environment')
            assessment_id = await conn.fetchval(
                """
                INSERT INTO m3_kpi_assessments
                    (session_id, family_id, zone, rag_status, notes)
                SELECT $1, id, $2, 'green', $3
                FROM m3_kpi_families WHERE slug = 'environment' LIMIT 1
                RETURNING id
                """,
                session_id, body.zone, body.notes,
            )
            for r in body.readings:
                await conn.execute(
                    """
                    INSERT INTO m3_kpi_signal_readings
                        (assessment_id, signal_id, signal_label, value_numeric, value_text)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    assessment_id, r.signal_id, r.signal_label, r.value_numeric, r.value_text,
                )
    return {"assessment_id": assessment_id}
