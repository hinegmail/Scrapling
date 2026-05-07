"""WebSocket connection manager"""

import logging
import json
from typing import Dict, Set
from uuid import UUID

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        """Initialize connection manager"""
        # Map of user_id -> set of WebSocket connections
        self.active_connections: Dict[UUID, Set[WebSocket]] = {}
        # Map of task_id -> set of user_ids subscribed
        self.task_subscriptions: Dict[UUID, Set[UUID]] = {}

    async def connect(self, websocket: WebSocket, user_id: UUID):
        """
        Accept and register a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        logger.info(f"WebSocket connected for user: {user_id}")

    def disconnect(self, websocket: WebSocket, user_id: UUID):
        """
        Unregister and close a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        logger.info(f"WebSocket disconnected for user: {user_id}")

    async def subscribe_task(self, user_id: UUID, task_id: UUID):
        """
        Subscribe user to task updates.
        
        Args:
            user_id: User ID
            task_id: Task ID
        """
        if task_id not in self.task_subscriptions:
            self.task_subscriptions[task_id] = set()
        
        self.task_subscriptions[task_id].add(user_id)
        logger.info(f"User {user_id} subscribed to task {task_id}")

    async def unsubscribe_task(self, user_id: UUID, task_id: UUID):
        """
        Unsubscribe user from task updates.
        
        Args:
            user_id: User ID
            task_id: Task ID
        """
        if task_id in self.task_subscriptions:
            self.task_subscriptions[task_id].discard(user_id)
            
            if not self.task_subscriptions[task_id]:
                del self.task_subscriptions[task_id]
        
        logger.info(f"User {user_id} unsubscribed from task {task_id}")

    async def broadcast_task_update(self, task_id: UUID, message: dict):
        """
        Broadcast task update to all subscribed users.
        
        Args:
            task_id: Task ID
            message: Message to broadcast
        """
        if task_id not in self.task_subscriptions:
            return
        
        message_json = json.dumps(message)
        
        for user_id in self.task_subscriptions[task_id]:
            if user_id in self.active_connections:
                for websocket in self.active_connections[user_id]:
                    try:
                        await websocket.send_text(message_json)
                    except Exception as e:
                        logger.error(f"Error sending message to user {user_id}: {str(e)}")

    async def send_personal_message(self, message: dict, user_id: UUID):
        """
        Send message to specific user.
        
        Args:
            message: Message to send
            user_id: User ID
        """
        if user_id not in self.active_connections:
            return
        
        message_json = json.dumps(message)
        
        for websocket in self.active_connections[user_id]:
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending personal message to user {user_id}: {str(e)}")

    def get_active_users(self) -> int:
        """Get number of active users"""
        return len(self.active_connections)

    def get_active_connections_count(self) -> int:
        """Get total number of active connections"""
        return sum(len(conns) for conns in self.active_connections.values())


# Global connection manager instance
manager = ConnectionManager()
