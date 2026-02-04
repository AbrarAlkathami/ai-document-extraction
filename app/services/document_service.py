import os
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import EmptyFilesError, DocumentUploadError
from app.models import Document, DocumentStatus
from app.repositories.document_repository import document_repository
from app.schemas.document import DocumentsUploadResponse

settings = get_settings()


async def upload_documents(files: list[UploadFile], db: AsyncSession) -> DocumentsUploadResponse:
    if not files:
        raise EmptyFilesError()

    storage_dir = Path(settings.STORAGE_DIR)
    storage_dir.mkdir(parents=True, exist_ok=True)

    documents: list[Document] = []
    created_paths: list[Path] = []

    try:
        for file in files:
            doc_id = uuid4()
            original_name = file.filename or "unknown"
            ext = Path(original_name).suffix
            file_path = storage_dir / f"{doc_id}{ext}"

            content = await file.read()  
            with open(file_path, "wb") as f:
                f.write(content)

            created_paths.append(file_path)

            doc = Document(
                id=doc_id,
                filename=original_name,
                file_path=str(file_path),
                content_type=file.content_type or "application/octet-stream",
                size_bytes=len(content),
                status=DocumentStatus.UPLOADED,
            )

            await document_repository.create(db, doc)
            documents.append(doc)

        await db.commit()
        return DocumentsUploadResponse.from_documents(documents)

    except Exception as e:
        await db.rollback()

        # cleanup saved files if something fails
        for p in created_paths:
            try:
                os.remove(p)
            except Exception:
                pass

        raise DocumentUploadError(original_name, str(e))

