"use client";

import Image from "next/image";
import { useRef } from "react";
import fileicon from "@/assets/file.png";
import addicon from "@/assets/add.png";

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

  /* ---------------- COLLAPSED ---------------- */
  if (collapsed) {
    return (
      <>
        <div
          onClick={handleClick}
          className="flex justify-center items-center py-4 cursor-pointer"
        >
          <div className="w-10 h-10 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center transition">
            <Image src={addicon} alt="add" width={12} height={12} />
          </div>
        </div>

        <input
        aria-label="file"
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={handleFileChange}
        />
      </>
    );
  }

  /* ---------------- NORMAL ---------------- */
  return (
    <>
      <button
        onClick={handleClick}
        className="w-full h-28 rounded-xl bg-slate-100 hover:bg-slate-200 transition flex flex-col items-center justify-center gap-2"
      >
        <div className="w-10 h-10 flex items-center justify-center">
          <Image src={fileicon} alt="add" className="w-5 opacity-80" />
        </div>

        <p className="text-sm font-medium text-slate-700">
          Add sources
        </p>
      </button>

      <input
      aria-label="file"
        ref={fileInputRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={handleFileChange}
      />
    </>
  );
};

export default FileUpload;