"use client";

import React, { useState, useRef, useEffect } from "react";
import SourceItem from "./SourceItem";
import FileUpload from "./FileUpload";
import { withBase } from "@/lib/url";

import sidebaricon from "../../assets/sidebar.png";
import selectAllChecked from "../../assets/marked.png";
import selectAllUnchecked from "../../assets/unmarked.png";
import selectAllIndeterminate from "../../assets/partialmarked.png";
import logo from "../../assets/logo.png";
import { FiMenu, FiX } from "react-icons/fi";
import { useNotebookId } from "@/hooks/useNotebookId";

import { listPdfs } from "@/lib/router";
import type { PDFListItem } from "@/lib/interfaces";
import type { UIPDFItem } from "@/lib/interfaces";

export type SidebarItem = UIPDFItem;








export interface PDFListResponse {
  pdfs: PDFListItem[];
}


interface SidebarProps {
  width: number;
  defaultWidth: number; 
  onWidthChange: (width: number) => void;
  onFileSelect: (fileName: string) => void;
  checkedPdfs: string[];
  setCheckedPdfs: React.Dispatch<React.SetStateAction<string[]>>;
  sources: SidebarItem[];
  setSources: React.Dispatch<React.SetStateAction<SidebarItem[]>>;
  selectedFilename: string | null;
  setSelectedFilename: React.Dispatch<
    React.SetStateAction<string | null>
  >;
  setIsPDFEnabled: React.Dispatch<React.SetStateAction<boolean>>;
  setShowRightSidebar: React.Dispatch<React.SetStateAction<boolean>>;
    isMobile?: boolean;
  onMobileClose?: () => void;
  onExposeUploadTrigger?: (fn: () => void) => void;
}

