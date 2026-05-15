"""Result routes"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.result import (
    ResultResponse,
    ResultListResponse,
    ResultDetailResponse,
    ClipboardData,
)
from app.services.result_service import ResultService
from app.services.export_service import ExportService
from app.middleware.auth import get_current_user
from app.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/tasks", tags=["results"])


@router.get("/{task_id}/results", response_model=ResultListResponse)
async def list_results(
    task_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    sort_by: str = Query("extracted_at"),
    sort_order: str = Query("desc"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get results for a task with pagination, filtering, and sorting.
    
    - **task_id**: Task ID (required)
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    - **search**: Search in data fields (optional)
    - **sort_by**: Sort field (default: extracted_at)
    - **sort_order**: Sort order - asc or desc (default: desc)
    """
    try:
        results, total = ResultService.get_results(
            db,
            current_user["id"],
            task_id,
            page,
            page_size,
            search,
            sort_by,
            sort_order,
        )
        total_pages = (total + page_size - 1) // page_size

        return ResultListResponse(
            items=results,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    except NotFoundError as e:
        logger.warning(f"Task not found: {task_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list results",
        )


@router.get("/{task_id}/results/{result_id}", response_model=ResultDetailResponse)
async def get_result(
    task_id: UUID,
    result_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific result by ID"""
    try:
        result = ResultService.get_result(db, current_user["id"], task_id, result_id)
        return result
    except NotFoundError as e:
        logger.warning(f"Result not found: {result_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting result: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get result",
        )


@router.post("/{task_id}/results/export")
async def export_results(
    task_id: UUID,
    format_type: str = Query("csv", regex="^(csv|json|excel)$"),
    columns: Optional[list[str]] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Export results in specified format.
    
    - **task_id**: Task ID (required)
    - **format_type**: Export format - csv, json, or excel (default: csv)
    - **columns**: List of columns to include (optional)
    """
    try:
        # Validate format
        ExportService.validate_export_format(format_type)

        # Get results for export
        results = ResultService.get_results_for_export(db, current_user["id"], task_id)

        if not results:
            raise ValidationError("No results to export")

        # Generate export
        if format_type == "csv":
            content = ExportService.export_to_csv(results, columns)
            return StreamingResponse(
                iter([content]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=results.csv"},
            )

        elif format_type == "json":
            content = ExportService.export_to_json(results, columns)
            return StreamingResponse(
                iter([content]),
                media_type="application/json",
                headers={"Content-Disposition": "attachment; filename=results.json"},
            )

        elif format_type == "excel":
            content = ExportService.export_to_excel(results, columns)
            return StreamingResponse(
                iter([content]),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=results.xlsx"},
            )

    except NotFoundError as e:
        logger.warning(f"Task not found: {task_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error exporting results: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export results",
        )


@router.post("/{task_id}/results/clipboard", response_model=ClipboardData)
async def prepare_clipboard_data(
    task_id: UUID,
    format_type: str = Query("text", regex="^(text|json|csv|html)$"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Prepare results for clipboard in specified format.
    
    - **task_id**: Task ID (required)
    - **format_type**: Format type - text, json, csv, or html (default: text)
    """
    try:
        # Get results
        results = ResultService.get_results_for_export(db, current_user["id"], task_id)

        if not results:
            raise ValidationError("No results to copy")

        # Generate clipboard data
        data = ExportService.get_clipboard_data(results, format_type)

        return ClipboardData(format=format_type, data=data)

    except NotFoundError as e:
        logger.warning(f"Task not found: {task_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error preparing clipboard data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to prepare clipboard data",
        )
