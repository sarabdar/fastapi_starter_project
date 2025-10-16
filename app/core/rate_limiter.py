"""
Rate Limiter for API endpoints
Prevents brute force attacks and API abuse
"""

from fastapi import HTTPException, Request, status
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict
import asyncio

from app.core.config import settings

class RateLimiter:
    """
    In-memory rate limiter for API endpoints.
    For production, consider using Redis for distributed rate limiting.
    """
    
    def __init__(self):
        # Store: {ip_address: [(timestamp, endpoint), ...]}
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = asyncio.Lock()
    
    async def check_rate_limit(
        self,
        request: Request,
        max_requests: int = settings.MAX_REQUEST_LIMIT_FOR_AUTH,
        window_seconds: int = settings.WINDOW_FOR_GENERAL_API
    ) -> None:
        """
        Check if the request exceeds rate limit.
        
        Args:
            request: FastAPI request object
            max_requests: Maximum number of requests allowed
            window_seconds: Time window in seconds
            
        Raises:
            HTTPException: If rate limit is exceeded
        """
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        endpoint = request.url.path
        current_time = datetime.now()
        
        async with self.lock:
            # Clean old requests outside the window
            cutoff_time = current_time - timedelta(seconds=window_seconds)
            self.requests[client_ip] = [
                (ts, ep) for ts, ep in self.requests[client_ip]
                if ts > cutoff_time
            ]
            
            # Count requests to this endpoint
            endpoint_requests = [
                ts for ts, ep in self.requests[client_ip]
                if ep == endpoint
            ]
            
            if len(endpoint_requests) >= max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds."
                )
            
            # Add current request
            self.requests[client_ip].append((current_time, endpoint))
    
    async def cleanup_old_entries(self, max_age_hours: int = 24):
        """Periodic cleanup of old entries to prevent memory bloat"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        async with self.lock:
            for ip in list(self.requests.keys()):
                self.requests[ip] = [
                    (ts, ep) for ts, ep in self.requests[ip]
                    if ts > cutoff_time
                ]
                if not self.requests[ip]:
                    del self.requests[ip]


# Global rate limiter instance
rate_limiter = RateLimiter()


# Dependency for FastAPI endpoints
async def rate_limit_auth(request: Request):
    """
    Rate limit for authentication endpoints.
    Stricter limits to prevent brute force attacks.
    """
    await rate_limiter.check_rate_limit(
        request,
        max_requests=settings.MAX_REQUEST_LIMIT_FOR_AUTH,  
        window_seconds=settings.WINDOW_FOR_AUTH_API  
    )


async def rate_limit_api(request: Request):
    """
    Rate limit for general API endpoints.
    More lenient limits for regular operations.
    """
    await rate_limiter.check_rate_limit(
        request,
        max_requests=settings.MAX_REQUEST_LIMIT_FOR_GENERAL_API,  
        window_seconds=settings.WINDOW_FOR_GENERAL_API  
    )
