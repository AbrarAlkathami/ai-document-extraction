from typing import TYPE_CHECKING, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import ExtractionStatus

if TYPE_CHECKING:
    from app.models import Extraction


class CreateExtractionRequest(BaseModel):
    """Request schema for creating an extraction job."""

    document_ids: list[UUID]


class ExtractionCreateResponse(BaseModel):
    """Response schema for POST /extractions (create endpoint)."""

    model_config = ConfigDict(from_attributes=True)

    extraction_id: UUID
    status: ExtractionStatus

    @classmethod
    def from_extraction(cls, extraction: "Extraction") -> Self:
        return cls(extraction_id=extraction.id, status=extraction.status)


class ExtractionOut(BaseModel):
    """Response schema for GET /extractions/{id} (status endpoint)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: ExtractionStatus
    total_documents: int = 0
    total_records: int = 0

    @classmethod
    def from_extraction(
        cls,
        extraction: "Extraction",
        total_documents: int,
        total_records: int,
    ) -> Self:
        return cls(
            id=extraction.id,
            status=extraction.status,
            total_documents=total_documents,
            total_records=total_records,
        )
