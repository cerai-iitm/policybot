"use client";

import React, { useState } from "react";
import { usePathname } from "next/navigation";
import { AdminProvider } from "./AdminContext";
import LeftSidebar from "@/components/leftSidebar/LeftSidebar";
import ChatSection from "@/components/chat/ChatSection";
import RightSidebar from "@/components/RightSidebar/RightSidebar";
import { SidebarItem } from "@/components/leftSidebar/LeftSidebar";

interface MainLayoutProps {
  isAdmin?: boolean;
}

export default function MainLayout({ isAdmin: isAdminProp }: MainLayoutProps) {
  const pathname = usePathname();
  const isAdmin = isAdminProp ?? (pathname?.endsWith("/config") ?? false);

  const sidebarWidth = 256;
  const [leftSidebarWidth, setLeftSidebarWidth] = useState(sidebarWidth);
  const [rightSidebarWidth, setRightSidebarWidth] = useState(320);

  const [showRightSidebar, setShowRightSidebar] = useState(false);
  const [checkedPdfs, setCheckedPdfs] = useState<string[]>([]);
  const [isPDFEnabled, setIsPDFEnabled] = useState(false);
  const [selectedFilename, setSelectedFilename] = useState<string | null>(null);
  const [sources, setSources] = useState<SidebarItem[]>([]);

  const handleFileSelect = (filename: string) => {
    setSelectedFilename(filename);
    setIsPDFEnabled(true);
    if (!showRightSidebar) {
      setShowRightSidebar(true);
      setRightSidebarWidth(320);
    }
  };

  return (
    <AdminProvider isAdmin={isAdmin}>
      <main className="flex h-screen bg-bg-light text-text text-sm">
        {/* Left Sidebar */}
        <div className="h-full" style={{ width: leftSidebarWidth, minWidth: leftSidebarWidth }}>
          <LeftSidebar
            width={leftSidebarWidth}
            onWidthChange={setLeftSidebarWidth}
            checkedPdfs={checkedPdfs}
            setCheckedPdfs={setCheckedPdfs}
            sources={sources}
            setSources={setSources}
            selectedFilename={selectedFilename}
            setSelectedFilename={setSelectedFilename}
            setIsPDFEnabled={setIsPDFEnabled}
            setShowRightSidebar={setShowRightSidebar}
            onFileSelect={handleFileSelect}
          />
        </div>

        {/* Middle Chat Section - Takes remaining space */}
        <div className="flex-1 min-w-0 h-full flex flex-col">
          <ChatSection checkedPdfs={checkedPdfs} sources={sources} />
        </div>

        {/* Right Sidebar */}
        {showRightSidebar && (
          <div className="h-full" style={{ width: rightSidebarWidth, minWidth: rightSidebarWidth }}>
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
    </AdminProvider>
  );
}