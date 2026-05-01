"use client";

import React, { useEffect } from "react";

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
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };

    if (open) window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [open]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 bg-black/30 flex items-center justify-center"
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="w-[600px] max-h-[70vh] bg-white rounded-2xl shadow-xl border p-6 flex flex-col"
      >
        {/* HEADER */}
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-slate-800">
            Processing PDF
          </h2>

          <button
            onClick={onClose}
            className="text-slate-500 hover:text-slate-700"
          >
            ✕
          </button>
        </div>

        {/* FILE NAME */}
        <p className="text-sm text-slate-500 mb-3">
          {filename}
        </p>

        {/* LOGS */}
        <div className="flex-1 overflow-y-auto bg-slate-50 rounded-lg p-4 text-sm text-slate-700 space-y-2 border">
          {logs.length === 0 && (
            <p className="text-slate-400">Starting process...</p>
          )}

          {logs.map((log, i) => (
            <p key={i}>• {log}</p>
          ))}
        </div>

        {/* FOOTER */}
        <div className="mt-4 text-xs text-slate-400">
          Live updates from server...
        </div>
      </div>
    </div>
  );
};

export default ProcessingModal;