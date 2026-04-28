"use client";

import { useState } from "react";
import { Message } from "../types/chat.types";
import { v4 as uuidv4 } from "uuid";

export const useChatUI = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");

  const addUserMessage = (text: string) => {
    const msg: Message = {
      id: uuidv4(),
      type: "user",
      content: text,
    };

    setMessages((prev) => [...prev, msg]);
  };

  const addAIMessage = (text: string) => {
    const msg: Message = {
      id: uuidv4(),
      type: "ai",
      content: text,
    };

    setMessages((prev) => [...prev, msg]);
  };

  const clearChat = () => setMessages([]);

  return {
    messages,
    input,
    setInput,
    addUserMessage,
    addAIMessage,
    clearChat,
  };
};