"use client";


import ChatBody from "./components/ChatBody";
import ChatInput from "../chat/components/chatinput/ChatInput"
import ChatFooter from "./components/ChatFooter";
import BaseSideContainer from "@/features/layout/components/BaseSideContainer";
import { useChatUI } from "./hooks/useChatUI";

const ChatView = () => {

  const getMockResponse = (input: string) => {
  const text = input.toLowerCase();

  if (text.includes("hello")) {
    return "Hey 👋 How can I help you today?";
  }

  if (text.includes("policy")) {
    return "This is a mock policy explanation. Real API will replace this.";
  }

  if (text.includes("price")) {
    return "Pricing depends on your plan. This is just a mock response.";
  }

  return "This is a mock AI response for testing UI flow.";
};


  const {
  messages,
  input,
  setInput,
  addUserMessage,
  addAILoadingMessage,
  updateAIMessage,
} = useChatUI();

const handleSend = () => {
  if (!input.trim()) return;

  const userText = input;

  // 1️⃣ Add user message
  addUserMessage(userText);

  // 2️⃣ Add AI loading
  const aiMessageId = addAILoadingMessage();

  setInput("");

  // 3️⃣ Mock AI response
  setTimeout(() => {
    const mockResponse = getMockResponse(userText);

    updateAIMessage(aiMessageId, mockResponse);
  }, 1200);
};

 return (
  <BaseSideContainer title="Chat">
    
    <div className="flex flex-col h-full">

      <ChatBody messages={messages} />

      <ChatInput
  value={input}
  onChange={(e) => setInput(e.target.value)}
  onSend={handleSend}
  disabled={false}
  selectedCount={0}
/>

      <ChatFooter />

    </div>

  </BaseSideContainer>
);
};

export default ChatView;