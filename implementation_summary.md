# PolicyBot Backend Implementation Summary

**Version:** 2.0  
**Purpose:** Software Specification & Implementation Guide  
**Related:** [plan.md](./plan.md) - Detailed refactoring plan

---

## 1. Project Overview

**PolicyBot** is an AI-powered document processing and RAG (Retrieval-Augmented Generation) API. It allows users to:

- Upload PDF documents organized into notebooks
- Process PDFs through AI pipelines (text extraction, chunking, embeddings, summaries)
- Chat with documents using natural language
- Get AI-generated suggested questions based on document content

### Core Features

| Feature | Description |
|---------|-------------|
| User Authentication | JWT-based auth with register/login |
| Notebook Management | Create, list, delete notebooks (user-isolated) |
| PDF Processing | Upload, process, track status, delete PDFs |
| RAG Chat | Query documents with AI, get context chunks |
| Chat History | Persistent chat history per user/session |
| Suggested Questions | AI-generated follow-up questions |

### Target Users

- Knowledge workers needing to query policy documents
- Teams organizing and querying PDF repositories
- Any use case requiring document Q&A with RAG

---

## 2. Technology Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Database | PostgreSQL (async with asyncpg) |
| ORM | SQLAlchemy 2.0 (async) |
| Vector Store | Qdrant |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Validation | Pydantic v2 |
| LLM Integration | LangChain (multiple providers) |
| Logging | structlog |
| Deployment | Gunicorn + Uvicorn workers |

---

## 3. Complete Folder Structure

```
backend/
├── app/                          # Application entry point
│   ├── __init__.py
│   ├── main.py                  # FastAPI app creation, lifespan, CORS
│   └── config.py               # Settings (Pydantic, lru_cache)
│
├── api/                        # HTTP layer
│   ├── __init__.py
│   ├── deps.py                 # Dependencies (get_current_user, get_db)
│   ├── errors.py              # Custom HTTP exceptions
│   ├── router.py              # Main router combining all routes
│   ├── schemas/               # Pydantic request/response models
│   │   ├── __init__.py
│   │   ├── base.py           # CustomBase (shared config)
│   │   ├── auth.py           # RegisterRequest, LoginRequest, TokenResponse, UserResponse
│   │   ├── notebook.py       # NotebookCreateRequest, NotebookResponse, NotebookListResponse
│   │   ├── pdf.py            # PDFUploadResponse, PDFListResponse, PDFSummaryResponse
│   │   └── chat.py            # ChatQueryRequest, ChatResponse, SuggestedQueriesResponse
│   └── routes/                # Route handlers
│       ├── __init__.py
│       ├── auth.py           # /auth/register, /auth/login
│       ├── notebooks.py      # CRUD for notebooks
│       ├── pdfs.py           # Upload, list, status, delete PDFs
│       └── chat.py           # /chat/query, /chat/history, /chat/suggested-queries
│
├── core/                       # Cross-cutting concerns
│   ├── __init__.py
│   ├── security.py            # JWT create/verify, password hash/verify
│   ├── prompts.py            # All LLM prompt templates
│   └── logger.py             # Logging setup (structlog)
│
├── db/                        # Data layer
│   ├── __init__.py
│   ├── base.py               # SQLAlchemy declarative Base
│   ├── session.py            # AsyncSession factory, get_db()
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py           # User table (id, email, hashed_password, full_name, created_at)
│   │   ├── notebook.py        # Notebook table (id, notebook_id, user_id FK, title, description)
│   │   ├── pdf.py            # PDF table (id, notebook_id FK, file_name, file_path, processing_status)
│   │   └── chat_message.py   # ChatMessage table (id, user_id FK, session_id, role, content)
│   └── repositories/         # Data access layer
│       ├── __init__.py
│       ├── base.py           # BaseRepository (generic CRUD)
│       ├── user_repo.py      # UserRepository (get_by_email, create_user)
│       ├── notebook_repo.py  # NotebookRepository (get_by_user, get_by_user_and_notebook_id)
│       ├── pdf_repo.py       # PDFRepository (get_by_notebook, get_by_notebook_and_filename)
│       └── chat_repo.py      # ChatRepository (get_session_messages, add_message)
│
├── services/                 # Business logic layer
│   ├── __init__.py
│   ├── auth_service.py       # register, login, get_user_by_id
│   ├── notebook_service.py   # create, list, get, delete (user-isolated)
│   ├── pdf_service.py        # upload, list, get_status, delete (user-isolated)
│   └── chat_service.py       # get_session_history, save_message, validate_notebook_access
│
├── providers/               # External integrations (factory pattern)
│   ├── __init__.py
│   ├── base.py             # Abstract base classes (BaseLLM, BaseEmbeddings, BaseReranker)
│   │
│   ├── llm/               # LLM providers
│   │   ├── __init__.py
│   │   ├── factory.py     # LLMFactory.get(provider, model) -> BaseLLM
│   │   ├── base.py        # BaseLLM (generate, generate_stream)
│   │   ├── ollama.py      # OllamaLLM (ChatOllama wrapper)
│   │   ├── gemini.py      # GeminiLLM (ChatGoogleGenerativeAI wrapper)
│   │   └── openai.py      # OpenAILLM (ChatOpenAI for vLLM/OpenAI compatible)
│   │
│   ├── embedding/         # Embedding providers
│   │   ├── __init__.py
│   │   ├── factory.py     # EmbeddingFactory.get(provider, model) -> BaseEmbeddings
│   │   ├── base.py        # BaseEmbeddings (embed_query, embed_documents)
│   │   ├── sentence_transformers.py  # HuggingFaceEmbeddings
│   │   └── vllm.py        # OpenAIEmbeddings for vLLM
│   │
│   └── reranker/         # Reranker providers
│       ├── __init__.py
│       ├── factory.py     # RerankerFactory.get(provider) -> BaseReranker
│       ├── base.py        # BaseReranker (rerank)
│       ├── flag.py        # FlagRerankerWrapper (flagembedding)
│       └── tei.py         # TEIReranker (HTTP client)
│
└── utils/                  # Utilities
    ├── __init__.py
    ├── pdf_processor.py   # PDF text extraction, chunking (from existing code)
    └── vector_store.py    # Qdrant operations (upsert, query, delete)
```

