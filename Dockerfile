# Dockerfile for AI Voice Assistant FastAPI Backend

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements_fastapi.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_fastapi.txt

# Copy application files
COPY backend_fastapi.py .
COPY *.gguf . 2>/dev/null || true

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/')"

# Run the application
CMD ["python", "backend_fastapi.py"]
