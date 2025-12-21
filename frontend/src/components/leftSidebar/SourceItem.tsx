import React, { useState, useRef, useEffect } from "react";
import {
  FiCheckCircle,
  FiFileText,
  FiCircle,
  FiMoreVertical,
  FiTrash2,
} from "react-icons/fi";
import { SidebarItem } from "./LeftSidebar";
import { withBase } from "@/lib/url";

interface SourceItemProps {
  item: SidebarItem;
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

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false);
      }
    };

    if (isMenuOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => {
        document.removeEventListener("mousedown", handleClickOutside);
      };
    }
  }, [isMenuOpen]);

  // Handle delete file
  const handleDeleteFile = async (e: React.MouseEvent) => {
    e.stopPropagation();

    try {
      const response = await fetch(
        withBase(`/api/pdf/delete/${encodeURIComponent(item.name)}`),
        { method: "DELETE" }
      );

      if (response.ok) {
        setIsMenuOpen(false);
        // Call the parent callback to remove from list
        if (onDelete) {
          onDelete(item.name);
        }
      } else {
        console.error("Failed to delete file");
        alert("Failed to delete file. Please try again.");
      }
    } catch (error) {
      console.error("Error deleting file:", error);
      alert("Error deleting file. Please try again.");
    }
  };

  // Toggle menu and prevent event bubbling
  const handleMenuClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsMenuOpen(!isMenuOpen);
  };

  if (isCollapsed) {
    return (
      <div className="flex justify-center items-center p-2">
        <FiFileText className="text-red-500" size={20} aria-hidden="true" />
      </div>
    );
  }

  return (
    <div className="relative">
      <div
        className="p-2  hover:bg-bg-dark  text-text-muted hover:text-text rounded cursor-pointer flex justify-between items-center"
        onClick={onClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <button
          onClick={handleMenuClick}
          className="flex-shrink-0 flex items-center justify-center p-1 rounded hover:bg-bg-muted transition-colors"
          aria-label="File options menu"
          title="More options"
        >
          {isHovered ? (
            <FiMoreVertical className="text-text" size={20} />
          ) : (
            <FiFileText className="text-red-500" size={20} />
          )}
        </button>
        <span className="truncate flex-grow min-w-0 mr-2 ">{item.name}</span>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onToggle(item.name);
          }}
          className="ml-2 flex-shrink-0 flex items-center justify-center"
          aria-label={checked ? "Uncheck" : "Check"}
        >
          {checked ? (
            <FiCheckCircle className="text-text" size={20} />
          ) : (
            <FiCircle className="text-text" size={20} />
          )}
        </button>
      </div>

      {/* Dropdown Menu */}
      {isMenuOpen && (
        <div
          ref={menuRef}
          className="absolute left-0 top-full mt-1 bg-bg-light border border-border-muted rounded shadow-lg z-50 min-w-32"
        >
          <button
            onClick={handleDeleteFile}
            className="w-full flex items-center gap-2 px-4 py-2 text-red-500 hover:bg-bg-dark rounded transition-colors first:rounded-t last:rounded-b"
            title="Delete this PDF"
          >
            <FiTrash2 size={16} />
            <span>Delete</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default SourceItem;
