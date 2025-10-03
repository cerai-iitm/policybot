"use client";
import LeftSidebar from "@/components/leftSidebar/LeftSidebar";
import { useState } from "react";
import ChatSection from "@/components/chat/ChatSection";
import RightSidebar from "@/components/RightSidebar/RightSidebar";

export default function Home() {
  const sidebarWidth = 256;
  const [leftSidebarWidth, setLeftSidebarWidth] = useState(sidebarWidth);
  const [rightSidebarWidth, setRightSidebarWidth] = useState(320);

  const [showRightSidebar, setShowRightSidebar] = useState(false);
  const [checkedPdfs, setCheckedPdfs] = useState<string[]>([]);
  const [isPDFEnabled, setIsPDFEnabled] = useState(false);
  const [selectedFilename, setSelectedFilename] = useState<string | null>(null);

  return (
    <main className="flex h-screen">
      {/* Left Sidebar */}
      <div style={{ width: leftSidebarWidth, minWidth: leftSidebarWidth }}>
        <LeftSidebar
          width={leftSidebarWidth}
          onWidthChange={setLeftSidebarWidth}
          checkedPdfs={checkedPdfs}
          setCheckedPdfs={setCheckedPdfs}
          onFileSelect={(filename) => {
            setSelectedFilename(filename); // Update the filename
            setIsPDFEnabled(true); // Enable the PDF viewer
            if (!showRightSidebar) {
              setShowRightSidebar(true);
              setRightSidebarWidth(320); // Reset only if sidebar was closed
            }
          }}
        />
      </div>

      {/* Middle Chat Section - Takes remaining space */}
      <div className="flex-1 min-w-0">
        <ChatSection checkedPdfs={checkedPdfs} />
      </div>

      {/* Right Sidebar */}
      {showRightSidebar && (
        <div style={{ width: rightSidebarWidth, minWidth: rightSidebarWidth }}>
          <RightSidebar
            width={rightSidebarWidth}
            onWidthChange={setRightSidebarWidth}
            onClose={() => setShowRightSidebar(false)}
            isPDFEnabled={isPDFEnabled}
            selectedFilename={selectedFilename}
          />
        </div>
      )}
    </main>
  );
}
