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
  updateAIMessage: (
    id: string,
    v: string | ((p: string) => string),
    isStreaming?: boolean,
  ) => void;
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
  const { pushChunk, complete, reset } =
    useTypingEngine(updateAIMessage);

  const handleSend = async (
  overrideText?: string | React.SyntheticEvent
) => {
  onCitationsUpdate([]);

  /**
   * 🚫 HARD BLOCK: NO SOURCES SELECTED
   * (This is now SOURCE OF TRUTH)
   */
  if (selectedPdfIds.length === 0) {
    console.warn("Blocked: No sources selected");
    return;
  }

  /**
   * FORCE CLEAN TEXT ONLY
   */
  let text = "";

  if (typeof overrideText === "string") {
    text = overrideText;
  } else {
    text = input;
  }

  text = String(text ?? "").trim();

  if (!text) return;

  reset();
  hasStartedRef.current = true;

  addUserMessage(text);

  const aiId = addAILoadingMessage();

  /**
   * ALWAYS CLEAR INPUT
   */
  setInput("");

  try {
    await sendQueryStream(
      {
        query: text,
        session_id: sessionId,
        notebook_id: notebookId,
        pdf_ids: selectedPdfIds,
      },
      (chunk) => pushChunk(chunk, aiId),
      (chunks) => {
        updateAIMessageChunks(aiId, chunks);
        onCitationsUpdate(chunks);
      },
      () => complete(aiId)
    );
  } catch (error) {
    console.error(error);
    reset();
    updateAIMessage(
  aiId,
  "Error: Failed to get response.",
  false
);
  }
};

  return { handleSend };
};