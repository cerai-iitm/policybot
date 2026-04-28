"use client";
import React from "react";
import { FiFile } from "react-icons/fi";

interface SourceChunk {
  text: string;
  source: string;
  page_number: number | null;
}

const SourcePanel = React.forwardRef<
  HTMLDivElement,
  { chunks: SourceChunk[] }
>(({ chunks }, ref) => {
  return (
    <div ref={ref} className="mt-6 space-y-4">
      <div className="text-xs font-semibold text-slate-500 uppercase">
        Source References
      </div>

      {chunks.map((chunk, idx) => (
        <div key={idx} className="bg-white border rounded-2xl p-4">
          <div className="flex justify-between mb-3">
            <div className="flex gap-2">
              <FiFile />
              <span>{chunk.source}</span>
            </div>

            {chunk.page_number !== null && (
              <span className="text-xs">Page {chunk.page_number}</span>
            )}
          </div>

          <p className="text-sm text-slate-700">{chunk.text}</p>
        </div>
      ))}
    </div>
  );
});

/* ✅ FIX: Add display name */
SourcePanel.displayName = "SourcePanel";

export default SourcePanel;