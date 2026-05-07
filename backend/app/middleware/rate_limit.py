"""Rate limiting middleware"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Tuple
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import settings

logger = logging.getLogger(__name__)

# In-memory rate limit store (in production, use Redis)
rate_limit_store: Dict[str, list] = {}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""

    async def dispatch(self, request: Request, call_next):
        if not settings.rate_limit_enabled:
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Check rate limit
        if not self._check_rate_limit(client_ip):
            logger.warning(
                f"Rate limit exceeded for {client_ip}",
                extra={"client_ip": client_ip},
            )

            return JSONResponse(
                status_code=429,
                content={
                    "error_code": "RATE_LIMIT",
                    "message": "Rate limit exceeded",
                    "status_code": 429,
                    "details": {},
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

        return await call_next(request)

    @staticmethod
    def _check_rate_limit(client_ip: str) -> bool:
        """Check if client is within rate limit"""
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=settings.rate_limit_period)

        # Initialize or get request times for this client
        if client_ip not in rate_limit_store:
            rate_limit_store[client_ip] = []

        # Remove old requests outside the window
        rate_limit_store[client_ip] = [
            req_time for req_time in rate_limit_store[client_ip]
            if req_time > window_start
        ]

        # Check if limit exceeded
        if len(rate_limit_store[client_ip]) >= settings.rate_limit_requests:
            return False

        # Add current request
        rate_limit_store[client_ip].append(now)
        return True
