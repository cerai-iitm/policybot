"use client";

import { useRef } from "react";
import FileUploadUI from "./FileUploadUI";

interface Props {
  collapsed?: boolean;
  onFileSelect: (file: File) => void;
}

const FileUpload: React.FC<Props> = ({ collapsed, onFileSelect }) => {
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // ✅ Allow only PDF
    if (file.type !== "application/pdf") {
      alert("Only PDF files are allowed");
      return;
    }

    onFileSelect(file);

    // reset input so same file can be selected again
    e.target.value = "";
  };

  return (
    <FileUploadUI
      collapsed={collapsed}
      onClick={handleClick}
      inputRef={fileInputRef}
      onChange={handleFileChange}
    />
  );
};

export default FileUpload;