# PolicyBot - macOS Setup Guide

This guide provides instructions for running PolicyBot on macOS, specifically optimized for Apple Silicon (M1/M2/M3) MacBooks.

## Prerequisites

### 1. Install Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Docker Desktop for Mac
Download and install Docker Desktop from [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

### 3. Install Ollama
```bash
# Option 1: Using Homebrew (recommended)
brew install ollama

# Option 2: Direct download
curl -fsSL https://ollama.ai/install.sh | sh
```

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd policybot
```

### 2. Start Ollama Service
```bash
# Start Ollama service (this will run in the background)
ollama serve
```

### 3. Pull the Required Model
In a new terminal window:
```bash
# Pull the default model used by PolicyBot
ollama pull gemma3n:e4b

# Alternative models you can try:
# ollama pull llama2:7b
# ollama pull mistral:7b
# ollama pull codellama:7b
```

### 4. Verify Ollama is Running
```bash
# Test if Ollama is accessible
curl http://localhost:11434/api/tags
```

You should see a JSON response with available models.

### 5. Build and Run with Docker

#### Option A: Using Docker Compose (Recommended)
```bash
# Build and start the application
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

#### Option B: Using Docker directly
```bash
# Build the image
docker build -t policybot-macos .

# Run the container
docker run -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/db:/app/db \
  -e IN_DOCKER=1 \
  -e OLLAMA_IP=host.docker.internal \
  -e OLLAMA_PORT=11434 \
  --add-host host.docker.internal:host-gateway \
  policybot-macos
```

### 6. Access the Application
Open your browser and navigate to: `http://localhost:8501`

## Local Development (Without Docker)

### 1. Create Python Virtual Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 2. Install Dependencies
```bash
# Install macOS-optimized dependencies
pip install -r requirements-macos.txt
```

### 3. Set Environment Variables
```bash
# Create .env file or export variables
export OLLAMA_PORT=11434
export OLLAMA_IP=localhost
```

### 4. Run the Application
```bash
# Start Streamlit app
streamlit run streamlit_app.py --server.port=8501
```

## Troubleshooting

### Common Issues on macOS

#### 1. Ollama Connection Issues
```bash
# Check if Ollama is running
ps aux | grep ollama

# Restart Ollama if needed
pkill ollama
ollama serve
```

#### 2. Docker Build Issues
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

#### 3. Memory Issues
- Close unnecessary applications to free up RAM
- For M1/M2/M3 Macs with 8GB RAM, consider using smaller models:
```bash
ollama pull phi:2.7b
# Update MODEL_NAME in src/config.py to "phi:2.7b"
```

#### 4. Python Package Conflicts
```bash
# Clean install in virtual environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-macos.txt
```

### Performance Tips for Apple Silicon

1. **Use smaller models for better performance**:
   - `phi:2.7b` - Fast, good for basic queries
   - `llama2:7b` - Balanced performance
   - `mistral:7b` - Good accuracy

2. **Monitor system resources**:
   - Activity Monitor → CPU/Memory tabs
   - Close heavy applications during processing

3. **Optimize Docker settings**:
   - Docker Desktop → Preferences → Resources
   - Allocate 6-8GB RAM for Docker (if you have 16GB+ total)

## Model Configuration

To change the model used by PolicyBot:

1. Pull a different model:
```bash
ollama pull llama2:7b
```

2. Update the configuration in `src/config.py`:
```python
MODEL_NAME = "llama2:7b"  # Change from "gemma3n:e4b"
```

3. Restart the application.

## File Structure for macOS

```
policybot/
├── Dockerfile                    # Updated for macOS compatibility
├── docker-compose.yml           # No GPU requirements
├── requirements-macos.txt       # Apple Silicon optimized
├── src/
│   ├── config.py               # Updated for MPS support
│   └── util/util.py           # Apple Silicon device detection
├── data/                      # PDF files (created automatically)
├── db/                       # SQLite database (created automatically)
├── logs/                     # Application logs (created automatically)
└── chroma/                   # Vector database (created automatically)
```

## Support

For macOS-specific issues:
1. Check that Ollama is running: `curl http://localhost:11434/api/tags`
2. Verify Docker is using Apple Silicon: `docker version`
3. Monitor system resources in Activity Monitor
4. Check application logs: `tail -f logs/app.log`

## Notes

- This setup is optimized for Apple Silicon Macs (M1/M2/M3)
- GPU acceleration is not available (uses CPU/MPS)
- Processing will be slower than NVIDIA GPU setups but still functional
- Consider using smaller models for better performance on laptops