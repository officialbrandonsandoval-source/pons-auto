"""API router for feed integrations."""

from typing import List
from fastapi import APIRouter, HTTPException
from pons.feed_integrations import feed_service, FeedSource, VehicleRawData

router = APIRouter()


@router.post("/sources", status_code=201)
async def register_feed_source(source: FeedSource):
    """Register a new feed source."""
    await feed_service.register_feed(source)
    return {"message": f"Feed source '{source.name}' registered successfully"}


@router.get("/sources")
async def list_feed_sources():
    """List all registered feed sources."""
    return {"sources": list(feed_service.sources.keys())}


@router.post("/fetch/{source_name}")
async def fetch_feed_data(source_name: str) -> List[VehicleRawData]:
    """Fetch data from a specific feed source."""
    try:
        vehicles = await feed_service.fetch_feed(source_name)
        return vehicles
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching feed: {str(e)}")
