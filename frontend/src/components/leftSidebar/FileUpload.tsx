/* ============================================================
   Imports
   ============================================================ */

import { withBase } from "@/lib/url";
import React, { useState, useRef, useEffect } from "react";
import addicon from "../../assets/add.png";
import { createPortal } from "react-dom";
import { api, monitorPdfProcessing } from "@/lib/router";


import {
  FiUpload,
  FiCheckCircle,
  FiXCircle,
  FiX,
} from "react-icons/fi";

/* ============================================================
   Props Interface
   ============================================================ */

interface FileUploadProps {
  uploadEndpoint: string;
   notebookId: string;
  onUploadSuccess: (newSource: { name: string }) => void;
  isCollapsedSidebar: boolean;
  triggerRef?: React.RefObject<HTMLButtonElement | null>; // external trigger ref
}

/* ============================================================
   Component
   ============================================================ */

const FileUpload: React.FC<FileUploadProps> = ({
  uploadEndpoint,
    notebookId,
  onUploadSuccess,
  isCollapsedSidebar,
  triggerRef,
}) => {

  /* ---------------- State Management ---------------- */

  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [uploadStatus, setUploadStatus] = useState<{
    type: "idle" | "uploading" | "success" | "error";
    message: string;
  }>({ type: "idle", message: "" });

  const [isDragOver, setIsDragOver] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingMessage, setProcessingMessage] = useState("");

  /* ---------------- Refs ---------------- */

  const fileInputRef = useRef<HTMLInputElement>(null);

  /* ============================================================
     File Selection (Browse)
     ============================================================ */

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];

      if (file.type === "application/pdf") {
        setSelectedFile(file);
        setUploadStatus({ type: "idle", message: "" });
      } else {
        setUploadStatus({
          type: "error",
          message: "Please select a PDF file.",
        });
      }
    }
  };

  /* ============================================================
     Drag & Drop Handlers
     ============================================================ */

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    const files = e.dataTransfer.files;

    if (files.length > 0) {
      const file = files[0];

      if (file.type === "application/pdf") {
        setSelectedFile(file);
        setUploadStatus({ type: "idle", message: "" });
      } else {
        setUploadStatus({
          type: "error",
          message: "Please drop a PDF file.",
        });
      }
    }
  };

  /* ============================================================
     Upload Handler
     ============================================================ */

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus({
        type: "error",
        message: "Please select a file first.",
      });
      return;
    }

    const formData = new FormData();
formData.append("file", selectedFile);
formData.append("notebook_id", notebookId);


    setUploadStatus({ type: "uploading", message: "Uploading..." });

    try {
      const response = await api.post(
  uploadEndpoint,
  formData,
  { headers: { "Content-Type": "multipart/form-data" } }
);

const result = response.data;


      /* -------- New File Upload -------- */
      if (response.status === 201) {
        setUploadStatus({
          type: "success",
          message: "File uploaded! Processing...",
        });

        setIsProcessing(true);

        try {
          await handleProcessing(result.filename);

          onUploadSuccess({ name: result.filename });

          setUploadStatus({
            type: "success",
            message: "Processing complete!",
          });

          setTimeout(() => setIsModalOpen(false), 2000);
        } catch {
          setUploadStatus({
            type: "error",
            message: "Upload successful but processing failed.",
          });
        }

        setSelectedFile(null);
        if (fileInputRef.current) fileInputRef.current.value = "";
      }

      /* -------- Resume Processing -------- */
      else if (response.status === 200) {
        setUploadStatus({
          type: "success",
          message: `${result.message} Processing...`,
        });

        setIsProcessing(true);

        try {
          await handleProcessing(result.filename);

          setUploadStatus({
            type: "success",
            message: "Processing complete!",
          });

          setTimeout(() => setIsModalOpen(false), 2000);
        } catch {
          setUploadStatus({
            type: "error",
            message: "Processing continuation failed.",
          });
        }

        setSelectedFile(null);
        if (fileInputRef.current) fileInputRef.current.value = "";
      }

      /* -------- Error Cases -------- */
      else if (response.status === 201) {
        setUploadStatus({
          type: "error",
          message: result.detail || "File already fully processed.",
        });
      } else if (response.status === 201) {
        setUploadStatus({
          type: "error",
          message: "Invalid file format. Please upload a PDF.",
        });
      } else {
        setUploadStatus({
          type: "error",
          message: "Failed to upload file.",
        });
      }
    } catch {
      setUploadStatus({
        type: "error",
        message: "An error occurred while uploading.",
      });
    }
  };

  /* ============================================================
     Server-Sent Events (Processing Progress)
     ============================================================ */

