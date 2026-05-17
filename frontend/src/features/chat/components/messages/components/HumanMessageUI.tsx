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
    <div
      className="
        w-full
        flex flex-col items-end

        px-2 sm:px-4
        my-1.5 sm:my-2
      "
    >
      {/* ================= MESSAGE BUBBLE ================= */}
      <div
        className="
          inline-block

          /* MOBILE */
          max-w-[94%]

          /* DESKTOP - UNCHANGED */
          sm:max-w-[85%]
          md:max-w-140

          bg-slate-50
          border border-slate-300

          rounded-3xl
          rounded-br-sm

          /* MOBILE */
          px-3.5 py-2.5

          /* DESKTOP - UNCHANGED */
          sm:px-5
          sm:py-3

          overflow-hidden
        "
      >
        <p
          className="
            text-[15px]
            sm:text-md

            text-[#334155]

            leading-6

            break-words
            whitespace-pre-wrap
          "
        >
          {content}
        </p>
      </div>

      {/* ================= COPY BUTTON ================= */}
      <div
        className="
          mt-1.5 sm:mt-2
          pr-1
        "
      >
        <button
          onClick={onCopy}
          title="Copy message"
          aria-label="Copy message"
          className="
            p-1

            text-slate-400
            hover:text-slate-700

            transition
          "
        >
          {copied ? (
            <FiCheck size={16} />
          ) : (
            <FiCopy size={16} />
          )}
        </button>
      </div>
    </div>
  );
};

export default HumanMessageUI;