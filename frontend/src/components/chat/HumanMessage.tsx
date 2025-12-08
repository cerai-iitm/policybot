"use client";
import React from "react";

interface HumanMessageProps {
  content: string;
}

const HumanMessage: React.FC<HumanMessageProps> = ({ content }) => {
  return (
    <div className="p-4 rounded-xl bg-bg-dark text-text text-base max-w-4xl break-words ml-auto mr-4 my-3 shadow-sm hover:shadow-md transition-all duration-200 border border-border-muted">
      <div className="text-text text-base leading-relaxed">{content}</div>
    </div>
  );
};

export default HumanMessage;
