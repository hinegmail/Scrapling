"""Dashboard routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.dashboard import DashboardService

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/statistics")
async def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Get dashboard statistics.
    
    Returns:
        dict: Statistics including total tasks, monthly tasks, success rate, total data
    """
    try:
        stats = DashboardService.get_statistics(db, current_user.id)
        return {
            "status": "success",
            "data": stats,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends")
async def get_trends(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Get task execution trends for the last N days.
    
    Args:
        days: Number of days to retrieve (default 7, max 30)
        
    Returns:
        dict: Daily trend data with task counts and success rates
    """
    if days < 1 or days > 30:
        raise HTTPException(status_code=400, detail="Days must be between 1 and 30")

    try:
        trends = DashboardService.get_trends(db, current_user.id, days)
        return {
            "status": "success",
            "data": trends,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fetcher-stats")
async def get_fetcher_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Get fetcher usage statistics.
    
    Returns:
        dict: Fetcher type usage statistics
    """
    try:
        stats = DashboardService.get_fetcher_stats(db, current_user.id)
        return {
            "status": "success",
            "data": stats,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources")
async def get_resources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Get system resource usage statistics.
    
    Returns:
        dict: Resource usage statistics (CPU, memory, disk, network)
    """
    try:
        resources = DashboardService.get_resource_stats(db, current_user.id)
        return {
            "status": "success",
            "data": resources,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
