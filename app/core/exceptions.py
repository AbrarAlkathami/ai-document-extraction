from uuid import UUID


class AppException(Exception):
    """Base exception for application errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(AppException):
    """Raised when a resource is not found."""

    pass


class ValidationError(AppException):
    """Raised when input validation fails."""

    pass


class DocumentNotFoundError(NotFoundError):
    """Raised when one or more documents are not found."""

    def __init__(self, missing_ids: list[UUID]):
        self.missing_ids = missing_ids
        message = f"Documents not found: {', '.join(str(id) for id in missing_ids)}"
        super().__init__(message)


class ExtractionNotFoundError(NotFoundError):
    """Raised when an extraction is not found."""

    def __init__(self, extraction_id: UUID):
        self.extraction_id = extraction_id
        super().__init__(f"Extraction not found: {extraction_id}")


class DocumentUploadError(AppException):
    """Raised when document upload fails."""

    def __init__(self, filename: str, reason: str):
        self.filename = filename
        super().__init__(f"Failed to upload {filename}: {reason}")


class EmptyFilesError(ValidationError):
    """Raised when no files are provided for upload."""

    def __init__(self):
        super().__init__("At least one file is required")
