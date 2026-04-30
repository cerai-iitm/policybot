"use client";

import React from "react";

interface Props {
  filename: string;
  displayName: string;
  isLongName: boolean;
  onToggle: () => void;
}

const SourceItemFilename: React.FC<Props> = ({
  filename,
  displayName,
  isLongName,
  onToggle,
}) => {
  return (
    <div
      className="flex-1 overflow-hidden cursor-pointer"
      onClick={(e) => {
        e.stopPropagation();
        onToggle();
      }}
    >
      {isLongName ? (
        <>
          <span className="group-hover:hidden block truncate text-sm text-slate-600">
            {displayName}
          </span>

          <span className="hidden group-hover:block text-sm text-slate-600 overflow-hidden whitespace-nowrap">
            <span className="marquee animate-marquee">
              {filename}
            </span>
          </span>
        </>
      ) : (
        <span className="block truncate text-sm text-slate-600">
          {filename}
        </span>
      )}
    </div>
  );
};

export default SourceItemFilename;