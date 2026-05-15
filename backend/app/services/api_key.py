"""API Key service"""

import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.api_key import APIKey
from app.exceptions import NotFoundError, ValidationError


class APIKeyService:
    """Service for API key management"""

    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a new API key.
        
        Returns:
            str: A 32-character random API key
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """
        Hash an API key using SHA-256.
        
        Args:
            api_key: The API key to hash
            
        Returns:
            str: The hashed API key
        """
        return hashlib.sha256(api_key.encode()).hexdigest()

    @staticmethod
    def create_api_key(
        db: Session,
        user_id: UUID,
        name: str,
        description: Optional[str] = None,
        expires_in_days: Optional[int] = None,
        permissions: str = "read,write",
    ) -> tuple[APIKey, str]:
        """
        Create a new API key for a user.
        
        Args:
            db: Database session
            user_id: User ID
            name: API key name
            description: Optional description
            expires_in_days: Optional expiration time in days
            permissions: Comma-separated permissions (default: "read,write")
            
        Returns:
            tuple: (APIKey object, plain API key string)
        """
        if not name:
            raise ValidationError("API key name is required")

        # Generate the API key
        plain_key = APIKeyService.generate_api_key()
        key_hash = APIKeyService.hash_api_key(plain_key)
        key_preview = plain_key[-4:]

        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        # Create the API key record
        api_key = APIKey(
            user_id=user_id,
            name=name,
            description=description,
            key_hash=key_hash,
            key_preview=key_preview,
            expires_at=expires_at,
            permissions=permissions,
        )

        db.add(api_key)
        db.commit()
        db.refresh(api_key)

        return api_key, plain_key

    @staticmethod
    def get_api_key(db: Session, user_id: UUID, api_key_id: UUID) -> APIKey:
        """
        Get an API key by ID.
        
        Args:
            db: Database session
            user_id: User ID
            api_key_id: API key ID
            
        Returns:
            APIKey: The API key object
        """
        api_key = db.query(APIKey).filter(
            and_(APIKey.id == api_key_id, APIKey.user_id == user_id)
        ).first()

        if not api_key:
            raise NotFoundError("API key not found")

        return api_key

    @staticmethod
    def get_api_keys(
        db: Session,
        user_id: UUID,
        page: int = 1,
        page_size: int = 10,
        is_active: Optional[bool] = None,
    ) -> tuple[list[APIKey], int]:
        """
        Get API keys for a user with pagination.
        
        Args:
            db: Database session
            user_id: User ID
            page: Page number (1-indexed)
            page_size: Number of items per page
            is_active: Filter by active status
            
        Returns:
            tuple: (List of API keys, total count)
        """
        query = db.query(APIKey).filter(APIKey.user_id == user_id)

        if is_active is not None:
            query = query.filter(APIKey.is_active == is_active)

        total = query.count()

        offset = (page - 1) * page_size
        api_keys = query.offset(offset).limit(page_size).all()

        return api_keys, total

    @staticmethod
    def verify_api_key(db: Session, plain_key: str) -> Optional[APIKey]:
        """
        Verify an API key and return the associated APIKey object.
        
        Args:
            db: Database session
            plain_key: The plain API key to verify
            
        Returns:
            APIKey: The API key object if valid, None otherwise
        """
        key_hash = APIKeyService.hash_api_key(plain_key)

        api_key = db.query(APIKey).filter(
            and_(
                APIKey.key_hash == key_hash,
                APIKey.is_active == True,
            )
        ).first()

        if not api_key:
            return None

        # Check if expired
        if api_key.expires_at and api_key.expires_at < datetime.now(timezone.utc):
            return None

        # Update usage statistics
        api_key.last_used_at = datetime.now(timezone.utc)
        api_key.usage_count += 1
        db.commit()

        return api_key

    @staticmethod
    def update_api_key(
        db: Session,
        user_id: UUID,
        api_key_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
        permissions: Optional[str] = None,
    ) -> APIKey:
        """
        Update an API key.
        
        Args:
            db: Database session
            user_id: User ID
            api_key_id: API key ID
            name: New name
            description: New description
            is_active: New active status
            permissions: New permissions
            
        Returns:
            APIKey: The updated API key
        """
        api_key = APIKeyService.get_api_key(db, user_id, api_key_id)

        if name is not None:
            api_key.name = name
        if description is not None:
            api_key.description = description
        if is_active is not None:
            api_key.is_active = is_active
        if permissions is not None:
            api_key.permissions = permissions

        api_key.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(api_key)

        return api_key

    @staticmethod
    def delete_api_key(db: Session, user_id: UUID, api_key_id: UUID) -> None:
        """
        Delete an API key.
        
        Args:
            db: Database session
            user_id: User ID
            api_key_id: API key ID
        """
        api_key = APIKeyService.get_api_key(db, user_id, api_key_id)
        db.delete(api_key)
        db.commit()

    @staticmethod
    def revoke_api_key(db: Session, user_id: UUID, api_key_id: UUID) -> APIKey:
        """
        Revoke (deactivate) an API key.
        
        Args:
            db: Database session
            user_id: User ID
            api_key_id: API key ID
            
        Returns:
            APIKey: The revoked API key
        """
        return APIKeyService.update_api_key(db, user_id, api_key_id, is_active=False)
