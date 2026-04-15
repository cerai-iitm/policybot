export interface ChatQueryRequest {
  query: string
  notebook_id: number   // ✅ FIXED
  session_id: string
  pdf_ids?: number[]    // ✅ FIXED
}

export interface ChatMessage {
  id: number
  role: "user" | "assistant"
  content: string
  created_at: string
}