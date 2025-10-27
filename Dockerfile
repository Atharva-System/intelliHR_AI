FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable stdout/stderr buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies often required for image processing, PDFs, and building some wheels
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        g++ \
        git \
        libjpeg-dev \
        zlib1g-dev \
        poppler-utils \
        tesseract-ocr \
        libpoppler-dev \
        libmagic1 \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copy application source
COPY . /app

# Ensure the app package is importable
ENV PYTHONPATH=/app

# Default port used by this FastAPI app
EXPOSE 8000

# Run with uvicorn. The project exposes the FastAPI app in `app.main:app`.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
