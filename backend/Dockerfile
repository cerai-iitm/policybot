# Multi-stage Dockerfile for backend
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

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip && \
	pip install --no-cache-dir -r requirements.txt

# Downloading models single stage 
FROM base AS model_downloader

# Create cache directory with proper ownership
RUN mkdir -p /app/cache/huggingface && \
	chown -R appuser:appuser /app

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip && \
	pip install --no-cache-dir huggingface-hub

COPY download_models.py .env ./

VOLUME [ "/app/cache/huggingface" ]

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	HF_HOME=/app/cache/huggingface \
	TRANSFORMERS_CACHE=/app/cache/huggingface

USER appuser
CMD [ "python", "download_models.py" ]

# Development stage
FROM base AS development

# Create directories with proper ownership
RUN mkdir -p /app/data /app/logs /app/cache/huggingface && \
	chown -R appuser:appuser /app && \
	chmod 755 /app/data /app/logs /app/cache/huggingface

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	HF_HOME=/app/cache/huggingface \
	TRANSFORMERS_CACHE=/app/cache/huggingface

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY src/ ./src/

EXPOSE 8000
USER appuser
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production runner
FROM base AS production

# Create directories with proper ownership
RUN mkdir -p /app/data /app/logs /app/cache/huggingface && \
	chown -R appuser:appuser /app && \
	chmod 755 /app/data /app/logs /app/cache/huggingface

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	HF_HOME=/app/cache/huggingface \
	TRANSFORMERS_CACHE=/app/cache/huggingface

WORKDIR /app

# Copy site-packages and binaries from builder so we don't reinstall at runtime
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

RUN apt-get update && apt-get install -y --no-install-recommends \
	netcat-openbsd \
	ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

COPY src/ ./src/

EXPOSE 8000
USER appuser
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
