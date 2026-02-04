from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api import documents_router, extractions_router
from app.core.config import get_settings
from app.core.exception_handlers import (
    document_upload_error_handler,
    not_found_handler,
    validation_error_handler,
)
from app.core.exceptions import DocumentUploadError, NotFoundError, ValidationError
from app.db import engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,
    debug=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(NotFoundError, not_found_handler)
app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(DocumentUploadError, document_upload_error_handler)

# Include API routers
app.include_router(documents_router)
app.include_router(extractions_router)


@app.get("/")
async def root():
    return {"message": "AI Document Extraction API"}


@app.get("/health")
def health():
    return {"message": "API is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
