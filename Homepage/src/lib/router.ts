// frontend/src/lib/router.ts
// Notebook, PDF, and Chat router wrappers.
// Backend reference files:
//   - backend/src/api/routers/notebooks.py (notebooks)
//   - backend/src/api/routers/pdf.py (PDFs)
//   - backend/src/api/routers/chat.py (chat)
//
// Exact backend routes (notebooks):
//   POST  /notebooks/create   (backend file: backend/src/api/routers/notebooks.py -> @router.post(\"/create\"))
//   GET   /notebooks/list     (backend file: backend/src/api/routers/notebooks.py -> @router.get(\"/list\"))
//
// Exact backend routes (PDFs, under /api/pdf prefix):
//   POST  /upload             (backend file: backend/src/api/routers/pdf.py -> @router.post(\"/upload\"))
//   GET   /list               (backend file: backend/src/api/routers/pdf.py -> @router.get(\"/list\"))
//   POST  /remove             (backend file: backend/src/api/routers/pdf.py -> @router.post(\"/remove\"))
//   GET   /process            (backend file: backend/src/api/routers/pdf.py -> @router.get(\"/process\"))
//   GET   /view               (backend file: backend/src/api/routers/pdf.py -> @router.get(\"/view\"))
//   GET   /summary            (backend file: backend/src/api/routers/pdf.py -> @router.get(\"/summary\"))
//
// Exact backend routes (chat, under /api prefix):
//   POST  /query              (backend file: backend/src/api/routers/chat.py -> @router.post(\"/query\"))
//   GET   /overall_summary    (backend file: backend/src/api/routers/chat.py -> @router.get(\"/overall_summary\"))
//   GET   /suggested_queries  (backend file: backend/src/api/routers/chat.py -> @router.get(\"/suggested_queries\"))
//   GET   /default_model      (backend file: backend/src/api/routers/chat.py -> @router.get(\"/default_model\"))
//
// Use axios for requests. Ensure NEXT_PUBLIC_API_BASE points to backend base URL (e.g. http://localhost:8000)
// and NEXT_PUBLIC_BASE_PATH to '/policybot'

import axios, { AxiosInstance, AxiosResponse } from "axios";
import { withBase } from "@/lib/url";
import {
  NotebookCreateResponse,
  NotebookListResponse,
  PDFUploadResponse,
  PDFListResponse,
  PDFDeleteResponse,
  PDFSummaryResponse,
  QueryRequest,
  QueryResponse,
  QueryErrorResponse,
  OverallSummaryResponse,
  SuggestedQueriesResponse,
  DefaultModelResponse,
  ApiResult,
} from "./interfaces";

// Use relative URL to go through nginx proxy (avoids CORS)
const BASE = import.meta.env.VITE_API_BASE ?? "";

export const api: AxiosInstance = axios.create({
  baseURL: BASE,
  headers: {
    Accept: "application/json",
  },
});

/* -----------------------
   Notebook endpoints
   ----------------------- */

/**
 * Create a notebook using form POST.
 *
 * Backend route (exact):
 *   POST /notebooks/create
 *   backend file: backend/src/api/routers/notebooks.py (decorator: @router.post(\"/create\"))
 *
 * Returns NotebookCreateResponse.
 */
export async function createNotebook(
  title: string,
  description?: string | null,
): ApiResult<NotebookCreateResponse> {
  const form = new FormData();
  form.append("title", title);
  if (description != null) form.append("description", description);

  const resp: AxiosResponse<NotebookCreateResponse> = await api.post(
    withBase("/api/notebooks/create"),
    form,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    },
  );
  return resp.data;
}

/**
 * List notebooks. Backend may include first_notebook_pdfs for quick initial load.
 *
 * Backend route (exact):
 *   GET /notebooks/list
 *   backend file: backend/src/api/routers/notebooks.py (decorator: @router.get(\"/list\"))
 */
export async function listNotebooks(): ApiResult<NotebookListResponse> {
  const resp: AxiosResponse<NotebookListResponse> = await api.get(
    withBase("/api/notebooks/list"),
  );
  return resp.data;
}

/* -----------------------
   PDF endpoints
   ----------------------- */

/**
 * Upload a PDF to a notebook.
 *
 * Backend route (exact):
 *   POST /upload
 *   backend file: backend/src/api/routers/pdf.py -> @router.post(\"/upload\")
 *
 * Returns PDFUploadResponse (201 for new, 200 if exists).
 */
export async function uploadPdf(
  notebookId: string,
  file: File,
): ApiResult<PDFUploadResponse> {
  const form = new FormData();
  form.append("notebook_id", notebookId);
  form.append("file", file, file.name);

  const resp = await api.post<PDFUploadResponse>(
    withBase("/api/pdf/upload"),
    form,
    {
      headers: { "Content-Type": "multipart/form-data" },
    },
  );
  return resp.data;
}

/**
 * List PDFs in a notebook.
 *
 * Backend route (exact):
 *   GET /list
 *   backend file: backend/src/api/routers/pdf.py -> @router.get(\"/list\")
 */
export async function listPdfs(notebookId: string): ApiResult<PDFListResponse> {
  const resp = await api.get<PDFListResponse>(withBase("/api/pdf/list"), {
    params: { notebook_id: notebookId },
  });
  return resp.data;
}

