# PolicyBot Backend Refactor Plan

## Overview

This document outlines the complete refactoring of the PolicyBot backend from its current messy state to a clean, scalable architecture following FastAPI best practices.

**Current State Problems:**
- No authentication/JWT
- No user isolation (notebooks/PDFs have no owner)
- Monolithic service layer with mixed concerns
- Hardcoded provider logic embedded in services
- In-memory chat history (lost on restart)
- Config mixed with prompts and business logic
- Unclear folder structure

**Target State:**
- Complete JWT authentication with user model
- Repository pattern with user-scoped data access
- Clean separation: api → services → repositories → db
- Factory pattern for providers (LLM, embedding, reranker)
- Persistent chat history
- Clear, discoverable codebase

---

## Architecture Overview

```
backend/
├── app/                         # Application entry point
│   ├── __init__.py
│   ├── main.py                 # FastAPI app creation
│   └── config.py               # Pydantic Settings (env vars)
│
├── api/                        # HTTP layer (routes, schemas, deps)
│   ├── __init__.py
│   ├── deps.py                 # Dependencies (get_current_user, get_db)
│   ├── errors.py              # Custom exceptions
│   ├── router.py              # Main router combining all routes
│   ├── schemas/               # Pydantic request/response models
│   │   ├── __init__.py
│   │   ├── auth.py            # Token, LoginRequest, RegisterRequest
│   │   ├── notebook.py        # NotebookCreate, NotebookResponse
│   │   ├── pdf.py             # PDFUpload, PDFResponse
│   │   └── chat.py            # ChatRequest, ChatResponse
│   └── routes/                # Route handlers
│       ├── __init__.py
│       ├── auth.py            # /auth endpoints
│       ├── notebooks.py       # /notebooks endpoints
│       ├── pdfs.py            # /pdfs endpoints
│       └── chat.py            # /chat endpoints
│
├── core/                       # Cross-cutting concerns
│   ├── __init__.py
│   ├── security.py            # JWT create/verify, password hashing
│   ├── prompts.py            # Prompt templates (moved from src/core)
│   └── logger.py             # Logging setup
│
├── db/                        # Data layer
│   ├── __init__.py
│   ├── base.py               # SQLAlchemy Base
│   ├── session.py            # AsyncSession factory + get_db
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py           # User (id, email, hashed_password, created_at)
│   │   ├── notebook.py       # Notebook (id, user_id, title, description)
│   │   ├── pdf.py            # PDF (id, notebook_id, filename, status)
│   │   └── chat_message.py   # ChatHistory (id, user_id, session_id, role, content)
│   └── repositories/         # Data access layer
│       ├── __init__.py
│       ├── base.py           # BaseRepository (generic CRUD)
│       ├── user_repo.py
│       ├── notebook_repo.py
│       ├── pdf_repo.py
│       └── chat_repo.py
│
├── services/                 # Business logic layer
│   ├── __init__.py
│   ├── auth_service.py       # Login, register, token validation
│   ├── notebook_service.py   # Notebook CRUD + user isolation
│   ├── pdf_service.py        # PDF upload, processing, status
│   └── chat_service.py       # Query handling, context building
│
├── providers/               # External integrations (factory pattern)
│   ├── __init__.py
│   ├── base.py             # Abstract base classes
│   │
│   ├── llm/               # LLM providers
│   │   ├── __init__.py
│   │   ├── factory.py     # get_llm(provider, model) -> BaseLLM
│   │   ├── base.py        # BaseLLM (generate, generate_stream)
│   │   ├── openai.py      # vLLM, OpenAI compatible
│   │   ├── ollama.py
│   │   └── gemini.py
│   │
│   ├── embedding/         # Embedding providers
│   │   ├── __init__.py
│   │   ├── factory.py
│   │   ├── base.py
│   │   ├── sentence_transformers.py
│   │   └── vllm.py
│   │
│   └── reranker/         # Reranker providers
│       ├── __init__.py
│       ├── factory.py
│       ├── base.py
│       ├── flag.py
│       └── tei.py
│
└── utils/                  # Utilities
    ├── __init__.py
    ├── pdf_processor.py   # PDF text extraction, chunking
    └── vector_store.py   # Qdrant operations
```

---

## Layer Responsibilities

| Layer | Responsibility | Changes When |
|-------|---------------|--------------|
| `api/routes` | HTTP handling, request validation, response formatting | Frontend contract changes |
| `api/schemas` | Pydantic models for request/response | API contract changes |
| `api/deps` | FastAPI dependencies (auth, db session) | Auth flow changes |
| `services` | Business logic, orchestration, validation | Business logic changes |
| `repositories` | Data access, SQL queries, user-filtered queries | Data access changes |
| `db/models` | SQLAlchemy ORM models, table definitions | Schema changes |
| `providers` | External API integrations (LLM, embeddings) | New provider added |
| `core` | Security, prompts, logging (shared utilities) | Security/prompt changes |

---

## Data Flow

```
HTTP Request
     │
     ▼
api/routes (validate request, call service)
     │
     ▼
services (business logic, user_id passed)
     │
     ▼
repositories (data access, user-filtered queries)
     │
     ▼
db/models (SQLAlchemy ORM)
     │
     ▼
Database (PostgreSQL)
```

---

## FastAPI Best Practices Applied

This architecture follows these production-ready best practices:

### 1. Async/Await Correctly
- Use `async def` with `await` for I/O operations (database, external APIs)
- Use regular `def` for blocking code (CPU-intensive work)
- Never mix `async def` with blocking operations

```python
# ✅ Good: async for I/O
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

# ✅ Good: regular def for blocking operations
def process_heavy_computation(data: dict):
    # CPU-intensive work runs in thread pool
    return complex_calculation(data)
```

### 2. Use FastAPI Dependencies (Depency Injection)
- Reuse common logic across endpoints
- Keep routes clean and focused

```python
# api/deps.py - reusable dependency
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: DBSession
) -> User:
    # Token validation logic in one place
    ...

# Routes become clean
@router.get("/users/me")
async def get_me(current_user: CurrentUser):
    return current_user
```

### 3. Pydantic Models Effectively
- Use custom base model with shared config
- Let Pydantic handle validation and serialization

```python
# api/schemas/base.py
from pydantic import BaseModel, ConfigDict

class CustomBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        str_strip_whitespace=True
    )

# All schemas inherit
class UserResponse(CustomBase):
    id: int
    email: str
```

### 4. Background Tasks for Non-Critical Operations
- Never make users wait for non-essential operations
- Use `BackgroundTasks` for simple tasks

