"""Feed validation and error handling."""

from pydantic import BaseModel, field_validator, Field
from typing import Any, Dict, List, Optional, Tuple
import re


class VehicleFeedSchema(BaseModel):
    """Validation schema for vehicle feed data."""
    
    vin: str = Field(..., min_length=17, max_length=17)
    stock_number: Optional[str] = None
    year: int = Field(..., ge=1900, le=2030)
    make: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    trim: Optional[str] = None
    price: Optional[int] = Field(None, ge=0)
    mileage: Optional[int] = Field(None, ge=0)
    exterior_color: Optional[str] = None
    
    @field_validator('vin')
    @classmethod
    def validate_vin(cls, v: str) -> str:
        """Validate VIN format."""
        if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', v.upper()):
            raise ValueError('Invalid VIN format')
        return v.upper()
    
    @field_validator('year')
    @classmethod
    def validate_year(cls, v: int) -> int:
        """Validate reasonable year range."""
        if v < 1900 or v > 2030:
            raise ValueError('Year must be between 1900 and 2030')
        return v
    
    model_config = {"str_strip_whitespace": True}


class FeedValidator:
    """Validate vehicle feed data."""
    
    @staticmethod
    def validate_vehicle(data: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Validate vehicle data.
        
        Returns:
            (is_valid, error_message, validated_data)
        """
        try:
            validated = VehicleFeedSchema(**data)
            return True, None, validated.model_dump()
        except Exception as e:
            return False, str(e), None
    
    @staticmethod
    def validate_batch(vehicles: List[Dict[str, Any]]) -> Dict[str, List[Any]]:
        """
        Validate a batch of vehicles.
        
        Returns:
            {
                'valid': [validated_vehicles],
                'invalid': [{'data': {}, 'error': ''}]
            }
        """
        result: Dict[str, List[Any]] = {
            'valid': [],
            'invalid': []
        }
        
        for vehicle in vehicles:
            is_valid, error, validated = FeedValidator.validate_vehicle(vehicle)
            
            if is_valid:
                result['valid'].append(validated)
            else:
                result['invalid'].append({
                    'data': vehicle,
                    'error': error
                })
        
        return result