const handleProcessing = (filename: string) => {
  return new Promise<void>((resolve, reject) => {
    const eventSource = monitorPdfProcessing(
      notebookId,
      filename,
      (message) => {
        if (message === "done") {
          setIsProcessing(false);
          setProcessingMessage("");
          eventSource.close();
          resolve();
        } else {
          setProcessingMessage(message);
        }
      },
      () => {
        setIsProcessing(false);
        eventSource.close();
        reject();
      }
    );
  });
};


  /* ============================================================
     Helpers
     ============================================================ */

  const openFileDialog = () => fileInputRef.current?.click();

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedFile(null);
    setUploadStatus({ type: "idle", message: "" });

    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  /* ============================================================
     Lock Body Scroll When Modal Is Open
     ============================================================ */

  useEffect(() => {
    if (isModalOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isModalOpen]);

  /* ============================================================
     UI
     ============================================================ */

  return (
    <>
      {/* Sidebar Trigger */}
      {isCollapsedSidebar ? (
        <div className="flex justify-center py-4 ">
          <button
            aria-label="button"
            className="cursor-pointer w-10 h-10 flex items-center justify-center bg-slate-100 border border-slate-300 rounded-lg hover:bg-slate-200 transition"
            onClick={() => setIsModalOpen(true)}
          >
            <img src={addicon.src} className="w-4 h-4" alt="img" />
          </button>
        </div>
      ) : (
        <button
          ref={triggerRef}
          className=" cursor-pointer w-full flex items-center justify-center bg-slate-100 border border-slate-300 rounded-lg h-12 text-sm font-medium text-slate-700 hover:bg-slate-200 transition"
          onClick={() => setIsModalOpen(true)}
        >
          <img src={addicon.src} className="w-3 h-3 mr-3" alt="img" />
          Add sources
        </button>
      )}

      {/* Modal */}
      {isModalOpen &&
        typeof document !== "undefined" &&
        createPortal(
          <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl shadow-xl p-4 sm:p-6 w-full max-w-[90vw] sm:max-w-md mx-3 sm:mx-4 border border-slate-200">

              {/* Header */}
              <div className="flex justify-between items-center mb-5 sm:mb-5">
                <h3 className="text-base sm:text-lg font-semibold text-slate-900">
                  Add Sources
                </h3>

                <button
                  aria-label="button"
                  onClick={closeModal}
                  className="text-slate-400 hover:text-slate-700"
                >
                  <FiX size={22} />
                </button>
              </div>

              {/* Drop Zone */}
              <div
                className={`relative border-2 border-dashed rounded-lg p-4 sm:p-6 text-center transition ${
                  isDragOver
                    ? "border-blue-400 bg-blue-50"
                    : selectedFile
                    ? "border-green-400 bg-green-50"
                    : "border-slate-300 bg-slate-50"
                }`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                {!selectedFile && (
                  <div
                    onClick={openFileDialog}
                    className="absolute inset-0 cursor-pointer"
                  />
                )}

                <input
                  alt="input"
                  aria-label="button"
                  ref={fileInputRef}
                  type="file"
                  accept="application/pdf"
                  onChange={handleFileChange}
                  className="hidden"
                />

                <FiUpload className="mx-auto h-9 w-9 sm:h-12 sm:w-12 text-slate-400 mb-3 sm:mb-4" />

                <p className="text-xs sm:text-sm text-slate-500 mb-3">
                  {selectedFile
                    ? `Selected: ${selectedFile.name}`
                    : "Drag & drop a PDF here, or click to browse"}
                </p>

                <button
                  className="px-3 py-2 sm:px-4 text-[10px] sm:text-sm font-medium bg-[#1E40AF] text-white rounded-md hover:bg-blue-700"
                  type="button"
                  onClick={handleUpload}
                  disabled={!selectedFile || uploadStatus.type === "uploading"}
                >
                  {uploadStatus.type === "uploading"
                    ? "Uploading..."
                    : "Upload PDF"}
                </button>
              </div>

              {/* Status */}
              {uploadStatus.message && (
                <div
                  className={`mt-4 p-3 rounded flex items-center text-sm ${
                    uploadStatus.type === "success"
                      ? "bg-green-50 text-green-600"
                      : uploadStatus.type === "error"
                      ? "bg-red-50 text-red-600"
                      : "bg-blue-50 text-blue-600"
                  }`}
                >
                  {uploadStatus.type === "success" && (
                    <FiCheckCircle className="mr-2" />
                  )}
                  {uploadStatus.type === "error" && (
                    <FiXCircle className="mr-2" />
                  )}
                  {uploadStatus.message}
                </div>
              )}

              {/* Processing */}
              {isProcessing && (
                <div className="mt-4 p-3 bg-blue-50 text-blue-600 rounded flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                  <span className="text-xs sm:text-sm">
                    {processingMessage || "Processing..."}
                  </span>
                </div>
              )}
            </div>
          </div>,
          document.body
        )}
    </>
  );
};

export default FileUpload;