```python
from fastapi import BackgroundTasks

@router.post("/pdf/upload")
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    ...
):
    # Return immediately, process in background
    background_tasks.add_task(process_pdf_background, pdf_id)
    return {"status": "uploaded", "pdf_id": pdf_id}
```

### 5. Hide API Docs in Production
```python
# app/main.py
import os

app = FastAPI(
    docs_url="/docs" if os.getenv("ENV") == "development" else None,
    redoc_url="/redoc" if os.getenv("ENV") == "development" else None,
)
```

### 6. Database Connection Pooling
```python
# db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
```

### 7. Use Lifespan Events for Resource Management
```python
# app/main.py
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.redis = await redis.from_url("redis://localhost")
    yield
    # Shutdown
    await app.state.redis.close()
```

### 8. Never Hardcode Secrets
```python
# app/config.py - already using pydantic_settings
class Settings(BaseSettings):
    jwt_secret: str
    database_url: str
    
    class Config:
        env_file = ".env"
```

### 9. Structured Logging
```python
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# Usage
logger.info("user_action", user_id=123, action="login")
```

### 10. Production Deployment (Gunicorn + Uvicorn)
```bash
# Run with multiple workers
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
```

### 11. Health Check Endpoints
```python
# app/main.py
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

# Step-by-Step Refactor Plan

## Phase 1: Foundation (Setup & Config)

### Step 1.1: Create Folder Structure

Create the directory structure with all `__init__.py` files:

```bash
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── config.py
├── api/
│   ├── __init__.py
│   ├── deps.py
│   ├── errors.py
│   ├── router.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── notebook.py
│   │   ├── pdf.py
│   │   └── chat.py
│   └── routes/
│       ├── __init__.py
│       ├── auth.py
│       ├── notebooks.py
│       ├── pdfs.py
│       └── chat.py
├── core/
│   ├── __init__.py
│   ├── security.py
│   ├── prompts.py
│   └── logger.py
├── db/
│   ├── __init__.py
│   ├── base.py
│   ├── session.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── notebook.py
│   │   ├── pdf.py
│   │   └── chat_message.py
│   └── repositories/
│       ├── __init__.py
│       ├── base.py
│       ├── user_repo.py
│       ├── notebook_repo.py
│       ├── pdf_repo.py
│       └── chat_repo.py
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── notebook_service.py
│   ├── pdf_service.py
│   └── chat_service.py
├── providers/
│   ├── __init__.py
│   ├── base.py
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── factory.py
│   │   ├── base.py
│   │   ├── openai.py
│   │   ├── ollama.py
│   │   └── gemini.py
│   ├── embedding/
│   │   ├── __init__.py
│   │   ├── factory.py
│   │   ├── base.py
│   │   ├── sentence_transformers.py
│   │   └── vllm.py
│   └── reranker/
│       ├── __init__.py
│       ├── factory.py
│       ├── base.py
│       ├── flag.py
│       └── tei.py
└── utils/
    ├── __init__.py
    ├── pdf_processor.py
    └── vector_store.py
```

### Step 1.2: Create app/config.py

Pydantic Settings for type-safe environment configuration with cached singleton:

```python
# app/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/policybot"
    
    # JWT Settings
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 30
    jwt_refresh_expire_days: int = 7
    
    # LLM Settings
    llm_provider: str = "ollama"
    default_model: str = "gemma3n:e4b"
    
    # Embedding Settings
    embedding_provider: str = "sentence-transformers"
    embedding_model: str = "Alibaba-NLP/gte-multilingual-base"
    
    # Reranker Settings
    reranker_provider: str = "tei"
    
    # Vector Store (Qdrant)
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    collection_name: str = "pdf_embeddings"
    
    # Other Settings
    max_context_tokens: int = 32000
    temperature: float = 0.5
    top_k: int = 10
    
    # External Services (existing config preserved)
    ollama_url: str = "http://localhost:11434"
    gemini_api_key: Optional[str] = None
    vllm_llm_url: str = "http://localhost:8080/v1"
    vllm_llm_model: str = "unsloth/gemma-3n-E4B-it"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

**Usage throughout the codebase:**
```python
from app.config import get_settings

settings = get_settings()
# Access like: settings.database_url, settings.jwt_secret, etc.
```

**Why lru_cache:**
- Settings are loaded once and cached
- No re-parsing of env file on every import
- Thread-safe singleton pattern

### Step 1.3: Create app/main.py

FastAPI application entry point with best practices (lifespan, production docs hiding):

```python
# app/main.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import api_router
from core.logger import setup_logging
from db.session import engine
from app.config import get_settings


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize resources
    setup_logging()
    yield
    # Shutdown: Cleanup resources
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="PolicyBot API",
        version="2.0.0",
        description="AI-powered document processing and RAG API",
        # Hide API docs in production
        docs_url="/docs" if os.getenv("ENV") == "development" else None,
        redoc_url="/redoc" if os.getenv("ENV") == "development" else None,
        openapi_url="/openapi.json" if os.getenv("ENV") == "development" else None,
        lifespan=lifespan,
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(api_router, prefix="/api")
    
    # Health check (best practice)
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

**Key Best Practices Applied:**
- **Lifespan events**: Properly initialize/cleanup resources
- **Environment-based docs**: Hide Swagger in production
- **Health check**: Ready for container orchestration

### Step 1.4: Create core/logger.py

```python
# core/logger.py
import logging
import sys


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


logger = logging.getLogger("policybot")
```

### Step 1.5: Create core/prompts.py

Move all prompt templates from existing `src/core/prompts.py`:

```python
# core/prompts.py

QUERY_REWRITE_SYSTEM_PROMPT = """..."""

SYSTEM_PROMPT = """..."""

GENERATED_EXAMPLE_DOCUMENT_PROMPT = """..."""

QUERY_CLASSIFICATION_PROMPT = """..."""

SUGGESTED_QUERIES_PROMPT = """..."""

MAP_SUMMARIZATION_PROMPT = """..."""

REDUCE_SUMMARIZATION_PROMPT = """..."""

FINAL_SUMMARY_PROMPT = """..."""
```

---

## Phase 2: Database & Models

### Step 2.1: Create db/base.py

```python
# db/base.py
from sqlalchemy.orm import declarative_base

Base = declarative_base()
```

### Step 2.2: Create db/session.py

```python
# db/session.py
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=False)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

### Step 2.3: Create db/models/user.py

```python
# db/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, func
from db.base import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(String, default="true")
```

### Step 2.4: Create db/models/notebook.py

