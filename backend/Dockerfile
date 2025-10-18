FROM astral/uv:python3.12-trixie-slim

ARG MODE=dev
ENV MODE=${MODE}

WORKDIR /app

# networking: curl, iputils-ping, for google debug: ca-certificates
RUN apt-get update && apt-get install -y \
  build-essential \
  libpq-dev \
  netcat-openbsd \
  ca-certificates \
  curl \
  iputils-ping \
  dnsutils \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY src/ ./src/
COPY .env ./
COPY entrypoint.sh ./
COPY download_models.py ./

RUN uv run download_models.py
RUN mkdir -p data
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
