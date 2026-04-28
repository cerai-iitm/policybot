"use client";

import React, { useEffect, useRef } from "react";
import { Message } from "../types/chat.types";
import HumanMessage from "./messages/HumanMessage";
import AIMessage from "./messages/AIMessage";

const ChatBody = ({ messages }: { messages: Message[] }) => {
  // 👉 Ref for auto-scroll
  const bottomRef = useRef<HTMLDivElement | null>(null);

  // 👉 Scroll to bottom whenever messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto pt-4 custom-scrollbar">
      <div className="w-full md:w-[90%] max-w-4xl mx-auto flex flex-col">

        {messages.length === 0 && (
          <div className="text-center mt-20 text-slate-500">
            Start a conversation
          </div>
        )}

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
              <AIMessage content={m.content} />
            )}
          </div>
        ))}

        {/* 👉 Invisible div to scroll into view */}
        <div ref={bottomRef} />

      </div>
    </div>
  );
};

export default ChatBody;