import asyncio
import random
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import DocumentNotFoundError, ExtractionNotFoundError
from app.db import async_session_factory
from app.models import Extraction, ExtractionRecord, ExtractionStatus
from app.repositories import document_repository, extraction_repository
from app.schemas.extraction import ExtractionOut
from app.schemas.extraction_record import ExtractionRecordsResponse

settings = get_settings()


async def create_extraction(
    document_ids: list[UUID],
    db: AsyncSession,
) -> Extraction:
    """
    Create a new extraction job for the specified documents.

    Returns the Extraction model. The route converts it to ExtractionCreateResponse.

    Raises:
        DocumentNotFoundError: If any document IDs are not found
    """
    found_docs = await document_repository.find_by_ids(db, document_ids)

    if len(found_docs) != len(document_ids):
        found_ids = {doc.id for doc in found_docs}
        missing_ids = [doc_id for doc_id in document_ids if doc_id not in found_ids]
        raise DocumentNotFoundError(missing_ids)

    extraction = Extraction(status=ExtractionStatus.PENDING)
    await extraction_repository.create(extraction, db)
    await db.flush()

    for doc_id in document_ids:
        await extraction_repository.add_document_link(extraction.id, doc_id, db)

    await db.flush()

    return extraction


async def get_extraction(
    extraction_id: UUID,
    db: AsyncSession,
) -> ExtractionOut:
    """
    Get extraction details by ID.

    Raises:
        ExtractionNotFoundError: If extraction not found
    """
    extraction = await extraction_repository.find_by_id(extraction_id, db)

    if not extraction:
        raise ExtractionNotFoundError(extraction_id)

    total_documents = await extraction_repository.count_documents(extraction_id, db)
    total_records = await extraction_repository.count_records(extraction_id, db)

    return ExtractionOut.from_extraction(
        extraction=extraction,
        total_documents=total_documents,
        total_records=total_records,
    )


async def get_extraction_records(
    extraction_id: UUID,
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0,
) -> ExtractionRecordsResponse:
    """
    Get extraction records with pagination.

    Raises:
        ExtractionNotFoundError: If extraction not found
    """
    extraction = await extraction_repository.find_by_id(extraction_id, db)

    if not extraction:
        raise ExtractionNotFoundError(extraction_id)

    total_documents = await extraction_repository.count_documents(extraction_id, db)
    total_records = await extraction_repository.count_records(extraction_id, db)
    records = await extraction_repository.find_records_paginated(
        extraction_id, db, limit=limit, offset=offset
    )

    return ExtractionRecordsResponse.from_extraction(
        extraction=extraction,
        records=records,
        total_documents=total_documents,
        total_records=total_records,
    )


async def process_extraction(extraction_id: UUID) -> None:
    """
    Background task to process an extraction job.

    Creates a NEW DB session (not reusing request db).
    Simulates AI extraction by generating mock JSONB records for each document.
    Status transitions: PENDING → PROCESSING → COMPLETED (or FAILED on error).
    """
    async with async_session_factory() as db:
        try:
            extraction = await extraction_repository.find_by_id_with_documents(
                extraction_id, db
            )

            if not extraction:
                return

            # Mark as PROCESSING
            extraction.status = ExtractionStatus.PROCESSING
            await db.commit()

            # Simulate AI processing delay
            delay_seconds = settings.MOCK_AI_DELAY_MS / 1000.0
            await asyncio.sleep(delay_seconds)

            # Generate mock records per document using configurable count
            mock_field_templates = [
                {"field": "doc_type", "value": "invoice", "confidence": 0.92},
                {"field": "amount", "value": "1500.00", "confidence": 0.87},
                {"field": "vendor", "value": "Acme Corp", "confidence": 0.95},
                {"field": "date", "value": "2026-01-15", "confidence": 0.89},
                {"field": "invoice_number", "value": "INV-2026-001", "confidence": 0.94},
            ]

            records: list[ExtractionRecord] = []
            for ext_doc in extraction.extraction_documents:
                for i in range(settings.RECORDS_PER_DOCUMENT):
                    # Cycle through templates with slight randomization
                    template = mock_field_templates[i % len(mock_field_templates)].copy()
                    template["confidence"] = round(
                        random.uniform(0.75, 0.99), 2
                    )
                    records.append(
                        ExtractionRecord(
                            extraction_id=extraction_id,
                            document_id=ext_doc.document_id,
                            data=template,
                        )
                    )

            db.add_all(records)
            extraction.status = ExtractionStatus.COMPLETED
            await db.commit()

        except Exception:
            # Mark FAILED if anything breaks
            async with async_session_factory() as error_db:
                extraction = await extraction_repository.find_by_id(
                    extraction_id, error_db
                )
                if extraction:
                    extraction.status = ExtractionStatus.FAILED
                    await error_db.commit()
