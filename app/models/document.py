from sqlalchemy import BigInteger, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import DocumentStatus


class Document(Base, UUIDMixin, TimestampMixin):
    """Stores uploaded file metadata."""

    __tablename__ = "documents"

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus),
        default=DocumentStatus.UPLOADED,
        nullable=False,
    )

    # Relationships
    extraction_documents: Mapped[list["ExtractionDocument"]] = relationship(
        "ExtractionDocument",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    extraction_records: Mapped[list["ExtractionRecord"]] = relationship(
        "ExtractionRecord",
        back_populates="document",
        cascade="all, delete-orphan",
    )


# Import at end to avoid circular imports
from app.models.extraction import ExtractionDocument  # noqa: E402, F401
from app.models.extraction_record import ExtractionRecord  # noqa: E402, F401
