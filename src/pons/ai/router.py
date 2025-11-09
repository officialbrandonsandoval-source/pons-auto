"""API router for AI services - descriptions and image processing."""

from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from pons.ai import ai_description_service, ai_image_service, AIDescription, AIBackgroundResult

router = APIRouter()


class DescriptionRequest(BaseModel):
    """Request for AI-generated vehicle description."""
    year: int
    make: str
    model: str
    trim: Optional[str] = None
    mileage: Optional[int] = None
    features: Optional[List[str]] = None
    condition: Optional[str] = None
    price: Optional[float] = None


class ImageBackgroundRequest(BaseModel):
    """Request for AI background replacement."""
    image_url: str
    background_style: str = "professional showroom"


class BatchImageRequest(BaseModel):
    """Request for batch image processing (select all)."""
    image_urls: List[str]
    background_style: str = "professional showroom"


@router.post("/description", response_model=AIDescription)
async def generate_description(request: DescriptionRequest) -> AIDescription:
    """
    Generate SEO-optimized vehicle description using GPT-4.
    
    Features:
    - Compelling title and description
    - Natural keyword integration for Meta's algorithm
    - Relevant hashtags
    - SEO score calculation
    
    This is the "set and forget" feature - just provide vehicle data
    and get back a complete, optimized listing description.
    """
    
    description = await ai_description_service.generate_description(
        year=request.year,
        make=request.make,
        model=request.model,
        trim=request.trim,
        mileage=request.mileage,
        features=request.features,
        condition=request.condition,
        price=request.price
    )
    
    return description


@router.post("/image/background", response_model=AIBackgroundResult)
async def replace_background(request: ImageBackgroundRequest) -> AIBackgroundResult:
    """
    Replace vehicle image background using AI.
    
    Background styles:
    - professional showroom: Modern dealership setting
    - scenic: Mountain road with blue sky
    - gradient: Professional studio gradient
    - studio: Clean photography studio
    - luxury: Upscale dealership
    - outdoor: Natural outdoor setting
    """
    
    result = await ai_image_service.remove_background(
        image_url=request.image_url,
        background_style=request.background_style
    )
    
    return result


@router.post("/image/background/batch", response_model=List[AIBackgroundResult])
async def batch_replace_backgrounds(request: BatchImageRequest) -> List[AIBackgroundResult]:
    """
    Process multiple images at once (select all feature).
    
    Applies the same background style to all selected images.
    Processes in parallel for speed.
    """
    
    if len(request.image_urls) > 20:
        raise HTTPException(
            status_code=400,
            detail="Maximum 20 images per batch request"
        )
    
    results = await ai_image_service.batch_process_images(
        image_urls=request.image_urls,
        background_style=request.background_style
    )
    
    return results


@router.get("/health")
async def health_check() -> dict:
    """Check if AI services are available."""
    import os
    
    openai_configured = bool(os.getenv("OPENAI_API_KEY"))
    
    return {
        "status": "healthy" if openai_configured else "degraded",
        "openai_configured": openai_configured,
        "services": {
            "description_generator": "available",
            "image_processing": "available" if openai_configured else "requires_api_key"
        }
    }
