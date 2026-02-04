from typing import Any
from uuid import UUID

from sqlalchemy import ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class ExtractionRecord(Base, UUIDMixin, TimestampMixin):
    """Stores extracted JSON results per document per extraction."""

    __tablename__ = "extraction_records"

    extraction_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("extractions.id", ondelete="CASCADE"),
        nullable=False,
    )
    document_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    # Relationships
    extraction: Mapped["Extraction"] = relationship(
        "Extraction",
        back_populates="extraction_records",
    )
    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="extraction_records",
    )

    __table_args__ = (
        Index("ix_extraction_records_extraction_id", "extraction_id"),
        Index("ix_extraction_records_document_id", "document_id"),
    )


# Import at end to avoid circular imports
from app.models.document import Document  # noqa: E402, F401
from app.models.extraction import Extraction  # noqa: E402, F401
