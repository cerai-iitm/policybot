"use client";

import React, { useState } from "react";
import { FiMoreVertical } from "react-icons/fi";
import Image from "next/image";

import docicon from "@/assets/doc.png";
import uncheckedicon from "@/assets/unmarked.png";
import checkedicon from "@/assets/marked.png";

interface Props {
  item: any;
  checked: boolean;
  onToggle: (filename: string) => void;
  onDelete?: (id: string) => void;
  onClick?: () => void;
  isCollapsedSidebar?: boolean;
  
}

const SourceItem: React.FC<Props> = ({
  item,
  checked,
  onToggle,
  onClick,
  isCollapsedSidebar,
  onDelete
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  const filename = item.filename || "";

  // Only long names get marquee
  const isLongName = filename.length > 22;

  /* ------------ keep .pdf visible while truncating ------------ */
  const getDisplayName = (name: string) => {
    if (!isLongName) return name;

    const lastDot = name.lastIndexOf(".");
    if (lastDot === -1) {
      return name.slice(0, 18) + "...";
    }

    const base = name.slice(0, lastDot);
    const ext = name.slice(lastDot); // .pdf

    return `${base.slice(0, 16)}...${ext}`;
  };

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
    <>
      <style jsx>{`
        @keyframes marqueeScroll {
          0% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-100%);
          }
        }

        .marquee {
          display: inline-block;
          white-space: nowrap;
        }

        .group:hover .animate-marquee {
          animation: marqueeScroll 8s linear infinite;
        }
      `}</style>

      <div
        className="group h-12 px-6 rounded-lg flex items-center justify-between hover:bg-slate-100 overflow-hidden"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onClick={onClick}
      >
        {/* LEFT */}
        <div className="flex items-center gap-3 min-w-0 flex-1 overflow-hidden">
          
          {/* ICON / MENU */}
         <div className="relative">
  <button
    onClick={(e) => {
      e.stopPropagation();
      setShowMenu((prev) => !prev);
    }}
    className="w-8 h-8 flex items-center justify-center rounded hover:bg-slate-200"
  >
    {isHovered ? (
      <FiMoreVertical size={18} />
    ) : (
      <Image src={docicon} alt="document" width={16} height={16} />
    )}
  </button>

  {/* DROPDOWN */}
  {showMenu && (
    <div className="absolute left-0 mt-2 w-32 bg-white border rounded-lg shadow-md z-20">
      <button
        onClick={(e) => {
          e.stopPropagation();
          setShowMenu(false);
          onDelete?.(item.pdf_id);
        }}
        className="w-full text-left px-4 py-2 text-sm hover:bg-red-50 text-red-600"
      >
        Delete
      </button>
    </div>
  )}
</div>

          {/* FILE NAME */}
          <div
            className="flex-1 overflow-hidden cursor-pointer"
            onClick={(e) => {
              e.stopPropagation();
              onToggle(item.pdf_id);
            }}
          >
            {isLongName ? (
              <>
                {/* default truncated text with ... */}
                <span className="group-hover:hidden block truncate text-sm text-slate-600">
                  {getDisplayName(filename)}
                </span>

                {/* only on hover long names scroll */}
                <span className="hidden group-hover:block text-sm text-slate-600 overflow-hidden whitespace-nowrap">
                  <span className="marquee animate-marquee">
                    {filename}
                  </span>
                </span>
              </>
            ) : (
              <span className="block truncate text-sm text-slate-600">
                {filename}
              </span>
            )}
          </div>
        </div>

        {/* RIGHT */}
        <div className="flex items-center gap-2 shrink-0">
          <button
            aria-label="toggle source"
            onClick={(e) => {
              e.stopPropagation();
              onToggle(item.pdf_id);
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
    </>
  );
};

export default SourceItem;