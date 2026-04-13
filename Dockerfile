# Multi-stage Dockerfile for PolicyBot
FROM python:3.12-slim AS base

# Create non-root user and group
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home appuser

# ==============================================================================
# BUILDER STAGE - Install dependencies based on .env config
# ==============================================================================
FROM base AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Copy pyproject, lock, and .env
COPY backend/pyproject.toml backend/uv.lock ./
COPY backend/.env ./

# Build uv sync command based on .env providers
RUN set -e; \
    LLM_PROV=$(grep '^LLM_PROVIDER=' .env | cut -d= -f2 | tr -d '\r\n' || echo "vllm"); \
    EMB_PROV=$(grep '^EMBEDDING_PROVIDER=' .env | cut -d= -f2 | tr -d '\r\n' || echo "vllm"); \
    RERANK_PROV=$(grep '^RERANKER_PROVIDER=' .env | cut -d= -f2 | tr -d '\r\n' || echo "tei"); \
    echo "Installing: llm-${LLM_PROV}, embedding-${EMB_PROV}, reranker-${RERANK_PROV}"; \
    uv sync --no-install-project \
    --extra "llm-${LLM_PROV}" \
    --extra "embedding-${EMB_PROV}" \
    --extra "reranker-${RERANK_PROV}"

# ==============================================================================
# Stage: Build Frontend (static export) - COMMENTED OUT
# ==============================================================================
# FROM node:20-alpine AS frontend-builder
#
# WORKDIR /build
#
# COPY frontend/package*.json ./
# RUN npm ci
#
# COPY frontend/ .
# RUN npm run build

# ==============================================================================
# Development stage
# ==============================================================================
FROM base AS development

# Create directories with proper ownership
RUN mkdir -p /app/backend/logs /app/static/frontend && \
    chown -R appuser:appuser /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend

WORKDIR /app

# Copy .venv from builder - no reinstall needed
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy built frontend files (static export -> out folder) - COMMENTED OUT
# COPY --from=frontend-builder /build/out ./static/frontend

# Copy backend code (new structure)
COPY backend/app/ ./backend/app/
COPY backend/api/ ./backend/api/
COPY backend/db/ ./backend/db/
COPY backend/providers/ ./backend/providers/
COPY backend/services/ ./backend/services/
COPY backend/core/ ./backend/core/
COPY backend/alembic.ini ./backend/
COPY backend/migrations/ ./migrations/
COPY backend/.env ./backend/
COPY backend/entrypoint.sh ./

EXPOSE 8000
USER appuser

# Run app with hot reload
ENTRYPOINT [ "./entrypoint.sh" ]
CMD ["sh", "-c", "cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]

# ==============================================================================
# Production stage
# ==============================================================================
FROM base AS production

# Create directories with proper ownership
RUN mkdir -p /app/backend/logs /app/static/frontend && \
    chown -R appuser:appuser /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend

WORKDIR /app

# Copy .venv from builder - no reinstall needed
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy built frontend files (static export -> out folder) - COMMENTED OUT
# COPY --from=frontend-builder /build/out ./static/frontend

# Install runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY backend/app/ ./backend/app/
COPY backend/api/ ./backend/api/
COPY backend/db/ ./backend/db/
COPY backend/providers/ ./backend/providers/
COPY backend/services/ ./backend/services/
COPY backend/core/ ./backend/core/
COPY backend/alembic.ini ./backend/
COPY backend/migrations/ ./migrations/

EXPOSE 8000
USER appuser

# Run app
CMD ["sh", "-c", "cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
