"""API router for normalization service."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from pons.normalization import normalization_service, NormalizedVehicle

router = APIRouter()


class NormalizeRequest(BaseModel):
    """Request model for normalization."""
    source: str
    raw_data: Dict[str, Any]


@router.post("/normalize")
async def normalize_vehicle(request: NormalizeRequest) -> NormalizedVehicle:
    """Normalize raw vehicle data."""
    try:
        normalized = normalization_service.normalize_vehicle(
            request.raw_data,
            request.source
        )
        return normalized
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Normalization error: {str(e)}")


@router.post("/enrich")
async def enrich_vehicle(vehicle: NormalizedVehicle) -> NormalizedVehicle:
    """Enrich normalized vehicle data."""
    try:
        enriched = await normalization_service.enrich_vehicle(vehicle)
        return enriched
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Enrichment error: {str(e)}")
