"""API Key authentication middleware"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.api_key import APIKeyService
from app.models.user import User

logger = logging.getLogger(__name__)


async def get_api_key_user(
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Optional[dict]:
    """
    Authenticate user via API key.
    
    Args:
        x_api_key: API key from X-API-Key header
        db: Database session
        
    Returns:
        dict: User information if authenticated, None otherwise
        
    Raises:
        HTTPException: If API key is invalid or expired
    """
    if not x_api_key:
        return None

    try:
        api_key = APIKeyService.verify_api_key(db, x_api_key)
        
        if not api_key:
            logger.warning("Invalid or expired API key attempted")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired API key",
            )

        # Get user
        user = db.query(User).filter(User.id == api_key.user_id).first()
        if not user or not user.is_active:
            logger.warning(f"User not found or inactive for API key: {api_key.id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "api_key_id": api_key.id,
            "permissions": api_key.permissions.split(","),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in API key authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )


async def require_api_key_permission(
    required_permission: str,
    user: dict = Depends(get_api_key_user),
) -> dict:
    """
    Verify that the API key has the required permission.
    
    Args:
        required_permission: Required permission (e.g., "read", "write")
        user: User information from API key authentication
        
    Returns:
        dict: User information if authorized
        
    Raises:
        HTTPException: If user lacks required permission
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
        )

    if required_permission not in user.get("permissions", []):
        logger.warning(
            f"API key {user.get('api_key_id')} lacks permission: {required_permission}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"API key lacks required permission: {required_permission}",
        )

    return user