---

## 4. Implementation Phases

| Phase | Description | Files to Create |
|-------|-------------|-----------------|
| 1 | Foundation - Config, Main, Logger, Prompts | app/config.py, app/main.py, core/logger.py, core/prompts.py |
| 2 | Database - Models | db/base.py, db/session.py, db/models/*.py |
| 3 | Security - JWT & Passwords | core/security.py |
| 4 | Repositories - Data Access | db/repositories/base.py, user_repo.py, notebook_repo.py, pdf_repo.py, chat_repo.py |
| 5 | API Dependencies | api/deps.py |
| 6 | API Schemas | api/schemas/base.py, auth.py, notebook.py, pdf.py, chat.py |
| 7 | Services - Business Logic | services/auth_service.py, notebook_service.py, pdf_service.py, chat_service.py |
| 8 | API Routes | api/routes/auth.py, notebooks.py, pdfs.py, chat.py |
| 9 | Error Handling | api/errors.py, api/router.py |
| 10 | Providers | providers/base.py, providers/*/factory.py, providers/*/*.py |
| 11 | Utils | utils/pdf_processor.py, utils/vector_store.py |

---

## 5. All API Endpoints

### Base URL: `/api`

---

### 5.1 Authentication (No Auth Required)

#### POST /api/auth/register
**Description:** Register a new user

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2025-04-11T10:00:00"
}
```

**Validation:**
- email: Valid email format (EmailStr)
- password: String, no specific validation currently
- full_name: Optional string

---

#### POST /api/auth/login
**Description:** Login and receive JWT tokens

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error (401):** Invalid email or password

---

### 5.2 Notebooks (Auth Required)

#### POST /api/notebooks
**Description:** Create a new notebook

**Headers:** `Authorization: Bearer <access_token>`

**Request:**
```json
{
  "title": "My Policy Documents",
  "description": "Collection of company policies"
}
```

**Response (201):**
```json
{
  "id": 1,
  "notebook_id": "nb_a1b2c3d4",
  "title": "My Policy Documents",
  "description": "Collection of company policies",
  "created_at": "2025-04-11T10:00:00"
}
```

**Validation:**
- title: Required, string, max 255 chars
- description: Optional, max 1000 chars

---

#### GET /api/notebooks
**Description:** List all notebooks for current user

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
  "notebooks": [
    {
      "id": 1,
      "notebook_id": "nb_a1b2c3d4",
      "title": "My Policy Documents",
      "description": "Collection of company policies",
      "created_at": "2025-04-11T10:00:00"
    }
  ]
}
```

**Note:** Only returns notebooks owned by current user (user isolation)

---

#### GET /api/notebooks/{notebook_id}
**Description:** Get a specific notebook

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
  "id": 1,
  "notebook_id": "nb_a1b2c3d4",
  "title": "My Policy Documents",
  "description": "Collection of company policies",
  "created_at": "2025-04-11T10:00:00"
}
```

**Error (404):** Notebook not found (or not owned by user)

---

#### DELETE /api/notebooks/{notebook_id}
**Description:** Delete a notebook and all associated PDFs

**Headers:** `Authorization: Bearer <access_token>`

**Response (204):** No content

**Error (404):** Notebook not found

---

### 5.3 PDFs (Auth Required)

#### POST /api/pdfs/upload
**Description:** Upload a PDF to a notebook (background processing)

**Headers:** `Authorization: Bearer <access_token>`

**Form Data:**
- notebook_id: string (required)
- file: file (required, must be PDF)

**Response (201):**
```json
{
  "filename": "policy.pdf",
  "notebook_id": "nb_a1b2c3d4",
  "pdf_id": 1,
  "processing_status": "uploaded"
}
```

**Processing States:**
- `uploaded`: Just uploaded
- `processing`: Text extraction in progress
- `embeddings_complete`: Embeddings stored, summary pending
- `summary_generation`: Summary being generated
- `complete`: Fully processed
- `error`: Processing failed

---

#### GET /api/pdfs/list?notebook_id={notebook_id}
**Description:** List completed PDFs in a notebook

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- notebook_id: string (required)

**Response (200):**
```json
{
  "notebook_id": "nb_a1b2c3d4",
  "pdfs": [
    {
      "filename": "policy.pdf",
      "status": "complete",
      "summary": "This document outlines..."
    }
  ]
}
```

**Note:** Only returns PDFs with `complete` status

---

#### GET /api/pdfs/status?notebook_id={notebook_id}&filename={filename}
**Description:** Get processing status of a PDF

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- notebook_id: string (required)
- filename: string (required)

**Response (200):**
```json
{
  "status": "complete"
}
```

---

#### DELETE /api/pdfs?notebook_id={notebook_id}&filename={filename}
**Description:** Delete a PDF and all associated data

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- notebook_id: string (required)
- filename: string (required)

**Response (204):** No content

**Deletes:**
- PDF file from disk
- Embeddings from Qdrant
- Summary from database
- PDF record from database

---

### 5.4 Chat (Auth Required)

#### POST /api/chat/query
**Description:** Query documents with AI (RAG pipeline)

**Headers:** `Authorization: Bearer <access_token>`

**Request:**
```json
{
  "query": "What is the vacation policy?",
  "pdfs": ["policy.pdf", "handbook.pdf"],
  "session_id": "sess_abc123",
  "notebook_id": "nb_a1b2c3d4",
  "model_name": "gemma3n:e4b"
}
```

**Fields:**
- query: string (required) - The question
- pdfs: array of strings (optional) - Which PDFs to search
- session_id: string (required) - Session for chat history
- notebook_id: string (required) - Which notebook contains the PDFs
- model_name: string (optional) - Override default model

**Response (200):**
```json
{
  "response": "According to the policy document, employees are entitled to...",
  "query_type": "rag_question",
  "context_chunks": [
    {
      "text": "Vacation Policy\n\nAll full-time employees...",
      "source": "policy.pdf",
      "page_number": 5
    }
  ]
}
```

**Query Types:**
- `conversational`: Greeting/thanks - returns direct response
- `rag_question`: Document query - runs RAG pipeline

---

#### GET /api/chat/history/{session_id}
**Description:** Get chat history for a session

**Headers:** `Authorization: Bearer <access_token>`

**Response (200):**
```json
{
  "messages": [
    {"role": "user", "content": "What is the vacation policy?"},
    {"role": "assistant", "content": "According to the policy..."},
    {"role": "user", "content": "How many days?"},
    {"role": "assistant", "content": "You get 20 days per year."}
  ]
}
```

---

#### POST /api/chat/suggested-queries
**Description:** Get AI-generated suggested questions

**Headers:** `Authorization: Bearer <access_token>`

**Request:**
```json
{
  "notebook_id": "nb_a1b2c3d4",
  "session_id": "sess_abc123",
  "selected_filenames": ["policy.pdf"]
}
```

**Response (200):**
```json
{
  "suggested_queries": [
    "What is the sick leave policy?",
    "How do I request time off?",
    "What are the overtime rules?"
  ]
}
```

---

## 6. Database Schema

### 6.1 User Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active VARCHAR DEFAULT 'true'
);
```

**Index:** email (unique)

---

### 6.2 Notebook Table
```sql
CREATE TABLE notebooks (
    id SERIAL PRIMARY KEY,
    notebook_id VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Indexes:**
- notebook_id (unique)
- user_id

**Foreign Key:** user_id -> users(id)

---

### 6.3 PDF Table
```sql
CREATE TABLE pdfs (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    notebook_id INTEGER REFERENCES notebooks(id) NOT NULL,
    processing_status VARCHAR(50) DEFAULT 'uploaded',
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Indexes:**
- file_name
- notebook_id

**Unique Constraint:** (file_name, notebook_id)

**Foreign Key:** notebook_id -> notebooks(id)

---

### 6.4 Chat Message Table
```sql
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,  -- user, assistant, system
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Indexes:**
- user_id
- session_id
- (user_id, session_id)

**Foreign Key:** user_id -> users(id)

---

## 7. Authentication Flow

### 7.1 Registration
```
1. Client sends POST /api/auth/register with email, password, full_name
2. AuthService.register() checks if email exists
3. If not, hash password with bcrypt
4. Create user in database
5. Return UserResponse (id, email, full_name, created_at)
```

### 7.2 Login
```
1. Client sends POST /api/auth/login with email, password
2. AuthService.login() finds user by email
3. Verify password with bcrypt
4. Create JWT access_token (expires in 30 min) and refresh_token (expires in 7 days)
5. Return TokenResponse (access_token, refresh_token, token_type)
```

### 7.3 Protected Endpoint Access
```
1. Client includes Authorization: Bearer <access_token>
2. api/deps.get_current_user() extracts token from header
3. core/security.verify_token() decodes JWT
4. Get user_id from token payload
5. Fetch user from database
6. Return User object to route handler
```

### 7.4 JWT Token Structure
```python
# Access Token Payload
{
    "sub": "1",           # user_id
    "exp": 1715432400,    # expiration timestamp
    "type": "access"
}

# Refresh Token Payload
{
    "sub": "1",
    "exp": 1716037200,
    "type": "refresh"
}
```

---

## 8. Provider Factory Pattern

### 8.1 LLM Providers

| Provider | Install Extra | Model Examples |
|----------|---------------|----------------|
| `ollama` | `llm-ollama` | gemma3n:e4b, llama4:latest |
| `gemini` | `llm-gemini` | gemini-2.5-flash |
| `vllm` | `llm-vllm` | unsloth/gemma-3n-E4B-it |

**Factory Usage:**
```python
from providers.llm.factory import LLMFactory

llm = LLMFactory.get(provider="ollama", model="gemma3n:e4b")
response = await llm.generate(prompt)
```

---

### 8.2 Embedding Providers

| Provider | Install Extra | Notes |
|----------|---------------|-------|
| `sentence-transformers` | `embed-sentence-transformers` | Requires torch (~2.5GB) |
| `vllm` | `embed-vllm` | Lightweight, no torch |

**Factory Usage:**
```python
from providers.embedding.factory import EmbeddingFactory

embedder = EmbeddingFactory.get(provider="sentence-transformers")
vectors = await embedder.embed_documents(["text1", "text2"])
```

---

### 8.3 Reranker Providers

| Provider | Install Extra | Notes |
|----------|---------------|-------|
| `tei` | `rerank-tei` | Lightweight HTTP |
| `flag` | `rerank-flag` | Requires torch (~500MB) |

**Factory Usage:**
```python
from providers.reranker.factory import RerankerFactory

reranker = RerankerFactory.get(provider="tei")
ranked_chunks, scores = reranker.rerank(query, chunks)
```

---

## 9. Environment Variables

### Required
```bash
# Database
database_url=postgresql+asyncpg://postgres:postgres@localhost:5432/policybot

# JWT
jwt_secret=your-super-secret-key-change-in-production
jwt_algorithm=HS256
jwt_access_expire_minutes=30
jwt_refresh_expire_days=7

# Providers (change based on installation)
llm_provider=vllm
default_model=gemma3n:e4b
embedding_provider=vllm
embedding_model=Alibaba-NLP/gte-multilingual-base
reranker_provider=tei
```

### Optional
```bash
# Qdrant
qdrant_host=localhost
qdrant_port=6333
collection_name=pdf_embeddings

# External Services
ollama_url=http://localhost:11434
gemini_api_key=
vllm_llm_url=http://localhost:8080/v1
vllm_llm_model=unsloth/gemma-3n-E4B-it

# Application
max_context_tokens=32000
temperature=0.5
top_k=10
```

---

## 10. Docker Configuration

### Build Commands

**Minimal (vLLM only - ~400MB):**
```bash
docker build \
    --build-arg LLM_PROVIDER=vllm \
    --build-arg EMBEDDING_PROVIDER=vllm \
    --build-arg RERANKER_PROVIDER=tei \
    -t policybot:vllm-minimal \
    .
```

**Full (sentence-transformers + flag - ~3GB):**
```bash
docker build \
    --build-arg LLM_PROVIDER=gemini \
    --build-arg EMBEDDING_PROVIDER=sentence-transformers \
    --build-arg RERANKER_PROVIDER=flag \
    -t policybot:full \
    .
```

**Development:**
```bash
docker build \
    --build-arg LLM_PROVIDER=ollama \
    --build-arg EMBEDDING_PROVIDER=vllm \
    --build-arg RERANKER_PROVIDER=tei \
    --build-arg ENVIRONMENT=development \
    -t policybot:dev \
    .

docker run -p 8000:8000 -v $(pwd):/app policybot:dev
```

### Docker Compose
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: policybot
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/policybot
      - QDRANT_HOST=qdrant
    depends_on:
      - postgres
      - qdrant

volumes:
  postgres_data:
  qdrant_data:
```

---

## 11. Quick Start Guide

### 11.1 Installation

```bash
# Clone and navigate
cd backend

# Install with specific providers (example: vLLM)
pip install -e ".[llm-vllm,embed-vllm,rerank-tei]"

# Or install core only, add providers manually
pip install -e "."
pip install langchain-openai openai
```

### 11.2 Database Setup

```bash
# Create .env file from example
cp .env.example .env
# Edit .env with your settings - app automatically reads from here
```

**Note:** All configuration is read from `.env` file automatically via Pydantic Settings. No hardcoded values needed.

### 11.3 Run Server

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
```

### 11.4 Verify

```bash
# Health check
curl http://localhost:8000/health

# Should return: {"status": "healthy"}
```

### 11.5 Makefile Automation (Recommended)

All common tasks are automated via Makefile. The Makefile automatically reads from `.env` for configuration.

```makefile
# Makefile - automate all common tasks

# Load environment variables
include .env
export

# Default target
help:
	@echo "PolicyBot Backend - Available Commands"
	@echo ""
	@echo "  make install          Install dependencies"
	@echo "  make dev              Run development server"
	@echo "  make dev-bg           Run development server in background"
	@echo "  make build            Build Docker image"
	@echo "  make up               Start all services (Docker Compose)"
	@echo "  make down             Stop all services"
	@echo "  make logs             View logs"
	@echo "  make migrate          Run database migrations"
	@echo "  make migrate-create   Create new migration"
	@echo "  make reset            Reset database (delete volumes)"
	@echo "  make clean            Remove cache and build files"
	@echo "  make test             Run tests"
	@echo "  make lint             Run linters"

# Install dependencies based on providers in .env
install:
	@echo "Installing dependencies for providers:"
	@echo "  LLM: $(LLM_PROVIDER)"
	@echo "  Embedding: $(EMBEDDING_PROVIDER)"
	@echo "  Reranker: $(RERANKER_PROVIDER)"
	@pip install -e ".[llm-$(LLM_PROVIDER),embed-$(EMBEDDING_PROVIDER),rerank-$(RERANKER_PROVIDER)]"

# Run development server
dev:
	@echo "Starting development server..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run development server in background
dev-bg:
	@echo "Starting development server in background..."
	@uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &

# Build Docker image with provider args from .env
build:
	@echo "Building Docker image for:"
	@echo "  LLM_PROVIDER=$(LLM_PROVIDER)"
	@echo "  EMBEDDING_PROVIDER=$(EMBEDDING_PROVIDER)"
	@echo "  RERANKER_PROVIDER=$(RERANKER_PROVIDER)"
	docker build \
		--build-arg LLM_PROVIDER=$(LLM_PROVIDER) \
		--build-arg EMBEDDING_PROVIDER=$(EMBEDDING_PROVIDER) \
		--build-arg RERANKER_PROVIDER=$(RERANKER_PROVIDER) \
		--build-arg ENVIRONMENT=production \
		-t policybot:$(LLM_PROVIDER)-$(EMBEDDING_PROVIDER) \
		.

# Start all services with Docker Compose
up:
	docker-compose up --build

# Stop all services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Run database migrations
migrate:
	alembic upgrade head

# Create new migration
migrate-create:
	alembic revision --autogenerate -m "$(NAME)"

# Reset database (delete volumes)
reset:
	docker-compose down -v
	@echo "Database reset complete. Run 'make up' to restart."

# Clean up cache and build files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .ruff_cache/ 2>/dev/null || true

# Run tests
test:
	pytest -v

# Run linters
lint:
	ruff check .
	mypy app/ --ignore-missing-imports
```

### 11.6 Example .env Configuration

```bash
# .env.example - copy to .env and customize

# ===================
# REQUIRED SETTINGS
# ===================

# Database
database_url=postgresql+asyncpg://postgres:postgres@localhost:5432/policybot

# JWT (change in production!)
jwt_secret=change-this-to-a-secure-random-string-in-production
jwt_algorithm=HS256
jwt_access_expire_minutes=30
jwt_refresh_expire_days=7

# ===================
# PROVIDER SELECTION
# ===================
# Options: ollama, gemini, vllm
llm_provider=vllm

# Options: sentence-transformers, vllm
embedding_provider=vllm

# Options: tei, flag
reranker_provider=tei

# ===================
# DEFAULT MODELS
# ===================
default_model=gemma3n:e4b
embedding_model=Alibaba-NLP/gte-multilingual-base

# ===================
# VECTOR STORE
# ===================
qdrant_host=localhost
qdrant_port=6333
collection_name=pdf_embeddings

# ===================
# EXTERNAL SERVICES
# ===================
ollama_url=http://localhost:11434
gemini_api_key=
vllm_llm_url=http://localhost:8080/v1
vllm_llm_model=unsloth/gemma-3n-E4B-it

# ===================
# APPLICATION
# ===================
max_context_tokens=32000
temperature=0.5
top_k=10

# ===================
# ENVIRONMENT
# ===================
environment=development
```

---

## How Configuration Works

### Automatic Loading

1. **At startup**, `app/config.py` loads settings:
```python
# app/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    llm_provider: str
    # ... other fields
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

2. **Everywhere in the app**, use:
```python
from app.config import get_settings

settings = get_settings()
# Use: settings.database_url, settings.llm_provider, etc.
```

3. **Docker builds** read from .env via `--build-arg`:
```bash
docker build --build-arg LLM_PROVIDER=$LLM_PROVIDER ...
```

### No Hardcoded Values

- All config via `.env`
- Changing providers = just change `llm_provider` in `.env`
- Docker rebuild picks up new values automatically
- Makefile commands read from `.env` for automation

---

## 12. Feature Parity Checklist

Use this checklist to verify implementation matches original backend functionality:

### Authentication
- [ ] User can register with email/password
- [ ] User can login and receive JWT tokens
- [ ] Protected routes require valid JWT
- [ ] Invalid/expired tokens return 401

### Notebooks
- [ ] User can create notebook (with title, optional description)
- [ ] User can list their notebooks (only their notebooks)
- [ ] User can get specific notebook
- [ ] User can delete notebook
- [ ] Cannot access other users' notebooks (returns 404)

### PDFs
- [ ] User can upload PDF to their notebook
- [ ] Upload triggers background processing
- [ ] User can list completed PDFs in notebook
- [ ] User can get PDF processing status
- [ ] User can delete PDF (file, embeddings, DB record)
- [ ] Processing states: uploaded → processing → complete

### Chat
- [ ] User can send query with session_id and notebook_id
- [ ] System classifies query as conversational or rag_question
- [ ] For rag_question: retrieves context chunks, generates response
- [ ] Returns context chunks with source and page_number
- [ ] Chat history persists in database
- [ ] User can get chat history by session_id
- [ ] User can get suggested questions

### Providers
- [ ] LLM Factory can create ollama, gemini, vllm providers
- [ ] Embedding Factory can create sentence-transformers, vllm
- [ ] Reranker Factory can create tei, flag
- [ ] Config determines which provider is used at runtime

### Data Isolation
- [ ] All notebook queries filter by current_user.id
- [ ] All PDF queries filter through notebooks owned by user
- [ ] All chat queries filter by current_user.id
- [ ] Cannot access other user's data through any endpoint

---

## 13. Common Issues & Solutions

### Issue: "No module named 'app'"
**Solution:** Ensure you're running from backend directory with correct Python path, or use `python -m uvicorn app.main:app`

### Issue: "Database connection refused"
**Solution:** Ensure PostgreSQL is running and DATABASE_URL is correct

### Issue: "Qdrant connection failed"
**Solution:** Ensure Qdrant is running on configured host/port

### Issue: "Invalid token"
**Solution:** Check JWT_SECRET matches between token creation and verification

### Issue: "torch not found" when using sentence-transformers
**Solution:** Install with `pip install policybot[embed-sentence-transformers]`

---

## 14. File Dependencies Reference

### Key Imports Chain
```
api/routes → services → repositories → db/models → db/session → db/base
     ↓
api/schemas
     ↓
api/deps (get_current_user → core/security)
     ↓
providers/*/factory (uses app/config)
```

### Configuration Flow
```
app/config.py (Settings class with lru_cache)
    ↓
get_settings() used throughout
    ↓
db/session.py (creates engine)
core/security.py (uses jwt settings)
providers/*/factory.py (uses provider settings)
```

---

## 15. Next Steps After Implementation

1. **Run all tests** to verify functionality
2. **Test with real PDFs** - upload and process documents
3. **Test chat** - ask questions and verify RAG works
4. **Migrate legacy data** - create system user, migrate existing notebooks
5. **Performance testing** - check response times, optimize if needed
6. **Security audit** - verify JWT implementation, input validation

---

**End of Implementation Summary**

*For detailed implementation steps, see [plan.md](./plan.md)*