# Release Notes

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