```python
# db/models/notebook.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from db.base import Base


class Notebook(Base):
    __tablename__ = "notebooks"
    
    id = Column(Integer, primary_key=True, index=True)
    notebook_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # USER ISOLATION
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", backref="notebooks")
    pdfs = relationship("PDF", back_populates="notebook", cascade="all, delete-orphan")
```

### Step 2.5: Create db/models/pdf.py

```python
# db/models/pdf.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from db.base import Base


class PDF(Base):
    __tablename__ = "pdfs"
    
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    notebook_id = Column(Integer, ForeignKey("notebooks.id"), nullable=False)
    processing_status = Column(String(50), default="uploaded")
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    notebook = relationship("Notebook", back_populates="pdfs")
```

### Step 2.6: Create db/models/chat_message.py

```python
# db/models/chat_message.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from db.base import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # USER ISOLATION
    session_id = Column(String(100), index=True, nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

---

## Phase 3: Security (JWT & Passwords)

### Step 3.1: Create core/security.py

```python
# core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_expire_minutes)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.jwt_refresh_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None
```

---

## Phase 4: Repositories (Data Access Layer)

### Step 4.1: Create db/repositories/base.py

```python
# db/repositories/base.py
from typing import TypeVar, Generic, Type, Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def get(self, id: int) -> Optional[ModelType]:
        return await self.db.get(self.model, id)
    
    async def get_all(self) -> List[ModelType]:
        result = await self.db.execute(select(self.model))
        return list(result.scalars().all())
    
    async def create(self, **kwargs) -> ModelType:
        obj = self.model(**kwargs)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj
    
    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        obj = await self.get(id)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            await self.db.commit()
            await self.db.refresh(obj)
        return obj
    
    async def delete(self, id: int) -> bool:
        obj = await self.get(id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
            return True
        return False
```

### Step 4.2: Create db/repositories/user_repo.py

```python
# db/repositories/user_repo.py
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.user import User
from db.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        return await self.get(user_id)
    
    async def create_user(self, email: str, hashed_password: str, full_name: str = None) -> User:
        return await self.create(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name
        )
```

### Step 4.3: Create db/repositories/notebook_repo.py

```python
# db/repositories/notebook_repo.py
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.notebook import Notebook
from db.repositories.base import BaseRepository


class NotebookRepository(BaseRepository[Notebook]):
    def __init__(self, db: AsyncSession):
        super().__init__(Notebook, db)
    
    async def get_by_user(self, user_id: int) -> List[Notebook]:
        """Get all notebooks for a user - USER ISOLATION"""
        result = await self.db.execute(
            select(Notebook).where(Notebook.user_id == user_id)
        )
        return list(result.scalars().all())
    
    async def get_by_user_and_notebook_id(self, user_id: int, notebook_id: str) -> Optional[Notebook]:
        """Get single notebook with ownership check - USER ISOLATION"""
        result = await self.db.execute(
            select(Notebook).where(
                Notebook.notebook_id == notebook_id,
                Notebook.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_title_for_user(self, user_id: int, title: str) -> Optional[Notebook]:
        """Check if title exists for user"""
        result = await self.db.execute(
            select(Notebook).where(
                Notebook.title == title,
                Notebook.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def create_for_user(self, user_id: int, title: str, description: str = None, notebook_id: str = None) -> Notebook:
        import secrets
        if not notebook_id:
            notebook_id = f"nb_{secrets.token_hex(8)}"
        return await self.create(
            user_id=user_id,
            title=title,
            description=description,
            notebook_id=notebook_id
        )
```

### Step 4.4: Create db/repositories/pdf_repo.py

```python
# db/repositories/pdf_repo.py
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.pdf import PDF
from db.repositories.base import BaseRepository


class PDFRepository(BaseRepository[PDF]):
    def __init__(self, db: AsyncSession):
        super().__init__(PDF, db)
    
    async def get_by_notebook(self, notebook_id: int) -> List[PDF]:
        result = await self.db.execute(
            select(PDF).where(PDF.notebook_id == notebook_id)
        )
        return list(result.scalars().all())
    
    async def get_by_notebook_and_filename(self, notebook_id: int, filename: str) -> Optional[PDF]:
        result = await self.db.execute(
            select(PDF).where(
                PDF.notebook_id == notebook_id,
                PDF.file_name == filename
            )
        )
        return result.scalar_one_or_none()
    
    async def create_for_notebook(self, notebook_id: int, file_name: str, file_path: str) -> PDF:
        return await self.create(
            notebook_id=notebook_id,
            file_name=file_name,
            file_path=file_path,
            processing_status="uploaded"
        )
```

### Step 4.5: Create db/repositories/chat_repo.py

```python
# db/repositories/chat_repo.py
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.chat_message import ChatMessage
from db.repositories.base import BaseRepository


class ChatRepository(BaseRepository[ChatMessage]):
    def __init__(self, db: AsyncSession):
        super().__init__(ChatMessage, db)
    
    async def get_session_messages(self, user_id: int, session_id: str, limit: int = 50) -> List[ChatMessage]:
        result = await self.db.execute(
            select(ChatMessage)
            .where(
                ChatMessage.user_id == user_id,
                ChatMessage.session_id == session_id
            )
            .order_by(ChatMessage.created_at)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def add_message(self, user_id: int, session_id: str, role: str, content: str) -> ChatMessage:
        return await self.create(
            user_id=user_id,
            session_id=session_id,
            role=role,
            content=content
        )
```

---

## Phase 5: API Dependencies

### Step 5.1: Create api/deps.py

```python
# api/deps.py
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from core.security import verify_token
from db.repositories.user_repo import UserRepository
from db.models.user import User

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(int(user_id))
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
DBSession = Annotated[AsyncSession, Depends(get_db)]
```

---

## Phase 6: API Schemas

### Step 6.0: Create Custom Base Schema (Pydantic Best Practice)

```python
# api/schemas/base.py
from pydantic import BaseModel, ConfigDict


class CustomBase(BaseModel):
    """Base Pydantic model with shared configuration."""
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        str_strip_whitespace=True
    )
```

**Usage:** All schemas inherit from `CustomBase` instead of `BaseModel`.

### Step 6.1: Create api/schemas/auth.py

```python
# api/schemas/auth.py
from pydantic import EmailStr
from typing import Optional
from api.schemas.base import CustomBase


class RegisterRequest(CustomBase):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class LoginRequest(CustomBase):
    email: EmailStr
    password: str


class TokenResponse(CustomBase):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(CustomBase):
    id: int
    email: str
    full_name: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True
```

### Step 6.2: Create api/schemas/notebook.py

```python
# api/schemas/notebook.py
from pydantic import BaseModel
from typing import Optional


class NotebookCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None


class NotebookResponse(BaseModel):
    id: int
    notebook_id: str
    title: str
    description: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class NotebookListResponse(BaseModel):
    notebooks: list[NotebookResponse]
```

### Step 6.3: Create api/schemas/pdf.py

```python
# api/schemas/pdf.py
from pydantic import BaseModel
from typing import Optional


class PDFUploadResponse(BaseModel):
    filename: str
    notebook_id: str
    pdf_id: int
    processing_status: str


class PDFListResponse(BaseModel):
    notebook_id: str
    pdfs: list[dict]  # Simplified for now


class PDFSummaryResponse(BaseModel):
    summary: str
    filename: str
    notebook_id: str
```

### Step 6.4: Create api/schemas/chat.py

```python
# api/schemas/chat.py
from pydantic import BaseModel
from typing import Optional, List


class ChatQueryRequest(BaseModel):
    query: str
    pdfs: Optional[List[str]] = None
    session_id: str
    notebook_id: str
    model_name: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    query_type: str = "rag_question"
    context_chunks: list[dict] = []


class SuggestedQueriesResponse(BaseModel):
    suggested_queries: List[str]
```

---

## Phase 7: Services (Business Logic)

### Step 7.1: Create services/auth_service.py

```python
# services/auth_service.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from db.repositories.user_repo import UserRepository
from db.models.user import User
from api.errors import AuthenticationError, UserAlreadyExistsError


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def register(self, email: str, password: str, full_name: Optional[str] = None) -> User:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise UserAlreadyExistsError(email)
        
        hashed_password = get_password_hash(password)
        user = await self.user_repo.create_user(email, hashed_password, full_name)
        return user
    
    async def login(self, email: str, password: str) -> dict:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise AuthenticationError("Invalid email or password")
        
        if not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")
        
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user
        }
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return await self.user_repo.get_by_id(user_id)
```

### Step 7.2: Create services/notebook_service.py

```python
# services/notebook_service.py
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories.notebook_repo import NotebookRepository
from db.models.notebook import Notebook
from api.errors import NotebookNotFoundError, NotebookAlreadyExistsError


class NotebookService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.notebook_repo = NotebookRepository(db)
    
    async def create(self, user_id: int, title: str, description: str = None) -> Notebook:
        existing = await self.notebook_repo.get_by_title_for_user(user_id, title)
        if existing:
            raise NotebookAlreadyExistsError(title)
        
        return await self.notebook_repo.create_for_user(user_id, title, description)
    
    async def list(self, user_id: int) -> List[Notebook]:
        return await self.notebook_repo.get_by_user(user_id)
    
    async def get(self, user_id: int, notebook_id: str) -> Notebook:
        notebook = await self.notebook_repo.get_by_user_and_notebook_id(user_id, notebook_id)
        if not notebook:
            raise NotebookNotFoundError(notebook_id)
        return notebook
    
    async def delete(self, user_id: int, notebook_id: str) -> bool:
        notebook = await self.get(user_id, notebook_id)
        return await self.notebook_repo.delete(notebook.id)
```

### Step 7.3: Create services/pdf_service.py

```python
# services/pdf_service.py
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories.pdf_repo import PDFRepository
from db.repositories.notebook_repo import NotebookRepository
from db.models.pdf import PDF
from api.errors import NotebookNotFoundError, PDFNotFoundError


class PDFService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pdf_repo = PDFRepository(db)
        self.notebook_repo = NotebookRepository(db)
    
    async def upload(self, user_id: int, notebook_id: str, file_name: str, file_path: str) -> PDF:
        notebook = await self.notebook_repo.get_by_user_and_notebook_id(user_id, notebook_id)
        if not notebook:
            raise NotebookNotFoundError(notebook_id)
        
        existing = await self.pdf_repo.get_by_notebook_and_filename(notebook.id, file_name)
        if existing:
            return existing
        
        return await self.pdf_repo.create_for_notebook(notebook.id, file_name, file_path)
    
    async def list(self, user_id: int, notebook_id: str) -> List[PDF]:
        notebook = await self.notebook_repo.get_by_user_and_notebook_id(user_id, notebook_id)
        if not notebook:
            raise NotebookNotFoundError(notebook_id)
        return await self.pdf_repo.get_by_notebook(notebook.id)
    
    async def get_status(self, user_id: int, notebook_id: str, filename: str) -> str:
        notebook = await self.notebook_repo.get_by_user_and_notebook_id(user_id, notebook_id)
        if not notebook:
            raise NotebookNotFoundError(notebook_id)
        
        pdf = await self.pdf_repo.get_by_notebook_and_filename(notebook.id, filename)
        if not pdf:
            raise PDFNotFoundError(filename)
        
        return pdf.processing_status
    
    async def delete(self, user_id: int, notebook_id: str, filename: str) -> bool:
        notebook = await self.notebook_repo.get_by_user_and_notebook_id(user_id, notebook_id)
        if not notebook:
            raise NotebookNotFoundError(notebook_id)
        
        pdf = await self.pdf_repo.get_by_notebook_and_filename(notebook.id, filename)
        if not pdf:
            raise PDFNotFoundError(filename)
        
        return await self.pdf_repo.delete(pdf.id)
```

### Step 7.4: Create services/chat_service.py

```python
# services/chat_service.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories.chat_repo import ChatRepository
from db.repositories.notebook_repo import NotebookRepository
from db.repositories.pdf_repo import PDFRepository
from api.errors import NotebookNotFoundError


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.chat_repo = ChatRepository(db)
        self.notebook_repo = NotebookRepository(db)
        self.pdf_repo = PDFRepository(db)
    
    async def get_session_history(self, user_id: int, session_id: str) -> List[dict]:
        messages = await self.chat_repo.get_session_messages(user_id, session_id)
        return [
            {"role": m.role, "content": m.content}
            for m in messages
        ]
    
    async def save_message(self, user_id: int, session_id: str, role: str, content: str):
        await self.chat_repo.add_message(user_id, session_id, role, content)
    
    async def validate_notebook_access(self, user_id: int, notebook_id: str) -> bool:
        notebook = await self.notebook_repo.get_by_user_and_notebook_id(user_id, notebook_id)
        return notebook is not None
```

---

## Phase 8: API Routes

### Step 8.1: Create api/routes/auth.py

```python
# api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import DBSession
from api.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: DBSession):
    service = AuthService(db)
    user = await service.register(request.email, request.password, request.full_name)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: DBSession):
    service = AuthService(db)
    result = await service.login(request.email, request.password)
    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"]
    )
```

### Step 8.2: Create api/routes/notebooks.py

```python
# api/routes/notebooks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import DBSession, CurrentUser
from api.schemas.notebook import NotebookCreateRequest, NotebookResponse, NotebookListResponse
from services.notebook_service import NotebookService

router = APIRouter(prefix="/notebooks", tags=["notebooks"])


@router.post("", response_model=NotebookResponse, status_code=status.HTTP_201_CREATED)
async def create_notebook(
    request: NotebookCreateRequest,
    db: DBSession,
    current_user: CurrentUser
):
    service = NotebookService(db)
    notebook = await service.create(current_user.id, request.title, request.description)
    return notebook


@router.get("", response_model=NotebookListResponse)
async def list_notebooks(
    db: DBSession,
    current_user: CurrentUser
):
    service = NotebookService(db)
    notebooks = await service.list(current_user.id)
    return {"notebooks": notebooks}


@router.get("/{notebook_id}", response_model=NotebookResponse)
async def get_notebook(
    notebook_id: str,
    db: DBSession,
    current_user: CurrentUser
):
    service = NotebookService(db)
    notebook = await service.get(current_user.id, notebook_id)
    return notebook


@router.delete("/{notebook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notebook(
    notebook_id: str,
    db: DBSession,
    current_user: CurrentUser
):
    service = NotebookService(db)
    await service.delete(current_user.id, notebook_id)
```

### Step 8.3: Create api/routes/pdfs.py

```python
# api/routes/pdfs.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import DBSession, CurrentUser
from api.schemas.pdf import PDFUploadResponse, PDFListResponse
from services.pdf_service import PDFService

router = APIRouter(prefix="/pdfs", tags=["pdfs"])


@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(
    notebook_id: str = Form(...),
    file: UploadFile = File(...),
    db: DBSession,
    current_user: CurrentUser
):
    service = PDFService(db)
    # Note: File saving logic to be implemented with utils/pdf_processor.py
    file_path = f"{notebook_id}/{file.filename}"
    pdf = await service.upload(current_user.id, notebook_id, file.filename, file_path)
    return PDFUploadResponse(
        filename=pdf.file_name,
        notebook_id=notebook_id,
        pdf_id=pdf.id,
        processing_status=pdf.processing_status
    )


@router.get("/list", response_model=PDFListResponse)
async def list_pdfs(
    notebook_id: str,
    db: DBSession,
    current_user: CurrentUser
):
    service = PDFService(db)
    pdfs = await service.list(current_user.id, notebook_id)
    return {"notebook_id": notebook_id, "pdfs": [{"filename": p.file_name, "status": p.processing_status} for p in pdfs]}


@router.get("/status")
async def get_pdf_status(
    notebook_id: str,
    filename: str,
    db: DBSession,
    current_user: CurrentUser
):
    service = PDFService(db)
    status = await service.get_status(current_user.id, notebook_id, filename)
    return {"status": status}


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pdf(
    notebook_id: str,
    filename: str,
    db: DBSession,
    current_user: CurrentUser
):
    service = PDFService(db)
    await service.delete(current_user.id, notebook_id, filename)
```

### Step 8.4: Create api/routes/chat.py

```python
# api/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import DBSession, CurrentUser
from api.schemas.chat import ChatQueryRequest, ChatResponse, SuggestedQueriesResponse
from services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/query", response_model=ChatResponse)
async def chat_query(
    request: ChatQueryRequest,
    db: DBSession,
    current_user: CurrentUser
):
    service = ChatService(db)
    
    # Validate notebook access
    is_valid = await service.validate_notebook_access(current_user.id, request.notebook_id)
    if not is_valid:
        raise HTTPException(status_code=404, detail="Notebook not found")
    
    # TODO: Integrate with providers/llm for actual chat logic
    # This is where the RAG pipeline will be called
    
    return ChatResponse(
        response="Response placeholder",
        query_type="rag_question",
        context_chunks=[]
    )


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    db: DBSession,
    current_user: CurrentUser
):
    service = ChatService(db)
    history = await service.get_session_history(current_user.id, session_id)
    return {"messages": history}


