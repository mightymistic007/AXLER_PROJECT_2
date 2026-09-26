# Base Python image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies required for compiling PyArrow/snappy
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libsnappy-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Set default command for lakehouse consumer
CMD ["python", "iceberg_manager.py"]