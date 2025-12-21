"use client";
import React, { useEffect, useState } from "react";
import MarkdownRenderer from "../common/Markdown";
import { FiChevronDown, FiChevronUp } from "react-icons/fi";
import { withBase } from "@/lib/url";

interface SummaryProps {
  filename: string | null;
}

const Summary: React.FC<SummaryProps> = ({ filename }) => {
  const [summary, setSummary] = useState<string>("No summary available.");
  const [loading, setLoading] = useState<boolean>(false);
  const [collapsed, setCollapsed] = useState<boolean>(false);

  useEffect(() => {
    if (!filename) {
      setSummary("");
      return;
    }
    // open when switching files
    setCollapsed(false);

    setLoading(true);
    fetch(withBase(`/api/pdf/summary/${encodeURIComponent(filename)}`))
      .then((res) => res.json())
      .then((data) => setSummary(data.summary))
      .catch(() => setSummary("No summary available."))
      .finally(() => setLoading(false));
  }, [filename]);

  if (!filename) return null;

  return (
    <div className="mb-6 p-4 bg-bg-light rounded-lg flex flex-col w-full">
      <div className="w-full">
        <button
          type="button"
          aria-expanded={!collapsed}
          aria-controls="summary-content"
          onClick={() => setCollapsed((c) => !c)}
          className="w-full relative flex items-center justify-between py-3 px-0 rounded hover:bg-bg-muted focus:outline-none"
          title={collapsed ? "Show summary" : "Hide summary"}
        >
          {/* Title: always left-aligned; add border only when expanded */}
          <span
            className={`text-text font-bold text-lg flex-1 ${
              !collapsed ? "border-b border-border-muted pb-2" : ""
            }`}
          >
            Summary
          </span>

          {/* Chevron fixed on the right */}
          <span className="ml-2 flex-shrink-0">
            {collapsed ? <FiChevronDown /> : <FiChevronUp />}
          </span>
        </button>
      </div>

      {/* colored bar shown only when expanded; uses theme token so it respects dark mode */}
      {!collapsed && <div className="mt-2 h-0.5 w-14 rounded bg-bg-muted" />}

      {!collapsed && (
        <div id="summary-content" className="text-text mt-3">
          <MarkdownRenderer text={loading ? "Loading summary..." : summary} />
        </div>
      )}
    </div>
  );
};

export default Summary;
