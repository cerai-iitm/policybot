"use client";
import React from "react";
import ReactMarkdown from "react-markdown";

interface AIMessageProps {
  content: string;
}

const AIMessage: React.FC<AIMessageProps> = ({ content }) => {
  return (
    <div className="p-2 rounded-md bg-gray-300 text-black max-w-[70%] break-words mx-8 whitespace-pre-wrap">
      <ReactMarkdown
        components={{
          h1: ({ node, ...props }) => (
            <h1 className="text-3xl font-bold my-4" {...props} />
          ),
          h2: ({ node, ...props }) => (
            <h2 className="text-2xl font-semibold my-3" {...props} />
          ),
          ul: ({ node, ...props }) => (
            <ul className="list-disc pl-6 my-2" {...props} />
          ),
          ol: ({ node, ...props }) => (
            <ol className="list-decimal pl-6 my-2" {...props} />
          ),
          code: ({ node, ...props }) => (
            <code className="bg-gray-200 rounded px-1" {...props} />
          ),
          // ...add more as needed
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default AIMessage;
