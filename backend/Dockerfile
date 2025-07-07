# backend/Dockerfile
FROM python:3.11.6-slim

WORKDIR /app

# Fix TLS errors with MongoDB Atlas
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    libffi-dev \
    ca-certificates \
    curl \
    build-essential \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy source
COPY . /app

# Install Python deps
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
