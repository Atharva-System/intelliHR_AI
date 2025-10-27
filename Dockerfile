FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Accept ENVIRONMENT build argument (default: dev)
ARG ENVIRONMENT=dev
ENV ENVIRONMENT=${ENVIRONMENT}

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Copy the correct .env file
COPY .env.${ENVIRONMENT} .env

# Create directory for downloaded files
RUN mkdir -p downloaded_files

# Expose the port your FastAPI app uses (default is 2001)
EXPOSE 2001

# Set environment variables
ENV PYTHONPATH=/app

# Run the FastAPI application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "2001"]