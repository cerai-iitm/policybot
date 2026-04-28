"use client";

import React, { useState } from "react";
import { FiMoreVertical, FiTrash2 } from "react-icons/fi";
import Image from "next/image";

import docicon from "@/assets/doc.png";
import uncheckedicon from "@/assets/unmarked.png";
import checkedicon from "@/assets/marked.png";

interface Props {
  item: any;
  checked: boolean;
  onToggle: (filename: string) => void;
  onDelete?: (id: string, filename: string) => void;
  onClick?: () => void;
  isCollapsedSidebar?: boolean;
}

const SourceItem: React.FC<Props> = ({
  item,
  checked,
  onToggle,
  onDelete,
  onClick,
  isCollapsedSidebar,
}) => {
  const [isHovered, setIsHovered] = useState(false);

  /* ---------------- COLLAPSED ---------------- */
 if (isCollapsedSidebar) {
  return (
    <div
      className="flex justify-center items-center p-2"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="w-8 h-8 flex items-center justify-center rounded hover:bg-slate-200 cursor-pointer">
        {isHovered ? (
          <FiMoreVertical size={16} />
        ) : (
          <Image
            src={docicon}
            alt="document"
            width={18}
            height={18}
          />
        )}
      </div>
    </div>
  );
}

  /* ---------------- NORMAL ---------------- */
  return (
    <div
      className="group h-12 px-6 rounded-lg flex items-center justify-between hover:bg-slate-100"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick}
    >
      {/* LEFT */}
      <div className="flex items-center gap-3 min-w-0 flex-1">
        
        {/* ICON / MENU */}
        <button className="w-8 h-8 flex items-center justify-center rounded hover:bg-slate-200">
          {isHovered ? (
            <FiMoreVertical size={18} />
          ) : (
            <Image
              src={docicon}
              alt="document"
              width={16}
              height={16}
            />
          )}
        </button>

        {/* FILE NAME */}
        <span
          className="truncate text-sm text-slate-600 cursor-pointer"
          onClick={(e) => {
            e.stopPropagation();
            onToggle(item.filename);
          }}
        >
          {item.filename}
        </span>
      </div>

      {/* RIGHT */}
      <div className="flex items-center gap-2">

        {/* CHECKBOX */}
        <button
          aria-label="toggle source"
          onClick={(e) => {
            e.stopPropagation();
            onToggle(item.filename);
          }}
        >
          <Image
            src={checked ? checkedicon : uncheckedicon}
            alt="checkbox"
            width={20}
            height={20}
          />
        </button>

      
       
      </div>
    </div>
  );
};

export default SourceItem;