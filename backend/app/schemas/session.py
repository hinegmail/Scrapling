"""Session schemas"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SessionResponse(BaseModel):
    """Session response schema"""

    id: str
    user_id: str
    token: str
    expires_at: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
