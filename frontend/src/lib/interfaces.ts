// frontend/src/lib/interfaces.ts
// Backend references:
//   - backend/src/api/routers/notebooks.py (notebook endpoints)
//   - backend/src/api/routers/pdf.py (PDF endpoints)
//   - backend/src/api/routers/chat.py (chat endpoints)
//
// HTTP endpoints used:
// Notebooks:
//   POST  /notebooks/create   -> create notebook
//   GET   /notebooks/list     -> list notebooks
// PDFs:
//   POST  /upload             -> upload PDF (backend file: backend/src/api/routers/pdf.py -> @router.post(\"/upload\"))
//   GET   /list               -> list PDFs (backend file: backend/src/api/routers/pdf.py -> @router.get(\"/list\"))
//   POST  /remove             -> delete PDF (backend file: backend/src/api/routers/pdf.py -> @router.post(\"/remove\"))
//   GET   /process            -> SSE status (backend file: backend/src/api/routers/pdf.py -> @router.get(\"/process\"))
//   GET   /view               -> download PDF (backend file: backend/src/api/routers/pdf.py -> @router.get(\"/view\"))
//   GET   /summary            -> get summary (backend file: backend/src/api/routers/pdf.py -> @router.get(\"/summary\"))
// Chat:
//   POST  /query              -> query with RAG (backend file: backend/src/api/routers/chat.py -> @router.post(\"/query\"))
//   GET   /overall-summary    -> get overall summary (backend file: backend/src/api/routers/chat.py -> @router.get(\"/overall-summary\"))
//   POST  /suggested-queries  -> get suggested queries (backend file: backend/src/api/routers/chat.py -> @router.post(\"/suggested-queries\"))
//   GET   /default-model      -> get default model (backend file: backend/src/api/routers/chat.py -> @router.get(\"/default-model\"))

export type ISODateString = string;


export type ProcessingStatus =
  | "pending"
  | "processing"
  | "done"
  | "error";

  export type UIPDFItem = Omit<PDFListItem, "pdf_id" | "file_path"> & {
  pdf_id?: number;
  file_path?: string;
};



export interface PDFListResponse {
  pdfs: PDFListItem[];
}


/* Notebook responses */
export interface NotebookCreateResponse {
  id: number;
  notebook_id: string;
  title: string;
  description?: string | null;
  created_at: ISODateString;
}

export interface NotebookListItem {
  id: number;
  notebook_id: string;
  title: string;
  description?: string | null;
  created_at: ISODateString;
}

/* First notebook PDF item includes optional base64 contents for fast initial load */
export interface FirstNotebookPDFItem {
  filename: string;
  file_path: string;
  processing_status: string;
  uploaded_at: ISODateString;
  pdf_id: number;
  content_base64?: string | null;
  summary?: string | null;
}

/* List response (backend may include first_notebook fields) */
export interface NotebookListResponse {
  notebooks: NotebookListItem[];
  first_notebook_id?: string | null;
  first_notebook_pdfs?: FirstNotebookPDFItem[] | null;
}

/* PDF responses */
export interface PDFUploadResponse {
  filename: string;
  notebook: string;
  notebook_id: string;
  pdf_id: number;
  processing_state: string;
  file_path: string;
}

export interface PDFListItem {
  filename: string;
  file_path: string;
  processing_status: string;
  uploaded_at: ISODateString;
  pdf_id: number;
  summary?: string | null;
}

export interface PDFListResponse {
  notebook: string;
  notebook_id: string;
  pdfs: PDFListItem[];
}

export interface PDFDeleteResponse {
  message: string;
  file_deleted: boolean;
  embeddings_deleted: boolean;
  summary_deleted: boolean;
  overall_summaries_deleted: number;
  pdf_record_deleted: boolean;
}

export interface PDFSummaryResponse {
  summary: string;
  filename: string;
  notebook: string;
  notebook_id: string;
}

/* Chat request/response interfaces */
export interface QueryRequest {
  query: string;
  pdfs?: string[] | null;
  session_id: string;
  model_name?: string | null;
  notebook_id: string;
}

export interface ContextChunk {
  text: string;
  source: string;
  page_number: number;
}

export interface QueryResponse {
  response: string;
  context_chunks: ContextChunk[];
}

export interface QueryErrorResponse {
  error: string;
  context_chunks: ContextChunk[];
}

export interface OverallSummaryResponse {
  summary: string;
  files: string[];
}

export interface SuggestedQueriesRequest {
  session_id: string;
}

export interface SuggestedQueriesResponse {
  suggested_queries: string[];
}

export interface DefaultModelResponse {
  model_name: string;
  provider: string;
  supported_models: any[]; // Adjust based on actual shape (likely {id: string, name: string}[])
}

/* Standard error shape returned by backend JSON */
export interface ErrorResponse {
  detail: string;
}

/* Generic promise wrapper type used across router functions */
export type ApiResult<T> = Promise<T>;

/* -----------------------
   Helper utilities
   ----------------------- */

/**
 * Try to parse standard backend error JSON from axios error.
 * Returns ErrorResponse or null if parse failed.
 */
export function parseBackendError(err: unknown): ErrorResponse | null {
  // best-effort parsing of Axios-like error
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const anyErr = err as any;
  if (anyErr?.response?.data && typeof anyErr.response.data.detail === 'string') {
    return { detail: anyErr.response.data.detail };
  }
  return null;
}
