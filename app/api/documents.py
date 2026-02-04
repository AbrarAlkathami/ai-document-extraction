from fastapi import APIRouter, Depends, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas.document import DocumentsUploadResponse
from app.services import document_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "",
    response_model=DocumentsUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_documents(
    files: list[UploadFile],
    db: AsyncSession = Depends(get_db),
) -> DocumentsUploadResponse:
    """Upload one or more files."""
    return await document_service.upload_documents(files, db)
