export interface UploadPdfPayload {
  notebook_id: string;
  file: File;
}

export interface PdfItem {
  pdf_id: string;              // stored_filename
  filename: string;            // original_filename
  notebook_id: string;
  processing_status: string;
  summary: string;
  uploaded_at: string;
  suggested_queries: string[];
}
