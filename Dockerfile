FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application structure
COPY src/ src/
COPY scripts/ scripts/
COPY config/ config/
COPY data/ data/

# Set Python path to include src directory
ENV PYTHONPATH="/app:${PYTHONPATH}"

EXPOSE 8000 8501

# Use an environment variable to choose between FastAPI and Streamlit
ENV APP_TYPE=fastapi

CMD if [ "$APP_TYPE" = "streamlit" ]; then \
        streamlit run src/api/web_interface.py --server.port 8501 --server.address 0.0.0.0; \
    else \
        uvicorn src.api.main_api:app --host 0.0.0.0 --port 8000; \
    fi
