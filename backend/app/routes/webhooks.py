"""Webhook management routes"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.webhook import WebhookStatus
from app.services.webhook import WebhookService
from app.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


class WebhookResponse:
    """Response model for webhook"""

    def __init__(self, webhook):
        self.id = str(webhook.id)
        self.name = webhook.name
        self.description = webhook.description
        self.url = webhook.url
        self.events = webhook.events.split(",")
        self.is_active = webhook.is_active
        self.max_retries = webhook.max_retries
        self.retry_delay_seconds = webhook.retry_delay_seconds
        self.created_at = webhook.created_at.isoformat()
        self.updated_at = webhook.updated_at.isoformat()
        self.last_triggered_at = webhook.last_triggered_at.isoformat() if webhook.last_triggered_at else None
        self.trigger_count = webhook.trigger_count

    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "url": self.url,
            "events": self.events,
            "is_active": self.is_active,
            "max_retries": self.max_retries,
            "retry_delay_seconds": self.retry_delay_seconds,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_triggered_at": self.last_triggered_at,
            "trigger_count": self.trigger_count,
        }


class WebhookDeliveryResponse:
    """Response model for webhook delivery"""

    def __init__(self, delivery):
        self.id = str(delivery.id)
        self.webhook_id = str(delivery.webhook_id)
        self.event = delivery.event.value
        self.status = delivery.status.value
        self.http_status_code = delivery.http_status_code
        self.error_message = delivery.error_message
        self.attempt_count = delivery.attempt_count
        self.created_at = delivery.created_at.isoformat()
        self.next_retry_at = delivery.next_retry_at.isoformat() if delivery.next_retry_at else None

    def dict(self):
        return {
            "id": self.id,
            "webhook_id": self.webhook_id,
            "event": self.event,
            "status": self.status,
            "http_status_code": self.http_status_code,
            "error_message": self.error_message,
            "attempt_count": self.attempt_count,
            "created_at": self.created_at,
            "next_retry_at": self.next_retry_at,
        }


@router.post("")
async def create_webhook(
    name: str,
    url: str,
    events: list[str],
    description: Optional[str] = None,
    secret: Optional[str] = None,
    max_retries: int = 3,
    retry_delay_seconds: int = 60,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Create a new webhook.
    
    Args:
        name: Webhook name
        url: Webhook URL
        events: List of events to subscribe to
        description: Optional description
        secret: Optional secret for HMAC signature
        max_retries: Maximum number of retries
        retry_delay_seconds: Delay between retries in seconds
        
    Returns:
        dict: Created webhook
    """
    try:
        webhook = WebhookService.create_webhook(
            db,
            current_user.id,
            name,
            url,
            events,
            description,
            secret,
            max_retries,
            retry_delay_seconds,
        )

        return {
            "status": "success",
            "data": WebhookResponse(webhook).dict(),
        }
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("")
async def list_webhooks(
    page: int = 1,
    page_size: int = 10,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    List webhooks for the current user.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        is_active: Filter by active status
        
    Returns:
        dict: List of webhooks with pagination info
    """
    try:
        webhooks, total = WebhookService.get_webhooks(
            db,
            current_user.id,
            page,
            page_size,
            is_active,
        )

        return {
            "status": "success",
            "data": [WebhookResponse(webhook).dict() for webhook in webhooks],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "pages": (total + page_size - 1) // page_size,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{webhook_id}")
async def get_webhook(
    webhook_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Get a specific webhook.
    
    Args:
        webhook_id: Webhook ID
        
    Returns:
        dict: Webhook details
    """
    try:
        webhook = WebhookService.get_webhook(db, current_user.id, webhook_id)
        return {
            "status": "success",
            "data": WebhookResponse(webhook).dict(),
        }
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{webhook_id}")
async def update_webhook(
    webhook_id: UUID,
    name: Optional[str] = None,
    url: Optional[str] = None,
    events: Optional[list[str]] = None,
    description: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Update a webhook.
    
    Args:
        webhook_id: Webhook ID
        name: New name
        url: New URL
        events: New events list
        description: New description
        is_active: New active status
        
    Returns:
        dict: Updated webhook
    """
    try:
        webhook = WebhookService.update_webhook(
            db,
            current_user.id,
            webhook_id,
            name,
            url,
            events,
            description,
            is_active,
        )

        return {
            "status": "success",
            "data": WebhookResponse(webhook).dict(),
        }
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Delete a webhook.
    
    Args:
        webhook_id: Webhook ID
        
    Returns:
        dict: Success message
    """
    try:
        WebhookService.delete_webhook(db, current_user.id, webhook_id)
        return {
            "status": "success",
            "message": "Webhook deleted successfully",
        }
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{webhook_id}/deliveries")
async def get_webhook_deliveries(
    webhook_id: UUID,
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Get webhook delivery history.
    
    Args:
        webhook_id: Webhook ID
        page: Page number (1-indexed)
        page_size: Number of items per page
        status: Filter by delivery status
        
    Returns:
        dict: List of deliveries with pagination info
    """
    try:
        # Verify webhook belongs to user
        WebhookService.get_webhook(db, current_user.id, webhook_id)

        # Parse status if provided
        delivery_status = None
        if status:
            try:
                delivery_status = WebhookStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status}",
                )

        deliveries, total = WebhookService.get_deliveries(
            db,
            webhook_id,
            page,
            page_size,
            delivery_status,
        )

        return {
            "status": "success",
            "data": [WebhookDeliveryResponse(delivery).dict() for delivery in deliveries],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "pages": (total + page_size - 1) // page_size,
            },
        }
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
