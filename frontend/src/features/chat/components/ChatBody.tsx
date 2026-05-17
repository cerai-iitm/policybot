"use client";

import React, { useEffect, useRef } from "react";
import { Message } from "../types/chat.types";
import HumanMessage from "./messages/HumanMessage";
import AIMessage from "./messages/AIMessage";
import SuggestedQuestions from "./suggestedquestions/SuggestedQuestions";

const ChatBody = ({
  messages,
  loading,
  summary,
  suggestedQueries,
  isSummaryLoading,
  onSuggestedClick,
  onSourcesClick,
}: {
  messages: Message[];
  loading?: boolean;
  summary?: string;
  suggestedQueries?: string[];
  isSummaryLoading?: boolean;
  onSuggestedClick?: (q: string) => void;
  onSourcesClick?: () => void;
}) => {
  const isInitialLoading = loading || isSummaryLoading;

  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, summary, suggestedQueries]);

  return (
    <div className="flex-1 overflow-x-hidden min-h-0 overscroll-contain overflow-y-auto pt-3 md:pt-4 custom-scrollbar">
      <div className="w-full md:w-[90%] max-w-4xl mx-auto flex flex-col px-3 md:px-0">

        {/* ================= EMPTY STATE ================= */}
        {!isInitialLoading &&
          messages.length === 0 &&
          !summary && (
            <div className="
              flex flex-col items-center justify-center text-center
              mt-16 md:mt-24
              px-4 md:px-6
            ">
              <h2 className="
                text-base md:text-lg
                font-semibold
                text-slate-800
                mb-2
              ">
                Add a policy document to begin
              </h2>

              <p className="
                text-xs md:text-sm
                text-slate-500
                max-w-md
              ">
                Upload a policy file to start asking questions and receive answers grounded in the original document with clear citations.
              </p>
            </div>
        )}

        {/* ================= LOADING ================= */}
        {isInitialLoading && (
          <div className="
            text-center
            mt-16 md:mt-20
            text-slate-500
            text-sm md:text-base
          ">
            Loading...
          </div>
        )}

        {/* ================= SUMMARY + SUGGESTIONS ================= */}
        {!isInitialLoading && (
          <>
            {isSummaryLoading && (
              <div className="flex justify-start">
                <AIMessage content="" loadingType="summary" />
              </div>
            )}

            {!isSummaryLoading && summary && (
              <div className="flex justify-start">
                <AIMessage content={summary} />
              </div>
            )}

            {!isSummaryLoading &&
              Array.isArray(suggestedQueries) &&
              suggestedQueries.length > 0 && (
                <div className="px-1 md:px-0">
                  <SuggestedQuestions
                    key={suggestedQueries.join("-")}
                    questions={suggestedQueries}
                    onSelect={(q) => onSuggestedClick?.(q)}
                  />
                </div>
              )}
          </>
        )}

        {/* ================= CHAT MESSAGES ================= */}
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex ${
              m.type === "user" ? "justify-end" : "justify-start"
            } mb-2`}
          >
            {m.type === "user" ? (
              <HumanMessage content={m.content} />
            ) : (
            <AIMessage
  content={m.content}
  sourceChunks={m.sourceChunks}
  isStreaming={m.isStreaming}
  onSourcesClick={onSourcesClick}
/>
            )}
          </div>
        ))}

        {/* 👇 AUTO SCROLL */}
        <div ref={bottomRef} />
      </div>
    </div>
  );
};

export default ChatBody;
