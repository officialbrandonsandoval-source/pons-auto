"""API router for inventory management."""

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query
from pons.inventory import inventory_service, InventoryVehicle

router = APIRouter()


@router.post("/vehicles", status_code=201)
async def add_vehicle(vehicle: InventoryVehicle):
    """Add a vehicle to inventory."""
    result = await inventory_service.add_vehicle(vehicle)
    return result


@router.get("/vehicles/{vin}")
async def get_vehicle(vin: str):
    """Get a vehicle by VIN."""
    vehicle = await inventory_service.get_vehicle(vin)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.put("/vehicles/{vin}")
async def update_vehicle(vin: str, updates: Dict[str, Any]):
    """Update a vehicle in inventory."""
    vehicle = await inventory_service.update_vehicle(vin, updates)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.delete("/vehicles/{vin}")
async def remove_vehicle(vin: str):
    """Remove a vehicle from inventory."""
    success = await inventory_service.remove_vehicle(vin)
    if not success:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"message": "Vehicle removed successfully"}


@router.get("/vehicles")
async def list_vehicles(
    status: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0)
) -> Dict[str, Any]:
    """List vehicles in inventory."""
    vehicles = await inventory_service.list_vehicles(status, limit, offset)
    return {"vehicles": vehicles, "count": len(vehicles)}


@router.post("/vehicles/search")
async def search_vehicles(query: Dict[str, Any]) -> Dict[str, Any]:
    """Search vehicles by criteria."""
    vehicles = await inventory_service.search_vehicles(query)
    return {"vehicles": vehicles, "count": len(vehicles)}
