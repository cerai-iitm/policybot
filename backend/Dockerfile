FROM astral/uv:python3.12-trixie-slim

ARG MODE=dev
ENV MODE=${MODE}

WORKDIR /app

RUN apt-get update && apt-get install -y \
  build-essential \
  libpq-dev \
  netcat-openbsd \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY src/ ./src/
COPY .env ./
COPY entrypoint.sh ./

RUN mkdir -p data
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
