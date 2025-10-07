FROM python:3.11.12-slim
# Set build-time argument for mode (default: dev)
ARG MODE=dev
ENV MODE=${MODE}

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source code
COPY src/ ./src

# Copy .env if needed
COPY .env ./

EXPOSE 8000

# Run the appropriate command based on MODE
CMD if [ "$MODE" = "prod" ]; then \
      uvicorn src.main:app --host 0.0.0.0 --port 8000; \
    else \
      uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload; \
    fi
