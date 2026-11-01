# Production Dockerfile for Assessment Portal
FROM python:3.12-slim

# Install system dependencies, compilers & runtimes for code execution
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    default-jdk-headless \
    gcc \
    g++ \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy application files
COPY server.py app.js styles.css index.html create_admin.py ./
COPY runner ./runner

# Create persistent data directory
RUN mkdir -p /app/data

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    ASSESSMENT_HOST=0.0.0.0 \
    ASSESSMENT_PORT=8000 \
    ASSESSMENT_DATA_DIR=/app/data

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

ENTRYPOINT ["python3", "server.py"]

