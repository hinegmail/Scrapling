"""Global error handling middleware"""

import logging
from datetime import datetime, timezone
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.exceptions import AppException

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Global error handler middleware"""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except AppException as exc:
            logger.warning(
                f"Application exception: {exc.error_code} - {exc.message}",
                extra={
                    "error_code": exc.error_code,
                    "status_code": exc.status_code,
                    "path": request.url.path,
                    "method": request.method,
                },
            )

            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error_code": exc.error_code,
                    "message": exc.message,
                    "status_code": exc.status_code,
                    "details": exc.details,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
        except Exception as exc:
            logger.error(
                f"Unexpected error: {str(exc)}",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                },
                exc_info=True,
            )

            return JSONResponse(
                status_code=500,
                content={
                    "error_code": "INTERNAL_ERROR",
                    "message": "Internal server error",
                    "status_code": 500,
                    "details": {},
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
