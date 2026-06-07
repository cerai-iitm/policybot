"use client";
import React from "react";
import dynamic from "next/dynamic";

const MarkdownRenderer = dynamic(
  () => import("../../../markdown/Markdown"),
  { ssr: false }
);

interface Props {
  content: string;
  isGenerating: boolean;
}

const MessageContent: React.FC<Props> = ({ content, isGenerating }) => {
  return (
    <div className="text-slate-700">
      <div className="relative">
        <MarkdownRenderer text={content} />
        {isGenerating && (
          <span className="inline-block w-2 ml-1 bg-black animate-pulse align-middle" />
        )}
      </div>
    </div>
  );
};

export default MessageContent;