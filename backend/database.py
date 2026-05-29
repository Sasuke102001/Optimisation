"""
Dual connection pool:
  get_m3_pool()  → Azure PostgreSQL (polynovea_m3)  — full read/write
  get_m2_pool()  → AWS RDS (polynovea_module2)      — read + write to m3_* tables only
"""
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


async def fetch_m2_venue_list() -> list[dict]:
    """
    Returns all active venues from M2 RDS for the venue search bar.
    Returns empty list if M2 pool is not available.
    """
    pool = get_m2_pool()
    if pool is None:
        return []
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, name, area, city, types
            FROM venues
            WHERE city IN ('Mumbai', 'Navi Mumbai', 'Thane')
            ORDER BY name ASC
            """,
        )
    return [dict(r) for r in rows]
