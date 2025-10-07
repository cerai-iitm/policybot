"use client";
import React from "react";
import ReactMarkdown from "react-markdown";

interface HumanMessageProps {
  content: string;
}

const HumanMessage: React.FC<HumanMessageProps> = ({ content }) => {
  return (
    <div className="max-w-[70%] ml-auto bg-bg-dark text-base text-text rounded-md p-2 mb-2 overflow-x-auto shadow">
      {content}
    </div>
  );
};

export default HumanMessage;
