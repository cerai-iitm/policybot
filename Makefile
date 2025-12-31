# Makefile: Docker Compose helpers for PolicyBot
# 
# Main workflows:
#   make prod        # Complete production deployment (build → models → start)
#   make dev         # Development with hot-reload (use BUILD=1 for first run)
#   make clean       # Stop all containers (keep data)
# 
# Run 'make help' for full reference

# Configurable variables (can be overridden on CLI)
COMPOSE:=docker compose
ENV_FILE:=--env-file ./backend/.env
BASE_FILES:=-f docker-compose.yml
DEV_FILES:=-f docker-compose.yml -f docker-compose.dev.yml
PROJECT_NAME:=policybot
BUILD:=1
MODEL_DOWNLOADER:=model_downloader

help:
	@echo ""
	@echo "PolicyBot - Makefile Target Reference"
	@echo "====================================="
	@echo ""
	@echo "PRODUCTION (Main Workflow):"
	@echo "  make prod              Build + Download models + Start stack"
	@echo "  make build-prod        Build production images only"
	@echo "  make download-models   Download/update LLM models"
	@echo "  make prod-down         Stop production services"
	@echo ""
	@echo "DEVELOPMENT:"
	@echo "  make dev               Start dev with hot-reload"
	@echo "  make dev BUILD=1       Rebuild images, then start"
	@echo "  make dev-down          Stop development services"
	@echo ""
	@echo "CLEANUP:"
	@echo "  make clean             Stop all containers (keep volumes)"
	@echo "  make clean-volumes     Stop all + delete data (DESTRUCTIVE)"
	@echo ""
	@echo "INFORMATION:"
	@echo "  make help              Show this message"
	@echo ""

# ==============================================================================
# PRODUCTION TARGETS
# ==============================================================================

# Complete automated production workflow
.PHONY: prod
prod:
	@echo "=========================================="
	@echo "PRODUCTION DEPLOYMENT WORKFLOW"
	@echo "=========================================="
	@echo ""
	@echo "Step 1: Building production images..."
	$(COMPOSE) $(BASE_FILES) $(ENV_FILE) -p $(PROJECT_NAME) build
	@echo ""
	@echo "Step 2: Downloading LLM models (this may take a few minutes)..."
	$(MAKE) download-models
	@echo ""
	@echo "Step 3: Starting production services..."
	$(COMPOSE) $(BASE_FILES) $(ENV_FILE) -p $(PROJECT_NAME) up -d
	@echo ""
	@echo "Production stack is running!"
	@echo "Access at: http://localhost/policybot"

# Build production images only (no models, no startup)
.PHONY: build-prod
build-prod:
	@echo "Building production images..."
	$(COMPOSE) $(BASE_FILES) $(ENV_FILE) -p $(PROJECT_NAME) build
	@echo "Build complete. Run 'make prod' to start."

# Download/cache LLM models
.PHONY: download-models
download-models:
	@echo "Building model downloader image..."
	$(COMPOSE) $(BASE_FILES) $(ENV_FILE) -p $(PROJECT_NAME) build $(MODEL_DOWNLOADER)
	@echo "Downloading/caching models (this may take several minutes)..."
	$(COMPOSE) $(BASE_FILES) $(ENV_FILE) -p $(PROJECT_NAME) run --rm $(MODEL_DOWNLOADER)
	@echo "Models ready!"

# Stop production services
.PHONY: prod-down
prod-down:
	@echo "Stopping production services..."
	$(COMPOSE) $(BASE_FILES) -p $(PROJECT_NAME) down
	@echo "Production services stopped."

# ==============================================================================
# DEVELOPMENT TARGETS
# ==============================================================================

# Development with hot-reload, optional rebuild
.PHONY: dev
dev:
ifeq ($(BUILD),1)
	@echo "Building development images..."
	$(MAKE) download-models
	$(COMPOSE) $(DEV_FILES) $(ENV_FILE) -p $(PROJECT_NAME)-dev up --build --watch
else
	@echo "Starting development services (no rebuild)..."
	$(COMPOSE) $(DEV_FILES) $(ENV_FILE) -p $(PROJECT_NAME)-dev up --watch
endif

# Stop development services
.PHONY: dev-down
dev-down:
	@echo "Stopping development services..."
	$(COMPOSE) $(DEV_FILES) -p $(PROJECT_NAME)-dev down
	@echo "Development services stopped."

# ==============================================================================
# CLEANUP TARGETS
# ==============================================================================

# Safe cleanup: stops containers, keeps volumes
.PHONY: clean
clean:
	@echo "Stopping all containers..."
	$(COMPOSE) $(BASE_FILES) $(DEV_FILES) -p $(PROJECT_NAME) -p $(PROJECT_NAME)-dev down
	@echo "Containers stopped. Data preserved in volumes."

# Aggressive cleanup: removes everything including volumes
.PHONY: clean-volumes
clean-volumes:
	@echo "WARNING: This will DELETE all data in volumes!"
	@echo "Models cache, database, and embeddings will be lost."
	@echo ""
	@read -p "Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		$(COMPOSE) $(BASE_FILES) $(DEV_FILES) -p $(PROJECT_NAME) -p $(PROJECT_NAME)-dev down -v; \
		docker system prune -f; \
		echo "Full cleanup complete. All data removed."; \
	else \
		echo "Cleanup cancelled."; \
	fi
