# AI Document Extraction

FastAPI backend for uploading documents, creating async extraction jobs, and retrieving AI-extracted records with clean architecture.

## Features

- **Document Upload** - Upload PDF, images, and other file types with metadata tracking
- **Extraction Jobs** - Create async extraction jobs for one or more documents
- **Background Processing** - Automatic status transitions (PENDING → PROCESSING → COMPLETED)
- **Paginated Results** - Retrieve extracted data with pagination support
- **JSONB Storage** - Flexible schema for extracted data

## Tech Stack

- **FastAPI** - Modern async web framework
- **PostgreSQL 16** - Database with JSONB support
- **SQLAlchemy 2.0** - Async ORM with type annotations
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

## Quick Start

### Prerequisites

- Python 3.14+
- Docker & Docker Compose
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### 1. Start the Database

```bash
docker-compose up -d
```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Run Migrations

```bash
uv run alembic upgrade head
```

### 4. Start the Server

```bash
uv run uvicorn main:app --reload
```

The API is now available at http://localhost:8000

### 5. Open API Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| POST | `/documents` | Upload documents |
| POST | `/extractions` | Create extraction job |
| GET | `/extractions/{id}` | Get extraction status |
| GET | `/extractions/{id}/records` | Get extraction records (paginated) |

## Example Workflow

```bash
# 1. Upload a document
curl -X POST http://localhost:8000/documents \
  -F "files=@invoice.pdf"

# 2. Create extraction job (use document ID from step 1)
curl -X POST http://localhost:8000/extractions \
  -H "Content-Type: application/json" \
  -d '{"document_ids": ["<document-uuid>"]}'

# 3. Check extraction status
curl http://localhost:8000/extractions/<extraction-uuid>

# 4. Get extraction records
curl "http://localhost:8000/extractions/<extraction-uuid>/records?limit=10"
```

## Project Structure

```
ai-document-extraction/
├── main.py                 # FastAPI app entry point
├── docker-compose.yml      # PostgreSQL setup
├── alembic/                # Database migrations
└── app/
    ├── core/               # Config, exceptions, exception handlers
    ├── db/                 # Database session & base
    ├── models/             # SQLAlchemy ORM models
    ├── schemas/            # Pydantic schemas with factory methods
    ├── repositories/       # Data access layer
    ├── services/           # Business logic layer
    └── api/                # Thin route handlers
```

### Architecture Layers

```
API Routes → Services → Repositories → Database
     ↑           ↑            ↑
   HTTP      Business     Data Access
  Handling    Logic       Abstraction
```

## Documentation

Detailed documentation is available in the [doc/](doc/) folder:

| Document | Description |
|----------|-------------|
| [INDEX.md](doc/INDEX.md) | Documentation reading guide |
| [ARCHITECTURE.md](doc/ARCHITECTURE.md) | Clean architecture, services, repositories, exceptions |
| [API_REFERENCE.md](doc/API_REFERENCE.md) | Complete API specification |
| [DATABASE_DESIGN.md](doc/DATABASE_DESIGN.md) | Schema & ERD |
| [MODELS.md](doc/MODELS.md) | SQLAlchemy models |
| [SCHEMAS.md](doc/SCHEMAS.md) | Pydantic schemas with factory methods |
| [CONFIGURATION.md](doc/CONFIGURATION.md) | Environment variables & settings |
| [IMPLEMENTATION.md](doc/IMPLEMENTATION.md) | Implementation details |

## Configuration

Environment variables can be set in `.env.local`:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | (required) | PostgreSQL connection string |
| `STORAGE_DIR` | `storage/documents` | File storage directory |
| `MOCK_AI_DELAY_MS` | `300` | Simulated AI processing delay |
| `RECORDS_PER_DOCUMENT` | `2` | Mock records generated per document |
| `LOG_LEVEL` | `INFO` | Logging level |

## Development

### Run Tests

```bash
uv run pytest
```

### Create a Migration

```bash
uv run alembic revision --autogenerate -m "description"
```

### Check Migration Status

```bash
uv run alembic current
```

## Tradeoffs & Shortcuts

### Design Decisions

| Decision | Tradeoff | Rationale |
|----------|----------|-----------|
| **FastAPI BackgroundTasks** | Not as robust as Celery/RQ | Simpler setup, no Redis/broker dependency; sufficient for demo |
| **Local file storage** | Not scalable to multiple instances | Avoids S3/cloud complexity; easy to swap with cloud storage later |
| **Mock AI extraction** | No real AI/ML processing | Focuses on API design and async flow; real AI would be a separate service |
| **PostgreSQL JSONB** | Less type safety than normalized tables | Flexible schema for varying extraction results; enables rapid iteration |
| **In-process background tasks** | Tasks lost on server restart | Acceptable for demo; production would use persistent queue |
| **No authentication** | API is open | Simplifies testing; auth would be added via FastAPI middleware |

### Shortcuts Taken

- **No retry logic** for failed extractions - would add exponential backoff in production
- **No file validation** beyond content-type - production would validate file contents
- **No rate limiting** - would add for production to prevent abuse
- **Single database connection pool** - would tune pool size for production workload
- **No request tracing** - would add correlation IDs for debugging

## Improvements with More Time

### High Priority

1. **Real AI Integration**
   - Integrate with OpenAI/Claude API for actual document extraction
   - Add OCR pipeline for image-based documents (Tesseract/AWS Textract)
   - Support structured output schemas (invoices, receipts, contracts)

2. **Production-Ready Background Processing**
   - Replace BackgroundTasks with Celery + Redis/RabbitMQ
   - Add job persistence and retry with exponential backoff
   - Implement dead letter queue for failed jobs
   - Add progress tracking (e.g., 50% complete)

3. **Cloud Storage**
   - AWS S3 / GCS integration for document storage
   - Signed URL generation for secure uploads/downloads
   - Automatic cleanup of old documents

### Medium Priority

4. **Authentication & Authorization**
   - JWT-based authentication
   - Role-based access control (RBAC)
   - API key management for integrations

5. **Observability**
   - Structured logging with correlation IDs
   - Prometheus metrics (request latency, queue depth)
   - Distributed tracing (OpenTelemetry)
   - Health check endpoints for dependencies

6. **Testing**
   - Unit tests for services and repositories
   - Integration tests with test database
   - E2E tests for API workflows
   - Load testing with Locust

### Nice to Have

7. **API Enhancements**
   - Webhook notifications on extraction completion
   - Batch document upload endpoint
   - Extraction templates for different document types
   - Search/filter extractions by date, status

8. **Developer Experience**
   - OpenAPI client generation
   - Postman collection
   - Docker Compose for full local stack
   - GitHub Actions CI/CD pipeline

## License

MIT
