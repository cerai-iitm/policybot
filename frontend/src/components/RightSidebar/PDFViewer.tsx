"use client";
import React from "react";

interface PDFViewerProps {
  filename: string | null;
}

const PDFViewer: React.FC<PDFViewerProps> = ({ filename }) => {
  if (!filename) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        Select a PDF to view
      </div>
    );
  }

  // TODO: Re-enable PDF viewer when ready
  // const fileUrl = `pdf/view/${encodeURIComponent(filename)}`;

  return (
    <div className="w-full flex-1 min-h-0 flex flex-col items-center overflow-auto">
      {/* PDF viewer disabled - to be implemented */}
      {/* <embed
        src={fileUrl}
        type="application/pdf"
        width="100%"
        height="100%"
        style={{ border: "none" }}
      /> */}
    </div>
  );
};

export default PDFViewer;
