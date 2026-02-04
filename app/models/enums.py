import enum


class DocumentStatus(str, enum.Enum):
    """Status of a document in the system."""

    UPLOADED = "uploaded"
    FAILED = "failed"


class ExtractionStatus(str, enum.Enum):
    """Status of an extraction job."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
