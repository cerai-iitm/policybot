"use client";

import { useCallback, useEffect, useRef } from "react";
import { TYPING_CONFIG } from "../config/typing.config";

type UpdateFn = (
  id: string,
  value: string | ((prev: string) => string)
) => void;

export const useTypingEngine = (updateAIMessage: UpdateFn) => {
  /**
   * ACTIVE MESSAGE SESSION
   * Prevents stale intervals from updating old/new messages.
   */
  const activeMessageIdRef = useRef<string | null>(null);

  /**
   * Typing queue for current message.
   */
  const queueRef = useRef<string[]>([]);

  /**
   * Buffer for incomplete words.
   */
  const bufferRef = useRef("");

  /**
   * Interval instance.
   */
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * Session token.
   * Incrementing invalidates previous typing loops.
   */
  const sessionRef = useRef(0);

  /**
   * FULL HARD RESET
   */
  const reset = useCallback(() => {
    sessionRef.current += 1;

    queueRef.current = [];
    bufferRef.current = "";
    activeMessageIdRef.current = null;

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  /**
   * Flush remaining buffer safely.
   */
  const flushBuffer = useCallback(() => {
    if (!bufferRef.current.trim()) return;

    queueRef.current.push(bufferRef.current);
    bufferRef.current = "";
  }, []);

  /**
   * Starts typing loop for a specific session.
   */
  const startTyping = useCallback(
    (messageId: string) => {
      /**
       * Already running.
       */
      if (intervalRef.current) return;

      activeMessageIdRef.current = messageId;

      const currentSession = sessionRef.current;

      intervalRef.current = setInterval(() => {
        /**
         * Session invalidated.
         */
        if (currentSession !== sessionRef.current) {
          clearInterval(intervalRef.current!);
          intervalRef.current = null;
          return;
        }

        /**
         * Message changed.
         */
        if (activeMessageIdRef.current !== messageId) {
          clearInterval(intervalRef.current!);
          intervalRef.current = null;
          return;
        }

        /**
         * Queue empty.
         */
        if (queueRef.current.length === 0) {
          clearInterval(intervalRef.current!);
          intervalRef.current = null;
          return;
        }

        const next = queueRef.current.shift();

        if (!next) return;

        updateAIMessage(messageId, (prev: string) => prev + next);
      }, TYPING_CONFIG.speed);
    },
    [updateAIMessage]
  );

  /**
   * Push streamed chunk.
   */
  const pushChunk = useCallback(
    (chunk: string, messageId: string) => {
      /**
       * New message session detected.
       */
      if (
        activeMessageIdRef.current &&
        activeMessageIdRef.current !== messageId
      ) {
        reset();
      }

      activeMessageIdRef.current = messageId;

      bufferRef.current += chunk;

      let units: string[] = [];

      if (TYPING_CONFIG.mode === "word") {
        const parts = bufferRef.current.split(/(\s+)/);

        const last = parts.pop();

        units = parts;

        bufferRef.current = last || "";
      } else {
        units = bufferRef.current.split("");
        bufferRef.current = "";
      }

      queueRef.current.push(...units);

      startTyping(messageId);
    },
    [reset, startTyping]
  );

  /**
   * Finalize stream.
   * Flushes incomplete remaining text.
   */
  const complete = useCallback(
    (messageId: string) => {
      if (activeMessageIdRef.current !== messageId) return;

      flushBuffer();

      startTyping(messageId);
    },
    [flushBuffer, startTyping]
  );

  /**
   * Cleanup on unmount.
   */
  useEffect(() => {
    return () => {
      reset();
    };
  }, [reset]);

  return {
    pushChunk,
    complete,
    reset,
  };
};