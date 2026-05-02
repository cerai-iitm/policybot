export interface SourceChunk {
  text: string;
  source: string;
  page_number: number | null;
}

export interface Message {
  id: string;
  type: "user" | "ai";
  content: string;
  sourceChunks?: SourceChunk[];
  loading?: boolean;
  
}

export interface SourceChunk {
  text: string;
  source: string;
  page_number: number | null;
  original_filename?: string; // ✅ ADD THIS
}
