"use client";

import React from "react";
import { Message } from "../types/chat.types";
import HumanMessage from "./messages/HumanMessage";
import AIMessage from "./messages/AIMessage";

const ChatBody = ({ messages }: { messages: Message[] }) => {
  return (
    <div className="flex-1 overflow-y-auto pt-4 px-4">
      <div className="max-w-3xl mx-auto flex flex-col">

        {messages.length === 0 && (
          <div className="text-center mt-20 text-slate-500">
            Start a conversation
          </div>
        )}

        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex ${m.type === "user" ? "justify-end" : "justify-start"} mb-2`}
          >
            {m.type === "user" ? (
              <HumanMessage content={m.content} />
            ) : (
              <AIMessage content={m.content} />
            )}
          </div>
        ))}

      </div>
    </div>
  );
};

export default ChatBody;