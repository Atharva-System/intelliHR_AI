FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Accept ENVIRONMENT build argument (default: dev)
ARG ENVIRONMENT=dev
ENV ENVIRONMENT=${ENVIRONMENT}

# Accept build arguments for all environment variables
ARG API_KEY_1
ARG API_KEY_2
ARG API_KEY_3
ARG MODEL
ARG MAX_OUTPUT_TOKENS
ARG TEMPERATURE
ARG SAVE_DIR
ARG MAX_FILE_SIZE
ARG MAX_FILES_PER_REQUEST
ARG MINIMUM_ELIGIBLE_SCORE
ARG ALLOWED_FILE_TYPES
ARG LOG_LEVEL
ARG LOG_FILE
ARG API_HOST
ARG API_PORT
ARG DEBUG_MODE
ARG LANGSMITH_API_KEY
ARG LANGSMITH_PROJECT

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Create .env file from build args only
RUN { \
      [ -n "$API_KEY_1" ] && echo "API_KEY_1=$API_KEY_1"; \
      [ -n "$API_KEY_2" ] && echo "API_KEY_2=$API_KEY_2"; \
      [ -n "$API_KEY_3" ] && echo "API_KEY_3=$API_KEY_3"; \
      [ -n "$MODEL" ] && echo "MODEL=$MODEL"; \
      [ -n "$MAX_OUTPUT_TOKENS" ] && echo "MAX_OUTPUT_TOKENS=$MAX_OUTPUT_TOKENS"; \
      [ -n "$TEMPERATURE" ] && echo "TEMPERATURE=$TEMPERATURE"; \
      [ -n "$SAVE_DIR" ] && echo "SAVE_DIR=$SAVE_DIR"; \
      [ -n "$MAX_FILE_SIZE" ] && echo "MAX_FILE_SIZE=$MAX_FILE_SIZE"; \
      [ -n "$MAX_FILES_PER_REQUEST" ] && echo "MAX_FILES_PER_REQUEST=$MAX_FILES_PER_REQUEST"; \
      [ -n "$MINIMUM_ELIGIBLE_SCORE" ] && echo "MINIMUM_ELIGIBLE_SCORE=$MINIMUM_ELIGIBLE_SCORE"; \
      [ -n "$ALLOWED_FILE_TYPES" ] && echo "ALLOWED_FILE_TYPES=$ALLOWED_FILE_TYPES"; \
      [ -n "$LOG_LEVEL" ] && echo "LOG_LEVEL=$LOG_LEVEL"; \
      [ -n "$LOG_FILE" ] && echo "LOG_FILE=$LOG_FILE"; \
      [ -n "$API_HOST" ] && echo "API_HOST=$API_HOST"; \
      [ -n "$API_PORT" ] && echo "API_PORT=$API_PORT"; \
      [ -n "$DEBUG_MODE" ] && echo "DEBUG_MODE=$DEBUG_MODE"; \
      [ -n "$LANGSMITH_API_KEY" ] && echo "LANGSMITH_API_KEY=$LANGSMITH_API_KEY"; \
      [ -n "$LANGSMITH_PROJECT" ] && echo "LANGSMITH_PROJECT=$LANGSMITH_PROJECT"; \
    } > .env

# Create directory for downloaded files
RUN mkdir -p downloaded_files

# Expose the port your FastAPI app uses
EXPOSE 80

# Set environment variables
ENV PYTHONPATH=/app

# Run the FastAPI application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]