"use client";

import { useSearchParams } from "next/navigation";
import { v4 as uuidv4 } from "uuid";
import { useEffect, useRef, useState } from "react";

import ChatBody from "./components/ChatBody";
import ChatInput from "./components/chatinput/ChatInput";
import ChatFooter from "./components/ChatFooter";
import BaseSideContainer from "@/features/layout/components/BaseSideContainer";

import { useChatUI } from "./hooks/useChatUI";
import { sendQueryStream, getChatHistory, deleteChatHistory } from "@/lib/api/chat.api";
import { mapHistoryToMessages } from "./chat.mapper";

import ChatMenu from "./components/chatmenu/ChatMenu";
import CommonModal from "@/components/popup";
import { getPdfDetails } from "@/lib/api/notebook.api";


interface Props {
  notebookId: string;
  selectedPdfIds: string[];
  onCitationsUpdate: (chunks: any[]) => void;
  onOpenCitations: () => void;
}

const ChatView = ({ notebookId, selectedPdfIds,onCitationsUpdate,onOpenCitations }: Props) => {
  const searchParams = useSearchParams();

  const sessionRef = useRef<string>(uuidv4());
  const sessionId = searchParams.get("session_id") ?? sessionRef.current;

  const {
    messages,
    input,
    setInput,
    addUserMessage,
    addAILoadingMessage,
    updateAIMessage,
    setChatMessages,
    clearChat,
    updateAIMessageChunks
  } = useChatUI();

  const [isHistoryLoading, setIsHistoryLoading] = useState(true);
  const [menuOpen, setMenuOpen] = useState(false);

  // ✅ NEW: modal + loading
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const [summary, setSummary] = useState<string>("");
const [suggestedQueries, setSuggestedQueries] = useState<string[]>([]);
const [isSummaryLoading, setIsSummaryLoading] = useState(false);


// 🚫 prevents refresh after chat starts
const hasUserStartedChatRef = useRef(false);


useEffect(() => {
  let retryTimer: NodeJS.Timeout;

  const fetchSummary = async (retry = 0) => {
    if (!selectedPdfIds.length) {
      setSummary("");
      setSuggestedQueries([]);
      return;
    }

    if (hasUserStartedChatRef.current) return;

    try {
      setIsSummaryLoading(true);

      const res = await getPdfDetails(notebookId, selectedPdfIds);

      const summaryData = res.summary || "";
      const queriesData = Array.isArray(res.suggested_queries)
        ? res.suggested_queries
        : [];

      setSummary(summaryData);
      setSuggestedQueries([...queriesData]);

      // 🔥 RETRY if queries not ready yet
      if (queriesData.length === 0 && retry < 5) {
        retryTimer = setTimeout(() => {
          fetchSummary(retry + 1);
        }, 1500); // wait for backend processing
      }

    } catch (err) {
      console.error("Failed to fetch summary", err);
      setSummary("");
      setSuggestedQueries([]);
    } finally {
      setIsSummaryLoading(false);
    }
  };

  fetchSummary();

  return () => clearTimeout(retryTimer);
}, [notebookId, selectedPdfIds]);



  const isDisabled = selectedPdfIds.length === 0;

  // =========================
  // FETCH HISTORY
  // =========================
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

  // =========================
  // SEND MESSAGE
  // =========================
const handleSend = async (overrideText?: string) => {
  onCitationsUpdate([]); 
  
  const textToSend = overrideText ?? input;

  if (!textToSend.trim() || isDisabled) return;

  hasUserStartedChatRef.current = true;

  addUserMessage(textToSend);
  const aiMessageId = addAILoadingMessage();

  // only clear input if user typed
  if (!overrideText) {
    setInput("");
  }

  try {
    let fullText = "";

   await sendQueryStream(
  {
    query: textToSend,
    session_id: sessionId,
    notebook_id: notebookId,
    pdf_ids: selectedPdfIds,
  },
  (chunk: string) => {
    fullText += chunk;
    updateAIMessage(aiMessageId, fullText);
  },
  (chunks) => {
    // ✅ attach to message
    updateAIMessageChunks(aiMessageId, chunks);

    // ✅ push to sidebar
    onCitationsUpdate(chunks);
  }
);
  } catch {
    updateAIMessage(
      aiMessageId,
      "Error: Failed to get response. Please try again."
    );
  }
};
const handleSuggestedClick = (q: string) => {
  handleSend(q);
};
  // =========================
  // DELETE FLOW (UPDATED)
  // =========================

  // 🔹 open modal (instead of direct delete)
  const handleDeleteClick = () => {
    setMenuOpen(false);
    setShowDeleteModal(true);
  };

  // 🔹 confirm delete
  const handleConfirmDelete = async () => {
    try {
      setIsDeleting(true);

      await deleteChatHistory(sessionId);

      clearChat();
      setShowDeleteModal(false);
    } catch (err) {
      console.error("Failed to delete chat history", err);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <>
      <BaseSideContainer
        title="Chat"
        rightAction={
          <ChatMenu
            open={menuOpen}
            onToggle={() => setMenuOpen((prev) => !prev)}
            onClose={() => setMenuOpen(false)}
            onDeleteChat={handleDeleteClick} // ✅ UPDATED
          />
        }
      >
        <div className="flex flex-col h-full">
          <ChatBody
  messages={messages}
  loading={isHistoryLoading}

  summary={summary}
  suggestedQueries={suggestedQueries}
  isSummaryLoading={isSummaryLoading}
  onSuggestedClick={handleSuggestedClick}
  onSourcesClick={onOpenCitations} 
/>

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

      {/* =========================
          DELETE CONFIRM MODAL
         ========================= */}
      <CommonModal
        isOpen={showDeleteModal}
        title="Delete chat history?"
        description="This will permanently delete all messages in this session. This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={handleConfirmDelete}
        onCancel={() => setShowDeleteModal(false)}
        isDanger
        isLoading={isDeleting}
      />
    </>
  );
};

export default ChatView;