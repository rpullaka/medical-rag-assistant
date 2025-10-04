# Migration Guide: Professional Project Structure

## Overview
The Medical RAG Assistant has been reorganized into a professional project structure following Python best practices.

## What Changed

### File Relocations

#### Python Modules → `/src/` Package Structure
- `main_api.py` → `src/api/main_api.py`
- `web_interface.py` → `src/api/web_interface.py`
- `rag.py` → `src/core/rag.py`
- `database.py` → `src/database/database.py`
- `db.py` → `src/database/db.py`
- `vector_db.py` → `src/database/vector_db.py`
- `s3_service.py` → `src/services/s3_service.py`

#### Configuration Files → `/config/`
- `docker-compose.yaml` → `config/docker-compose.yaml`
- `grafana_dashboard.json` → `config/grafana_dashboard.json`

#### Utility Scripts → `/scripts/`
- `ingest.py` → `scripts/ingest.py`
- `db_prep.py` → `scripts/db_prep.py`

#### Documentation Assets → `/docs/assets/`
- `Images/` → `docs/assets/`

## Updated Commands

### Development Commands
| Old Command | New Command |
|-------------|-------------|
| `python main_api.py` | `PYTHONPATH=. python -m uvicorn src.api.main_api:app --reload` |
| `streamlit run web_interface.py` | `PYTHONPATH=. streamlit run src/api/web_interface.py` |
| `python ingest.py` | `PYTHONPATH=. python scripts/ingest.py` |
| `python db_prep.py` | `PYTHONPATH=. python scripts/db_prep.py` |

### Docker Commands
| Old Command | New Command |
|-------------|-------------|
| `docker-compose up` | `cd config && docker-compose up` |
| `docker-compose build` | `cd config && docker-compose build` |

### Makefile Commands (unchanged)
- `make run-api` - Start FastAPI server
- `make run-web` - Start Streamlit interface  
- `make docker-up` - Start all services
- `make ingest-data` - Run data ingestion

## Import Changes

### Old Import Style (deprecated)
```python
import database as db
from rag import rag
from s3_service import upload_logs_to_s3
```

### New Import Style
```python
from src.database import database as db
from src.core.rag import rag
from src.services.s3_service import upload_logs_to_s3
```

## Benefits of New Structure

1. **Professional Organization**: Clear separation of concerns
2. **Scalability**: Easy to add new components
3. **Maintainability**: Logical code organization
4. **Best Practices**: Follows Python package standards
5. **Docker Optimization**: Better containerization support

## Backward Compatibility

The new structure maintains functionality while providing better organization. All original features work exactly the same way, just with improved file organization and cleaner import paths.