#!/bin/bash
# filepath: /home/Gautam/Projects/cerai/policybot/debug_ollama.sh


# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Timestamp function
timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

# Logging function
log() {
    echo -e "${GREEN}[$(timestamp)]${NC} $1" | tee -a debug_execution.log
}

warn() {
    echo -e "${YELLOW}[$(timestamp)] WARNING:${NC} $1" | tee -a debug_execution.log
}

error() {
    echo -e "${RED}[$(timestamp)] ERROR:${NC} $1" | tee -a debug_execution.log
}

echo "🔧 Starting Ollama Debug Process..." | tee debug_execution.log
echo "=================================================" | tee -a debug_execution.log

# 1. Check host machine Ollama status
log "📋 Checking host machine Ollama status..."
echo "Host Ollama Status:" | tee -a debug_execution.log
netstat -tlnp | grep 11434 | tee -a debug_execution.log || echo "No Ollama listening on 11434" | tee -a debug_execution.log

ps aux | grep ollama | grep -v grep | tee -a debug_execution.log || echo "No Ollama processes found" | tee -a debug_execution.log

echo "OLLAMA_HOST environment variable: ${OLLAMA_HOST:-not_set}" | tee -a debug_execution.log
echo "=================================================" | tee -a debug_execution.log

# 2. Test localhost Ollama connectivity (IPv4 and IPv6) - Continue on failure
log "🏠 Testing localhost Ollama connectivity..."

# Test IPv4 localhost connection
log "📡 Testing IPv4 localhost connection to Ollama..."
if ping -c 2 127.0.0.1 > /dev/null 2>&1; then
    log "✅ IPv4 localhost ping: SUCCESS"
    
    # Test HTTP to IPv4 localhost
    if curl -s --connect-timeout 5 http://127.0.0.1:11434/api/version > /dev/null 2>&1; then
        log "✅ IPv4 localhost HTTP: SUCCESS"
        curl -s http://127.0.0.1:11434/api/version | tee -a debug_execution.log || warn "Failed to get version details"
    else
        error "❌ IPv4 localhost HTTP: FAILED (continuing anyway)"
    fi
else
    error "❌ IPv4 localhost ping: FAILED (continuing anyway)"
fi

# Test IPv6 localhost connection  
log "📡 Testing IPv6 localhost connection to Ollama..."
if ping6 -c 2 ::1 > /dev/null 2>&1 || ping -6 -c 2 ::1 > /dev/null 2>&1; then
    log "✅ IPv6 localhost ping: SUCCESS"
    
    # Test HTTP to IPv6 localhost
    if curl -s --connect-timeout 5 http://[::1]:11434/api/version > /dev/null 2>&1; then
        log "✅ IPv6 localhost HTTP: SUCCESS"
        curl -s http://[::1]:11434/api/version | tee -a debug_execution.log || warn "Failed to get IPv6 version details"
    else
        error "❌ IPv6 localhost HTTP: FAILED (continuing anyway)"
    fi
else
    error "❌ IPv6 localhost ping: FAILED (continuing anyway)"
fi

# Test actual generation on localhost IPv4 - Continue on failure
log "🧠 Testing Ollama generation on IPv4 localhost..."
if curl -X POST http://127.0.0.1:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"gemma3n:e4b","prompt":"IPv4 localhost test","stream":false,"options":{"temperature":0.1}}' \
  2>&1 | tee -a debug_execution.log; then
    log "✅ IPv4 Ollama generation: SUCCESS"
else
    error "❌ IPv4 Ollama generation: FAILED (continuing anyway)"
fi

# Test actual generation on localhost IPv6 - Continue on failure  
log "🧠 Testing Ollama generation on IPv6 localhost..."
if curl -X POST http://[::1]:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"gemma3n:e4b","prompt":"IPv6 localhost test","stream":false,"options":{"temperature":0.1}}' \
  2>&1 | tee -a debug_execution.log; then
    log "✅ IPv6 Ollama generation: SUCCESS"
