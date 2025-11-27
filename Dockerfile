FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Accept ENVIRONMENT build argument (default: dev)
ARG ENVIRONMENT=dev
ENV ENVIRONMENT=${ENVIRONMENT}

# Accept .env file content as a single build argument
ARG ENV_FILE_CONTENT

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Create .env file from build arg (entire .env file content passed as one arg)
RUN if [ -n "$ENV_FILE_CONTENT" ]; then \
      echo "$ENV_FILE_CONTENT" > .env; \
    fi

# Create directory for downloaded files
RUN mkdir -p downloaded_files

# Expose the port your FastAPI app uses
EXPOSE 80

# Set environment variables
ENV PYTHONPATH=/app

# Run the FastAPI application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]