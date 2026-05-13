"use client";

import { sendQueryStream } from "@/lib/api/chat.api";
import { useTypingEngine } from "./useTypingEngine";

type ChatControllerProps = {
  sessionId: string;
  notebookId: string;
  selectedPdfIds: string[];
  input: string;
  setInput: (v: string) => void;
  addUserMessage: (t: string) => void;
  addAILoadingMessage: () => string;
  updateAIMessage: (id: string, v: string | ((p: string) => string)) => void;
  updateAIMessageChunks: (id: string, chunks: any[]) => void;
  onCitationsUpdate: (chunks: any[]) => void;
  hasStartedRef: React.MutableRefObject<boolean>;
  
};


export const useChatController = ({
  sessionId,
  notebookId,
  selectedPdfIds,
  input,
  setInput,
  addUserMessage,
  addAILoadingMessage,
  updateAIMessage,
  updateAIMessageChunks,
  onCitationsUpdate,
  hasStartedRef,
}: ChatControllerProps) => {
  const { pushChunk, flushBuffer, reset } = useTypingEngine(updateAIMessage);

  const handleSend = async (overrideText?: string) => {
    onCitationsUpdate([]);

    const text = overrideText ?? input;
    if (!text.trim()) return;

    hasStartedRef.current = true;

    addUserMessage(text);
    const aiId = addAILoadingMessage();

    if (!overrideText) setInput("");

    reset();

    try {
      await sendQueryStream(
        {
          query: text,
          session_id: sessionId,
          notebook_id: notebookId,
          pdf_ids: selectedPdfIds,
        },
        (chunk: string) => {
          pushChunk(chunk, aiId);
        },
        (chunks) => {
          updateAIMessageChunks(aiId, chunks);
          onCitationsUpdate(chunks);
        },
        () => {
          flushBuffer(aiId);
        }
      );
    } catch {
      updateAIMessage(aiId, "Error: Failed to get response.");
    }
  };

  return { handleSend };
};