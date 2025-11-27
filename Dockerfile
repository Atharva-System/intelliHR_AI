FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Accept ENVIRONMENT build argument (default: dev)
ARG ENVIRONMENT=dev
ENV ENVIRONMENT=${ENVIRONMENT}

# Accept build arguments for secrets
ARG API_KEY_1
ARG API_KEY_2
ARG API_KEY_3
ARG MODEL=gemini-2.0-flash
ARG LANGSMITH_API_KEY
ARG LANGSMITH_PROJECT

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Create .env file from build args (if secrets are provided) or copy existing .env file
RUN if [ -n "$API_KEY_1" ]; then \
      echo "API_KEY_1=$API_KEY_1" > .env && \
      [ -n "$API_KEY_2" ] && echo "API_KEY_2=$API_KEY_2" >> .env || true && \
      [ -n "$API_KEY_3" ] && echo "API_KEY_3=$API_KEY_3" >> .env || true && \
      echo "MODEL=$MODEL" >> .env && \
      [ -n "$LANGSMITH_API_KEY" ] && echo "LANGSMITH_API_KEY=$LANGSMITH_API_KEY" >> .env || true && \
      [ -n "$LANGSMITH_PROJECT" ] && echo "LANGSMITH_PROJECT=$LANGSMITH_PROJECT" >> .env || true; \
    else \
      cp .env.${ENVIRONMENT} .env || true; \
    fi

# Create directory for downloaded files
RUN mkdir -p downloaded_files

# Expose the port your FastAPI app uses
EXPOSE 80

# Set environment variables
ENV PYTHONPATH=/app

# Run the FastAPI application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]