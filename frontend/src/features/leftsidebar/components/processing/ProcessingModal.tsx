"use client";

import React, { useEffect, useMemo } from "react";

interface Props {
  open: boolean;
  onClose: () => void;
  logs: string[];
  filename?: string;
}

const ProcessingModal: React.FC<Props> = ({
  open,
  onClose,
  logs,
  filename,
}) => {
  const currentMessage = useMemo(() => {
    if (!logs || logs.length === 0) return "Preparing document...";
    return logs[logs.length - 1];
  }, [logs]);

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };

    if (open) window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 bg-black/30 flex items-center justify-center px-4"
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-md bg-white rounded-2xl shadow-xl border border-slate-200 px-8 py-9"
      >
        {/* HEADER */}
        <div className="flex items-start justify-between mb-7">
          <div>
            <h2 className="text-base font-semibold text-slate-800">
              Processing document
            </h2>
          </div>

          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 text-lg cursor-pointer"
          >
            ✕
          </button>
        </div>

        {/* FILE INFO */}
        <div className="mb-9">
          <p className="text-xs text-slate-400 mb-1">File</p>
          <p className="text-sm text-slate-700 truncate">
            {filename}
          </p>
        </div>

        {/* STATUS */}
        <div className="mb-7">
          <p className="text-sm text-slate-600 animate-fadeIn">
            {currentMessage}
          </p>
        </div>

        {/* IMPROVED PROGRESS BAR */}
        <div className="w-full h-0.75 bg-slate-100 rounded-full overflow-hidden relative">
          <div className="absolute inset-0 bg-linear-to-r from-transparent via-slate-400/60 to-transparent animate-shimmer" />
        </div>

        {/* STYLES */}
        <style jsx>{`
          @keyframes shimmer {
            0% {
              transform: translateX(-100%);
            }
            100% {
              transform: translateX(100%);
            }
          }

          @keyframes fadeIn {
            from {
              opacity: 0;
              transform: translateY(4px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }

          .animate-shimmer {
            animation: shimmer 1.4s ease-in-out infinite;
          }

          .animate-fadeIn {
            animation: fadeIn 0.25s ease-in-out;
          }
        `}</style>
      </div>
    </div>
  );
};

export default ProcessingModal;