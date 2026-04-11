import React, { useState, useRef, useEffect } from "react";
import {
  FiMoreVertical,
  FiTrash2,
} from "react-icons/fi";
import { SidebarItem } from "./LeftSidebar";
import { withBase } from "@/lib/url";
import docicon from "../../assets/doc.png";
import uncheckedicon from "../../assets/unmarked.png";
import checkedicon from "../../assets/marked.png";

interface SourceItemProps {
   item: {
    filename: string;
    processing_status: string;
    uploaded_at: string;
  };
  checked: boolean;
  
  onToggle: (id: string) => void;
  isCollapsedSidebar: boolean;
  onClick: () => void;
  onDelete?: (filename: string) => void;
}

const SourceItem: React.FC<SourceItemProps> = ({
  item,
  checked,
  onToggle,
  isCollapsedSidebar: isCollapsed,
  onClick,
  onDelete,
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  /* ---------------- CLOSE MENU ON OUTSIDE CLICK ---------------- */
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target as Node)
      ) {
        setIsMenuOpen(false);
      }
    };

    if (isMenuOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => {
        document.removeEventListener(
          "mousedown",
          handleClickOutside
        );
      };
    }
  }, [isMenuOpen]);

  /* ---------------- DELETE FILE ---------------- */
  const handleDeleteFile = async (e: React.MouseEvent) => {
    e.stopPropagation();

    try {
      const formData = new FormData();
      formData.append("filename", item.filename
);

      const response = await fetch(
        withBase(`/api/pdf/remove`),
        {
          method: "POST",
          body: formData,
        }
      );

      if (response.ok) {
        setIsMenuOpen(false);
        onDelete?.(item.filename
);
      } else {
        alert("Failed to delete file. Please try again.");
      }
    } catch (error) {
      alert("Error deleting file. Please try again.");
    }
  };

  const handleMenuClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsMenuOpen((prev) => !prev);
  };

  /* ---------------- COLLAPSED VIEW ---------------- */
  if (isCollapsed) {
    return (
      <div className="flex justify-center items-center p-2">
        <img
          src={docicon.src}
          alt="doc"
          className="w-5 h-5"
        />
      </div>
    );
  }

  /* ---------------- EXPANDED VIEW ---------------- */
  return (
    <div className="relative">
      <div
        className="group h-12 px-6 rounded-lg flex items-center justify-between hover:bg-slate-100"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* LEFT SIDE (Icon + Name) */}
        <div className="flex items-center gap-3 min-w-0 flex-1">
          
          {/* Icon / Menu Button */}
          <button
            onClick={handleMenuClick}
            className="w-8 h-8 flex items-center justify-center shrink-0 rounded hover:bg-slate-200 cursor-pointer"
            aria-label="File options"
          >
            {isHovered ? (
              <FiMoreVertical
                className="text-slate-600"
                size={18}
              />
            ) : (
              <img
                src={docicon.src}
                alt="doc"
                className="w-4 h-4"
              />
            )}
          </button>

          {/* File Name → TOGGLE CHECKBOX */}
          <span
            className="truncate text-sm font-inter text-slate-600 cursor-pointer"
            onClick={(e) => {
              e.stopPropagation();
              onToggle(item.filename
);
            }}
          >
            {item.filename
}
          </span>
        </div>

        {/* RIGHT SIDE (Checkbox) */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onToggle(item.filename
);
          }}
          className="ml-2 flex items-center justify-center shrink-0 w-6 h-6 cursor-pointer"
        >
          <img
            src={
              checked
                ? checkedicon.src
                : uncheckedicon.src
            }
            className="w-5 h-5"
            alt="check"
          />
        </button>
      </div>

      {/* Dropdown Menu */}
      {isMenuOpen && (
        <div
          ref={menuRef}
          className="absolute left-0 top-full mt-1 bg-white border border-slate-200 rounded shadow-lg z-50 min-w-32"
        >
          <button
            onClick={handleDeleteFile}
            className="w-full flex items-center gap-2 px-4 py-2 text-red-500 hover:bg-slate-100"
          >
            <FiTrash2 size={16} />
            Delete
          </button>
        </div>
      )}
    </div>
  );
};

export default SourceItem;
