"use client";
import { FiChevronLeft, FiChevronRight } from "react-icons/fi";
import React, { useState, useRef, useEffect } from "react";
import SourceItem from "./SourceItem";
import FileUpload from "./FileUpload";

export interface SidebarItem {
  name: string;
}
interface SidebarProps {
  width: number;
  onWidthChange: (width: number) => void;
  checkedPdfs: string[];
  setCheckedPdfs: React.Dispatch<React.SetStateAction<string[]>>;
}

const LeftSidebar: React.FC<SidebarProps> = ({
  width,
  onWidthChange,
  checkedPdfs,
  setCheckedPdfs,
}) => {
  // Fetch PDFs on component mount to populate the list
  const [sources, setSources] = useState<SidebarItem[]>([]);
  useEffect(() => {
    const fetchPdfs = async () => {
      try {
        const response = await fetch("http://localhost:8000/pdf/list");
        if (response.ok) {
          const data = await response.json();
          setSources(data.pdfs.map((filename: string) => ({ name: filename })));
        } else {
          console.error("Failed to fetch PDFs");
        }
      } catch (error) {
        console.error("Error fetching PDFs:", error);
      }
    };
    fetchPdfs();
  }, []);

  // Maintain list of checked PDFs
  const toggleChecked = (filename: string) => {
    setCheckedPdfs((prev) =>
      prev.includes(filename)
        ? prev.filter((f) => f !== filename)
        : [...prev, filename],
    );
  };

  // Updating sidebar when new source uploaded
  const handleUploadSuccess = (newSource: { name: string }) => {
    setSources((prev) => [...prev, newSource]);
  };

  // Used for resizing
  const handleRef = useRef<HTMLDivElement>(null);

  // Handles the resizing of the sidebar
  const [resizing, setResizing] = useState(false);
  const startResizing = (e: React.MouseEvent) => {
    e.preventDefault();
    setResizing(true);
    const startX = e.clientX;
    const startWidth = width;
    let latestWidth = startWidth;

    const onMouseMove = (moveEvent: MouseEvent) => {
      const newWidth = Math.min(
        window.innerWidth / 3,
        Math.max(64, startWidth + moveEvent.clientX - startX),
      );
      onWidthChange(newWidth);
      latestWidth = newWidth;
    };

    const onMouseUp = () => {
      if (!(width < 150) && latestWidth <= 150) {
        onWidthChange(64);
      }
      document.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("mouseup", onMouseUp);
      setResizing(false);
    };

    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", onMouseUp);
  };

  return (
    <aside
      className={`flex flex-col h-screen bg-gray-200 relative ${
        !resizing ? "transition-all duration-300" : ""
      }`}
      style={{ width: width }}
    >
      {!(width < 150) && (
        <>
          <div className="flex items-center justify-between px-4 pt-8">
            <span className="text-lg font-semibold">Sources</span>
            <button
              className="p-2 bg-primary rounded text-white"
              onClick={() => onWidthChange(64)}
              aria-label="Collapse sidebar"
            >
              <FiChevronLeft size={20} />
            </button>
          </div>
          <div className="border-b border-gray-600 my-2 mx-4" />
        </>
      )}
      {width < 150 && (
        <div className="flex items-center justify-center pt-8">
          <button
            className="p-2 bg-primary rounded text-white"
            onClick={() => onWidthChange(256)}
            aria-label="Expand sidebar"
          >
            <FiChevronRight size={20} />
          </button>
        </div>
      )}
      {/* Only show items and add button if not collapsed */}
      <div className="flex-1 pt-4 px-4 overflow-y-auto w-full">
        {sources.map((item) => (
          <SourceItem
            key={item.name}
            item={item}
            checked={checkedPdfs.includes(item.name)}
            onToggle={toggleChecked}
            isCollapsedSidebar={width < 150}
            //TODO: Implement onClick to preview PDF
            onClick={() => {}}
          />
        ))}
      </div>
      <FileUpload
        uploadEndpoint="http://localhost:8000/pdf/upload"
        onUploadSuccess={handleUploadSuccess}
        isCollapsedSidebar={width < 150}
      />
      <div
        ref={handleRef}
        className="absolute top-0 right-0 h-full w-2 cursor-ew-resize z-20"
        onMouseDown={startResizing}
        aria-label="Resize sidebar"
        style={{ userSelect: "none" }}
      />
    </aside>
  );
};

export default LeftSidebar;
