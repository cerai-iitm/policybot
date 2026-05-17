"use client";

import { useCallback, useEffect, useRef } from "react";
import { TYPING_CONFIG } from "../config/typing.config";

type UpdateFn = (
  id: string,
  value: string | ((prev: string) => string),
  isStreaming?: boolean
) => void;

export const useTypingEngine = (
  updateAIMessage: UpdateFn
) => {
  const activeMessageIdRef =
    useRef<string | null>(null);

  const queueRef = useRef<string[]>([]);

  const bufferRef = useRef("");

  const intervalRef =
    useRef<NodeJS.Timeout | null>(null);

  const sessionRef = useRef(0);

  /**
   * TRUE only after SSE stream finishes.
   */
  const isCompletingRef = useRef(false);

  /**
   * RESET
   */
  const reset = useCallback(() => {
    sessionRef.current += 1;

    queueRef.current = [];

    bufferRef.current = "";

    activeMessageIdRef.current = null;

    isCompletingRef.current = false;

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  /**
   * FLUSH REMAINING BUFFER
   */
  const flushBuffer = useCallback(() => {
    if (!bufferRef.current) return;

    queueRef.current.push(bufferRef.current);

    bufferRef.current = "";
  }, []);

  /**
   * START TYPING LOOP
   */
  const startTyping = useCallback(
    (messageId: string) => {
      if (intervalRef.current) return;

      activeMessageIdRef.current = messageId;

      const currentSession = sessionRef.current;

      intervalRef.current = setInterval(() => {
        /**
         * SESSION INVALIDATED
         */
        if (
          currentSession !== sessionRef.current
        ) {
          clearInterval(intervalRef.current!);
          intervalRef.current = null;
          return;
        }

        /**
         * MESSAGE CHANGED
         */
        if (
          activeMessageIdRef.current !==
          messageId
        ) {
          clearInterval(intervalRef.current!);
          intervalRef.current = null;
          return;
        }

        /**
         * QUEUE EMPTY
         */
        if (queueRef.current.length === 0) {
          /**
           * STREAM FULLY COMPLETE
           */
          if (isCompletingRef.current) {
            updateAIMessage(
              messageId,
              (prev) => prev,
              false
            );

            isCompletingRef.current = false;
          }

          clearInterval(intervalRef.current!);

          intervalRef.current = null;

          return;
        }

        const next = queueRef.current.shift();

        if (!next) return;

        /**
         * STILL STREAMING
         */
        updateAIMessage(
          messageId,
          (prev) => prev + next,
          true
        );
      }, TYPING_CONFIG.speed);
    },
    [updateAIMessage]
  );

  /**
   * PUSH CHUNK
   */
  const pushChunk = useCallback(
    (chunk: string, messageId: string) => {
      /**
       * New session protection
       */
      if (
        activeMessageIdRef.current &&
        activeMessageIdRef.current !==
          messageId
      ) {
        reset();
      }

      activeMessageIdRef.current = messageId;

      bufferRef.current += chunk;

      let units: string[] = [];

      if (TYPING_CONFIG.mode === "word") {
        const parts =
          bufferRef.current.split(/(\s+)/);

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
   * COMPLETE STREAM
   */
  const complete = useCallback(
    (messageId: string) => {
      if (
        activeMessageIdRef.current !==
        messageId
      ) {
        return;
      }

      /**
       * Mark stream ending.
       */
      isCompletingRef.current = true;

      /**
       * Flush final partial word.
       */
      flushBuffer();

      /**
       * Ensure typing loop runs.
       */
      startTyping(messageId);
    },
    [flushBuffer, startTyping]
  );

  /**
   * CLEANUP
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