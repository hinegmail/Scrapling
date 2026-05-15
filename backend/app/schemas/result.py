"""Result schemas"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ResultBase(BaseModel):
    """Base result schema"""

    data: dict = Field(..., description="Extracted data")
    source_url: str = Field(..., description="Source URL where data was extracted")
    extracted_at: datetime = Field(..., description="Extraction timestamp")


class ResultCreate(ResultBase):
    """Result creation schema"""

    pass


class ResultResponse(ResultBase):
    """Result response schema"""

    id: UUID
    task_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResultListResponse(BaseModel):
    """Result list response schema"""

    items: list[ResultResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        from_attributes = True


class ResultDetailResponse(ResultResponse):
    """Result detail response schema"""

    pass


class ResultSearchFilter(BaseModel):
    """Result search and filter schema"""

    search: Optional[str] = Field(None, description="Search in data fields")
    sort_by: Optional[str] = Field("extracted_at", description="Sort field")
    sort_order: Optional[str] = Field("desc", description="Sort order (asc/desc)")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Items per page")

    class Config:
        from_attributes = True


class ClipboardData(BaseModel):
    """Clipboard data format schema"""

    format: str = Field(..., description="Format type (text, json, csv, html)")
    data: str = Field(..., description="Formatted data for clipboard")

    class Config:
        from_attributes = True
