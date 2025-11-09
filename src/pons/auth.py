"""Authentication and security middleware."""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Optional

from pons.config import settings

# API Key Header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """Verify API key from request header."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key"
        )
    
    # Check against configured API keys
    valid_keys = settings.API_KEYS.get("api_keys", {})
    
    for key_name, key_value in valid_keys.items():
        if api_key == key_value:
            return key_name
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid API Key"
    )


def get_optional_api_key(api_key: Optional[str] = Security(api_key_header)) -> Optional[str]:
    """Get API key without requiring it (for optional auth endpoints)."""
    if not api_key:
        return None
    
    valid_keys = settings.API_KEYS.get("api_keys", {})
    for key_name, key_value in valid_keys.items():
        if api_key == key_value:
            return key_name
    
    return None
