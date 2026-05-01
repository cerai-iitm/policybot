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
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/20"
      onClick={onClose}
    >
      {/* MODAL */}
      <div
        role="dialog"
        aria-modal="true"
        onClick={(e) => e.stopPropagation()}
        className="w-[520px] rounded-3xl bg-white shadow-[0_20px_60px_rgba(0,0,0,0.15)] border border-slate-200 p-6 relative"
      >
        {/* CLOSE BUTTON */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-full hover:bg-slate-100 transition"
        >
          <span className="text-slate-500 text-sm">✕</span>
        </button>

        {/* HEADER */}
        <div className="text-center mb-5">
          <h2 className="text-lg font-semibold text-slate-800">
            Upload PDF
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Add documents to your policy workspace
          </p>
        </div>

        {/* DROP ZONE */}
        <div
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          className={`
            relative
            rounded-2xl
            border
            border-dashed
            px-6
            py-10
            flex
            flex-col
            items-center
            justify-center
            text-center
            transition-all
            duration-200

            ${
              isDragging
                ? "bg-blue-50 border-blue-400 scale-[1.01]"
                : "bg-slate-50 border-slate-300 hover:bg-slate-100"
            }

            ${error ? "border-red-400 bg-red-50" : ""}
          `}
        >
          {/* ICON */}
          <div className="w-12 h-12 mb-3 rounded-full bg-white shadow-sm flex items-center justify-center border border-slate-200">
            <Image src={fileicon} alt="file" width={16} height={16} />
          </div>

          {/* TEXT */}
          <p className="text-sm font-medium text-slate-700">
            Drag & drop your PDF here
          </p>

          <p className="text-xs text-slate-500 mt-1">
            or upload from your device
          </p>

          {/* BUTTON */}
          <button
            onClick={onBrowseClick}
            className="mt-4 px-5 py-2.5 text-sm font-medium rounded-lg bg-slate-900 text-white hover:bg-slate-800 transition shadow-sm"
          >
            Upload files
          </button>

          {/* ERROR MESSAGE */}
          {error && (
            <p className="mt-4 text-sm text-red-500 font-medium">
              {error}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default UploadModalUI;