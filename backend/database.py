"""
Dual connection pool:
  get_m3_pool()  → Azure PostgreSQL (polynovea_m3)  — full read/write
  get_m2_pool()  → AWS RDS (polynovea_module2)      — read + write to m3_* tables only
"""
import json
import os
from typing import AsyncGenerator

import asyncpg
from dotenv import load_dotenv

load_dotenv()

_m3_pool: asyncpg.Pool | None = None
_m2_pool: asyncpg.Pool | None = None


async def init_pools() -> None:
    global _m3_pool, _m2_pool

    _m3_pool = await asyncpg.create_pool(
        host=os.environ["M3_DB_HOST"],
        port=int(os.environ.get("M3_DB_PORT", 5432)),
        database=os.environ["M3_DB_NAME"],
        user=os.environ["M3_DB_USER"],
        password=os.environ["M3_DB_PASSWORD"],
        ssl="require",
        min_size=2,
        max_size=10,
    )

    m2_url = os.environ.get("M2_DATABASE_URL")
    if m2_url:
        _m2_pool = await asyncpg.create_pool(
            dsn=m2_url,
            min_size=1,
            max_size=5,
        )
    else:
        print("WARNING: M2_DATABASE_URL not set — M2 pool not initialised.")


async def close_pools() -> None:
    if _m3_pool:
        await _m3_pool.close()
    if _m2_pool:
        await _m2_pool.close()


def get_m3_pool() -> asyncpg.Pool:
    if _m3_pool is None:
        raise RuntimeError("M3 pool not initialised — did lifespan run?")
    return _m3_pool


def get_m2_pool() -> asyncpg.Pool | None:
    """Returns None if M2 is not configured (dev without M2 creds)."""
    return _m2_pool


async def fetch_m2_venue_context(venue_id: int) -> dict:
    """
    Assemble Layer A behavioral intelligence from M2 RDS.
    Returns a dict with keys: venue, fitness, segments, primitives.
    Returns empty dict if M2 pool is not available.
    """
    pool = get_m2_pool()
    if pool is None:
        return {}

    async with pool.acquire() as conn:
        venue = await conn.fetchrow(
            "SELECT id, name, area, city, types FROM venues WHERE id = $1",
            venue_id,
        )
        fitness = await conn.fetchrow(
            """
            SELECT fitness_for_office_lunch, fitness_for_repeat_habit,
                   fitness_for_social_dwell, fitness_for_group_energy,
                   fitness_for_destination_visit, operational_quality,
                   retention_strength, monetization_potential
            FROM venue_fitness_dimensions
            WHERE venue_id = $1 AND source = 'blended'
            LIMIT 1
            """,
            venue_id,
        )
        segments = await conn.fetch(
            """
            SELECT segment_id, alignment_score, segment_rank
            FROM venue_demographic_scores
            WHERE venue_id = $1
            ORDER BY alignment_score DESC
            LIMIT 7
            """,
            venue_id,
        )
        primitives = await conn.fetch(
            """
            SELECT primitive_id, score
            FROM primitives_scores
            WHERE venue_id = $1
            ORDER BY score DESC
            LIMIT 15
            """,
            venue_id,
        )

    return {
        "venue":      dict(venue)    if venue     else {},
        "fitness":    dict(fitness)  if fitness   else {},
        "segments":   [dict(r) for r in segments],
        "primitives": [dict(r) for r in primitives],
    }


async def sync_venues_from_m2() -> int:
    """
    Pulls all venues from M2 RDS and upserts into m3_venues.
    Called at backend startup and via POST /api/venues/sync.
    Returns the number of venues synced.
    M2 unavailable → logs warning, returns 0 (non-fatal).
    """
    m2_pool = get_m2_pool()
    if m2_pool is None:
        print("WARNING: sync_venues_from_m2 skipped — M2 pool not available.")
        return 0

    async with m2_pool.acquire() as m2_conn:
        rows = await m2_conn.fetch(
            "SELECT id, name, area, city, types FROM venues ORDER BY id ASC"
        )

    if not rows:
        return 0

    m3_pool = get_m3_pool()
    async with m3_pool.acquire() as m3_conn:
        await m3_conn.executemany(
            """
            INSERT INTO m3_venues (venue_id, venue_name, area, city, types, last_synced)
            VALUES ($1, $2, $3, $4, $5::jsonb, NOW())
            ON CONFLICT (venue_id) DO UPDATE
                SET venue_name  = EXCLUDED.venue_name,
                    area        = EXCLUDED.area,
                    city        = EXCLUDED.city,
                    types       = EXCLUDED.types,
                    last_synced = EXCLUDED.last_synced
            """,
            [
                (r["id"], r["name"], r["area"], r["city"],
                 json.dumps(r["types"]) if isinstance(r["types"], list)
                 else r["types"])  # already a JSON string from M2 TEXT column
                for r in rows
            ],
        )

    print(f"sync_venues_from_m2: {len(rows)} venues synced from M2.")
    return len(rows)


async def fetch_m3_venue_list() -> list[dict]:
    """
    Returns all active venues from the local m3_venues table.
    m3_venues is populated by sync_venues_from_m2() at startup.
    Fast — no cross-DB call on the hot path.
    """
    pool = get_m3_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT venue_id AS id, venue_name AS name, area, city, types
            FROM m3_venues
            WHERE active = TRUE
            ORDER BY venue_name ASC
            """
        )
    result = []
    for r in rows:
        d = dict(r)
        t = d.get('types')
        if isinstance(t, str):
            try:
                d['types'] = json.loads(t)
            except Exception:
                d['types'] = []
        elif t is None:
            d['types'] = []
        result.append(d)
    return result
