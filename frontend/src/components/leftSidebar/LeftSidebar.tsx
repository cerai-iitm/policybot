"use client";
import { FiChevronLeft, FiChevronRight, FiCircle } from "react-icons/fi";
import { AiOutlineCheckCircle, AiOutlineMinusCircle } from "react-icons/ai";
import React, { useState, useRef, useEffect } from "react";
import SourceItem from "./SourceItem";
import FileUpload from "./FileUpload";

export interface SidebarItem {
  name: string;
}
interface SidebarProps {
  width: number;
  onWidthChange: (width: number) => void;
  onFileSelect: (fileName: string) => void;
  checkedPdfs: string[];
  setCheckedPdfs: React.Dispatch<React.SetStateAction<string[]>>;
  sources: SidebarItem[];
  setSources: React.Dispatch<React.SetStateAction<SidebarItem[]>>;
}

const LeftSidebar: React.FC<SidebarProps> = ({
  width,
  onWidthChange,
  onFileSelect,
  checkedPdfs,
  setCheckedPdfs,
  sources,
  setSources,
}) => {
  const initializedRef = useRef(false);

  // Fetch PDFs on component mount to populate the list
  useEffect(() => {
    const fetchPdfs = async () => {
      try {
        const response = await fetch("http://localhost:8000/pdf/list");
        if (response.ok) {
          const data = await response.json();
          const names = data.pdfs.map((filename: string) => ({
            name: filename,
          }));
          setSources(names);
          if (!initializedRef.current) {
            setCheckedPdfs(names.map((n: SidebarItem) => n.name));
            initializedRef.current = true;
          }
        } else {
          console.error("Failed to fetch PDFs");
        }
      } catch (error) {
        console.error("Error fetching PDFs:", error);
      }
    };
    fetchPdfs();
  }, []);

  const handleFileSelect = (filename: string) => {
    console.log("Reached handle file select ", filename);
    onFileSelect(filename);
  };
  // Maintain list of checked PDFs
  const toggleChecked = (filename: string) => {
    setCheckedPdfs((prev) =>
      prev.includes(filename)
        ? prev.filter((f) => f !== filename)
        : [...prev, filename]
    );
  };

  // Updating sidebar when new source uploaded
  const handleUploadSuccess = (newSource: { name: string }) => {
    setSources((prev) => [...prev, newSource]);
    // keep default selection behaviour: newly uploaded file should be selected
    setCheckedPdfs((prev) => {
      if (prev.includes(newSource.name)) return prev;
      return [...prev, newSource.name];
    });
  };

  // Select / Deselect All toggle
  const selectAllToggle = () => {
    const allNames = sources.map((s) => s.name);
    if (allNames.length === 0) return;
    const areAllSelected =
      allNames.length > 0 && allNames.every((n) => checkedPdfs.includes(n));
    if (areAllSelected) {
      // deselect all
      setCheckedPdfs([]);
    } else {
      // select all
      setCheckedPdfs(allNames);
    }
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
        Math.max(64, startWidth + moveEvent.clientX - startX)
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

  // compute select-all icon state
  const allNames = sources.map((s) => s.name);
  const areAllSelected =
    allNames.length > 0 && allNames.every((n) => checkedPdfs.includes(n));
  const areNoneSelected = allNames.every((n) => !checkedPdfs.includes(n));
  const isPartial = !areAllSelected && !areNoneSelected;
  // use circled icons for the three states; use the same open circle as SourceItem for "none"
  const SelectAllIcon = areAllSelected
    ? AiOutlineCheckCircle
    : areNoneSelected
    ? FiCircle
    : AiOutlineMinusCircle;

  return (
    <aside
      className={`flex flex-col h-screen bg-bg text-text relative  ${
        !resizing ? "transition-all duration-300" : ""
      }`}
      style={{ width: width }}
    >
      {!(width < 150) && (
        <>
          <div className="flex items-center justify-between px-4 pt-8">
            <span className="text-lg text-black font-semibold">Sources</span>
            <button
              className="p-2 bg-background-dark rounded text-foreground"
              onClick={() => onWidthChange(64)}
              aria-label="Collapse sidebar"
            >
              <FiChevronLeft size={20} />
            </button>
          </div>
          <div className="border-b border-gray-600 my-2 mx-4" />

          {/* Select / Deselect All - only visible when sidebar not collapsed */}
          {allNames.length > 0 && (
            <div className="p-2 text-text-muted rounded flex justify-between items-center">
              <div className="flex items-center">
                {/* placeholder to align with SourceItem's left file icon (20px) */}
                <div className="w-5 mr-2 flex-shrink-0" aria-hidden="true" />
                <span className="truncate flex-grow min-w-0 text-sm">All</span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  selectAllToggle();
                }}
                aria-label="Select or deselect all sources"
                className="ml-5 flex-shrink-0 p-1 rounded flex items-center justify-center"
              >
                {/* match size and vertical centering of SourceItem icons */}
                <SelectAllIcon size={20} className="text-text" />
              </button>
            </div>
          )}
        </>
      )}
      {width < 150 && (
        <div className="flex items-center justify-center pt-8 text-foreground">
          <button
            className="p-2 bg-background rounded"
            onClick={() => onWidthChange(256)}
            aria-label="Expand sidebar"
          >
            <FiChevronRight size={20} />
          </button>
        </div>
      )}
      {/* Only show items and add button if not collapsed */}
      <div className="flex-1 pt-4 px-4 overflow-y-auto w-full text-foreground">
        {sources.map((item) => (
          <SourceItem
            key={item.name}
            item={item}
            checked={checkedPdfs.includes(item.name)}
            onToggle={toggleChecked}
            isCollapsedSidebar={width < 150}
            onClick={() => handleFileSelect(item.name)}
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
