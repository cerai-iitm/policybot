"use client";
import React from "react";

interface Props {
  type?: "thinking" | "summary";
}

const MessageLoader: React.FC<Props> = ({ type }) => {
  return (
    <div className="flex items-center gap-2 py-2">
      <div className="flex gap-1">
        <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></span>
        <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-150"></span>
        <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-300"></span>
      </div>
      <span className="text-slate-500 text-sm">
        {type === "summary" ? "Generating summary" : "Thinking"}
      </span>
    </div>
  );
};

export default MessageLoader;