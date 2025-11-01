FROM python:3.12-slim-bookworm AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 

RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  libpq-dev \
  curl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
  pip install --no-cache-dir -r requirements.txt

COPY download_models.py .env ./
RUN python download_models.py

FROM python:3.12-slim-bookworm AS final

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  MODE=${MODE:-prod}

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# TODO: Remove these after debugging curl, iputils-ping, dnsutils
RUN apt-get update && apt-get install -y --no-install-recommends \
  netcat-openbsd \
  ca-certificates \
  curl \ 
  iputils-ping \
  dnsutils \
  && rm -rf /var/lib/apt/lists/*

COPY src/ ./src/
COPY .env ./
COPY entrypoint.sh ./
COPY download_models.py ./

RUN mkdir -p /root/.cache/huggingface data

RUN chmod +x entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