else
    error "❌ IPv6 Ollama generation: FAILED (continuing anyway)"
fi

echo "=================================================" | tee -a debug_execution.log

# 3. Test Gemini API directly from host - Continue on failure
log "🤖 Testing Gemini API directly from host..."
GEMINI_API_KEY=$(grep "GEMINI_API_KEY=" backend/.env 2>/dev/null | cut -d'=' -f2 | tr -d '"' | tr -d "'")

if [ -n "$GEMINI_API_KEY" ] && [ "$GEMINI_API_KEY" != "" ]; then
    log "✅ Found Gemini API key (first 5 chars): ${GEMINI_API_KEY:0:5}..."
    
    # Test Gemini - Continue on failure
    if curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$GEMINI_API_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "contents": [
          {
            "parts": [
              {
                "text": "Testing if the Gemini LLM is working. Return Gemini Response Okay if you get this prompt."
              }
            ]
          }
        ],
        "generationConfig": {
          "temperature": 0.1,
          "maxOutputTokens": 1000
        }
      }' \
      2>&1 | tee -a debug_execution.log; then
        log "✅ Gemini API test: SUCCESS"
    else
        error "❌ Gemini API test: FAILED (continuing anyway)"
    fi
else
    error "❌ GEMINI_API_KEY not found or empty (continuing anyway)"
fi

echo "=================================================" | tee -a debug_execution.log

# 4. Rebuild Docker containers - Continue on failure
log "🔨 Rebuilding Docker containers..."
if docker-compose down 2>&1 | tee -a debug_execution.log; then
    log "✅ Docker compose down: SUCCESS"
else
    error "❌ Docker compose down: FAILED (continuing anyway)"
fi

if docker-compose build 2>&1 | tee -a debug_execution.log; then
    log "✅ Docker compose build: SUCCESS"
else
    error "❌ Docker compose build: FAILED (continuing anyway)"
fi

if docker-compose up -d 2>&1 | tee -a debug_execution.log; then
    log "✅ Docker compose up: SUCCESS"
else
    error "❌ Docker compose up: FAILED (continuing anyway)"
fi

# Wait for containers to be ready
log "⏳ Waiting for containers to be ready..."
sleep 10

# 5. Check container status - Continue on failure
log "📦 Checking container status..."
docker-compose ps 2>&1 | tee -a debug_execution.log || warn "Failed to get container status (continuing anyway)"

# 6. Run debug script with full output capture - Continue on failure
log "🧪 Running debug script..."
echo "=================================================" | tee -a debug_execution.log
echo "DOCKER CONSOLE OUTPUT:" | tee -a debug_execution.log
echo "=================================================" | tee -a debug_execution.log

# Capture both stdout and stderr from docker exec - Continue on failure
if docker-compose exec -T backend uv run src/debug/debug_llm.py 2>&1 | tee -a debug_execution.log; then
    log "✅ Python debug script: SUCCESS"
else
    error "❌ Python debug script: FAILED (continuing anyway)"
fi

# 7. Copy debug_test.log from container to host - Continue on failure
log "📄 Copying debug_test.log from container..."
if docker-compose exec -T backend cat logs/debug_test.log > container_debug_test.log 2>/dev/null; then
    log "✅ Log file copy: SUCCESS"
else
    warn "❌ Could not copy debug_test.log from container (continuing anyway)"
fi

# 8. Summary - Always runs
log "📊 Debug Summary:"
echo "=================================================" | tee -a debug_execution.log
echo "Files created:" | tee -a debug_execution.log
echo "- debug_execution.log (this file)" | tee -a debug_execution.log
echo "- container_debug_test.log (from container)" | tee -a debug_execution.log
echo "=================================================" | tee -a debug_execution.log

log "✅ Debug process completed!"
log "📁 Check debug_execution.log for full output"
log "📁 Check container_debug_test.log for container debug logs"
echo "=================================================" | tee -a debug_execution.log