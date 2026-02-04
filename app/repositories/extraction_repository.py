from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Extraction, ExtractionDocument, ExtractionRecord


async def find_by_id(
    extraction_id: UUID,
    db: AsyncSession,
) -> Extraction | None:
    """Find extraction by ID."""
    stmt = select(Extraction).where(Extraction.id == extraction_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def find_by_id_with_documents(
    extraction_id: UUID,
    db: AsyncSession,
) -> Extraction | None:
    """Find extraction by ID with related documents loaded."""
    stmt = (
        select(Extraction)
        .options(selectinload(Extraction.extraction_documents))
        .where(Extraction.id == extraction_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create(extraction: Extraction, db: AsyncSession) -> Extraction:
    """Add an extraction to the session."""
    db.add(extraction)
    return extraction


async def add_document_link(
    extraction_id: UUID,
    document_id: UUID,
    db: AsyncSession,
) -> ExtractionDocument:
    """Link a document to an extraction."""
    ext_doc = ExtractionDocument(
        extraction_id=extraction_id,
        document_id=document_id,
    )
    db.add(ext_doc)
    return ext_doc


async def add_record(record: ExtractionRecord, db: AsyncSession) -> ExtractionRecord:
    """Add an extraction record."""
    db.add(record)
    return record


async def count_documents(extraction_id: UUID, db: AsyncSession) -> int:
    """Count documents linked to an extraction."""
    stmt = (
        select(func.count())
        .select_from(ExtractionDocument)
        .where(ExtractionDocument.extraction_id == extraction_id)
    )
    result = await db.execute(stmt)
    return result.scalar() or 0


async def count_records(extraction_id: UUID, db: AsyncSession) -> int:
    """Count records for an extraction."""
    stmt = (
        select(func.count())
        .select_from(ExtractionRecord)
        .where(ExtractionRecord.extraction_id == extraction_id)
    )
    result = await db.execute(stmt)
    return result.scalar() or 0


async def find_records_paginated(
    extraction_id: UUID,
    db: AsyncSession,
    limit: int = 100,
    offset: int = 0,
) -> list[ExtractionRecord]:
    """Get paginated records for an extraction."""
    stmt = (
        select(ExtractionRecord)
        .where(ExtractionRecord.extraction_id == extraction_id)
        .order_by(ExtractionRecord.created_at)
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
