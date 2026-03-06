"use client";
import React, { useState } from "react";
import { FiCopy, FiCheck } from "react-icons/fi";

interface HumanMessageProps {
  content: string;
}

const HumanMessage: React.FC<HumanMessageProps> = ({ content }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);

      setTimeout(() => {
        setCopied(false);
      }, 2000);
    } catch (err) {
      console.error("Copy failed", err);
    }
  };

  return (
    <div className="w-full flex flex-col items-end px-2 sm:px-4 my-1.5 sm:my-2
">
      
      {/* Message Bubble */}
      <div className="
        inline-block
        max-w-[90%] sm:max-w-[85%] md:max-w-[560px]
        bg-slate-50
        border border-slate-300
        rounded-[10px]
        px-4 sm:px-5
        py-2.5 sm:py-3
        transition-all duration-200
        sm:hover:shadow-md
      ">
        <p className="text-slate-800 text-[15px] sm:text-base leading-5 sm:leading-6 break-words">
          {content}
        </p>
      </div>

      {/* Copy Action Below Bubble */}
      <div className="mt-2 pr-1">
        <button
          onClick={handleCopy}
          className="text-slate-400 hover:text-slate-700 transition"
          title="Copy"
        >
          {copied ? <FiCheck size={16} /> : <FiCopy size={16} />}
        </button>
      </div>

    </div>
  );
};

export default HumanMessage;
