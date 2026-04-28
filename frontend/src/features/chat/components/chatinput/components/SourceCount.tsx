"use client";

import React from "react";

interface Props {
  count: number;
  onClick?: () => void;
}

const SourceCount: React.FC<Props> = ({ count, onClick }) => {
  return (
    <div
      onClick={onClick}
      className={`cursor-pointer px-2.5 py-1 text-xs rounded-full border whitespace-nowrap
        ${
          count === 0
            ? "bg-slate-100 text-slate-500 border-slate-200"
            : "bg-indigo-50 text-indigo-700 border-indigo-200"
        }`}
    >
      {count} source{count !== 1 ? "s" : ""}
    </div>
  );
};

export default SourceCount;