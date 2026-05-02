"use client";

import React, { useRef, useState } from "react";
import TooltipPortal from "./sendbutton/TooltipPortal";

interface Props {
  count: number;
  onClick?: () => void;
}

const SourceCount: React.FC<Props> = ({ count, onClick }) => {
  const wrapperRef = useRef<HTMLDivElement | null>(null);
  const [hovered, setHovered] = useState(false);

  const tooltipText =
    count === 0 ? "Select a source to continue" : "View selected sources";

  return (
    <>
      {/* ✅ Wrapper handles hover */}
      <div
        ref={wrapperRef}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        onClick={count === 0 ? undefined : onClick} // disable click when 0
        className={`
          px-2.5 py-1 text-xs rounded-full border whitespace-nowrap inline-flex
          ${count === 0
            ? "bg-slate-100 text-slate-500 border-slate-200 cursor-default "
            : "bg-indigo-50 text-indigo-700 border-indigo-200 cursor-default"}
        `}
      >
        {count} source{count !== 1 ? "s" : ""}
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

export default SourceCount;