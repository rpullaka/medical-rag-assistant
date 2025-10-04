# Medical RAG Assistant - Project Structure

## Overview

This project follows a professional Python project structure with clear separation of concerns and modular organization.

## Directory Structure

### `/src/` - Source Code
- **`api/`** - Web interfaces and API endpoints
  - `main_api.py` - FastAPI REST API
  - `web_interface.py` - Streamlit web interface
- **`core/`** - Core business logic
  - `rag.py` - RAG implementation and medical query processing
- **`database/`** - Data persistence layer
  - `database.py` - PostgreSQL operations
  - `db.py` - Database utilities and connection management
  - `vector_db.py` - Qdrant vector database operations
- **`services/`** - External service integrations
  - `s3_service.py` - AWS S3 logging and storage

### `/config/` - Configuration Files
- `docker-compose.yaml` - Multi-service orchestration
- `grafana_dashboard.json` - Monitoring dashboard configuration

### `/scripts/` - Utility Scripts
- `ingest.py` - Medical data ingestion pipeline
- `db_prep.py` - Database initialization script

### `/docs/` - Documentation
- `assets/` - Documentation images and screenshots

### `/data/` - Datasets and Evaluation Data
- Medical Q&A datasets
- Evaluation results and ground truth data

### `/tests/` - Test Suite
- Reserved for future test implementation

## Benefits of This Structure

1. **Modularity**: Clear separation of API, business logic, database, and services
2. **Scalability**: Easy to add new components without affecting existing code
3. **Maintainability**: Logical organization makes code easier to find and modify
4. **Professional Standards**: Follows Python packaging best practices
5. **Docker-Friendly**: Structure optimized for containerized deployment

## Running the Application

With the new structure, use these commands:

- **Start API**: `make run-api` or `PYTHONPATH=. python -m uvicorn src.api.main_api:app --reload`
- **Start Web Interface**: `make run-web` or `PYTHONPATH=. streamlit run src/api/web_interface.py`
- **Docker Services**: `make docker-up` or `cd config && docker-compose up --build`
- **Data Ingestion**: `make ingest-data` or `PYTHONPATH=. python scripts/ingest.py`

## Import Paths

All modules use absolute imports from the `src/` directory:
- `from src.database.db import init_db`
- `from src.core.rag import rag`
- `from src.services.s3_service import upload_logs_to_s3`

The `PYTHONPATH` is set to include the project root for proper module resolution.