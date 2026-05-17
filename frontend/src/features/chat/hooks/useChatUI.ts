"use client";

import { useState, useCallback } from "react";
import { Message } from "../types/chat.types";
import { v4 as uuidv4 } from "uuid";

type Updater =
  | string
  | ((prev: string) => string);

export const useChatUI = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");

  /**
   * HYDRATE CHAT
   */
  const setChatMessages = useCallback((msgs: Message[]) => {
    setMessages(msgs);
  }, []);

  /**
   * CLEAR CHAT
   */
  const clearChat = useCallback(() => {
    setMessages([]);
  }, []);

  /**
   * USER MESSAGE
   */
  const addUserMessage = (text: string) => {
    const msg: Message = {
      id: uuidv4(),
      type: "user",
      content: text,
      loading: false,
      isStreaming: false,
    };

    setMessages((prev) => [...prev, msg]);
  };

  /**
   * AI PLACEHOLDER
   */
  const addAILoadingMessage = () => {
    const id = uuidv4();

    const msg: Message = {
      id,
      type: "ai",

      /**
       * Empty initially.
       */
      content: "",

      /**
       * Loader visible initially.
       */
      loading: true,

      /**
       * CRITICAL:
       * Message is immediately considered streaming.
       */
      isStreaming: true,

      sourceChunks: [],
    };

    setMessages((prev) => [...prev, msg]);

    return id;
  };

  /**
   * UPDATE AI MESSAGE
   */
  const updateAIMessage = (
    id: string,
    value: Updater,
    isStreaming?: boolean
  ) => {
    setMessages((prevMessages) =>
      prevMessages.map((m) => {
        if (m.id !== id) return m;

        const nextContent =
          typeof value === "function"
            ? value(m.content || "")
            : value;

        return {
          ...m,

          /**
           * Remove loading once content arrives.
           */
          loading: false,

          content: nextContent,

          /**
           * Explicit streaming control.
           */
          isStreaming:
            typeof isStreaming === "boolean"
              ? isStreaming
              : m.isStreaming,
        };
      })
    );
  };

  /**
   * UPDATE CITATIONS
   */
  const updateAIMessageChunks = (
    id: string,
    chunks: any[]
  ) => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === id
          ? {
              ...msg,
              sourceChunks: chunks,
            }
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

    updateAIMessageChunks,

    clearChat,

    setChatMessages,
  };
};