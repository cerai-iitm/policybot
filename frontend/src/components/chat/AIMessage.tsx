"use client";
import React from "react";
import MarkdownRenderer from "../common/Markdown";

interface AIMessageProps {
  content: string;
}

const AIMessage: React.FC<AIMessageProps> = ({ content }) => {
  return (
    <div className="p-2 rounded-md bg-gray-300 text-black max-w-[70%] break-words mx-8 whitespace-pre-wrap">
      <MarkdownRenderer text={content} />
    </div>
  );
};

export default AIMessage;
