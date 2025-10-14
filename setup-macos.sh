#!/bin/bash

# PolicyBot macOS Setup Script
# This script helps set up PolicyBot on macOS with Apple Silicon

set -e

echo "🍎 PolicyBot macOS Setup Script"
echo "================================"

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is designed for macOS only."
    exit 1
fi

# Check for Apple Silicon
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    echo "✅ Detected Apple Silicon ($ARCH)"
else
    echo "⚠️  Detected Intel Mac ($ARCH) - this setup is optimized for Apple Silicon"
fi

echo ""
echo "📋 Checking prerequisites..."

# Check for Homebrew
if command -v brew >/dev/null 2>&1; then
    echo "✅ Homebrew is installed"
else
    echo "❌ Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Check for Docker
if command -v docker >/dev/null 2>&1; then
    echo "✅ Docker is installed"
    if docker info >/dev/null 2>&1; then
        echo "✅ Docker is running"
    else
        echo "⚠️  Docker is installed but not running. Please start Docker Desktop."
        echo "   You can start it from Applications or run: open -a Docker"
        read -p "Press Enter when Docker is running..."
    fi
else
    echo "❌ Docker not found. Please install Docker Desktop for Mac:"
    echo "   https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# Check for Ollama
if command -v ollama >/dev/null 2>&1; then
    echo "✅ Ollama is installed"
else
    echo "🔧 Installing Ollama..."
    if command -v brew >/dev/null 2>&1; then
        brew install ollama
    else
        curl -fsSL https://ollama.ai/install.sh | sh
    fi
fi

echo ""
echo "🚀 Setting up PolicyBot..."

# Start Ollama in background if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "🔧 Starting Ollama service..."
    ollama serve &
    OLLAMA_PID=$!
    echo "   Ollama started with PID: $OLLAMA_PID"
    sleep 3
else
    echo "✅ Ollama service is already running"
fi

# Test Ollama connection
echo "🔍 Testing Ollama connection..."
if curl -s http://localhost:11434/api/tags >/dev/null; then
    echo "✅ Ollama is accessible"
else
    echo "❌ Cannot connect to Ollama. Please check if it's running."
    exit 1
fi

# Pull the default model
echo "📥 Pulling required model (this may take a while)..."
if ollama list | grep -q "gemma3n:e4b"; then
    echo "✅ Model gemma3n:e4b is already available"
else
    echo "   Downloading gemma3n:e4b model..."
    ollama pull gemma3n:e4b
    echo "✅ Model downloaded successfully"
fi

# Build Docker image
echo "🔨 Building Docker image for macOS..."
if [[ -f "docker-compose-macos.yml" ]]; then
    docker-compose -f docker-compose-macos.yml build
    echo "✅ Docker image built successfully"
else
    echo "⚠️  Using default docker-compose.yml"
    docker-compose build
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📚 Next steps:"
echo "1. Start the application:"
if [[ -f "docker-compose-macos.yml" ]]; then
    echo "   docker-compose -f docker-compose-macos.yml up"
else
    echo "   docker-compose up"
fi
echo ""
echo "2. Open your browser to: http://localhost:8501"
echo ""
echo "3. Upload a PDF and start asking questions!"
echo ""
echo "📖 For detailed instructions, see README-macOS.md"
echo ""
echo "🛟 Troubleshooting tips:"
echo "- Check Ollama: curl http://localhost:11434/api/tags"
echo "- View logs: tail -f logs/app.log"
echo "- Monitor resources: Activity Monitor"
echo ""
echo "✨ Enjoy using PolicyBot on your Mac!"