@router.post("/suggested-queries", response_model=SuggestedQueriesResponse)
async def get_suggested_queries(
    notebook_id: str,
    session_id: str,
    db: DBSession,
    current_user: CurrentUser
):
    # TODO: Implement suggested queries
    return SuggestedQueriesResponse(suggested_queries=[])
```

---

## Phase 9: Error Handling

### Step 9.1: Create api/errors.py

```python
# api/errors.py
from fastapi import HTTPException, status


class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class UserAlreadyExistsError(HTTPException):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email {email} already exists"
        )


class NotebookNotFoundError(HTTPException):
    def __init__(self, notebook_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notebook {notebook_id} not found"
        )


class NotebookAlreadyExistsError(HTTPException):
    def __init__(self, title: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Notebook with title '{title}' already exists"
        )


class PDFNotFoundError(HTTPException):
    def __init__(self, filename: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PDF {filename} not found"
        )


class ForbiddenError(HTTPException):
    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
```

---

## Phase 10: API Router

### Step 10.1: Create api/router.py

```python
# api/router.py
from fastapi import APIRouter
from api.routes import auth, notebooks, pdfs, chat

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(notebooks.router)
api_router.include_router(pdfs.router)
api_router.include_router(chat.router)
```

---

## Phase 11: Providers (Factory Pattern)

### Step 11.1: Create providers/base.py

```python
# providers/base.py
from abc import ABC, abstractmethod
from typing import AsyncGenerator


