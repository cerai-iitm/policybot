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

      if (response.ok && response.status === 201) {
        const result = await response.json();
        setUploadStatus({
          type: "success",
          message: "File uploaded! Processing...",
        });
        setIsProcessing(true);
        await handleProcessing(result.filename); // Pass filename instead of ID
        onUploadSuccess({ name: result.filename });
        setUploadStatus({ type: "success", message: "Processing complete!" });
        setTimeout(() => setIsModalOpen(false), 2000);
        setSelectedFile(null);
        if (fileInputRef.current) fileInputRef.current.value = "";
      } else if (response.status === 400) {
        setUploadStatus({
          type: "error",
          message: "Invalid file format. Please upload a PDF.",
        });
      } else if (response.status === 409) {
        const result = await response.json();
        setUploadStatus({
          type: "error",
          message: result.detail || "File already exists.",
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
    return new Promise<void>((resolve) => {
      console.log("Starting EventSource for filename:", filename); // Add: Log start
      const eventSource = new EventSource(
        `http://localhost:8000/pdf/process/${encodeURIComponent(filename)}`,
      );

      eventSource.onopen = () => {
        console.log("EventSource opened successfully"); // Add: Confirm connection
      };

      eventSource.onmessage = (event) => {
        console.log("Received event data:", event.data); // Add: Log raw data
        if (event.data === "done") {
          console.log("Processing done, closing EventSource"); // Add: Log done
          setIsProcessing(false);
          setProcessingMessage("");
          eventSource.close();
          resolve();
        } else {
          console.log("Updating processingMessage to:", event.data); // Add: Log update
          setProcessingMessage(event.data);
        }
      };

      eventSource.onerror = (error) => {
        console.error("EventSource error:", error); // Already there, ensure it's logged
        setProcessingMessage("Processing failed.");
        setIsProcessing(false);
        eventSource.close();
        resolve();
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
        <div className="p-4 border-t border-gray-300 bg-gray-50 flex justify-center">
          <button
            className="p-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            onClick={() => setIsModalOpen(true)}
            aria-label="Add Source"
          >
            <FiPlus size={20} />
          </button>
        </div>
      ) : (
        <div className="p-4 border-t border-gray-300 bg-gray-50">
          <button
            className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
            onClick={() => setIsModalOpen(true)}
          >
            <FiPlus className="mr-2" />
            Add Sources
          </button>
        </div>
      )}

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Upload PDF</h3>
              <button
                onClick={closeModal}
                className="text-gray-500 hover:text-gray-700"
              >
                <FiX size={24} />
              </button>
            </div>
            <div
              className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                isDragOver
                  ? "border-blue-500 bg-blue-50"
                  : selectedFile
                    ? "border-green-500 bg-green-50"
                    : "border-gray-300 bg-gray-50"
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
              <FiUpload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p className="text-sm text-gray-600 mb-2">
                {selectedFile
                  ? `Selected: ${selectedFile.name}`
                  : "Drag & drop a PDF here, or click to browse"}
              </p>
              <button
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
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
                    ? "bg-green-100 text-green-800"
                    : uploadStatus.type === "error"
                      ? "bg-red-100 text-red-800"
                      : "bg-blue-100 text-blue-800"
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
              <div className="mt-4 p-3 bg-blue-100 text-blue-800 rounded flex items-center">
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
