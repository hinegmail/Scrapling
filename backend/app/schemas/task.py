"""Task schemas"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator, HttpUrl

from app.models.task import FetcherType, SelectorType, TaskStatus


class TaskBase(BaseModel):
    """Base task schema"""

    name: str = Field(..., min_length=1, max_length=255, description="Task name")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    target_url: str = Field(..., description="Target URL to scrape")
    fetcher_type: FetcherType = Field(..., description="Fetcher type (http, dynamic, stealthy)")
    selector: str = Field(..., min_length=1, max_length=1000, description="CSS or XPath selector")
    selector_type: SelectorType = Field(..., description="Selector type (css, xpath)")
    timeout: int = Field(30, ge=1, le=300, description="Request timeout in seconds")
    retry_count: int = Field(3, ge=0, le=10, description="Number of retries")

    # Advanced options
    use_proxy_rotation: bool = Field(False, description="Enable proxy rotation")
    solve_cloudflare: bool = Field(False, description="Solve Cloudflare challenges")
    custom_headers: Optional[dict] = Field(None, description="Custom HTTP headers")
    cookies: Optional[dict] = Field(None, description="Cookies as dict")

    # Browser configuration (for dynamic fetcher)
    wait_time: Optional[int] = Field(None, ge=0, le=60, description="Wait time for dynamic fetcher")
    viewport_width: Optional[int] = Field(None, ge=320, le=1920, description="Browser viewport width")
    viewport_height: Optional[int] = Field(None, ge=240, le=1080, description="Browser viewport height")

    @validator("target_url")
    def validate_url(cls, v):
        """Validate URL format"""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

    @validator("selector")
    def validate_selector(cls, v, values):
        """Validate selector based on type"""
        if "selector_type" not in values:
            return v

        selector_type = values["selector_type"]
        if selector_type == SelectorType.CSS:
            # Basic CSS selector validation
            if not v or v.startswith(" "):
                raise ValueError("Invalid CSS selector")
        elif selector_type == SelectorType.XPATH:
            # Basic XPath validation
            if not v.startswith("/") and not v.startswith("."):
                raise ValueError("Invalid XPath expression")

        return v

    class Config:
        from_attributes = True


class TaskCreate(TaskBase):
    """Task creation schema"""

    pass


class TaskUpdate(BaseModel):
    """Task update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    target_url: Optional[str] = Field(None)
    fetcher_type: Optional[FetcherType] = Field(None)
    selector: Optional[str] = Field(None, min_length=1, max_length=1000)
    selector_type: Optional[SelectorType] = Field(None)
    timeout: Optional[int] = Field(None, ge=1, le=300)
    retry_count: Optional[int] = Field(None, ge=0, le=10)
    use_proxy_rotation: Optional[bool] = Field(None)
    solve_cloudflare: Optional[bool] = Field(None)
    custom_headers: Optional[dict] = Field(None)
    cookies: Optional[dict] = Field(None)
    wait_time: Optional[int] = Field(None, ge=0, le=60)
    viewport_width: Optional[int] = Field(None, ge=320, le=1920)
    viewport_height: Optional[int] = Field(None, ge=240, le=1080)

    @validator("target_url")
    def validate_url(cls, v):
        """Validate URL format"""
        if v is not None and not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

    class Config:
        from_attributes = True


class TaskResponse(TaskBase):
    """Task response schema"""

    id: UUID
    user_id: UUID
    status: TaskStatus
    last_run_at: Optional[datetime] = None
    total_runs: int
    success_count: int
    error_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Task list response schema"""

    items: list[TaskResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        from_attributes = True


class TaskDetailResponse(TaskResponse):
    """Task detail response schema"""

    pass