class BaseLLM(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass
    
    @abstractmethod
    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        pass


class BaseEmbeddings(ABC):
    @abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        pass
    
    @abstractmethod
    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        pass


class BaseReranker(ABC):
    @abstractmethod
    def rerank(self, query: str, chunks: list[str]) -> tuple[list[str], list[float]]:
        pass
```

### Step 11.2: Create providers/llm/factory.py

```python
# providers/llm/factory.py
from typing import Optional
from app.config import get_settings

settings = get_settings()
from providers.llm.base import BaseLLM
from providers.llm.ollama import OllamaLLM
from providers.llm.gemini import GeminiLLM
from providers.llm.openai import OpenAILLM


class LLMFactory:
    _providers = {}
    
    @classmethod
    def register(cls, name: str, provider_cls: type[BaseLLM]):
        cls._providers[name.lower()] = provider_cls
    
    @classmethod
    def get(cls, provider: Optional[str] = None, model: Optional[str] = None) -> BaseLLM:
        provider = (provider or settings.llm_provider).lower()
        model = model or settings.default_model
        
        if provider not in cls._providers:
            raise ValueError(f"Unknown LLM provider: {provider}")
        
        return cls._providers[provider](model=model)


# Register providers
LLMFactory.register("ollama", OllamaLLM)
LLMFactory.register("gemini", GeminiLLM)
LLMFactory.register("vllm", OpenAILLM)  # vLLM uses OpenAI-compatible interface
LLMFactory.register("openai", OpenAILLM)
```

### Step 11.3: Create providers/llm/ollama.py

```python
# providers/llm/ollama.py
from typing import AsyncGenerator
from langchain_ollama import ChatOllama

from providers.llm.base import BaseLLM
from core.prompts import SYSTEM_PROMPT


class OllamaLLM(BaseLLM):
    def __init__(self, model: str):
        self.model = model
        self.llm = ChatOllama(
            model=model,
            temperature=0.5,
            base_url="http://localhost:11434",
        )
    
    async def generate(self, prompt: str) -> str:
        response = await self.llm.agenerate([{"role": "user", "content": prompt}])
        return response.generations[0][0].text
    
    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        async for chunk in self.llm.astream([{"role": "user", "content": prompt}]):
            yield chunk.content
```

### Step 11.4: Create providers/llm/gemini.py

```python
# providers/llm/gemini.py
from typing import AsyncGenerator
from langchain_google_genai import ChatGoogleGenerativeAI

from providers.llm.base import BaseLLM
from app.config import get_settings

settings = get_settings()


class GeminiLLM(BaseLLM):
    def __init__(self, model: str):
        self.model = model
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=settings.gemini_api_key,
            temperature=0.5,
        )
    
    async def generate(self, prompt: str) -> str:
        response = await self.llm.agenerate([{"role": "user", "content": prompt}])
        return response.generations[0][0].text
    
    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        async for chunk in self.llm.astream([{"role": "user", "content": prompt}]):
            yield chunk.content
