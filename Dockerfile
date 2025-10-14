FROM python:3.12.11-slim-bookworm

WORKDIR /app

# Install system dependencies for ARM64/Apple Silicon compatibility
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    tesseract-ocr \
    zlib1g-dev \
    libmagic1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

# Copy macOS-optimized requirements for Apple Silicon
COPY requirements-macos.txt /app/requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]