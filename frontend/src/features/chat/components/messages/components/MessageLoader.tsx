"use client";

import React from "react";

interface Props {
  type?: "thinking" | "summary";
}

const MessageLoader: React.FC<Props> = ({ type }) => {
  return (
    <div
      className="
        flex items-center

        gap-2 sm:gap-2

        py-2

        px-1 sm:px-0

        min-h-[32px]
      "
    >
      {/* ================= LOADER DOTS ================= */}
      <div
        className="
          flex
          items-center
          gap-1

          shrink-0
        "
      >
        <span
          className="
            w-2 h-2
            bg-slate-400
            rounded-full
            animate-bounce
          "
        />

        <span
          className="
            w-2 h-2
            bg-slate-400
            rounded-full
            animate-bounce
            delay-150
          "
        />

        <span
          className="
            w-2 h-2
            bg-slate-400
            rounded-full
            animate-bounce
            delay-300
          "
        />
      </div>

      {/* ================= TEXT ================= */}
   
    </div>
  );
};

export default MessageLoader;