from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Document

class DocumentRepository:
    async def find_by_ids(self, db: AsyncSession, document_ids: list[UUID]) -> list[Document]:
        if not document_ids:
            return []
        stmt = select(Document).where(Document.id.in_(document_ids))
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, document: Document) -> Document:
        db.add(document)
        return document


document_repository = DocumentRepository()

