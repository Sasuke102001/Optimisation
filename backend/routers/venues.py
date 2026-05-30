from fastapi import APIRouter

from database import fetch_m3_venue_list, sync_venues_from_m2

router = APIRouter()


@router.get("")
async def list_venues():
    """
    Returns all venues from the local m3_venues table.
    Populated at startup from M2 RDS and refreshed via /sync.
    """
    return await fetch_m3_venue_list()


@router.post("/sync")
async def sync_venues():
    """
    Pulls all venues from M2 RDS and upserts into m3_venues.
    Call this after M2 adds new venues without a backend restart.
    """
    count = await sync_venues_from_m2()
    return {"synced": count}
