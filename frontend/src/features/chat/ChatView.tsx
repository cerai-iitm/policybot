"use client";

import { useSearchParams } from "next/navigation";
import { v4 as uuidv4 } from "uuid";
import { useRef, useState } from "react";

import ChatBody from "./components/ChatBody";
import ChatInput from "./components/chatinput/ChatInput";
import ChatFooter from "./components/ChatFooter";
import BaseSideContainer from "@/features/layout/components/BaseSideContainer";

import { useChatUI } from "./hooks/useChatUI";
import { useChatHistory } from "./hooks/useChatHistory";
import { useSummary } from "./hooks/useSummary";
import { useChatController } from "./hooks/useChatController";

import ChatMenu from "./components/chatmenu/ChatMenu";
import CommonModal from "@/components/popup";
import { deleteChatHistory } from "@/lib/api/chat.api";

interface Props {
  notebookId: string;
  selectedPdfIds: string[];
  onCitationsUpdate: (chunks: any[]) => void;
  onOpenCitations: () => void;
}

const ChatView = ({ notebookId, selectedPdfIds, onCitationsUpdate, onOpenCitations }: Props) => {
  const searchParams = useSearchParams();
const [sessionId] = useState(() => {
  return searchParams.get("session_id") ?? uuidv4();
});
  const chatUI = useChatUI();

  const { isLoading } = useChatHistory(
    sessionId,
    chatUI.setChatMessages,
    chatUI.clearChat
  );

  const summaryState = useSummary(notebookId, selectedPdfIds);

  const { handleSend } = useChatController({
    sessionId,
    notebookId,
    selectedPdfIds,
    input: chatUI.input,
    setInput: chatUI.setInput,
    addUserMessage: chatUI.addUserMessage,
    addAILoadingMessage: chatUI.addAILoadingMessage,
    updateAIMessage: chatUI.updateAIMessage,
    updateAIMessageChunks: chatUI.updateAIMessageChunks,
    onCitationsUpdate,
    hasStartedRef: summaryState.hasStartedRef,
  });

  const [menuOpen, setMenuOpen] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const handleDelete = async () => {
    await deleteChatHistory(sessionId);
    chatUI.clearChat();
    setShowDeleteModal(false);
  };

  return (
    <>
      <BaseSideContainer
        title="Chat"
        showMobileHeader
        rightAction={
          <ChatMenu
            open={menuOpen}
            onToggle={() => setMenuOpen((p) => !p)}
            onClose={() => setMenuOpen(false)}
            onDeleteChat={() => setShowDeleteModal(true)}
          />
        }
      >
        <div className="flex flex-col h-full">
          <ChatBody
            messages={chatUI.messages}
            loading={isLoading}
            summary={summaryState.summary}
            suggestedQueries={summaryState.suggestedQueries}
            isSummaryLoading={summaryState.isSummaryLoading}
            onSuggestedClick={handleSend}
            onSourcesClick={onOpenCitations}
          />

          <ChatInput
            value={chatUI.input}
            onChange={(e) => chatUI.setInput(e.target.value)}
            onSend={handleSend}
            disabled={selectedPdfIds.length === 0}
            selectedCount={selectedPdfIds.length}
          />

          <ChatFooter />
        </div>
      </BaseSideContainer>

      <CommonModal
        isOpen={showDeleteModal}
        title="Delete chat history?"
        description="This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={handleDelete}
        onCancel={() => setShowDeleteModal(false)}
        isDanger
      />
    </>
  );
};

export default ChatView;