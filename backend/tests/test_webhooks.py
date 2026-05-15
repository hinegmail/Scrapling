"""Tests for webhook management"""

import pytest
from uuid import uuid4

from app.services.webhook import WebhookService
from app.models.webhook import WebhookEvent, WebhookStatus
from app.exceptions import NotFoundError, ValidationError


class TestWebhookService:
    """Test webhook service"""

    def test_create_webhook(self, db_session, test_user):
        """Test creating a webhook"""
        webhook = WebhookService.create_webhook(
            db_session,
            test_user.id,
            "Test Webhook",
            "https://example.com/webhook",
            ["task.completed", "task.failed"],
            "Test description",
            "secret123",
        )
        
        assert webhook.name == "Test Webhook"
        assert webhook.url == "https://example.com/webhook"
        assert webhook.user_id == test_user.id
        assert webhook.is_active is True
        assert "task.completed" in webhook.events
        assert "task.failed" in webhook.events

    def test_create_webhook_without_name(self, db_session, test_user):
        """Test creating a webhook without name raises error"""
        with pytest.raises(ValidationError):
            WebhookService.create_webhook(
                db_session,
                test_user.id,
                "",
                "https://example.com/webhook",
                ["task.completed"],
            )

    def test_create_webhook_invalid_url(self, db_session, test_user):
        """Test creating a webhook with invalid URL raises error"""
        with pytest.raises(ValidationError):
            WebhookService.create_webhook(
                db_session,
                test_user.id,
                "Test Webhook",
                "invalid-url",
                ["task.completed"],
            )

    def test_create_webhook_invalid_event(self, db_session, test_user):
        """Test creating a webhook with invalid event raises error"""
        with pytest.raises(ValidationError):
            WebhookService.create_webhook(
                db_session,
                test_user.id,
                "Test Webhook",
                "https://example.com/webhook",
                ["invalid.event"],
            )

    def test_get_webhook(self, db_session, test_user):
        """Test getting a webhook"""
        webhook = WebhookService.create_webhook(
            db_session,
            test_user.id,
            "Test Webhook",
            "https://example.com/webhook",
            ["task.completed"],
        )
        
        retrieved_webhook = WebhookService.get_webhook(
            db_session,
            test_user.id,
            webhook.id,
        )
        assert retrieved_webhook.id == webhook.id
        assert retrieved_webhook.name == "Test Webhook"

    def test_get_nonexistent_webhook(self, db_session, test_user):
        """Test getting a nonexistent webhook"""
        with pytest.raises(NotFoundError):
            WebhookService.get_webhook(db_session, test_user.id, uuid4())

    def test_get_webhooks(self, db_session, test_user):
        """Test listing webhooks"""
        # Create multiple webhooks
        for i in range(5):
            WebhookService.create_webhook(
                db_session,
                test_user.id,
                f"Test Webhook {i}",
                f"https://example.com/webhook{i}",
                ["task.completed"],
            )
        
        webhooks, total = WebhookService.get_webhooks(
            db_session,
            test_user.id,
            page=1,
            page_size=10,
        )
        assert len(webhooks) == 5
        assert total == 5

    def test_get_webhooks_pagination(self, db_session, test_user):
        """Test webhook pagination"""
        # Create 25 webhooks
        for i in range(25):
            WebhookService.create_webhook(
                db_session,
                test_user.id,
                f"Test Webhook {i}",
                f"https://example.com/webhook{i}",
                ["task.completed"],
            )
        
        # Get first page
        webhooks_page1, total = WebhookService.get_webhooks(
            db_session,
            test_user.id,
            page=1,
            page_size=10,
        )
        assert len(webhooks_page1) == 10
        assert total == 25
        
        # Get second page
        webhooks_page2, _ = WebhookService.get_webhooks(
            db_session,
            test_user.id,
            page=2,
            page_size=10,
        )
        assert len(webhooks_page2) == 10

    def test_get_webhooks_filter_active(self, db_session, test_user):
        """Test filtering webhooks by active status"""
        # Create active webhook
        active_webhook = WebhookService.create_webhook(
            db_session,
            test_user.id,
            "Active Webhook",
            "https://example.com/webhook1",
            ["task.completed"],
        )
        
        # Create inactive webhook
        inactive_webhook = WebhookService.create_webhook(
            db_session,
            test_user.id,
            "Inactive Webhook",
            "https://example.com/webhook2",
            ["task.completed"],
        )
        WebhookService.update_webhook(
            db_session,
            test_user.id,
            inactive_webhook.id,
            is_active=False,
        )
        
        # Get only active webhooks
        active_webhooks, total = WebhookService.get_webhooks(
            db_session,
            test_user.id,
            is_active=True,
        )
        assert len(active_webhooks) == 1
        assert active_webhooks[0].id == active_webhook.id

    def test_update_webhook(self, db_session, test_user):
        """Test updating a webhook"""
        webhook = WebhookService.create_webhook(
            db_session,
            test_user.id,
            "Original Name",
            "https://example.com/webhook",
            ["task.completed"],
        )
        
        updated_webhook = WebhookService.update_webhook(
            db_session,
            test_user.id,
            webhook.id,
            name="Updated Name",
            url="https://example.com/webhook-updated",
            events=["task.failed"],
        )
        
        assert updated_webhook.name == "Updated Name"
        assert updated_webhook.url == "https://example.com/webhook-updated"
        assert "task.failed" in updated_webhook.events

    def test_update_webhook_invalid_url(self, db_session, test_user):
        """Test updating a webhook with invalid URL raises error"""
        webhook = WebhookService.create_webhook(
            db_session,
            test_user.id,
            "Test Webhook",
            "https://example.com/webhook",
            ["task.completed"],
        )
        
        with pytest.raises(ValidationError):
            WebhookService.update_webhook(
                db_session,
                test_user.id,
                webhook.id,
                url="invalid-url",
            )

    def test_delete_webhook(self, db_session, test_user):
        """Test deleting a webhook"""
        webhook = WebhookService.create_webhook(
            db_session,
            test_user.id,
            "Test Webhook",
            "https://example.com/webhook",
            ["task.completed"],
        )
        
        WebhookService.delete_webhook(db_session, test_user.id, webhook.id)
        
        with pytest.raises(NotFoundError):
            WebhookService.get_webhook(db_session, test_user.id, webhook.id)

    def test_create_delivery(self, db_session, test_user):
        """Test creating a webhook delivery"""
        webhook = WebhookService.create_webhook(
            db_session,
            test_user.id,
            "Test Webhook",
            "https://example.com/webhook",
            ["task.completed"],
        )
        
        event_data = {
            "task_id": "123",
            "status": "completed",
            "result_count": 100,
        }
        
        delivery = WebhookService.create_delivery(
            db_session,
            webhook.id,
            WebhookEvent.TASK_COMPLETED,
            event_data,
        )
        
        assert delivery.webhook_id == webhook.id
        assert delivery.event == WebhookEvent.TASK_COMPLETED
        assert delivery.event_data == event_data
        assert delivery.status == WebhookStatus.PENDING

    def test_generate_signature(self):
        """Test HMAC signature generation"""
        payload = '{"test": "data"}'
        secret = "secret123"
        
        signature1 = WebhookService.generate_signature(payload, secret)
        signature2 = WebhookService.generate_signature(payload, secret)
        
        assert signature1 == signature2
        assert len(signature1) > 0

    def test_get_deliveries(self, db_session, test_user):
        """Test getting webhook deliveries"""
        webhook = WebhookService.create_webhook(
            db_session,
            test_user.id,
            "Test Webhook",
            "https://example.com/webhook",
            ["task.completed"],
        )
        
        # Create multiple deliveries
        for i in range(5):
            WebhookService.create_delivery(
                db_session,
                webhook.id,
                WebhookEvent.TASK_COMPLETED,
                {"task_id": str(i)},
            )
        
        deliveries, total = WebhookService.get_deliveries(
            db_session,
            webhook.id,
            page=1,
            page_size=10,
        )
        assert len(deliveries) == 5
        assert total == 5

    def test_get_deliveries_filter_status(self, db_session, test_user):
        """Test filtering deliveries by status"""
        webhook = WebhookService.create_webhook(
            db_session,
            test_user.id,
            "Test Webhook",
            "https://example.com/webhook",
            ["task.completed"],
        )
        
        # Create pending delivery
        pending_delivery = WebhookService.create_delivery(
            db_session,
            webhook.id,
            WebhookEvent.TASK_COMPLETED,
            {"task_id": "1"},
        )
        
        # Create failed delivery
        failed_delivery = WebhookService.create_delivery(
            db_session,
            webhook.id,
            WebhookEvent.TASK_COMPLETED,
            {"task_id": "2"},
        )
        failed_delivery.status = WebhookStatus.FAILED
        db_session.commit()
        
        # Get only pending deliveries
        pending_deliveries, total = WebhookService.get_deliveries(
            db_session,
            webhook.id,
            status=WebhookStatus.PENDING,
        )
        assert len(pending_deliveries) == 1
        assert pending_deliveries[0].id == pending_delivery.id
