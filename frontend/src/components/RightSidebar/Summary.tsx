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
          {/* Title: always left-aligned */}
          <span className="text-text font-bold text-lg flex-1">Summary</span>

          {/* Chevron fixed on the right */}
          <span className="ml-2 flex-shrink-0">
            {collapsed ? <FiChevronDown /> : <FiChevronUp />}
          </span>
        </button>
        {filename && (
          <div
            className="mt-1 text-xs text-slate-600 dark:text-slate-400 truncate"
            title={filename}
          >
            {filename}
          </div>
        )}
        {/* Persistent separator line shown below filename */}
        <div className="mt-2 h-px w-full bg-bg-muted" />
      </div>

      {/* Separator moved above; keep content below */}

      {!collapsed && (
        <div id="summary-content" className="text-text mt-3">
          <MarkdownRenderer text={loading ? "Loading summary..." : summary} />
        </div>
      )}
    </div>
  );
};

export default Summary;
