"use client";

import { useState } from "react";
import { Message } from "../types/chat.types";
import { v4 as uuidv4 } from "uuid";
import { useCallback } from "react";

export const useChatUI = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");

  // ✅ NEW: hydrate from API
const setChatMessages = useCallback((msgs: Message[]) => {
  setMessages(msgs);
}, []);

const clearChat = useCallback(() => {
  setMessages([]);
}, []);

  const addUserMessage = (text: string) => {
    const msg: Message = {
      id: uuidv4(),
      type: "user",
      content: text,
    };

    setMessages((prev) => [...prev, msg]);
  };

  const addAILoadingMessage = () => {
    const id = uuidv4();

    const msg: Message = {
      id,
      type: "ai",
      content: "",
      loading: true,
    };

    setMessages((prev) => [...prev, msg]);

    return id;
  };

  type Updater = string | ((prev: string) => string);

 const updateAIMessage = (id: string, value: Updater) => {
  setMessages((prevMessages) =>
    prevMessages.map((m) =>
      m.id === id
        ? {
            ...m,
            content:
              typeof value === "function"
                ? value(m.content || "")
                : value,
          }
        : m
    )
  );
};

  

  const updateAIMessageChunks = (id: string, chunks: any[]) => {
  setMessages((prev) =>
    prev.map((msg) =>
      msg.id === id
        ? { ...msg, sourceChunks: chunks }
        : msg
    )
  );
};

  return {
    messages,
    input,
    setInput,
    addUserMessage,
    addAILoadingMessage,
    updateAIMessage,
    clearChat,
    setChatMessages,
    updateAIMessageChunks
  };
};