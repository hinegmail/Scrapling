"""WebSocket routes"""

import logging
import json
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.middleware.auth import get_current_user
from app.websocket_manager import manager
from app.models.task import Task
from app.exceptions import NotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ws", tags=["websocket"])


@router.websocket("/tasks/{task_id}")
async def websocket_task_endpoint(
    websocket: WebSocket,
    task_id: str,
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    """
    WebSocket endpoint for task progress updates.
    
    - **task_id**: Task ID to subscribe to
    - **token**: JWT token for authentication
    """
    try:
        # Verify task exists and user has access
        task_uuid = UUID(task_id)
        task = db.query(Task).filter(Task.id == task_uuid).first()
        
        if not task:
            await websocket.close(code=4004, reason="Task not found")
            return
        
        # For now, we'll accept all connections
        # In production, verify token and user ownership
        user_id = task.user_id
        
        # Accept connection
        await manager.connect(websocket, user_id)
        
        # Subscribe to task updates
        await manager.subscribe_task(user_id, task_uuid)
        
        logger.info(f"WebSocket connected for task {task_id}, user {user_id}")
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                
                elif message.get("type") == "unsubscribe":
                    await manager.unsubscribe_task(user_id, task_uuid)
                    await websocket.close(code=1000, reason="Unsubscribed")
                    break
                
                else:
                    logger.warning(f"Unknown message type: {message.get('type')}")
        
        except WebSocketDisconnect:
            manager.disconnect(websocket, user_id)
            await manager.unsubscribe_task(user_id, task_uuid)
            logger.info(f"WebSocket disconnected for task {task_id}, user {user_id}")
        
        except Exception as e:
            logger.error(f"Error in WebSocket connection: {str(e)}")
            manager.disconnect(websocket, user_id)
            await manager.unsubscribe_task(user_id, task_uuid)
    
    except ValueError:
        await websocket.close(code=4000, reason="Invalid task ID")
    except Exception as e:
        logger.error(f"Error in WebSocket endpoint: {str(e)}")
        try:
            await websocket.close(code=4500, reason="Internal server error")
        except Exception:
            pass
