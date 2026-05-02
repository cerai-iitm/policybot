"use client";

import React, { useRef, useState } from "react";
import { MdSend } from "react-icons/md";
import TooltipPortal from "./TooltipPortal";

interface Props {
  onClick: () => void;
  disabled: boolean;
}

const SendButton: React.FC<Props> = ({ onClick, disabled }) => {
  const wrapperRef = useRef<HTMLDivElement | null>(null);
  const [hovered, setHovered] = useState(false);

  const tooltipText = disabled
    ? "Type a message to send"
    : "Send prompt";

  return (
    <>
      {/* ✅ WRAPPER handles hover (works even if button is disabled) */}
      <div
        ref={wrapperRef}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        className="inline-flex"
      >
        <button
          aria-label="Send prompt"
          onClick={onClick}
          disabled={disabled}
          className="cursor-pointer w-9 h-9 rounded-full flex items-center justify-center bg-indigo-100 hover:opacity-80 transition disabled:opacity-50 "
        >
          <MdSend className="w-5 h-5 text-blue-800" />
        </button>
      </div>

      {/* ✅ Tooltip */}
      <TooltipPortal anchorRef={wrapperRef} open={hovered}>
        <div className="text-xs bg-black text-white px-2 py-1 rounded shadow whitespace-nowrap">
          {tooltipText}
        </div>
      </TooltipPortal>
    </>
  );
};

export default SendButton;