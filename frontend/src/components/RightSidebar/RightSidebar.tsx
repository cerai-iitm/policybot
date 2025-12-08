"use client";
import React, { useRef, useState } from "react";
import { FiX } from "react-icons/fi";
import dynamic from "next/dynamic";
const PDFViewer = dynamic(() => import("./PDFViewer"), { ssr: false });
const Summary = dynamic(() => import("./Summary"), { ssr: false });

interface RightSidebarProps {
  width: number;
  onWidthChange: (width: number) => void;
  onClose: () => void;
  isPDFEnabled?: boolean;
  selectedFilename?: string | null;
}

const RightSidebar: React.FC<RightSidebarProps> = ({
  width,
  onWidthChange,
  onClose,
  isPDFEnabled,
  selectedFilename,
}) => {
  const [resizing, setResizing] = useState(false);
  const handleRef = useRef<HTMLDivElement>(null);

  // Resizing right didebar
  const startResizing = (e: React.MouseEvent) => {
    e.preventDefault();
    setResizing(true);
    const startX = e.clientX;
    const startWidth = width;
    let latestWidth = startWidth;

    const onMouseMove = (moveEvent: MouseEvent) => {
      const newWidth = Math.min(
        window.innerWidth / 3,
        Math.max(64, startWidth - (moveEvent.clientX - startX)),
      );
      onWidthChange(newWidth);
      latestWidth = newWidth;
    };

    const onMouseUp = () => {
      if (!(width < 150) && latestWidth <= 150) {
        onClose();
      }
      document.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("mouseup", onMouseUp);
      setResizing(false);
    };

    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", onMouseUp);
  };

  return (
    <div
      className={`h-full bg-bg-dark p-4 relative ${
        !resizing ? "transition-all duration-300" : ""
      }`}
      style={{ width }}
    >
      {/* Close Icon at Top-Right */}
      <FiX
        className="absolute top-2 right-2 text-black cursor-pointer m-2"
        size={24}
        onClick={onClose}
      />

      {/* PDF Viewer or Placeholder, always below the close icon */}
      <div className="pt-10 h-full w-full flex flex-col items-center">
        {isPDFEnabled && selectedFilename ? (
          <>
            <Summary filename={selectedFilename} />
            <PDFViewer filename={selectedFilename} />
          </>
        ) : (
          <div className="placeholder">Select a PDF to view</div>
        )}
      </div>

      {/* Resize Handle */}
      <div
        ref={handleRef}
        className="absolute top-0 left-0 h-full w-2 cursor-ew-resize z-20"
        onMouseDown={startResizing}
        aria-label="Resize right sidebar"
        style={{ userSelect: "none" }}
      />
    </div>
  );
};

export default RightSidebar;
