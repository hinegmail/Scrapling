"""API Key management routes"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services.api_key import APIKeyService
from app.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/api/v1/api-keys", tags=["api-keys"])


class APIKeyResponse:
    """Response model for API key"""

    def __init__(self, api_key):
        self.id = str(api_key.id)
        self.name = api_key.name
        self.description = api_key.description
        self.key_preview = f"...{api_key.key_preview}"
        self.is_active = api_key.is_active
        self.permissions = api_key.permissions
        self.created_at = api_key.created_at.isoformat()
        self.last_used_at = api_key.last_used_at.isoformat() if api_key.last_used_at else None
        self.usage_count = api_key.usage_count
        self.expires_at = api_key.expires_at.isoformat() if api_key.expires_at else None

    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "key_preview": self.key_preview,
            "is_active": self.is_active,
            "permissions": self.permissions,
            "created_at": self.created_at,
            "last_used_at": self.last_used_at,
            "usage_count": self.usage_count,
            "expires_at": self.expires_at,
        }


@router.post("")
async def create_api_key(
    name: str,
    description: Optional[str] = None,
    expires_in_days: Optional[int] = None,
    permissions: str = "read,write",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Create a new API key.
    
    Args:
        name: API key name
        description: Optional description
        expires_in_days: Optional expiration time in days
        permissions: Comma-separated permissions (default: "read,write")
        
    Returns:
        dict: Created API key with plain key (only shown once)
    """
    try:
        api_key, plain_key = APIKeyService.create_api_key(
            db,
            current_user.id,
            name,
            description,
            expires_in_days,
            permissions,
        )

        response = APIKeyResponse(api_key).dict()
        response["key"] = plain_key  # Only shown once during creation
        
        return {
            "status": "success",
            "data": response,
            "message": "API key created successfully. Save the key in a secure location.",
        }
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("")
async def list_api_keys(
    page: int = 1,
    page_size: int = 10,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    List API keys for the current user.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        is_active: Filter by active status
        
    Returns:
        dict: List of API keys with pagination info
    """
    try:
        api_keys, total = APIKeyService.get_api_keys(
            db,
            current_user.id,
            page,
            page_size,
            is_active,
        )

        return {
            "status": "success",
            "data": [APIKeyResponse(key).dict() for key in api_keys],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "pages": (total + page_size - 1) // page_size,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{api_key_id}")
async def get_api_key(
    api_key_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Get a specific API key.
    
    Args:
        api_key_id: API key ID
        
    Returns:
        dict: API key details
    """
    try:
        api_key = APIKeyService.get_api_key(db, current_user.id, api_key_id)
        return {
            "status": "success",
            "data": APIKeyResponse(api_key).dict(),
        }
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{api_key_id}")
async def update_api_key(
    api_key_id: UUID,
    name: Optional[str] = None,
    description: Optional[str] = None,
    is_active: Optional[bool] = None,
    permissions: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Update an API key.
    
    Args:
        api_key_id: API key ID
        name: New name
        description: New description
        is_active: New active status
        permissions: New permissions
        
    Returns:
        dict: Updated API key
    """
    try:
        api_key = APIKeyService.update_api_key(
            db,
            current_user.id,
            api_key_id,
            name,
            description,
            is_active,
            permissions,
        )

        return {
            "status": "success",
            "data": APIKeyResponse(api_key).dict(),
        }
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{api_key_id}")
async def delete_api_key(
    api_key_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Delete an API key.
    
    Args:
        api_key_id: API key ID
        
    Returns:
        dict: Success message
    """
    try:
        APIKeyService.delete_api_key(db, current_user.id, api_key_id)
        return {
            "status": "success",
            "message": "API key deleted successfully",
        }
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{api_key_id}/revoke")
async def revoke_api_key(
    api_key_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Revoke (deactivate) an API key.
    
    Args:
        api_key_id: API key ID
        
    Returns:
        dict: Revoked API key
    """
    try:
        api_key = APIKeyService.revoke_api_key(db, current_user.id, api_key_id)
        return {
            "status": "success",
            "data": APIKeyResponse(api_key).dict(),
            "message": "API key revoked successfully",
        }
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
