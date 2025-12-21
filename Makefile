# Makefile: docker compose helpers for this repo
# Usage examples:
#   make dev         # start the full stack in dev mode (uses docker-compose.dev.yml)
#   make prod        # start the stack for production
#   make build       # build all images for production
#   make down        # bring down all images for production

# Configurable variables (can be overridden on CLI)
COMPOSE:=docker compose
ENV_FILE:=--env-file ./backend/.env
BASE_FILES:=-f docker-compose.yml
DEV_FILES:=-f docker-compose.yml -f docker-compose.dev.yml
PROJECT_NAME:=policybot
BUILD:=1
MODEL_DOWNLOADER:=model_downloader


.PHONY: help dev prod build down download-models 

help:
	@echo "Makefile targets:"
	@echo "  make dev          - Up stack in dev mode (with docker-compose.dev.yml)"
	@echo "  make prod         - Up stack in production mode"
	@echo "  make build        - Build production images"
	@echo "  make down         - Bring down all prod images"
	@echo "  make download-models - Download required models"

# Development (explicit dev override)
dev:
ifeq ($(BUILD),1)
	$(MAKE) download-models
	$(COMPOSE) $(DEV_FILES) $(ENV_FILE) -p $(PROJECT_NAME)-dev up --build --watch
endif
	$(COMPOSE) $(DEV_FILES) -p $(PROJECT_NAME)-dev up --watch --force-recreate

# Production (default compose only)
prod:
ifeq ($(BUILD),1)
	$(MAKE) download-models
	$(COMPOSE) $(BASE_FILES) $(ENV_FILE) -p $(PROJECT_NAME) up --build -d
endif
	$(COMPOSE) $(BASE_FILES) $(ENV_FILE) -p $(PROJECT_NAME) up  -d


# Build production images only
build:
	$(MAKE) download-models
	$(COMPOSE) $(BASE_FILES) $(ENV_FILE) -p $(PROJECT_NAME) build
	$(COMPOSE) $(DEV_FILES) $(ENV_FILE) -p $(PROJECT_NAME)-dev build

down:
	$(COMPOSE) $(BASE_FILES) -p $(PROJECT_NAME) down 

models: 
	$(COMPOSE) $(BASE_FILES) -p $(PROJECT_NAME)

download-models:
	$(COMPOSE) $(BASE_FILES) $(ENV_FILE) -p $(PROJECT_NAME) build $(MODEL_DOWNLOADER)
	$(COMPOSE) $(BASE_FILES) $(ENV_FILE) -p $(PROJECT_NAME) run --rm $(MODEL_DOWNLOADER)
