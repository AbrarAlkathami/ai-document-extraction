from fastapi import UploadFile, File, APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.document import DocumentsUploadResponse
from app.services.document_service import upload_documents_service
from app.db import get_db


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentsUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_documents(
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
) -> DocumentsUploadResponse:
    
    return await upload_documents_service(files=files, db=db)
