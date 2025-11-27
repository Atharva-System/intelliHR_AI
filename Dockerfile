FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Create directory for downloaded files
RUN mkdir -p downloaded_files

# Expose the port your FastAPI app uses
EXPOSE 80

# Set environment variables
ENV PYTHONPATH=/app

# Run the FastAPI application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]