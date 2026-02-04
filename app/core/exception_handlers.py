from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import DocumentUploadError, NotFoundError, ValidationError


async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    """Handle NotFoundError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message},
    )


async def validation_error_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Handle ValidationError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )


async def document_upload_error_handler(
    request: Request, exc: DocumentUploadError
) -> JSONResponse:
    """Handle DocumentUploadError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": exc.message},
    )
