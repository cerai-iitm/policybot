"use client";


import ChatBody from "./components/ChatBody";
import ChatInputWrapper from "./components/ChatInputWrapper";
import ChatFooter from "./components/ChatFooter";
import BaseSideContainer from "@/features/layout/components/BaseSideContainer";
import { useChatUI } from "./hooks/useChatUI";

const ChatView = () => {
  const {
    messages,
    input,
    setInput,
    addUserMessage,
  } = useChatUI();

  const handleSend = () => {
    if (!input.trim()) return;

    addUserMessage(input);

    // 🔥 TEMP MOCK (REMOVE LATER)
    setTimeout(() => {
      console.log("Connect API here");
    }, 500);

    setInput("");
  };

 return (
  <BaseSideContainer title="Chat">
    
    <div className="flex flex-col h-full">

      <ChatBody messages={messages} />

      <ChatInputWrapper
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onSend={handleSend}
      />

      <ChatFooter />

    </div>

  </BaseSideContainer>
);
};

export default ChatView;