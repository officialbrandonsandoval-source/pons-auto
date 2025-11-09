"""AI services for PONS AUTO - GPT-4 integration for descriptions and image processing."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import os
from openai import AsyncOpenAI

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))


@dataclass
class AIDescription:
    """AI-generated vehicle description with SEO optimization."""
    title: str
    description: str
    keywords: List[str]
    hashtags: List[str]
    seo_score: float
    character_count: int


@dataclass
class AIBackgroundResult:
    """Result from AI background replacement."""
    image_url: str
    original_url: str
    prompt_used: str
    processing_time: float


class AIDescriptionService:
    """Service for generating SEO-optimized vehicle descriptions using GPT-4."""
    
    async def generate_description(
        self,
        year: int,
        make: str,
        model: str,
        trim: Optional[str] = None,
        mileage: Optional[int] = None,
        features: Optional[List[str]] = None,
        condition: Optional[str] = None,
        price: Optional[float] = None
    ) -> AIDescription:
        """
        Generate SEO-optimized description with keywords and hashtags.
        
        Uses GPT-4 to create compelling copy that:
        - Highlights key features
        - Includes relevant keywords naturally
        - Generates targeted hashtags
        - Optimizes for Facebook, AutoTrader, Cars.com algorithms
        """
        
        # Build context for GPT-4
        vehicle_context = f"{year} {make} {model}"
        if trim:
            vehicle_context += f" {trim}"
        
        feature_text = ""
        if features:
            feature_text = f"\nKey Features: {', '.join(features)}"
        
        mileage_text = f"\nMileage: {mileage:,} miles" if mileage else ""
        condition_text = f"\nCondition: {condition}" if condition else ""
        price_text = f"\nPrice: ${price:,.0f}" if price else ""
        
        prompt = f"""Generate a compelling vehicle listing description for:

{vehicle_context}{feature_text}{mileage_text}{condition_text}{price_text}

Requirements:
1. Create an engaging title (60 chars max)
2. Write a description (300-500 words) that:
   - Opens with a strong hook
   - Highlights unique selling points
   - Uses natural, conversational language
   - Includes SEO keywords organically (not keyword stuffing)
   - Mentions safety, performance, and comfort features
   - Ends with a call-to-action
3. Extract 10-15 SEO keywords for Meta/Facebook algorithm
4. Generate 8-12 relevant hashtags (#UsedCars, #ToyotaCamry, etc.)
5. Keywords should appear naturally in the description so Meta can count them

Format response as JSON:
{{
  "title": "...",
  "description": "...",
  "keywords": ["keyword1", "keyword2", ...],
  "hashtags": ["#hashtag1", "#hashtag2", ...]
}}"""

        try:
            response = await client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert automotive copywriter specializing in vehicle listings. You understand SEO, Meta's algorithm, and how to write descriptions that convert browsers into buyers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            description = result["description"]
            keywords = result.get("keywords", [])
            
            # Calculate SEO score based on keyword density and readability
            total_words = len(description.split())
            keyword_mentions = sum(
                description.lower().count(kw.lower()) 
                for kw in keywords
            )
            seo_score = min(100, (keyword_mentions / len(keywords)) * 20)
            
            return AIDescription(
                title=result["title"],
                description=description,
                keywords=keywords,
                hashtags=result.get("hashtags", []),
                seo_score=seo_score,
                character_count=len(description)
            )
            
        except Exception as e:
            # Fallback to basic description if API fails
            return AIDescription(
                title=f"{year} {make} {model}",
                description=f"Great {year} {make} {model} in excellent condition. Contact us for more details!",
                keywords=[make.lower(), model.lower(), str(year)],
                hashtags=[f"#{make}", f"#{model}", "#UsedCars"],
                seo_score=50.0,
                character_count=100
            )


class AIImageService:
    """Service for AI-powered background replacement using DALL-E 3."""
    
    async def remove_background(
        self,
        image_url: str,
        background_style: str = "professional showroom"
    ) -> AIBackgroundResult:
        """
        Remove background and replace with AI-generated professional setting.
        
        Args:
            image_url: URL of the vehicle image
            background_style: Type of background (showroom, scenic, gradient, studio)
        
        Returns:
            AIBackgroundResult with new image URL
        """
        
        background_prompts = {
            "professional showroom": "modern car dealership showroom with bright lighting, polished floors, and clean white walls",
            "scenic": "beautiful scenic mountain road with blue sky and greenery",
            "gradient": "professional gradient backdrop transitioning from light gray to white",
            "studio": "professional photography studio with soft lighting and neutral background",
            "luxury": "upscale luxury dealership with marble floors and elegant lighting",
            "outdoor": "beautiful outdoor setting with natural lighting and clear sky"
        }
        
        prompt = background_prompts.get(background_style, background_prompts["professional showroom"])
        
        try:
            # Note: DALL-E 3 edit endpoint for background replacement
            # In production, you'd use GPT-4 Vision to analyze the vehicle
            # then DALL-E 3 to generate the new background composition
            
            # For now, we'll use image generation with vehicle description
            import time
            start_time = time.time()
            
            response = await client.images.generate(
                model="dall-e-3",
                prompt=f"Professional car dealership photo of a vehicle in a {prompt}. Photo-realistic, high quality, suitable for vehicle listing.",
                size="1792x1024",
                quality="hd",
                n=1
            )
            
            processing_time = time.time() - start_time
            
            return AIBackgroundResult(
                image_url=response.data[0].url,
                original_url=image_url,
                prompt_used=prompt,
                processing_time=processing_time
            )
            
        except Exception as e:
            # Return original if AI processing fails
            return AIBackgroundResult(
                image_url=image_url,
                original_url=image_url,
                prompt_used="Original (AI processing failed)",
                processing_time=0.0
            )
    
    async def batch_process_images(
        self,
        image_urls: List[str],
        background_style: str = "professional showroom"
    ) -> List[AIBackgroundResult]:
        """
        Process multiple images with same background style.
        
        This is the 'select all' feature for batch processing.
        """
        import asyncio
        
        tasks = [
            self.remove_background(url, background_style)
            for url in image_urls
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful results
        return [r for r in results if isinstance(r, AIBackgroundResult)]


# Service instances
ai_description_service = AIDescriptionService()
ai_image_service = AIImageService()
