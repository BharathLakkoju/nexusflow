FROM python:3.11-slim

# System dependencies (tesseract for OCR, build tools)
RUN apt-get update && apt-get install -y \
  tesseract-ocr \
  tesseract-ocr-eng \
  libpq-dev \
  gcc \
  g++ \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
  pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Render sets $PORT)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "import httpx; httpx.get('http://localhost:${PORT:-8000}/health').raise_for_status()"

# Run with uvicorn; $PORT is set by Render
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --loop asyncio