const LeftSidebar: React.FC<SidebarProps> = ({
  width,
  defaultWidth,
  onWidthChange,
  onFileSelect,
  checkedPdfs,
  setCheckedPdfs,
  sources,
  setSources,
  selectedFilename,
  setSelectedFilename,
  setIsPDFEnabled,
  setShowRightSidebar,
  isMobile = false,
  onMobileClose, 
  onExposeUploadTrigger,
}) => {
  const initializedRef = useRef(false);
    const notebookId = useNotebookId(); // 🔥 CORE LINE
const uploadEndpoint = withBase("/api/pdf/upload");


  // Top
const uploadTriggerRef = useRef<HTMLButtonElement | null>(null);





useEffect(() => {
  onExposeUploadTrigger?.(() => {
    uploadTriggerRef.current?.click();
  });
}, []);

  /* ---------------- FETCH PDFs (ORIGINAL LOGIC) ---------------- */
useEffect(() => {
  const fetchPdfs = async () => {
    try {
     const { pdfs } = await listPdfs(notebookId);
setSources(pdfs); // ✅ NO ERROR


     

      if (!initializedRef.current) {
        setCheckedPdfs([]);
        initializedRef.current = true;
      }
    } catch (err) {
      console.error("Failed to load PDFs:", err);

      setSources([]);

      if (!initializedRef.current) {
        setCheckedPdfs([]);
        initializedRef.current = true;
      }
    }
  };

  fetchPdfs();
}, [notebookId]);

  /* ---------------- FILE SELECT ---------------- */
  const handleFileSelect = (filename: string) => {
    onFileSelect(filename);
  };

  /* ---------------- TOGGLE CHECK ---------------- */
const toggleChecked = (filename: string) => {
  setCheckedPdfs((prev) =>
    prev.includes(filename)
      ? prev.filter((f) => f !== filename)
      : [...prev, filename]
  );
};


  /* ---------------- UPLOAD SUCCESS ---------------- */
const handleUploadSuccess = (newSource: { name: string }) => {
  setSources((prev) => [
    ...prev,
    {
      filename: newSource.name,
      processing_status: "done",
      uploaded_at: new Date().toISOString(),
    },
  ]);
};



  /* ---------------- DELETE PDF ---------------- */
  const handleDeletePdf = (filename: string) => {
    setSources((prev) => prev.filter((s) => s.filename !== filename));
    setCheckedPdfs((prev) =>
      prev.filter((f) => f !== filename)
    );

    if (filename === selectedFilename) {
      setSelectedFilename(null);
      setIsPDFEnabled(false);
      setShowRightSidebar(false);
    }
  };

  /* ---------------- SELECT ALL ---------------- */
  const selectAllToggle = () => {
    const allNames = sources.map((s) => s.filename);
    if (!allNames.length) return;

    const areAllSelected = allNames.every((n) =>
      checkedPdfs.includes(n)
    );

    if (areAllSelected) {
      setCheckedPdfs([]);
    } else {
      setCheckedPdfs(allNames);
    }
  };

  const allNames = sources.map((s) => s.filename);
  const areAllSelected =
    allNames.length > 0 &&
    allNames.every((n) => checkedPdfs.includes(n));

  const areNoneSelected = allNames.every(
    (n) => !checkedPdfs.includes(n)
  );

  const selectAllIconSrc = areAllSelected
    ? selectAllChecked.src
    : areNoneSelected
    ? selectAllUnchecked.src
    : selectAllIndeterminate.src;

  /* ---------------- RESIZE ---------------- */
  const handleRef = useRef<HTMLDivElement>(null);
  const [resizing, setResizing] = useState(false);

  const startResizing = (e: React.MouseEvent) => {
    e.preventDefault();
    setResizing(true);

    const startX = e.clientX;
    const startWidth = width;
    let latestWidth = startWidth;

    const onMouseMove = (moveEvent: MouseEvent) => {
      const newWidth = Math.min(
        window.innerWidth * 0.4,
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

  /* ================= UI ================= */

  return (
    <aside
      className={`flex flex-col h-full bg-slate-50 border-r border-slate-200 relative ${
        !resizing ? "transition-all duration-300" : ""
      }`}
      style={{ width }}
    >
      {width < 150 ? (
        <div className="flex flex-col items-center pt-6 gap-4">
          <button
            className="p-2 bg-white rounded shadow-sm"
            onClick={() => onWidthChange(defaultWidth)}

          >
            <img
              src={sidebaricon.src}
              alt="Expand"
              className="w-4 h-4"
            />
          </button>
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between px-6 pt-6 pb-5">
           <img src={logo.src} alt="Logo" className="h-5 w-auto" />

        {isMobile ? (
  <button
    className="p-2 rounded-md hover:bg-slate-100"
    onClick={onMobileClose}
    aria-label="Close sidebar"
  >
    <FiX size={22} className="text-slate-800" />
  </button>
) : (
  <button
    className="p-2 rounded-md hover:bg-slate-100"
    onClick={() => onWidthChange(64)}
  >
    <img src={sidebaricon.src} alt="Collapse" className="w-4 h-4" />
  </button>
)}

          </div>

          <div className="border-b border-slate-200" />

          <div className="px-6 pt-8 ">
       <FileUpload
  uploadEndpoint={uploadEndpoint}
  notebookId={notebookId}
  onUploadSuccess={handleUploadSuccess}
  isCollapsedSidebar={false}
  triggerRef={uploadTriggerRef}
/>
          </div>

          {sources.length > 0 && (
            <div className="flex items-center justify-between px-5 pt-8 pb-2">
              <span className="text-sm font-medium text-slate-700">
                Select all sources
              </span>

              <button
                onClick={(e) => {
                  e.stopPropagation();
                  selectAllToggle();
                }}
                className="p-1"
              >
                <img
                  src={selectAllIconSrc}
                  alt="select all"
                  className="w-5 h-5 cursor-pointer"
                />
              </button>
            </div>
          )}
        </>
      )}

      <div className="flex-1 overflow-y-auto pt-2 space-y-1">
 {sources.map((item) => (
  <SourceItem
    key={item.filename}
    item={item}
    checked={checkedPdfs.includes(item.filename)}
    onToggle={toggleChecked}
    isCollapsedSidebar={width < 150}
    onClick={() => handleFileSelect(item.filename)}
    onDelete={handleDeletePdf}
  />
))}

      </div>

      {width >= 150 && (
        <div className="px-6 py-5 ">
          <button 
            onClick={() => window.location.href = '/policybot/notebook'}
            className="w-full h-11 rounded-lg border border-black/40 text-sm text-black/70 hover:bg-slate-100 transition"
          >
            Explore collections 
          </button>
        </div>
      )}

   {typeof window !== "undefined" && window.innerWidth >= 768 && (
  <div
    ref={handleRef}
    className="absolute top-0 right-0 h-full w-2 cursor-ew-resize z-20"
    onMouseDown={startResizing}
    style={{ userSelect: "none" }}
  />
)}
    </aside>
  );
};

export default LeftSidebar;
