"use client";

import React from "react";
import { FiCopy, FiCheck } from "react-icons/fi";

interface Props {
  content: string;
  copied: boolean;
  onCopy: () => void;
}

const HumanMessageUI: React.FC<Props> = ({
  content,
  copied,
  onCopy,
}) => {
  return (
    <div className="w-full flex flex-col items-end px-2 sm:px-4 my-1.5 sm:my-2">

      {/* Message Bubble */}
      <div
        className="
        inline-block
        max-w-[90%] sm:max-w-[85%] md:max-w-140
        bg-slate-50
        border border-slate-300
        rounded-[10px]
        px-4 sm:px-5
        py-2.5 sm:py-3
        
        
      "
      >
        <p className="text-sm text-[#334155] leading-6 wrap-break-words">
          {content}
        </p>
      </div>

      {/* Copy Button */}
      <div className="mt-2 pr-1">
        <button
          onClick={onCopy}
          className="text-slate-400 hover:text-slate-700 transition"
          title="Copy message"
          aria-label="Copy message"
        >
          {copied ? <FiCheck size={16} /> : <FiCopy size={16} />}
        </button>
      </div>
    </div>
  );
};

export default HumanMessageUI;