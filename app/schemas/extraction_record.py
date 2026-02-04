from typing import TYPE_CHECKING, Any, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.extraction import ExtractionOut

if TYPE_CHECKING:
    from app.models import Extraction, ExtractionRecord


class ExtractionRecordOut(BaseModel):
    """Response schema for a single extraction record."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    data: dict[str, Any]


class ExtractionRecordsResponse(ExtractionOut):
    """Response schema for extraction with its records."""

    records: list[ExtractionRecordOut] = []

    @classmethod
    def from_extraction(
        cls,
        extraction: "Extraction",
        records: list["ExtractionRecord"],
        total_documents: int,
        total_records: int,
    ) -> Self:
        """Create response from extraction model with records."""
        return cls(
            id=extraction.id,
            status=extraction.status,
            total_documents=total_documents,
            total_records=total_records,
            records=[ExtractionRecordOut.model_validate(r) for r in records],
        )