```

### Step 11.5: Create providers/llm/openai.py

```python
# providers/llm/openai.py
from typing import AsyncGenerator
from langchain_openai import ChatOpenAI

from providers.llm.base import BaseLLM
from app.config import get_settings

settings = get_settings()


class OpenAILLM(BaseLLM):
    def __init__(self, model: str):
        self.model = model
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.5,
            base_url=settings.vllm_llm_url,
            api_key="EMPTY",  # vLLM typically doesn't require key
        )
    
    async def generate(self, prompt: str) -> str:
        response = await self.llm.agenerate([{"role": "user", "content": prompt}])
        return response.generations[0][0].text
    
    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        async for chunk in self.llm.astream([{"role": "user", "content": prompt}]):
            yield chunk.content
```

### Step 11.6: Create providers/embedding/factory.py

```python
# providers/embedding/factory.py
from typing import Optional
from app.config import get_settings

settings = get_settings()
from providers.embedding.base import BaseEmbeddings
from providers.embedding.sentence_transformers import SentenceTransformersEmbeddings
from providers.embedding.vllm import VLLMEmbeddings


class EmbeddingFactory:
    _providers = {}
    
    @classmethod
    def register(cls, name: str, provider_cls: type[BaseEmbeddings]):
        cls._providers[name.lower()] = provider_cls
    
    @classmethod
    def get(cls, provider: Optional[str] = None, model: Optional[str] = None) -> BaseEmbeddings:
        provider = (provider or settings.embedding_provider).lower()
        model = model or settings.embedding_model
        
        if provider not in cls._providers:
            raise ValueError(f"Unknown embedding provider: {provider}")
        
        return cls._providers[provider](model=model)


# Register providers
EmbeddingFactory.register("sentence-transformers", SentenceTransformersEmbeddings)
EmbeddingFactory.register("vllm", VLLMEmbeddings)
```

### Step 11.7: Create providers/reranker/factory.py

```python
# providers/reranker/factory.py
from typing import Optional
from app.config import get_settings

settings = get_settings()
from providers.reranker.base import BaseReranker
from providers.reranker.flag import FlagReranker
from providers.reranker.tei import TEIReranker


class RerankerFactory:
    _providers = {}
    
    @classmethod
    def register(cls, name: str, provider_cls: type[BaseReranker]):
        cls._providers[name.lower()] = provider_cls
    
    @classmethod
    def get(cls, provider: Optional[str] = None) -> BaseReranker:
        provider = (provider or settings.reranker_provider).lower()
        
        if provider not in cls._providers:
            return TEIReranker()  # Default fallback
        
        return cls._providers[provider]()


# Register providers
RerankerFactory.register("flag", FlagReranker)
RerankerFactory.register("tei", TEIReranker)
```

---

## Phase 12: Utilities (Refactored from existing code)

### Step 12.1: Create utils/pdf_processor.py

Migrate from `src/services/pdf_processor.py` with cleaned-up structure.

### Step 12.2: Create utils/vector_store.py

Migrate Qdrant operations with proper abstraction.

---

## Phase 13: Migration of Existing Code

After all phases above are complete:

1. **Run existing tests** to ensure nothing broke
2. **Update imports** in all files to use new structure
3. **Test JWT flow** manually with curl/Postman
4. **Verify user isolation** - ensure you can't access other user's data

---

## Testing Checklist

- [ ] Register new user
- [ ] Login and receive JWT
- [ ] Create notebook (with auth token)
- [ ] List notebooks (should only show user's notebooks)
- [ ] Try accessing another user's notebook (should fail with 404)
- [ ] Upload PDF to notebook
- [ ] Chat query works
- [ ] Chat history persists in database

---

## Dependencies Management (Provider-Based)

This architecture uses `pyproject.toml` with optional dependencies to optimize image size and reduce attack surface. Only install dependencies for the providers you use.

### pyproject.toml Structure

```toml
# pyproject.toml
[project]
name = "policybot"
version = "2.0.0"
description = "AI-powered document processing and RAG API"
requires-python = ">=3.11"
dependencies = [
    # Core - always needed
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.27.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.29.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.6",
    "aiofiles>=23.0.0",
    "httpx>=0.26.0",
    "alembic>=1.13.0",
    "qdrant-client>=1.7.0",
    "structlog>=24.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
# LLM Providers
llm-ollama = [
    "langchain-ollama>=0.1.0",
]
llm-gemini = [
    "langchain-google-genai>=4.0.0",
    "google-genai>=1.55.0",
]
llm-vllm = [
    "langchain-openai>=1.1.0",
    "openai>=1.12.0",
]

# Embedding Providers
embed-sentence-transformers = [
    "sentence-transformers>=3.0.0",
    "torch>=2.0.0",
    "transformers>=4.36.0",
    "accelerate>=0.26.0",
    "flagembedding>=1.3.0",
]
embed-vllm = [
    "langchain-openai>=1.1.0",
    "openai>=1.12.0",
]

# Reranker Providers
rerank-tei = [
    "httpx>=0.26.0",
]
rerank-flag = [
    "flagembedding>=1.3.0",
    "torch>=2.0.0",
    "transformers>=4.36.0",
]

# Development dependencies
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.26.0",
    "ruff>=0.2.0",
    "mypy>=1.8.0",
]

