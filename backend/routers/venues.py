from fastapi import APIRouter
from database import fetch_m2_venue_list

router = APIRouter()


@router.get("")
async def list_venues():
    """Returns all M2 venues for the venue search bar."""
    return await fetch_m2_venue_list()
