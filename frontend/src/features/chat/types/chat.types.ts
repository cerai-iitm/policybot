export interface SourceChunk {
  text: string;
  source: string;
  page_number: number | null;
  original_filename?: string;
}

export interface Message {
  id: string;

  type: "user" | "ai";

  content: string;

  sourceChunks?: SourceChunk[];

  /**
   * Initial placeholder loader state
   */
  loading?: boolean;

  /**
   * TRUE while:
   * - SSE stream active
   * - typing queue draining
   *
   * FALSE only after full render completion.
   */
  isStreaming?: boolean;
}