[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### Installation Examples

```bash
# Full-featured (with torch, larger image ~3GB)
pip install policybot[llm-gemini,embed-sentence-transformers,rerank-flag]

# Lightweight vLLM only (no torch, ~500MB)
pip install policybot[llm-vllm,embed-vllm,rerank-tei]

# Ollama with sentence-transformers (mixed)
pip install policybot[llm-ollama,embed-sentence-transformers,rerank-tei]

# Production minimal (vLLM + TEI, smallest image ~400MB)
pip install policybot[llm-vllm,embed-vllm,rerank-tei]
```

### Dependency Matrix

| Provider | Install Extra | Dependencies | Image Size Impact |
|----------|---------------|--------------|-------------------|
| `ollama` | `llm-ollama` | langchain-ollama | +50MB |
| `gemini` | `llm-gemini` | langchain-google-genai | +100MB |
| `vllm` | `llm-vllm` | langchain-openai, openai | +30MB |
| `sentence-transformers` | `embed-sentence-transformers` | torch, transformers, sentence-transformers | +2.5GB |
| `vllm` (embed) | `embed-vllm` | langchain-openai | +30MB |
| `tei` | `rerank-tei` | httpx | +5MB |
| `flag` | `rerank-flag` | flagembedding, torch | +500MB |

---

## Environment Variables Required

```bash
# .env
database_url=postgresql+asyncpg://postgres:postgres@localhost:5432/policybot
jwt_secret=your-super-secret-key-change-in-production
jwt_algorithm=HS256
jwt_access_expire_minutes=30
jwt_refresh_expire_days=7

llm_provider=ollama
default_model=gemma3n:e4b

embedding_provider=sentence-transformers
embedding_model=Alibaba-NLP/gte-multilingual-base

reranker_provider=tei
```

---

## Summary

This refactor provides:

1. **Complete JWT authentication** - Register, login, protected routes
2. **User data isolation** - Every query scoped to `current_user.id`
3. **Repository pattern** - Clean data access layer with user filtering
4. **Service layer** - Business logic separated from HTTP handling
5. **Factory pattern for providers** - Easy to add new LLM/embedding/reranker
6. **Clear folder structure** - Anyone can find what they need
7. **Type-safe config** - Pydantic Settings with env validation
8. **Extensible** - Add features without touching existing code

The architecture follows FastAPI best practices and is ready for scale.

---

## Quick Reference: FastAPI Best Practices Checklist

### ✅ Async Rules
- [ ] Use `async def` with `await` for I/O operations (database, external APIs)
- [ ] Use regular `def` for blocking code or CPU-intensive work
- [ ] Never mix `async def` with blocking operations (e.g., `time.sleep()` instead of `asyncio.sleep()`)

### ✅ Dependencies
- [ ] Use `Depends()` for reusable logic (auth, database, validation)
- [ ] Create dependencies for authentication, database sessions
- [ ] Keep routes clean by moving logic to dependencies

### ✅ Background Tasks
- [ ] Never make users wait for non-critical operations
- [ ] Use `BackgroundTasks` for PDF processing, notifications
- [ ] Use Celery for heavy background work

### ✅ Security
- [ ] Hide API docs in production (`docs_url=None`)
- [ ] Never hardcode secrets - use environment variables
- [ ] Use Pydantic Settings for all config

### ✅ Database
- [ ] Use connection pooling (pool_size, max_overflow)
- [ ] Reuse connections via dependency injection
- [ ] Use async database drivers (asyncpg, async_sessionmaker)
- [ ] Use `pool_pre_ping=True` for connection health

### ✅ Validation
- [ ] Let Pydantic handle validation (EmailStr, Field constraints)
- [ ] Use `response_model` for automatic serialization
- [ ] Create custom base model for common configuration

### ✅ Deployment
- [ ] Use Gunicorn with Uvicorn workers (not raw uvicorn in production)
- [ ] Add health check endpoints (`/health`)
- [ ] Implement structured logging (JSON output)
- [ ] Use proper resource management with lifespan events

### ✅ Pydantic Best Practices
- [ ] Use custom base model with shared `model_config`
- [ ] Use `from_attributes = True` for ORM compatibility
- [ ] Use `str_strip_whitespace = True` for automatic trimming
- [ ] Use field validators for complex validation logic

---

## Production Deployment Command

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production (recommended)
gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120
```

---

## Docker Configuration (Multi-Provider Optimized)

This Dockerfile uses build arguments to install only the dependencies needed for your selected providers.

```dockerfile
# Dockerfile
# ============================================
# Multi-stage build for provider-optimized images
# ============================================
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv for faster package installation
RUN pip install --no-cache-dir uv

# Copy only pyproject.toml first (for dependency resolution)
COPY pyproject.toml .

# ============================================
# Build arguments for provider selection
# ============================================
ARG LLM_PROVIDER=ollama
ARG EMBEDDING_PROVIDER=vllm
ARG RERANKER_PROVIDER=tei
ARG ENVIRONMENT=production

# Function to map provider to extras
RUN echo "Installing provider-specific dependencies:" && \
    uv pip install --system --no-cache-dir \
        fastapi \
        uvicorn[standard] \
        sqlalchemy[asyncio] \
        asyncpg \
        pydantic \
        pydantic-settings \
        python-jose[cryptography] \
        passlib[bcrypt] \
        python-multipart \
        aiofiles \
        httpx \
        alembic \
        qdrant-client \
        structlog \
        python-dotenv && \
    if [ "$LLM_PROVIDER" = "ollama" ]; then \
        uv pip install --system --no-cache-dir langchain-ollama; \
    elif [ "$LLM_PROVIDER" = "gemini" ]; then \
        uv pip install --system --no-cache-dir langchain-google-genai google-genai; \
    elif [ "$LLM_PROVIDER" = "vllm" ]; then \
        uv pip install --system --no-cache-dir langchain-openai openai; \
    fi && \
    if [ "$EMBEDDING_PROVIDER" = "sentence-transformers" ]; then \
        uv pip install --system --no-cache-dir sentence-transformers torch transformers accelerate flagembedding; \
    elif [ "$EMBEDDING_PROVIDER" = "vllm" ]; then \
        uv pip install --system --no-cache-dir langchain-openai openai; \
    fi && \
    if [ "$RERANKER_PROVIDER" = "flag" ]; then \
        uv pip install --system --no-cache-dir flagembedding torch transformers; \
    elif [ "$RERANKER_PROVIDER" = "tei" ]; then \
        uv pip install --system --no-cache-dir httpx; \
    fi

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Environment-based configuration
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=$ENVIRONMENT

# Production: use gunicorn with uvicorn workers
# Development: use uvicorn with auto-reload
CMD if [ "$ENVIRONMENT" = "production" ]; then \
    exec gunicorn app.main:app \
        --workers 4 \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:8000 \
        --timeout 120; \
    else \
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload; \
    fi
```

### Build Commands for Different Configurations

```bash
# ============================================
# Production: vLLM only (smallest image ~400MB)
# ============================================
docker build \
    --build-arg LLM_PROVIDER=vllm \
    --build-arg EMBEDDING_PROVIDER=vllm \
    --build-arg RERANKER_PROVIDER=tei \
    --build-arg ENVIRONMENT=production \
    -t policybot:vllm-minimal \
    .

# ============================================
# Full-featured: sentence-transformers + flag (larger ~3GB)
# ============================================
docker build \
    --build-arg LLM_PROVIDER=gemini \
    --build-arg EMBEDDING_PROVIDER=sentence-transformers \
    --build-arg RERANKER_PROVIDER=flag \
    --build-arg ENVIRONMENT=production \
    -t policybot:full \
    .

# ============================================
# Development with hot reload
# ============================================
docker build \
    --build-arg LLM_PROVIDER=ollama \
    --build-arg EMBEDDING_PROVIDER=vllm \
    --build-arg RERANKER_PROVIDER=tei \
    --build-arg ENVIRONMENT=development \
    -t policybot:dev \
    .

# Run dev container
docker run -p 8000:8000 -v $(pwd):/app policybot:dev
```

### Docker Compose for Local Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: policybot
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # Qdrant (Vector Store)
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  # PolicyBot API
  api:
    build:
      context: .
      args:
        LLM_PROVIDER: ${LLM_PROVIDER:-ollama}
        EMBEDDING_PROVIDER: ${EMBEDDING_PROVIDER:-vllm}
        RERANKER_PROVIDER: ${RERANKER_PROVIDER:-tei}
        ENVIRONMENT: development
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/policybot
      - QDRANT_HOST=qdrant
      - ENVIRONMENT=development
    volumes:
      - .:/app
    depends_on:
      - postgres
      - qdrant

volumes:
  postgres_data:
  qdrant_data:
```

### Environment File for Docker

```bash
# .env.docker
# Provider selection (change these to optimize image)
LLM_PROVIDER=vllm
EMBEDDING_PROVIDER=vllm
RERANKER_PROVIDER=tei
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/policybot

# JWT
JWT_SECRET=dev-secret-change-in-production

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### Build and Run Scripts

```bash
# scripts/build.sh
#!/bin/bash
set -e

LLM_PROVIDER=${LLM_PROVIDER:-vllm}
EMBEDDING_PROVIDER=${EMBEDDING_PROVIDER:-vllm}
RERANKER_PROVIDER=${RERANKER_PROVIDER:-tei}
ENVIRONMENT=${ENVIRONMENT:-production}
IMAGE_TAG=${IMAGE_TAG:-policybot:custom}

echo "Building with providers: LLM=$LLM_PROVIDER, Embed=$EMBEDDING_PROVIDER, Rerank=$RERANKER_PROVIDER"

docker build \
    --build-arg LLM_PROVIDER=$LLM_PROVIDER \
    --build-arg EMBEDDING_PROVIDER=$EMBEDDING_PROVIDER \
    --build-arg RERANKER_PROVIDER=$RERANKER_PROVIDER \
    --build-arg ENVIRONMENT=$ENVIRONMENT \
    -t $IMAGE_TAG \
    .

echo "Built: $IMAGE_TAG"
```

```bash
# Quick start
export LLM_PROVIDER=vllm
export EMBEDDING_PROVIDER=vllm
export RERANKER_PROVIDER=tei
./scripts/build.sh
docker-compose up
```

---

## Quick Start Commands

```bash
# 1. Clone and setup
cd backend

# 2. Create pyproject.toml (from plan above)

# 3. Install with specific providers
pip install -e ".[llm-vllm,embed-vllm,rerank-tei]"

# 4. Run migrations
alembic upgrade head

# 5. Start server
uvicorn app.main:app --reload

# Or with Docker
docker-compose up --build
```

### Makefile Automation

Add a Makefile to automate all common tasks. The Makefile reads from `.env` for provider configuration:

```makefile
# Makefile - automate all common tasks

# Load environment variables
include .env
export

help:
	@echo "PolicyBot Backend - Available Commands"
	@echo ""
	@echo "  make install          Install dependencies (reads .env)"
	@echo "  make dev              Run development server"
	@echo "  make build            Build Docker image (reads .env)"
	@echo "  make up               Start all services"
	@echo "  make down             Stop all services"
	@echo "  make migrate          Run database migrations"
	@echo "  make reset            Reset database"
	@echo "  make clean            Clean cache files"

install:
	@echo "Installing for LLM=$(LLM_PROVIDER), Embed=$(EMBEDDING_PROVIDER), Rerank=$(RERANKER_PROVIDER)"
	@pip install -e ".[llm-$(LLM_PROVIDER),embed-$(EMBEDDING_PROVIDER),rerank-$(RERANKER_PROVIDER)]"

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

build:
	docker build \
		--build-arg LLM_PROVIDER=$$LLM_PROVIDER \
		--build-arg EMBEDDING_PROVIDER=$$EMBEDDING_PROVIDER \
		--build-arg RERANKER_PROVIDER=$$RERANKER_PROVIDER \
		-t policybot .

up:
	docker-compose up --build

down:
	docker-compose down

migrate:
	alembic upgrade head

reset:
	docker-compose down -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

.PHONY: help install dev build up down migrate reset clean
```

**Usage:**
```bash
# Just copy .env with your provider choices, then:
make install
make dev

# Docker:
make build
make up
```