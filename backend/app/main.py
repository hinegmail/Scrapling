"""FastAPI application entry point"""

import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import settings
from app.logging_config import setup_logging
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.routes import auth, tasks, selectors, proxies, task_execution, websocket, api_keys, webhooks
from app.services.dashboard import DashboardService
from app.db.database import get_db
from app.openapi import custom_openapi
from sqlalchemy.orm import Session

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

# Add custom OpenAPI schema
app.openapi = lambda: custom_openapi(app)

# Add middleware (order matters - add in reverse order of execution)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlerMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(selectors.router)
app.include_router(proxies.router)
app.include_router(task_execution.router)
app.include_router(websocket.router)
app.include_router(api_keys.router)
app.include_router(webhooks.router)


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint with system resource monitoring.
    
    Returns:
        dict: Health status including system resources and service connectivity
    """
    try:
        logger.info("Health check requested")
        
        # Get resource stats
        resources = DashboardService.get_resource_stats(db, None)
        
        # Check database connectivity
        db.execute("SELECT 1")
        db_status = "healthy"
        
        return {
            "status": "healthy",
            "version": settings.app_version,
            "services": {
                "database": db_status,
                "redis": "healthy",  # TODO: Add actual Redis health check
                "celery": "healthy",  # TODO: Add actual Celery health check
            },
            "resources": resources,
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "version": settings.app_version,
            "error": str(e),
        }


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": f"Welcome to {settings.app_name}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
