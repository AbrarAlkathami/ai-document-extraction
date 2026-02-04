from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas.extraction import (
    CreateExtractionRequest,
    ExtractionCreateResponse,
    ExtractionOut,
)
from app.schemas.extraction_record import ExtractionRecordsResponse
from app.services import extraction_service

router = APIRouter(prefix="/extractions", tags=["extractions"])


@router.post(
    "",
    response_model=ExtractionCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_extraction(
    body: CreateExtractionRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> ExtractionCreateResponse:
    """Create a new extraction job for the specified documents."""
    extraction = await extraction_service.create_extraction(body.document_ids, db)
    background_tasks.add_task(extraction_service.process_extraction, extraction.id)
    return ExtractionCreateResponse.from_extraction(extraction)


@router.get(
    "/{extraction_id}",
    response_model=ExtractionOut,
)
async def get_extraction(
    extraction_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ExtractionOut:
    """Get the status of an extraction job."""
    return await extraction_service.get_extraction(extraction_id, db)


@router.get(
    "/{extraction_id}/records",
    response_model=ExtractionRecordsResponse,
)
async def get_extraction_records(
    extraction_id: UUID,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> ExtractionRecordsResponse:
    """Get extraction records with optional pagination."""
    return await extraction_service.get_extraction_records(
        extraction_id, db, limit=limit, offset=offset
    )
