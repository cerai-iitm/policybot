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
  onSourcesClick
}: {
  messages: Message[];
  loading?: boolean;
  summary?: string;
  suggestedQueries?: string[];
  isSummaryLoading?: boolean;
  onSuggestedClick?: (q: string) => void;
  onSourcesClick?: () => void;
}) => {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, summary, suggestedQueries]); // ✅ include these

  return (
    <div className="flex-1 overflow-y-auto pt-4 custom-scrollbar">
      <div className="w-full md:w-[90%] max-w-4xl mx-auto flex flex-col">

        {/* ================= HISTORY LOADING ================= */}
        {loading && (
          <div className="text-center mt-20 text-slate-500">
            Loading chat history...
          </div>
        )}

        {/* ================= SUMMARY + SUGGESTIONS ================= */}
       {!loading && (
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
        <SuggestedQuestions
          key={suggestedQueries.join("-")} // 🔥 critical fix
          questions={suggestedQueries}
          onSelect={(q) => onSuggestedClick?.(q)}
        />
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