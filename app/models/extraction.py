from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import ExtractionStatus


class Extraction(Base, UUIDMixin, TimestampMixin):
    """Represents one extraction job."""

    __tablename__ = "extractions"

    status: Mapped[ExtractionStatus] = mapped_column(
        Enum(ExtractionStatus),
        default=ExtractionStatus.PENDING,
        nullable=False,
    )

    # Relationships
    extraction_documents: Mapped[list["ExtractionDocument"]] = relationship(
        "ExtractionDocument",
        back_populates="extraction",
        cascade="all, delete-orphan",
    )
    extraction_records: Mapped[list["ExtractionRecord"]] = relationship(
        "ExtractionRecord",
        back_populates="extraction",
        cascade="all, delete-orphan",
    )


class ExtractionDocument(Base, TimestampMixin):
    """Join table connecting extractions to documents (many-to-many)."""

    __tablename__ = "extraction_documents"

    extraction_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("extractions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    document_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Relationships
    extraction: Mapped["Extraction"] = relationship(
        "Extraction",
        back_populates="extraction_documents",
    )
    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="extraction_documents",
    )

    __table_args__ = (
        UniqueConstraint("extraction_id", "document_id", name="uq_extraction_document"),
        Index("ix_extraction_documents_extraction_id", "extraction_id"),
        Index("ix_extraction_documents_document_id", "document_id"),
    )


# Import at end to avoid circular imports
from app.models.document import Document  # noqa: E402, F401
from app.models.extraction_record import ExtractionRecord  # noqa: E402, F401
