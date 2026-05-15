"""Header service"""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.header import Header
from app.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


class HeaderService:
    """Service for managing custom headers"""

    @staticmethod
    def validate_header_data(header_data: dict) -> tuple[bool, Optional[str]]:
        """
        Validate header data.
        
        Args:
            header_data: Header data dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate key
        if not header_data.get("key"):
            return False, "Header key is required"
        
        key = header_data["key"]
        if not isinstance(key, str) or len(key) == 0 or len(key) > 255:
            return False, "Header key must be a non-empty string (max 255 characters)"
        
        # Validate value
        if not header_data.get("value"):
            return False, "Header value is required"
        
        value = header_data["value"]
        if not isinstance(value, str) or len(value) == 0 or len(value) > 1000:
            return False, "Header value must be a non-empty string (max 1000 characters)"
        
        return True, None

    @staticmethod
    def create_header(db: Session, user_id: UUID, header_data: dict) -> Header:
        """
        Create a new custom header.
        
        Args:
            db: Database session
            user_id: User ID
            header_data: Header data dictionary with 'key' and 'value'
            
        Returns:
            Created header
            
        Raises:
            ValidationError: If header data is invalid
        """
        # Validate header data
        is_valid, error_msg = HeaderService.validate_header_data(header_data)
        if not is_valid:
            raise ValidationError(error_msg or "Invalid header data")
        
        # Create header
        header = Header(
            user_id=user_id,
            key=header_data["key"],
            value=header_data["value"],
        )
        
        db.add(header)
        db.commit()
        db.refresh(header)
        
        logger.info(f"Header created: {header.id} for user {user_id}")
        return header

    @staticmethod
    def get_header(db: Session, user_id: UUID, header_id: UUID) -> Header:
        """
        Get a header by ID.
        
        Args:
            db: Database session
            user_id: User ID
            header_id: Header ID
            
        Returns:
            Header object
            
        Raises:
            NotFoundError: If header not found
        """
        header = db.query(Header).filter(
            Header.id == header_id,
            Header.user_id == user_id,
        ).first()
        
        if not header:
            raise NotFoundError("Header not found")
        
        return header

    @staticmethod
    def get_headers(
        db: Session,
        user_id: UUID,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Header], int]:
        """
        Get headers with pagination.
        
        Args:
            db: Database session
            user_id: User ID
            page: Page number (1-based)
            page_size: Number of items per page
            
        Returns:
            Tuple of (headers list, total count)
        """
        query = db.query(Header).filter(Header.user_id == user_id)
        
        total = query.count()
        
        offset = (page - 1) * page_size
        headers = query.offset(offset).limit(page_size).all()
        
        return headers, total

    @staticmethod
    def get_all_headers(db: Session, user_id: UUID) -> list[Header]:
        """
        Get all headers for a user without pagination.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of headers
        """
        headers = db.query(Header).filter(Header.user_id == user_id).all()
        return headers

    @staticmethod
    def update_header(db: Session, user_id: UUID, header_id: UUID, header_data: dict) -> Header:
        """
        Update a header.
        
        Args:
            db: Database session
            user_id: User ID
            header_id: Header ID
            header_data: Header data dictionary with fields to update
            
        Returns:
            Updated header
            
        Raises:
            NotFoundError: If header not found
            ValidationError: If header data is invalid
        """
        header = HeaderService.get_header(db, user_id, header_id)
        
        # Validate if key or value is being updated
        if "key" in header_data or "value" in header_data:
            # Create a complete header data dict for validation
            validation_data = {
                "key": header_data.get("key", header.key),
                "value": header_data.get("value", header.value),
            }
            is_valid, error_msg = HeaderService.validate_header_data(validation_data)
            if not is_valid:
                raise ValidationError(error_msg or "Invalid header data")
        
        # Update fields
        for field, value in header_data.items():
            if value is not None and field in ["key", "value"]:
                setattr(header, field, value)
        
        db.commit()
        db.refresh(header)
        
        logger.info(f"Header updated: {header_id}")
        return header

    @staticmethod
    def delete_header(db: Session, user_id: UUID, header_id: UUID) -> None:
        """
        Delete a header.
        
        Args:
            db: Database session
            user_id: User ID
            header_id: Header ID
            
        Raises:
            NotFoundError: If header not found
        """
        header = HeaderService.get_header(db, user_id, header_id)
        
        db.delete(header)
        db.commit()
        
        logger.info(f"Header deleted: {header_id}")

    @staticmethod
    def get_headers_dict(db: Session, user_id: UUID) -> dict[str, str]:
        """
        Get all headers as a dictionary (key -> value mapping).
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dictionary of headers
        """
        headers = HeaderService.get_all_headers(db, user_id)
        
        headers_dict = {}
        for header in headers:
            headers_dict[header.key] = header.value
        
        return headers_dict

    @staticmethod
    def delete_all_headers(db: Session, user_id: UUID) -> int:
        """
        Delete all headers for a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Number of headers deleted
        """
        count = db.query(Header).filter(Header.user_id == user_id).delete()
        db.commit()
        
        logger.info(f"Deleted {count} headers for user {user_id}")
        return count

