export interface ChatPayload {
  query: string;
  session_id: string;
  notebook_id: string;
  pdf_ids: string[];
}
