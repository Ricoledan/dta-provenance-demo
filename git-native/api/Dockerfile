# API Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install API dependencies
RUN pip install --no-cache-dir \
    fastapi>=0.100 \
    uvicorn>=0.23 \
    httpx>=0.24

# Copy source code
COPY . /app

# Install the package
RUN pip install -e .

# Create repo directory
RUN mkdir -p /repo

EXPOSE 8000

# Run the API server
CMD ["python", "-m", "src.cli", "serve", "--host", "0.0.0.0", "--port", "8000", "--repo", "/repo"]
