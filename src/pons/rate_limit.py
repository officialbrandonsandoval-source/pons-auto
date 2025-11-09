"""Rate limiting middleware."""

from fastapi import Request, HTTPException
from typing import Dict, List
import time


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[float]] = {}
    
    async def check_rate_limit(self, request: Request):
        """Check if request is within rate limit."""
        if not request.client:
            return  # Skip if no client info
        
        client_ip = request.client.host
        if not client_ip:
            return  # Skip if no IP
            
        current_time = time.time()
        
        # Initialize or clean old requests
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Remove requests older than 1 minute
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < 60
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Add current request
        self.requests[client_ip].append(current_time)


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=100)
