"""Selector validation routes"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.middleware.auth import get_current_user
from app.services.selector_validator import SelectorValidator
from app.exceptions import ValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/selectors", tags=["selectors"])


class SelectorValidateRequest(BaseModel):
    """Selector validation request"""
    selector: str = Field(..., min_length=1, max_length=1000)
    selector_type: str = Field(..., regex="^(css|xpath)$")


class SelectorValidateResponse(BaseModel):
    """Selector validation response"""
    is_valid: bool
    error_message: Optional[str] = None
    suggestions: list[str] = []


class SelectorTestRequest(BaseModel):
    """Selector test request"""
    selector: str = Field(..., min_length=1, max_length=1000)
    selector_type: str = Field(..., regex="^(css|xpath)$")
    html_content: str = Field(..., min_length=1)


class SelectorTestResponse(BaseModel):
    """Selector test response"""
    match_count: int
    preview_data: list[dict]
    suggestions: Optional[list[str]] = None


@router.post("/validate", response_model=SelectorValidateResponse)
async def validate_selector(
    request: SelectorValidateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Validate CSS or XPath selector syntax.
    
    - **selector**: CSS or XPath selector string
    - **selector_type**: Type of selector ('css' or 'xpath')
    """
    try:
        is_valid, error_message = SelectorValidator.validate_selector(
            request.selector, request.selector_type
        )
        
        suggestions = []
        if not is_valid and error_message:
            suggestions = SelectorValidator.get_selector_suggestions(
                request.selector, request.selector_type, error_message
            )
        
        logger.info(f"Selector validation: {request.selector_type} - valid={is_valid}")
        
        return SelectorValidateResponse(
            is_valid=is_valid,
            error_message=error_message,
            suggestions=suggestions,
        )
    except Exception as e:
        logger.error(f"Error validating selector: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate selector"
        )


@router.post("/test", response_model=SelectorTestResponse)
async def test_selector(
    request: SelectorTestRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Test selector against HTML content.
    
    - **selector**: CSS or XPath selector string
    - **selector_type**: Type of selector ('css' or 'xpath')
    - **html_content**: HTML content to test against
    """
    try:
        # First validate selector
        is_valid, error_message = SelectorValidator.validate_selector(
            request.selector, request.selector_type
        )
        
        if not is_valid:
            suggestions = SelectorValidator.get_selector_suggestions(
                request.selector, request.selector_type, error_message or ""
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_message or "Invalid selector",
            )
        
        # Test selector
        match_count, preview_data = SelectorValidator.test_selector(
            request.html_content, request.selector, request.selector_type
        )
        
        logger.info(f"Selector test: {request.selector_type} - matches={match_count}")
        
        return SelectorTestResponse(
            match_count=match_count,
            preview_data=preview_data,
        )
    except ValidationError as e:
        logger.warning(f"Validation error testing selector: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing selector: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to test selector"
        )
