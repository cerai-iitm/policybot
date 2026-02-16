# Multi-stage Dockerfile for PolicyBot (root level)
FROM python:3.12.12-slim AS base

# Create non-root user and group
RUN groupadd --gid 1000 appuser && \
	useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home appuser

# Build stage for dependencies
FROM base AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=off \
	PIP_DISABLE_PIP_VERSION_CHECK=on \
	PIP_DEFAULT_TIMEOUT=100

# Install build deps required for compiling some Python packages.
RUN set -eux; \
	apt-get update || true; \
	for i in 1 2 3; do \
	apt-get update && break || sleep 5; \
	done; \
	apt-get install -y --no-install-recommends \
	build-essential \
	libpq-dev \
	curl \
	; \
	rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend requirements and install
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir --upgrade pip && \
	pip install --no-cache-dir -r backend/requirements.txt

# Stage: Build Homepage
FROM node:20-alpine AS homepage-builder
WORKDIR /build
COPY Homepage/package*.json ./
RUN npm ci
COPY Homepage/ .
RUN npm run build

# Stage: Build Chat Frontend
FROM node:20-alpine AS chat-builder
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage: Model downloader
FROM base AS model_downloader

# Create cache directory with proper ownership
RUN mkdir -p /app/cache/huggingface && \
	chown -R appuser:appuser /app

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip && \
	pip install --no-cache-dir huggingface-hub

COPY backend/download_models.py backend/.env ./

VOLUME ["/app/cache/huggingface"]

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	HF_HOME=/app/cache/huggingface \
	HF_TOKEN=""

USER appuser
CMD ["python", "download_models.py"]

# Development stage
FROM base AS development

# Create directories with proper ownership
RUN mkdir -p /app/backend/data /app/backend/src/data /app/backend/logs /app/cache/huggingface /app/static/homepage /app/static/chat && \
    chown -R appuser:appuser /app && \
    chmod 755 /app/backend/data /app/backend/src/data /app/backend/logs /app/cache/huggingface /app/static/homepage /app/static/chat

# Install netcat for database connection check
RUN apt-get update && apt-get install -y --no-install-recommends \
	netcat-openbsd \
	&& rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	HF_HOME=/app/cache/huggingface

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy built static files
COPY --from=homepage-builder /build/dist ./static/homepage
COPY --from=chat-builder /build/dist ./static/chat

# Copy backend code
COPY backend/alembic.ini backend/pyproject.toml backend/populate_db.py ./backend/
COPY backend/migrations/ ./backend/migrations/
COPY backend/pdfs/ ./backend/pdfs/
COPY backend/src/ ./backend/src/

# Copy entrypoint script
COPY backend/entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000
USER appuser

# Use entrypoint for automatic migrations
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["uvicorn", "backend.src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production runner
FROM base AS production

# Create directories with proper ownership
RUN mkdir -p /app/backend/data /app/backend/src/data /app/backend/logs /app/cache/huggingface /app/static/homepage /app/static/chat && \
    chown -R appuser:appuser /app && \
    chmod 755 /app/backend/data /app/backend/src/data /app/backend/logs /app/cache/huggingface /app/static/homepage /app/static/chat

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	HF_HOME=/app/cache/huggingface \
	PYTHONPATH=/app

WORKDIR /app

# Copy site-packages and binaries from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy built static files
COPY --from=homepage-builder /build/dist ./static/homepage
COPY --from=chat-builder /build/dist ./static/chat

RUN apt-get update && apt-get install -y --no-install-recommends \
	netcat-openbsd \
	ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY backend/alembic.ini backend/pyproject.toml ./backend/
COPY backend/migrations/ ./backend/migrations/
COPY backend/src/ ./backend/src/

# Copy entrypoint script
COPY backend/entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000
USER appuser

# Use entrypoint for automatic migrations
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["uvicorn", "backend.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
