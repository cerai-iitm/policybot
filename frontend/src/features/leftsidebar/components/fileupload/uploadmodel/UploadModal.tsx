"use client";

import React, { useRef, useEffect, useState } from "react";
import UploadModalUI from "./UploadModalUI";

interface Props {
  open: boolean;
  onClose: () => void;
  onFileSelect: (file: File) => void;
}

const UploadModal: React.FC<Props> = ({
  open,
  onClose,
  onFileSelect,
}) => {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /* ---------------- CLEAN CLOSE ---------------- */
  const handleClose = () => {
    setError(null);        // ✅ reset here instead of useEffect
    setIsDragging(false);  // cleanup UI state
    onClose();
  };

  /* ---------------- ESC CLOSE ---------------- */
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") handleClose();
    };

    if (open) {
      window.addEventListener("keydown", handleEsc);
    }

    return () => {
      window.removeEventListener("keydown", handleEsc);
    };
  }, [open]);

  if (!open) return null;

  /* ---------------- FILE VALIDATION ---------------- */
  const handleFile = (file: File) => {
    if (file.type !== "application/pdf") {
      setError("Only PDF files are allowed");
      return;
    }

    setError(null);
    onFileSelect(file);
    handleClose(); // ✅ use clean close
  };

  /* ---------------- INPUT CHANGE ---------------- */
  const handleFileChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = e.target.files?.[0];
    if (!file) return;

    handleFile(file);
    e.target.value = "";
  };

  /* ---------------- DRAG EVENTS ---------------- */
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
    setError(null); // ✅ clear error when user retries
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const file = e.dataTransfer.files?.[0];
    if (!file) return;

    handleFile(file);
  };

  return (
    <>
      <UploadModalUI
        isDragging={isDragging}
        error={error}
        onClose={handleClose} // ✅ use wrapped close
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onBrowseClick={() => {
          setError(null); // ✅ clear error before retry
          inputRef.current?.click();
        }}
      />

      {/* HIDDEN INPUT */}
      <input
        aria-label="file"
        ref={inputRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={handleFileChange}
      />
    </>
  );
};

export default UploadModal;