# Release Notes

## v2.1.0 — Mar 6th, 2026

**Summary:** Adds a new Homepage SPA, first-class notebooks, optional `vllm` provider support, a chain-based summarization rewrite, and Alembic migrations configuration. These changes improve notebook-centric workflows, offer an alternative LLM/embedding provider, and make summaries more robust and maintainable.

### Added

- Full Homepage SPA: a standalone single-page app lives in `Homepage/` and provides the new landing experience for notebooks, PDF browsing, summaries and queries (see `Homepage/`).
- Notebooks: added notebook support for grouping PDFs together under project-defined logic; includes a persistent notebook model, notebook-scoped PDF lookups, and suggested-question import tooling (`backend/src/db/schema/notebooks.py`, `backend/src/db/crud/notebooks_crud.py`, `backend/scripts/import_suggested_examples.py`).
- Optional `vllm` provider: backend can use `vllm` for LLM and embeddings via `backend/src/services/external.py` and `backend/src/services/vllm_embeddings.py`; docker-compose includes vllm services for local runs.
- Chain-based summarization and rewritten-query generation: summarization flows moved into chain-based functions to improve consistency and reranking (`backend/src/services/LLM_interface.py`, `backend/src/services/retriever.py`).
- Alembic migrations: configuration added so schema migrations can be authored and applied (`backend/alembic.ini`).

### Changed

- Summaries: source and overall summary generation moved into new service flows and persisted via existing summary CRUD (`backend/src/db/crud/source_summaries_crud.py`, `backend/src/db/crud/overall_summaries_crud.py`).
- Embeddings & retrieval: backend can route embedding calls to `vllm` or the previous provider via the provider factory (`backend/src/services/external.py`); document ingestion updated to support the vllm path (`backend/src/services/pdf_processor.py`).
- Frontend: `Homepage/` is the official project Homepage — a detailed SPA that explains the project and provides the primary landing experience; it integrates with the backend APIs and can be run independently from the existing `frontend/` app.

### Breaking Changes & Upgrade Notes

- Embeddings provider change: the default embedding model has been changed to `embeddinggemma-300m` (`google/embeddinggemma-300m`) replacing the previous `Alibaba-NLP/gte-multilingual-base`. Enabling access to this model requires a valid Hugging Face token in your backend environment (set in your `.env`) and that the token's account has permission to use the model. You will also have to regenerate the embeddings for your existing PDFs
- vllm is optional — enabling it requires starting the vllm services in `docker-compose.yml` and setting the backend provider to `vllm` (configuration read by `backend/src/services/external.py`). Test in staging first: vllm instances are resource intensive.
- Run Alembic migrations after upgrading so DB schemas match the code (`cd backend && alembic upgrade head` when your Python environment and PYTHONPATH are configured).

## v2.0.0 — Jan 1st, 2026

**Summary:** Major migration from the v1 Streamlit + Chroma stack to a production-oriented FastAPI backend, Next.js frontend, and Qdrant retrieval. Adds multi-user-safe request handling, resumable PDF ingestion, and admin-only model overrides while keeping Docker/Nginx deployment flows.

### Added

- Multi-user-safe chat flow: per-session IDs, async LLM calls, and chunk metadata in responses for grounding (see [backend/src/routers/chat.py](backend/src/routers/chat.py)).
- Per-request model override for admins and default-model discovery endpoint for the UI (see [backend/src/routers/chat.py](backend/src/routers/chat.py)).
- Resumable PDF ingestion: state-aware upload validation, SSE-driven processing, and cleanup of embeddings/summaries on delete (see [backend/src/routers/pdf.py](backend/src/routers/pdf.py)).
- PDF management endpoints: list, view, summarize, delete, and continue processing partially ingested PDFs (see [backend/src/routers/pdf.py](backend/src/routers/pdf.py)).
- Qdrant-backed retrieval: query rewriting, multi-query embedding search, reciprocal-rank fusion, FlagReranker filtering, and source/page metadata returned for citations (see [backend/src/rag/retriever.py](backend/src/rag/retriever.py)).
- Overall summary generation and caching from source summaries to avoid recomputation (see [backend/src/routers/chat.py](backend/src/routers/chat.py)).
- Frontend UX: separate user (`/policybot`) and admin (`/policybot/config`) entry points; dark mode toggle; GitHub link in header; drag/drop uploads with progress modal; ability to delete PDFs; source-cited chat responses; admin model selector; chat UI shows citations (chunk text, source, page), keeps per-session conversation ID, and guards against sending with no PDFs selected (see [frontend/src/components/chat/ChatSection.tsx](frontend/src/components/chat/ChatSection.tsx) and [frontend/src/components/leftSidebar/FileUpload.tsx](frontend/src/components/leftSidebar/FileUpload.tsx)).

### Changed

- Platform migration: Streamlit UI and Chroma store replaced by FastAPI + Next.js + Qdrant for better concurrency, routing, and admin controls (see [backend/src/main.py](backend/src/main.py)).
- Data path now targets a Qdrant collection; embeddings and summaries are persisted via Qdrant + database instead of Chroma.
- API surface consolidated under `/api/*` and exposed through Nginx at `/policybot/api/*`; frontend served via Next.js at `/policybot`.
- Deployment defaults rely on Docker Compose with Nginx reverse proxy; `make dev`/`make prod` orchestrate builds and service startup; README includes GPU guidance for optional acceleration (see [README.md](README.md)).

### Breaking Changes & Upgrade Notes

- Chroma embeddings are not reused; re-embed PDFs into the Qdrant collection before querying.
- Frontend routes moved to Next.js (`/policybot` via Nginx); the old Streamlit endpoint is removed.
- API surface now under `policybot/api/*` with FastAPI; clients should call `POST policybot/api/query` and related endpoints.
- Ensure backend environment variables match the new stack (see `backend/.env.example`); set Qdrant host/port and model defaults.
