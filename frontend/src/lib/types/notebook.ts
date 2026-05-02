export interface CreateNotebookPayload {
  title: string;
  description: string;
}

export type NotebookListItem = {
  notebook_id: string;
  title: string;
  description?: string;
  created_at: string;
  processed_pdf_count: number; // ✅ ADD THIS
};

export type NotebookResponse = {
  id: number;
  notebook_id: string;
  title: string;
  description: string;
  created_at: string;
  processed_pdf_count: number;
};

export interface PdfDetailsResponse {
  summary: string;
  suggested_queries: string[];
}