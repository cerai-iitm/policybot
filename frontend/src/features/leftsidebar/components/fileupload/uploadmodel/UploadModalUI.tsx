"use client";

import React from "react";
import Image from "next/image";

import fileicon from "@/assets/file.png";

interface Props {
  isDragging: boolean;
  error: string | null;
  onClose: () => void;
  onDrop: (e: React.DragEvent<HTMLDivElement>) => void;
  onDragOver: (e: React.DragEvent<HTMLDivElement>) => void;
  onDragLeave: () => void;
  onBrowseClick: () => void;
}

const UploadModalUI: React.FC<Props> = ({
  isDragging,
  error,
  onClose,
  onDrop,
  onDragOver,
  onDragLeave,
  onBrowseClick,
}) => {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 px-4"
      onClick={onClose}
    >
      {/* MODAL */}
      <div
        role="dialog"
        aria-modal="true"
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-md bg-white rounded-2xl shadow-xl border border-slate-200 px-8 py-8 relative"
      >
        {/* HEADER */}
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-base font-semibold text-slate-800">
              Upload PDF
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              Add documents to your workspace
            </p>
          </div>

          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 text-lg"
          >
            ✕
          </button>
        </div>

        {/* DROP ZONE */}
        <div
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          className={`
            w-full
            rounded-xl
            border
            border-dashed
            px-6
            py-10
            flex
            flex-col
            items-center
            justify-center
            text-center
            transition

            ${
              isDragging
                ? "border-slate-400 bg-slate-50"
                : "border-slate-300 bg-slate-50 hover:bg-slate-100"
            }

            ${error ? "border-red-400 bg-red-50" : ""}
          `}
        >
          {/* ICON */}
          <div className="w-10 h-10 mb-3 flex items-center justify-center opacity-70">
            <Image src={fileicon} alt="file" width={20} height={20} />
          </div>

          {/* TEXT */}
          <p className="text-sm text-slate-700">
            Drag & drop your PDF here
          </p>

          <p className="text-xs text-slate-500 mt-1">
            or
          </p>

          {/* BUTTON */}
          <button
            onClick={onBrowseClick}
            className="mt-4 px-4 py-2 text-sm font-medium rounded-md border border-slate-300 bg-white hover:bg-[#3271EA] hover:text-white cursor-pointer transition"
          >
            Browse files
          </button>

          {/* ERROR */}
          {error && (
            <p className="mt-4 text-sm text-red-500">
              {error}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default UploadModalUI;