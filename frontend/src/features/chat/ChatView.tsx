"use client";

import { useSearchParams } from "next/navigation";
import { v4 as uuidv4 } from "uuid";
import { useEffect, useRef,useState } from "react";

import ChatBody from "./components/ChatBody";
import ChatInput from "./components/chatinput/ChatInput";
import ChatFooter from "./components/ChatFooter";
import BaseSideContainer from "@/features/layout/components/BaseSideContainer";

import { useChatUI } from "./hooks/useChatUI";
import { sendQueryStream } from "@/lib/api/chat.api";
import { getChatHistory } from "@/lib/api/chat.api";
import { mapHistoryToMessages } from "./chat.mapper";

interface Props {
  notebookId: string;
  selectedPdfIds: string[];
}

const ChatView = ({ notebookId, selectedPdfIds }: Props) => {
  const searchParams = useSearchParams();

  // 🔥 SESSION ID (from URL or fallback)
const sessionRef = useRef<string>(uuidv4());

// ✅ derive sessionId safely
const sessionId = searchParams.get("session_id") ?? sessionRef.current;

const {
  messages,
  input,
  setInput,
  addUserMessage,
  addAILoadingMessage,
  updateAIMessage,
  setChatMessages, // ✅ NEW
  clearChat,
} = useChatUI();

  const [isHistoryLoading, setIsHistoryLoading] = useState(true);

  const isDisabled = selectedPdfIds.length === 0;

  useEffect(() => {
  const fetchHistory = async () => {
    try {
      setIsHistoryLoading(true);

      const res = await getChatHistory(sessionId);

      const mapped = mapHistoryToMessages(res.messages || []);

      setChatMessages(mapped);
    } catch (err) {
      console.error("Failed to load chat history", err);
      clearChat();
    } finally {
      setIsHistoryLoading(false);
    }
  };

  fetchHistory();
}, [sessionId]);


  const handleSend = async () => {
    if (!input.trim() || isDisabled) return;

    const userText = input;

    // 1️⃣ Add user message
    addUserMessage(userText);

    // 2️⃣ Add AI loading message
    const aiMessageId = addAILoadingMessage();

    setInput("");

    try {
      let fullText = "";

      await sendQueryStream(
        {
          query: userText,
          session_id: sessionId,
          notebook_id: notebookId,
          pdf_ids: selectedPdfIds,
        },
        (chunk: string) => {
          fullText += chunk;

          // 🔥 LIVE STREAM UPDATE
          updateAIMessage(aiMessageId, fullText);
        }
      );
    } catch (err: any) {
      updateAIMessage(
        aiMessageId,
        "Error: Failed to get response. Please try again."
      );
    }
  };

  return (
    <BaseSideContainer title="Chat">
      <div className="flex flex-col h-full">
        <ChatBody messages={messages} loading={isHistoryLoading} />
        <ChatInput
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onSend={handleSend}
          disabled={isDisabled}
          selectedCount={selectedPdfIds.length}
        />

        <ChatFooter />
      </div>
    </BaseSideContainer>
  );
};

export default ChatView;