/**
 * Delete PDF (POST for firewall compatibility).
 *
 * Backend route (exact):
 *   POST /remove
 *   backend file: backend/src/api/routers/pdf.py -> @router.post(\"/remove\")
 */
export async function deletePdf(
  notebookId: string,
  filename: string,
): ApiResult<PDFDeleteResponse> {
  const form = new FormData();
  form.append("notebook_id", notebookId);
  form.append("filename", filename);

  const resp = await api.post<PDFDeleteResponse>(
    withBase("/api/pdf/remove"),
    form,
    {
      headers: { "Content-Type": "multipart/form-data" },
    },
  );
  return resp.data;
}

/**
 * Get PDF summary.
 *
 * Backend route (exact):
 *   GET /summary
 *   backend file: backend/src/api/routers/pdf.py -> @router.get(\"/summary\")
 */
export async function getPdfSummary(
  notebookId: string,
  filename: string,
): ApiResult<PDFSummaryResponse> {
  const resp = await api.get<PDFSummaryResponse>(withBase("/api/pdf/summary"), {
    params: { notebook_id: notebookId, filename },
  });
  return resp.data;
}

/**
 * Download PDF as Blob (for viewing/downloading).
 *
 * Backend route (exact):
 *   GET /view
 *   backend file: backend/src/api/routers/pdf.py -> @router.get(\"/view\")
 *
 * Returns Blob (application/pdf).
 */
export async function downloadPdfBlob(
  notebookId: string,
  filename: string,
): ApiResult<Blob> {
  const resp = await api.get<Blob>(withBase("/api/pdf/view"), {
    params: { notebook_id: notebookId, filename },
    responseType: "blob",
  });
  return resp.data;
}

/**
 * Convenience helper that returns a browser object URL for the PDF blob.
 * Caller should call URL.revokeObjectURL(url) when done.
 */
export async function getPdfObjectUrl(
  notebookId: string,
  filename: string,
): ApiResult<string> {
  const blob = await downloadPdfBlob(notebookId, filename);
  const url = URL.createObjectURL(blob);
  return url;
}

/**
 * Connect to SSE endpoint that streams processing status updates.
 * Uses EventSource for "yielding" status messages.
 *
 * Backend route (exact):
 *   GET /process
 *   backend file: backend/src/api/routers/pdf.py -> @router.get(\"/process\")
 *
 * Returns the EventSource instance (caller should call .close()).
 */
export function monitorPdfProcessing(
  notebookId: string,
  filename: string,
  onMessage: (message: string) => void,
  onError?: (ev: Event) => void,
): EventSource {
  // Build URL with base
  const base = BASE || window.location.origin;
  const url = new URL(withBase("/api/pdf/process"), base);
  url.searchParams.set("notebook_id", notebookId);
  url.searchParams.set("filename", filename);

  const es = new EventSource(url.toString());
  es.onmessage = (ev) => {
    // Each message's data contains status or final 'done'
    onMessage(ev.data);
  };
  es.onerror = (ev) => {
    if (onError) onError(ev);
    // leave EventSource open for caller to decide
  };
  return es;
}

/* -----------------------
   Chat endpoints
   ----------------------- */

/**
 * Query the chat system.
 *
 * Backend route (exact):
 *   POST /query
 *   backend file: backend/src/api/routers/chat.py -> @router.post(\"/query\")
 *
 * Returns QueryResponse or QueryErrorResponse.
 */
export async function queryChat(
  request: QueryRequest,
): ApiResult<QueryResponse | QueryErrorResponse> {
  const resp = await api.post<QueryResponse | QueryErrorResponse>(
    withBase("/api/query"),
    request,
    {
      headers: { "Content-Type": "application/json" },
    },
  );
  return resp.data;
}

/**
 * Get overall summary of all PDFs in a notebook.
 *
 * Backend route (exact):
 *   GET /overall_summary
 *   backend file: backend/src/api/routers/chat.py -> @router.get(\"/overall_summary\")
 */
export async function getOverallSummary(
  notebookId: string,
): ApiResult<OverallSummaryResponse> {
  const resp = await api.get<OverallSummaryResponse>(
    withBase("/api/overall_summary"),
    {
      params: { notebook_id: notebookId },
    },
  );
  return resp.data;
}

/**
 * Get suggested queries based on session history.
 *
 * Backend route (exact):
 *   GET /suggested_queries
 *   backend file: backend/src/api/routers/chat.py -> @router.get(\"/suggested_queries\")
 */
export async function getSuggestedQueries(
  sessionId: string,
): ApiResult<SuggestedQueriesResponse> {
  const resp = await api.get<SuggestedQueriesResponse>(
    withBase("/api/suggested_queries"),
    {
      params: { session_id: sessionId },
    },
  );
  return resp.data;
}

/**
 * Get the default model configuration.
 *
 * Backend route (exact):
 *   GET /default_model
 *   backend file: backend/src/api/routers/chat.py -> @router.get(\"/default_model\")
 */
export async function getDefaultModel(): ApiResult<DefaultModelResponse> {
  const resp = await api.get<DefaultModelResponse>(
    withBase("/api/default_model"),
  );
  return resp.data;
}
