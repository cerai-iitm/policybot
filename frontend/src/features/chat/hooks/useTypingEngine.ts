"use client";

import { useRef } from "react";
import { TYPING_CONFIG } from "../config/typing.config";
import { useEffect } from "react";

export const useTypingEngine = (updateAIMessage: (id: string, v: string | ((p: string) => string)) => void) => {
  const queueRef = useRef<string[]>([]);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
  return () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
  };
}, []);


  const startTyping = (messageId: string) => {
    if (intervalRef.current) return;

    intervalRef.current = setInterval(() => {
      if (queueRef.current.length === 0) {
        clearInterval(intervalRef.current!);
        intervalRef.current = null;
        return;
      }

      const next = queueRef.current.shift();

      if (next) {
        updateAIMessage(messageId, (prev: string) => prev + next);
      }
    }, TYPING_CONFIG.speed);
  };

  const bufferRef = useRef("");


  const pushChunk = (chunk: string, messageId: string) => {
  bufferRef.current += chunk;

  let units: string[] = [];

  if (TYPING_CONFIG.mode === "word") {
    const parts = bufferRef.current.split(/(\s+)/);

    const last = parts.pop(); // keep incomplete word
    units = parts;

    bufferRef.current = last || "";
  } else {
    units = bufferRef.current.split("");
    bufferRef.current = "";
  }

  queueRef.current.push(...units);
  startTyping(messageId);
};

  const flushBuffer = (messageId: string) => {
    if (bufferRef.current) {
      queueRef.current.push(bufferRef.current);
      bufferRef.current = "";
      startTyping(messageId);
    }
  };

  const reset = () => {
    queueRef.current = [];
    bufferRef.current = "";
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  return {
    pushChunk,
    flushBuffer,
    reset,
  };
};