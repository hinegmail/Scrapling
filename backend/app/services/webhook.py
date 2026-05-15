"""Webhook service"""

import asyncio
import hmac
import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import aiohttp
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.webhook import Webhook, WebhookDelivery, WebhookEvent, WebhookStatus
from app.exceptions import NotFoundError, ValidationError


class WebhookService:
    """Service for webhook management and delivery"""

    @staticmethod
    def create_webhook(
        db: Session,
        user_id: UUID,
        name: str,
        url: str,
        events: list[str],
        description: Optional[str] = None,
        secret: Optional[str] = None,
        max_retries: int = 3,
        retry_delay_seconds: int = 60,
    ) -> Webhook:
        """
        Create a new webhook.
        
        Args:
            db: Database session
            user_id: User ID
            name: Webhook name
            url: Webhook URL
            events: List of events to subscribe to
            description: Optional description
            secret: Optional secret for HMAC signature
            max_retries: Maximum number of retries
            retry_delay_seconds: Delay between retries in seconds
            
        Returns:
            Webhook: The created webhook
        """
        if not name or not url or not events:
            raise ValidationError("Name, URL, and events are required")

        if not url.startswith(("http://", "https://")):
            raise ValidationError("Invalid webhook URL")

        # Validate events
        valid_events = {e.value for e in WebhookEvent}
        for event in events:
            if event not in valid_events:
                raise ValidationError(f"Invalid event: {event}")

        webhook = Webhook(
            user_id=user_id,
            name=name,
            url=url,
            events=",".join(events),
            description=description,
            secret=secret,
            max_retries=max_retries,
            retry_delay_seconds=retry_delay_seconds,
        )

        db.add(webhook)
        db.commit()
        db.refresh(webhook)

        return webhook

    @staticmethod
    def get_webhook(db: Session, user_id: UUID, webhook_id: UUID) -> Webhook:
        """
        Get a webhook by ID.
        
        Args:
            db: Database session
            user_id: User ID
            webhook_id: Webhook ID
            
        Returns:
            Webhook: The webhook object
        """
        webhook = db.query(Webhook).filter(
            and_(Webhook.id == webhook_id, Webhook.user_id == user_id)
        ).first()

        if not webhook:
            raise NotFoundError("Webhook not found")

        return webhook

    @staticmethod
    def get_webhooks(
        db: Session,
        user_id: UUID,
        page: int = 1,
        page_size: int = 10,
        is_active: Optional[bool] = None,
    ) -> tuple[list[Webhook], int]:
        """
        Get webhooks for a user with pagination.
        
        Args:
            db: Database session
            user_id: User ID
            page: Page number (1-indexed)
            page_size: Number of items per page
            is_active: Filter by active status
            
        Returns:
            tuple: (List of webhooks, total count)
        """
        query = db.query(Webhook).filter(Webhook.user_id == user_id)

        if is_active is not None:
            query = query.filter(Webhook.is_active == is_active)

        total = query.count()

        offset = (page - 1) * page_size
        webhooks = query.offset(offset).limit(page_size).all()

        return webhooks, total

    @staticmethod
    def update_webhook(
        db: Session,
        user_id: UUID,
        webhook_id: UUID,
        name: Optional[str] = None,
        url: Optional[str] = None,
        events: Optional[list[str]] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Webhook:
        """
        Update a webhook.
        
        Args:
            db: Database session
            user_id: User ID
            webhook_id: Webhook ID
            name: New name
            url: New URL
            events: New events list
            description: New description
            is_active: New active status
            
        Returns:
            Webhook: The updated webhook
        """
        webhook = WebhookService.get_webhook(db, user_id, webhook_id)

        if name is not None:
            webhook.name = name
        if url is not None:
            if not url.startswith(("http://", "https://")):
                raise ValidationError("Invalid webhook URL")
            webhook.url = url
        if events is not None:
            valid_events = {e.value for e in WebhookEvent}
            for event in events:
                if event not in valid_events:
                    raise ValidationError(f"Invalid event: {event}")
            webhook.events = ",".join(events)
        if description is not None:
            webhook.description = description
        if is_active is not None:
            webhook.is_active = is_active

        webhook.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(webhook)

        return webhook

    @staticmethod
    def delete_webhook(db: Session, user_id: UUID, webhook_id: UUID) -> None:
        """
        Delete a webhook.
        
        Args:
            db: Database session
            user_id: User ID
            webhook_id: Webhook ID
        """
        webhook = WebhookService.get_webhook(db, user_id, webhook_id)
        db.delete(webhook)
        db.commit()

    @staticmethod
    def create_delivery(
        db: Session,
        webhook_id: UUID,
        event: WebhookEvent,
        event_data: dict,
    ) -> WebhookDelivery:
        """
        Create a webhook delivery record.
        
        Args:
            db: Database session
            webhook_id: Webhook ID
            event: Event type
            event_data: Event data
            
        Returns:
            WebhookDelivery: The created delivery record
        """
        delivery = WebhookDelivery(
            webhook_id=webhook_id,
            event=event,
            event_data=event_data,
            status=WebhookStatus.PENDING,
        )

        db.add(delivery)
        db.commit()
        db.refresh(delivery)

        return delivery

    @staticmethod
    def generate_signature(payload: str, secret: str) -> str:
        """
        Generate HMAC signature for webhook payload.
        
        Args:
            payload: JSON payload
            secret: Secret key
            
        Returns:
            str: HMAC signature
        """
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    async def deliver_webhook(
        db: Session,
        delivery_id: UUID,
        webhook: Webhook,
        event_data: dict,
    ) -> bool:
        """
        Deliver a webhook with retry logic.
        
        Args:
            db: Database session
            delivery_id: Delivery record ID
            webhook: Webhook object
            event_data: Event data
            
        Returns:
            bool: True if delivery succeeded, False otherwise
        """
        delivery = db.query(WebhookDelivery).filter(
            WebhookDelivery.id == delivery_id
        ).first()

        if not delivery:
            return False

        payload = json.dumps(event_data)
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Scrapling-Webhook/1.0",
        }

        # Add signature if secret is configured
        if webhook.secret:
            signature = WebhookService.generate_signature(payload, webhook.secret)
            headers["X-Webhook-Signature"] = f"sha256={signature}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook.url,
                    data=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    delivery.http_status_code = response.status
                    delivery.response_body = await response.text()

                    if response.status >= 200 and response.status < 300:
                        delivery.status = WebhookStatus.DELIVERED
                        webhook.last_triggered_at = datetime.now(timezone.utc)
                        webhook.trigger_count += 1
                        db.commit()
                        return True
                    else:
                        # Retry on non-2xx responses
                        if delivery.attempt_count < webhook.max_retries:
                            delivery.status = WebhookStatus.RETRYING
                            delivery.attempt_count += 1
                            delivery.next_retry_at = datetime.now(timezone.utc) + timedelta(
                                seconds=webhook.retry_delay_seconds
                            )
                        else:
                            delivery.status = WebhookStatus.FAILED
                            delivery.error_message = f"HTTP {response.status}: {delivery.response_body}"

                        db.commit()
                        return False

        except asyncio.TimeoutError:
            delivery.error_message = "Request timeout"
            if delivery.attempt_count < webhook.max_retries:
                delivery.status = WebhookStatus.RETRYING
                delivery.attempt_count += 1
                delivery.next_retry_at = datetime.now(timezone.utc) + timedelta(
                    seconds=webhook.retry_delay_seconds
                )
            else:
                delivery.status = WebhookStatus.FAILED

            db.commit()
            return False

        except Exception as e:
            delivery.error_message = str(e)
            if delivery.attempt_count < webhook.max_retries:
                delivery.status = WebhookStatus.RETRYING
                delivery.attempt_count += 1
                delivery.next_retry_at = datetime.now(timezone.utc) + timedelta(
                    seconds=webhook.retry_delay_seconds
                )
            else:
                delivery.status = WebhookStatus.FAILED

            db.commit()
            return False

    @staticmethod
    def get_deliveries(
        db: Session,
        webhook_id: UUID,
        page: int = 1,
        page_size: int = 10,
        status: Optional[WebhookStatus] = None,
    ) -> tuple[list[WebhookDelivery], int]:
        """
        Get webhook deliveries with pagination.
        
        Args:
            db: Database session
            webhook_id: Webhook ID
            page: Page number (1-indexed)
            page_size: Number of items per page
            status: Filter by delivery status
            
        Returns:
            tuple: (List of deliveries, total count)
        """
        query = db.query(WebhookDelivery).filter(WebhookDelivery.webhook_id == webhook_id)

        if status is not None:
            query = query.filter(WebhookDelivery.status == status)

        total = query.count()

        offset = (page - 1) * page_size
        deliveries = query.offset(offset).limit(page_size).order_by(
            WebhookDelivery.created_at.desc()
        ).all()

        return deliveries, total
