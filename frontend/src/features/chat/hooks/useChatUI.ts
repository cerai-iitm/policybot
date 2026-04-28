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

  // 🔥 ADD LOADING AI MESSAGE
  const addAILoadingMessage = () => {
    const id = uuidv4();

    const msg: Message = {
      id,
      type: "ai",
      content: "",
      loading: true,
    };

    setMessages((prev) => [...prev, msg]);

    return id; // return ID to update later
  };

  // 🔥 UPDATE AI MESSAGE
  const updateAIMessage = (id: string, text: string) => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === id
          ? { ...msg, content: text, loading: false }
          : msg
      )
    );
  };

  const clearChat = () => setMessages([]);

  return {
    messages,
    input,
    setInput,
    addUserMessage,
    addAILoadingMessage,
    updateAIMessage,
    clearChat,
  };
};