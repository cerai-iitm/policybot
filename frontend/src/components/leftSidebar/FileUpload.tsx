import { withBase } from "@/lib/url";
import React, { useState, useRef } from "react";

import {
  FiUpload,
  FiCheckCircle,
  FiXCircle,
  FiPlus,
  FiX,
} from "react-icons/fi";

interface FileUploadProps {
  uploadEndpoint: string;
  onUploadSuccess: (newSource: { name: string }) => void;
  isCollapsedSidebar: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({
  uploadEndpoint,
  onUploadSuccess,
  isCollapsedSidebar,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<{
    type: "idle" | "uploading" | "success" | "error";
    message: string;
  }>({ type: "idle", message: "" });
  const [isDragOver, setIsDragOver] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingMessage, setProcessingMessage] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

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
        setUploadStatus({ type: "error", message: "Please drop a PDF file." });
      }
    }
  };

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
    setUploadStatus({ type: "uploading", message: "Uploading..." });

    try {
      const response = await fetch(uploadEndpoint, {
        method: "POST",
        body: formData,
      });
      const result = await response.json();

      if (response.status === 201) {
        // New file uploaded successfully
        setUploadStatus({
          type: "success",
          message: "File uploaded! Processing...",
        });
        setIsProcessing(true);
        
        try {
          await handleProcessing(result.filename);
          // MOVED: Only call onUploadSuccess after successful processing
          onUploadSuccess({ name: result.filename });
          setUploadStatus({ type: "success", message: "Processing complete!" });
          setTimeout(() => setIsModalOpen(false), 2000);
        } catch (processingError) {
          setUploadStatus({
            type: "error", 
            message: "Upload successful but processing failed."
          });
          console.error("Processing failed:", processingError);
        }
        
        setSelectedFile(null);
        if (fileInputRef.current) fileInputRef.current.value = "";
        
      } else if (response.status === 200) {
        // Partial file - continue processing, don't add to sources
        setUploadStatus({
          type: "success",
          message: `${result.message} Processing...`,
        });
        setIsProcessing(true);
        
        try {
          await handleProcessing(result.filename);
          setUploadStatus({ type: "success", message: "Processing complete!" });
          setTimeout(() => setIsModalOpen(false), 2000);
        } catch (processingError) {
          setUploadStatus({
            type: "error",
            message: "Processing continuation failed."
          });
          console.error("Processing continuation failed:", processingError);
        }
        
        setSelectedFile(null);
        if (fileInputRef.current) fileInputRef.current.value = "";
        
      } else if (response.status === 409) {
        // File already fully processed
        setUploadStatus({
          type: "error",
          message: result.detail || "File already fully processed.",
        });
      } else if (response.status === 400) {
        setUploadStatus({
          type: "error",
          message: "Invalid file format. Please upload a PDF.",
        });
      } else {
        setUploadStatus({ type: "error", message: "Failed to upload file." });
      }
    } catch (error) {
      console.error("Error uploading file:", error);
      setUploadStatus({
        type: "error",
        message: "An error occurred while uploading.",
      });
    }
  };

  const handleProcessing = (filename: string) => {
    return new Promise<void>((resolve, reject) => {
      console.log("Starting EventSource for filename:", filename);
      const processingURL = withBase(
        `/api/pdf/process/${encodeURIComponent(filename)}`,
      );
      const eventSource = new EventSource(processingURL);

      eventSource.onopen = () => {
        console.log("EventSource opened successfully");
      };

      eventSource.onmessage = (event) => {
        console.log("Received event data:", event.data);
        
        if (event.data === "done") {
          console.log("Processing done, closing EventSource");
          setIsProcessing(false);
          setProcessingMessage("");
          eventSource.close();
          resolve();
        } else if (event.data.startsWith("Error:")) {
          console.error("Processing error received:", event.data);
          setProcessingMessage("Processing failed.");
          setIsProcessing(false);
          eventSource.close();
          reject(new Error(event.data));
        } else {
          console.log("Updating processingMessage to:", event.data);
          setProcessingMessage(event.data);
        }
      };

      eventSource.onerror = (error) => {
        console.error("EventSource error:", error);
        setProcessingMessage("Processing failed.");
        setIsProcessing(false);
        eventSource.close();
        reject(new Error("EventSource connection failed"));
      };
    });
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedFile(null);
    setUploadStatus({ type: "idle", message: "" });
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <>
      {isCollapsedSidebar ? (
        <div className="p-4 border-t border-border-muted bg-bg-light flex justify-center">
          <button
            className="p-2 bg-blue-600 text-white rounded hover:bg-blue-600/75"
            onClick={() => setIsModalOpen(true)}
            aria-label="Add Source"
          >
            <FiPlus size={20} />
          </button>
        </div>
      ) : (
        <div className="p-4 border-t border-border-muted bg-bg-light">
          <button
            className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-600/75 text-sm"
            onClick={() => setIsModalOpen(true)}
          >
            <FiPlus className="mr-2" />
            Add Sources
          </button>
        </div>
      )}

      {isModalOpen && (
        <div className="fixed inset-0 bg-bg-dark/50 flex items-center justify-center z-50">
          <div className="bg-bg rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-text">Upload PDF</h3>
              <button
                onClick={closeModal}
                className="text-text-muted hover:text-text"
              >
                <FiX size={24} />
              </button>
            </div>
            <div
              className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                isDragOver
                  ? "border-primary bg-primary/10"
                  : selectedFile
                    ? "border-success bg-success/10"
                    : "border-border-muted bg-bg-light"
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={openFileDialog}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}
                className="hidden"
              />
              <FiUpload className="mx-auto h-12 w-12 text-border-muted mb-4" />
              <p className="text-sm text-text-muted mb-2">
                {selectedFile
                  ? `Selected: ${selectedFile.name}`
                  : "Drag & drop a PDF here, or click to browse"}
              </p>
              <button
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-600/75 disabled:opacity-50"
                onClick={(e) => {
                  e.stopPropagation();
                  handleUpload();
                }}
                disabled={!selectedFile || uploadStatus.type === "uploading"}
              >
                {uploadStatus.type === "uploading"
                  ? "Uploading..."
                  : "Upload PDF"}
              </button>
            </div>
            {uploadStatus.message && (
              <div
                className={`mt-4 p-3 rounded flex items-center ${
                  uploadStatus.type === "success"
                    ? "bg-success/10 text-success"
                    : uploadStatus.type === "error"
                      ? "bg-danger/10 text-danger"
                      : "bg-info/10 text-info"
                }`}
              >
                {uploadStatus.type === "success" && (
                  <FiCheckCircle className="mr-2" />
                )}
                {uploadStatus.type === "error" && (
                  <FiXCircle className="mr-2" />
                )}
                <span className="text-sm">{uploadStatus.message}</span>
              </div>
            )}
            {isProcessing && (
              <div className="mt-4 p-3 bg-info/10 text-info rounded flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                <span className="text-sm">
                  {processingMessage || "Processing..."}
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default FileUpload;
