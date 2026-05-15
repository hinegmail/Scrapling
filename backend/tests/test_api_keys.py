"""Tests for API key management"""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from app.services.api_key import APIKeyService
from app.exceptions import NotFoundError, ValidationError


class TestAPIKeyService:
    """Test API key service"""

    def test_generate_api_key(self):
        """Test API key generation"""
        key1 = APIKeyService.generate_api_key()
        key2 = APIKeyService.generate_api_key()
        
        assert len(key1) > 0
        assert len(key2) > 0
        assert key1 != key2

    def test_hash_api_key(self):
        """Test API key hashing"""
        key = APIKeyService.generate_api_key()
        hash1 = APIKeyService.hash_api_key(key)
        hash2 = APIKeyService.hash_api_key(key)
        
        assert hash1 == hash2
        assert hash1 != key

    def test_create_api_key(self, db_session, test_user):
        """Test creating an API key"""
        api_key, plain_key = APIKeyService.create_api_key(
            db_session,
            test_user.id,
            "Test Key",
            "Test description",
            expires_in_days=30,
        )
        
        assert api_key.name == "Test Key"
        assert api_key.description == "Test description"
        assert api_key.user_id == test_user.id
        assert api_key.is_active is True
        assert api_key.expires_at is not None
        assert len(plain_key) > 0

    def test_create_api_key_without_name(self, db_session, test_user):
        """Test creating an API key without name raises error"""
        with pytest.raises(ValidationError):
            APIKeyService.create_api_key(db_session, test_user.id, "")

    def test_verify_api_key(self, db_session, test_user):
        """Test verifying an API key"""
        api_key, plain_key = APIKeyService.create_api_key(
            db_session,
            test_user.id,
            "Test Key",
        )
        
        verified_key = APIKeyService.verify_api_key(db_session, plain_key)
        assert verified_key is not None
        assert verified_key.id == api_key.id
        assert verified_key.usage_count == 1

    def test_verify_invalid_api_key(self, db_session):
        """Test verifying an invalid API key"""
        verified_key = APIKeyService.verify_api_key(db_session, "invalid_key")
        assert verified_key is None

    def test_verify_expired_api_key(self, db_session, test_user):
        """Test verifying an expired API key"""
        api_key, plain_key = APIKeyService.create_api_key(
            db_session,
            test_user.id,
            "Test Key",
            expires_in_days=-1,  # Already expired
        )
        
        verified_key = APIKeyService.verify_api_key(db_session, plain_key)
        assert verified_key is None

    def test_verify_inactive_api_key(self, db_session, test_user):
        """Test verifying an inactive API key"""
        api_key, plain_key = APIKeyService.create_api_key(
            db_session,
            test_user.id,
            "Test Key",
        )
        
        # Deactivate the key
        APIKeyService.update_api_key(
            db_session,
            test_user.id,
            api_key.id,
            is_active=False,
        )
        
        verified_key = APIKeyService.verify_api_key(db_session, plain_key)
        assert verified_key is None

    def test_get_api_key(self, db_session, test_user):
        """Test getting an API key"""
        api_key, _ = APIKeyService.create_api_key(
            db_session,
            test_user.id,
            "Test Key",
        )
        
        retrieved_key = APIKeyService.get_api_key(db_session, test_user.id, api_key.id)
        assert retrieved_key.id == api_key.id
        assert retrieved_key.name == "Test Key"

    def test_get_nonexistent_api_key(self, db_session, test_user):
        """Test getting a nonexistent API key"""
        with pytest.raises(NotFoundError):
            APIKeyService.get_api_key(db_session, test_user.id, uuid4())

    def test_get_api_keys(self, db_session, test_user):
        """Test listing API keys"""
        # Create multiple keys
        for i in range(5):
            APIKeyService.create_api_key(
                db_session,
                test_user.id,
                f"Test Key {i}",
            )
        
        keys, total = APIKeyService.get_api_keys(db_session, test_user.id, page=1, page_size=10)
        assert len(keys) == 5
        assert total == 5

    def test_get_api_keys_pagination(self, db_session, test_user):
        """Test API key pagination"""
        # Create 25 keys
        for i in range(25):
            APIKeyService.create_api_key(
                db_session,
                test_user.id,
                f"Test Key {i}",
            )
        
        # Get first page
        keys_page1, total = APIKeyService.get_api_keys(
            db_session,
            test_user.id,
            page=1,
            page_size=10,
        )
        assert len(keys_page1) == 10
        assert total == 25
        
        # Get second page
        keys_page2, _ = APIKeyService.get_api_keys(
            db_session,
            test_user.id,
            page=2,
            page_size=10,
        )
        assert len(keys_page2) == 10
        assert keys_page1[0].id != keys_page2[0].id

    def test_get_api_keys_filter_active(self, db_session, test_user):
        """Test filtering API keys by active status"""
        # Create active key
        active_key, _ = APIKeyService.create_api_key(
            db_session,
            test_user.id,
            "Active Key",
        )
        
        # Create inactive key
        inactive_key, _ = APIKeyService.create_api_key(
            db_session,
            test_user.id,
            "Inactive Key",
        )
        APIKeyService.update_api_key(
            db_session,
            test_user.id,
            inactive_key.id,
            is_active=False,
        )
        
        # Get only active keys
        active_keys, total = APIKeyService.get_api_keys(
            db_session,
            test_user.id,
            is_active=True,
        )
        assert len(active_keys) == 1
        assert active_keys[0].id == active_key.id

    def test_update_api_key(self, db_session, test_user):
        """Test updating an API key"""
        api_key, _ = APIKeyService.create_api_key(
            db_session,
            test_user.id,
            "Original Name",
        )
        
        updated_key = APIKeyService.update_api_key(
            db_session,
            test_user.id,
            api_key.id,
            name="Updated Name",
            description="Updated description",
        )
        
        assert updated_key.name == "Updated Name"
        assert updated_key.description == "Updated description"

    def test_delete_api_key(self, db_session, test_user):
        """Test deleting an API key"""
        api_key, _ = APIKeyService.create_api_key(
            db_session,
            test_user.id,
            "Test Key",
        )
        
        APIKeyService.delete_api_key(db_session, test_user.id, api_key.id)
        
        with pytest.raises(NotFoundError):
            APIKeyService.get_api_key(db_session, test_user.id, api_key.id)

    def test_revoke_api_key(self, db_session, test_user):
        """Test revoking an API key"""
        api_key, plain_key = APIKeyService.create_api_key(
            db_session,
            test_user.id,
            "Test Key",
        )
        
        revoked_key = APIKeyService.revoke_api_key(db_session, test_user.id, api_key.id)
        assert revoked_key.is_active is False
        
        # Verify the key can no longer be used
        verified_key = APIKeyService.verify_api_key(db_session, plain_key)
        assert verified_key is None
