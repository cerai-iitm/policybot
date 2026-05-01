"use client";

import React from "react";
import Image from "next/image";

import fileicon from "@/assets/file.png";
import addicon from "@/assets/add.png";

interface Props {
  collapsed?: boolean;
  onClick: () => void;
}

const FileUploadUI: React.FC<Props> = ({
  collapsed,
  onClick,
}) => {
  if (collapsed) {
    return (
      <div
        onClick={onClick}
        className="flex justify-center items-center py-4 cursor-pointer"
      >
        <div className="w-10 h-10 min-w-10 min-h-10 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center transition shrink-0 cursor-pointer">
          <Image src={addicon} alt="add" width={12} height={12} />
        </div>
      </div>
    );
  }

  return (
    <button
      onClick={onClick}
      className="w-full h-28 rounded-xl bg-slate-100 hover:bg-slate-200 transition flex flex-col items-center justify-center gap-2"
    >
      <div className="w-10 h-10 flex items-center justify-center">
        <Image src={fileicon} alt="file" className="w-5 opacity-80" />
      </div>

      <p className="text-sm font-medium text-slate-700">
        Add sources
      </p>
    </button>
  );
};

export default FileUploadUI;