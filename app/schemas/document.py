from uuid import UUID
from pydantic import BaseModel, ConfigDict

class DocumentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    size_bytes: int
  
class DocumentsUploadResponse(BaseModel):
    documents: list[DocumentSchema]

    @classmethod
    def from_documents(cls, documents: list) -> "DocumentsUploadResponse":
        return cls(documents=[DocumentSchema.model_validate(doc) for doc in documents])
