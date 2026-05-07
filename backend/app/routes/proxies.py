"""Proxy management routes"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.middleware.auth import get_current_user
from app.models.proxy import ProxyProtocol
from app.services.proxy import ProxyService
from app.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/config/proxies", tags=["proxies"])


class ProxyBase(BaseModel):
    """Base proxy schema"""
    name: str = Field(..., min_length=1, max_length=255)
    protocol: ProxyProtocol = Field(default=ProxyProtocol.HTTP)
    host: str = Field(..., min_length=1, max_length=255)
    port: int = Field(..., ge=1, le=65535)
    username: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, max_length=255)
    is_active: bool = Field(default=True)


class ProxyCreate(ProxyBase):
    """Proxy creation schema"""
    pass


class ProxyUpdate(BaseModel):
    """Proxy update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    protocol: Optional[ProxyProtocol] = Field(None)
    host: Optional[str] = Field(None, min_length=1, max_length=255)
    port: Optional[int] = Field(None, ge=1, le=65535)
    username: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = Field(None)


class ProxyResponse(ProxyBase):
    """Proxy response schema"""
    id: UUID
    user_id: UUID
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ProxyListResponse(BaseModel):
    """Proxy list response schema"""
    items: list[ProxyResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


@router.post("", response_model=ProxyResponse, status_code=status.HTTP_201_CREATED)
async def create_proxy(
    proxy_data: ProxyCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new proxy.
    
    - **name**: Proxy name
    - **protocol**: http, https, or socks5
    - **host**: Proxy host (IP or hostname)
    - **port**: Proxy port (1-65535)
    - **username**: Optional proxy username
    - **password**: Optional proxy password
    """
    try:
        proxy = ProxyService.create_proxy(db, current_user["id"], proxy_data.dict())
        logger.info(f"Proxy created: {proxy.id}")
        return proxy
    except ValidationError as e:
        logger.warning(f"Validation error creating proxy: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating proxy: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create proxy")


@router.get("", response_model=ProxyListResponse)
async def list_proxies(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get proxies with pagination and filtering.
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    - **is_active**: Filter by active status (optional)
    """
    try:
        proxies, total = ProxyService.get_proxies(
            db, current_user["id"], page, page_size, is_active
        )
        total_pages = (total + page_size - 1) // page_size
        
        return ProxyListResponse(
            items=proxies,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    except Exception as e:
        logger.error(f"Error listing proxies: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list proxies")


@router.get("/{proxy_id}", response_model=ProxyResponse)
async def get_proxy(
    proxy_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific proxy by ID"""
    try:
        proxy = ProxyService.get_proxy(db, current_user["id"], proxy_id)
        return proxy
    except NotFoundError as e:
        logger.warning(f"Proxy not found: {proxy_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting proxy: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get proxy")


@router.put("/{proxy_id}", response_model=ProxyResponse)
async def update_proxy(
    proxy_id: UUID,
    proxy_data: ProxyUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a proxy"""
    try:
        proxy = ProxyService.update_proxy(db, current_user["id"], proxy_id, proxy_data.dict(exclude_unset=True))
        logger.info(f"Proxy updated: {proxy_id}")
        return proxy
    except NotFoundError as e:
        logger.warning(f"Proxy not found: {proxy_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error updating proxy: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating proxy: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update proxy")


@router.delete("/{proxy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_proxy(
    proxy_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a proxy"""
    try:
        ProxyService.delete_proxy(db, current_user["id"], proxy_id)
        logger.info(f"Proxy deleted: {proxy_id}")
        return None
    except NotFoundError as e:
        logger.warning(f"Proxy not found: {proxy_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting proxy: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete proxy")
