"""Error response schemas"""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class ErrorDetail(BaseModel):
    """Error detail schema"""

    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    """Error response schema"""

    error_code: str
    message: str
    status_code: int
    details: Optional[Dict[str, Any]] = None
    timestamp: str
