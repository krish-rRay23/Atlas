# Multi-stage production Dockerfile for ATLAS Intelligence Workbench
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Production Runner Stage
FROM python:3.11-slim AS runner

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for enterprise container security
RUN groupadd -g 1001 atlasgroup && \
    useradd -u 1001 -g atlasgroup -m -s /bin/bash atlasuser

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source and data
COPY --chown=atlasuser:atlasgroup . .

# Create writable data directories
RUN mkdir -p data/raw data/processed data/evaluation logs && \
    chown -R atlasuser:atlasgroup /app

USER atlasuser

EXPOSE 8000 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

ENTRYPOINT ["python", "scripts/start_api.py"]
