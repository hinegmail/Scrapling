"""Proxy service"""

import logging
import re
from typing import Optional
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.proxy import Proxy, ProxyProtocol
from app.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


class ProxyService:
    """Service for managing proxies"""

    @staticmethod
    def validate_proxy_address(host: str, port: int) -> tuple[bool, Optional[str]]:
        """
        Validate proxy address format.
        
        Args:
            host: Proxy host (IP or hostname)
            port: Proxy port number
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate port
        if not isinstance(port, int) or port < 1 or port > 65535:
            return False, "Port must be between 1 and 65535"
        
        # Validate host
        if not host or not isinstance(host, str):
            return False, "Host cannot be empty"
        
        # Check if it's a valid IP or hostname
        ip_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        hostname_pattern = r"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$"
        
        if re.match(ip_pattern, host):
            # Validate IP octets
            octets = host.split(".")
            for octet in octets:
                try:
                    octet_value = int(octet)
                    if octet_value > 255:
                        return False, "Invalid IP address"
                except ValueError:
                    return False, "Invalid IP address"
            return True, None
        elif re.match(hostname_pattern, host):
            # Additional check: hostname should not be all digits (to avoid matching invalid IPs)
            # If it looks like an IP but doesn't match the IP pattern, it's invalid
            parts = host.split(".")
            if len(parts) == 4 and all(part.isdigit() for part in parts):
                # This looks like an IP but didn't match the IP pattern
                return False, "Invalid IP address"
            return True, None
        else:
            return False, "Invalid host format (must be IP or hostname)"

    @staticmethod
    def create_proxy(db: Session, user_id: UUID, proxy_data: dict) -> Proxy:
        """
        Create a new proxy.
        
        Args:
            db: Database session
            user_id: User ID
            proxy_data: Proxy data dictionary
            
        Returns:
            Created proxy
        """
        # Validate required fields
        if not proxy_data.get("name"):
            raise ValidationError("Proxy name is required")
        
        if not proxy_data.get("host"):
            raise ValidationError("Proxy host is required")
        
        if not proxy_data.get("port"):
            raise ValidationError("Proxy port is required")
        
        # Validate proxy address
        is_valid, error_msg = ProxyService.validate_proxy_address(
            proxy_data["host"], proxy_data["port"]
        )
        if not is_valid:
            raise ValidationError(error_msg or "Invalid proxy address")
        
        # Create proxy
        proxy = Proxy(
            user_id=user_id,
            name=proxy_data["name"],
            protocol=proxy_data.get("protocol", ProxyProtocol.HTTP),
            host=proxy_data["host"],
            port=proxy_data["port"],
            username=proxy_data.get("username"),
            password=proxy_data.get("password"),
            is_active=proxy_data.get("is_active", True),
        )
        
        db.add(proxy)
        db.commit()
        db.refresh(proxy)
        
        logger.info(f"Proxy created: {proxy.id} for user {user_id}")
        return proxy

    @staticmethod
    def get_proxy(db: Session, user_id: UUID, proxy_id: UUID) -> Proxy:
        """Get a proxy by ID"""
        proxy = db.query(Proxy).filter(
            and_(Proxy.id == proxy_id, Proxy.user_id == user_id)
        ).first()
        
        if not proxy:
            raise NotFoundError("Proxy not found")
        
        return proxy

    @staticmethod
    def get_proxies(
        db: Session,
        user_id: UUID,
        page: int = 1,
        page_size: int = 10,
        is_active: Optional[bool] = None,
    ) -> tuple[list[Proxy], int]:
        """Get proxies with pagination and filtering"""
        query = db.query(Proxy).filter(Proxy.user_id == user_id)
        
        if is_active is not None:
            query = query.filter(Proxy.is_active == is_active)
        
        total = query.count()
        
        offset = (page - 1) * page_size
        proxies = query.offset(offset).limit(page_size).all()
        
        return proxies, total

    @staticmethod
    def update_proxy(db: Session, user_id: UUID, proxy_id: UUID, proxy_data: dict) -> Proxy:
        """Update a proxy"""
        proxy = ProxyService.get_proxy(db, user_id, proxy_id)
        
        # Validate proxy address if host or port changed
        if "host" in proxy_data or "port" in proxy_data:
            host = proxy_data.get("host", proxy.host)
            port = proxy_data.get("port", proxy.port)
            is_valid, error_msg = ProxyService.validate_proxy_address(host, port)
            if not is_valid:
                raise ValidationError(error_msg or "Invalid proxy address")
        
        # Update fields
        for field, value in proxy_data.items():
            if value is not None:
                setattr(proxy, field, value)
        
        db.commit()
        db.refresh(proxy)
        
        logger.info(f"Proxy updated: {proxy_id}")
        return proxy

    @staticmethod
    def delete_proxy(db: Session, user_id: UUID, proxy_id: UUID) -> None:
        """Delete a proxy"""
        proxy = ProxyService.get_proxy(db, user_id, proxy_id)
        
        db.delete(proxy)
        db.commit()
        
        logger.info(f"Proxy deleted: {proxy_id}")

    @staticmethod
    def get_active_proxies(db: Session, user_id: UUID) -> list[Proxy]:
        """Get all active proxies for a user"""
        proxies = db.query(Proxy).filter(
            and_(Proxy.user_id == user_id, Proxy.is_active == True)
        ).all()
        
        return proxies

    @staticmethod
    def get_proxy_rotation_list(db: Session, user_id: UUID) -> list[str]:
        """
        Get list of proxy URLs for rotation.
        
        Returns:
            List of proxy URLs in format: protocol://[username:password@]host:port
        """
        proxies = ProxyService.get_active_proxies(db, user_id)
        
        proxy_urls = []
        for proxy in proxies:
            if proxy.username and proxy.password:
                url = f"{proxy.protocol}://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}"
            else:
                url = f"{proxy.protocol}://{proxy.host}:{proxy.port}"
            proxy_urls.append(url)
        
        return proxy_urls

    @staticmethod
    def rotate_proxy(proxy_list: list[str], request_index: int) -> Optional[str]:
        """
        Get the next proxy in rotation based on request index.
        
        For a list of N proxies, this function cycles through them:
        - Request 0 -> Proxy 0
        - Request 1 -> Proxy 1
        - ...
        - Request N-1 -> Proxy N-1
        - Request N -> Proxy 0 (cycle repeats)
        
        Args:
            proxy_list: List of proxy URLs
            request_index: Current request index (0-based)
            
        Returns:
            The proxy URL to use for this request, or None if list is empty
        """
        if not proxy_list:
            return None
        
        # Use modulo to cycle through proxies
        proxy_index = request_index % len(proxy_list)
        return proxy_list[proxy_index]
