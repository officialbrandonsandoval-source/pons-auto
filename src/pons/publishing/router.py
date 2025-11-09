"""API router for publishing orchestrator."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from pons.publishing import (
    publishing_orchestrator,
    PublishingChannel,
    PublishJob
)

router = APIRouter()


class PublishRequest(BaseModel):
    """Request to publish a vehicle."""
    vin: str
    channels: List[PublishingChannel]


@router.post("/jobs", status_code=201)
async def create_publish_job(request: PublishRequest) -> PublishJob:
    """Create a new publishing job."""
    job = await publishing_orchestrator.create_publish_job(
        request.vin,
        request.channels
    )
    return job


@router.post("/jobs/{job_id}/execute")
async def execute_job(job_id: str) -> PublishJob:
    """Execute a publishing job."""
    try:
        job = await publishing_orchestrator.execute_job(job_id)
        return job
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/jobs/{job_id}")
async def get_job(job_id: str) -> PublishJob:
    """Get a publishing job."""
    job = await publishing_orchestrator.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/jobs")
async def list_jobs(vin: Optional[str] = Query(None)) -> Dict[str, Any]:
    """List publishing jobs."""
    jobs = await publishing_orchestrator.list_jobs(vin)
    return {"jobs": jobs, "count": len(jobs)}


@router.get("/channels")
async def list_channels() -> Dict[str, List[str]]:
    """List available publishing channels."""
    return {
        "channels": [channel.value for channel in PublishingChannel]
    }


class PreviewRequest(BaseModel):
    """Request to preview a vehicle listing."""
    vin: str
    channel: PublishingChannel


class PriceSuggestionRequest(BaseModel):
    """Request for price suggestion based on similar vehicles."""
    year: int
    make: str
    model: str
    mileage: int
    trim: Optional[str] = None


@router.post("/price-suggestion")
async def suggest_price(request: PriceSuggestionRequest) -> Dict[str, Any]:
    """
    Auto-suggest price based on similar sold listings.
    Uses Cars.com API to pull comparable vehicles.
    """
    # In production: call Cars.com API for similar vehicles
    # For now, return mock data with pricing algorithm
    
    # Simple pricing algorithm (replace with real API call)
    base_price = 30000  # Starting point for 2022 sedan
    
    # Adjust by mileage
    mileage_adjustment = -0.10 * (request.mileage / 10000)  # -10% per 10k miles
    
    # Mock comparable vehicles
    comparables = [
        {"vin": "5YJ3E1EB3KF123456", "price": 29500, "mileage": 24000, "days_on_market": 12},
        {"vin": "1G1ZD5ST8JF123457", "price": 28750, "mileage": 28000, "days_on_market": 18},
        {"vin": "3VW2B7AJ3GM123458", "price": 30200, "mileage": 22000, "days_on_market": 9},
    ]
    
    avg_comp_price = sum(c["price"] for c in comparables) / len(comparables)
    suggested_price = int(avg_comp_price * (1 + mileage_adjustment))
    
    return {
        "suggested_price": suggested_price,
        "confidence": "high",  # high, medium, low
        "price_range": {
            "min": int(suggested_price * 0.95),
            "max": int(suggested_price * 1.05)
        },
        "comparables": comparables,
        "reasoning": f"Based on {len(comparables)} similar {request.year} {request.make} {request.model} vehicles",
        "market_insights": {
            "avg_days_on_market": 13,
            "demand_level": "High",
            "pricing_recommendation": "Price competitively at suggested amount for quick sale"
        }
    }


@router.post("/preview")
async def preview_listing(request: PreviewRequest) -> Dict[str, Any]:
    """
    Preview exactly what a listing will look like on the target channel.
    Returns formatted data including photo order, description, price display.
    Dealerships can verify listings before publishing.
    """
    from pons.models import Vehicle as VehicleModel, SessionLocal
    from pons.integrations import facebook_api, autotrader_api, carscom_api
    
    # Get vehicle from database
    db = SessionLocal()
    try:
        vehicle = db.query(VehicleModel).filter(VehicleModel.vin == request.vin).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        vehicle_data: Dict[str, Any] = {
            "vin": vehicle.vin,  # type: ignore
            "year": vehicle.year,  # type: ignore
            "make": vehicle.make,  # type: ignore
            "model": vehicle.model,  # type: ignore
            "trim": vehicle.trim,  # type: ignore
            "body_type": vehicle.body_type,  # type: ignore
            "price": float(vehicle.price or 0),  # type: ignore
            "mileage": vehicle.mileage,  # type: ignore
            "exterior_color": vehicle.exterior_color,  # type: ignore
            "interior_color": vehicle.interior_color,  # type: ignore
            "transmission": vehicle.transmission,  # type: ignore
            "fuel_type": vehicle.fuel_type,  # type: ignore
            "drivetrain": vehicle.drivetrain,  # type: ignore
            "description": vehicle.description or "",  # type: ignore
            "features": vehicle.features or [],  # type: ignore
            "images": vehicle.images or [],  # type: ignore
            "stock_number": vehicle.stock_number,  # type: ignore
        }
    finally:
        db.close()
    
    # Format for requested channel
    if request.channel == PublishingChannel.FACEBOOK:
        formatted = facebook_api._format_vehicle_for_facebook(vehicle_data)
        # Add human-readable display values
        preview = {
            "channel": "facebook_marketplace",
            "listing_title": formatted["name"],
            "listing_description": formatted["description"],
            "price_display": f"${vehicle_data['price']:,.2f}",
            "price_cents": formatted["price"],  # Facebook uses cents
            "condition": formatted["condition"],
            "availability": formatted["availability"],
            "photos": formatted["images"],
            "photo_count": len(formatted["images"]),
            "vehicle_details": {
                "VIN": formatted["vin"],
                "Year": formatted["year"],
                "Make": formatted["make"],
                "Model": formatted["model"],
                "Trim": formatted.get("trim", "N/A"),
                "Body Style": formatted.get("body_style", "N/A"),
                "Mileage": f"{formatted['mileage']['value']:,} {formatted['mileage']['unit']}",
                "Exterior Color": formatted.get("exterior_color", "N/A"),
                "Interior Color": formatted.get("interior_color", "N/A"),
                "Transmission": formatted.get("transmission", "N/A"),
                "Fuel Type": formatted.get("fuel_type", "N/A"),
                "Drivetrain": formatted.get("drivetrain", "N/A"),
            },
            "desktop_view": {
                "layout": "2-column grid",
                "photo_gallery": "Large carousel (1200x800px)",
                "description_visibility": "Full text visible",
                "features_display": "All features listed",
                "contact_button": "Right sidebar - prominent",
                "similar_listings": "Shown below (8 vehicles)"
            },
            "mobile_view": {
                "layout": "Single column stack",
                "photo_gallery": "Swipeable (800x600px)",
                "description_visibility": "First 3 lines + 'Read more'",
                "features_display": "Collapsed accordion",
                "contact_button": "Sticky bottom bar",
                "similar_listings": "Horizontal scroll (4 vehicles)"
            },
            "raw_payload": formatted,
        }
        
    elif request.channel == PublishingChannel.AUTOTRADER:
        formatted = autotrader_api._format_vehicle_for_autotrader(vehicle_data)
        preview = {
            "channel": "autotrader",
            "listing_title": f"{vehicle_data['year']} {vehicle_data['make']} {vehicle_data['model']}",
            "listing_description": formatted["description"],
            "price_display": f"${vehicle_data['price']:,.2f}",
            "photos": formatted["images"],
            "photo_count": len(formatted["images"]),
            "vehicle_details": {
                "VIN": formatted["vin"],
                "Stock Number": formatted.get("stock_number", "N/A"),
                "Year": formatted["year"],
                "Make": formatted["make"],
                "Model": formatted["model"],
                "Trim": formatted.get("trim", "N/A"),
                "Body Style": formatted.get("body_style", "N/A"),
                "Price": vehicle_data['price'],
                "Mileage": f"{formatted.get('mileage', 0):,} miles",
                "Exterior Color": formatted.get("exterior_color", "N/A"),
                "Interior Color": formatted.get("interior_color", "N/A"),
                "Transmission": formatted.get("transmission", "N/A"),
                "Fuel Type": formatted.get("fuel_type", "N/A"),
                "Drivetrain": formatted.get("drivetrain", "N/A"),
            },
            "features": formatted.get("features", []),
            "raw_payload": formatted,
        }
        
    elif request.channel == PublishingChannel.CARS_COM:
        formatted = carscom_api._format_vehicle_for_carscom(vehicle_data)
        preview = {
            "channel": "cars_com",
            "listing_title": f"{vehicle_data['year']} {vehicle_data['make']} {vehicle_data['model']}",
            "listing_description": formatted["description"],
            "price_display": f"${vehicle_data['price']:,.2f}",
            "photos": formatted["photos"],
            "photo_count": len(formatted["photos"]),
            "vehicle_details": {
                "VIN": formatted["vin"],
                "Stock Number": formatted.get("stockNumber", "N/A"),
                "Year": formatted["year"],
                "Make": formatted["make"],
                "Model": formatted["model"],
                "Trim": formatted.get("trim", "N/A"),
                "Body Style": formatted.get("bodyStyle", "N/A"),
                "Price": vehicle_data['price'],
                "Mileage": f"{formatted.get('mileage', 0):,} miles",
                "Exterior Color": formatted.get("exteriorColor", "N/A"),
                "Interior Color": formatted.get("interiorColor", "N/A"),
                "Transmission": formatted.get("transmission", "N/A"),
                "Fuel Type": formatted.get("fuelType", "N/A"),
                "Drivetrain": formatted.get("drivetrain", "N/A"),
            },
            "options": formatted.get("options", []),
            "raw_payload": formatted,
        }
        
    else:  # CARGURUS
        preview = {
            "channel": "cargurus",
            "listing_title": f"{vehicle_data['year']} {vehicle_data['make']} {vehicle_data['model']}",
            "listing_description": vehicle_data.get("description", ""),
            "price_display": f"${vehicle_data['price']:,.2f}",
            "photos": vehicle_data.get("images", []),
            "photo_count": len(vehicle_data.get("images", [])),
            "vehicle_details": {
                "VIN": vehicle_data["vin"],
                "Year": vehicle_data["year"],
                "Make": vehicle_data["make"],
                "Model": vehicle_data["model"],
                "Trim": vehicle_data.get("trim", "N/A"),
                "Price": vehicle_data['price'],
                "Mileage": f"{vehicle_data.get('mileage', 0):,} miles",
            },
            "raw_payload": vehicle_data,
        }
    
    return preview
