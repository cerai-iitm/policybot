"use client";
import { useIsMobile } from "@/hooks/useIsMobile";
import React, { useState, useRef } from "react";
import { usePathname } from "next/navigation";
import { AdminProvider } from "./AdminContext";
import LeftSidebar from "@/components/leftSidebar/LeftSidebar";
import ChatSection from "@/components/chat/ChatSection";

import { SidebarItem } from "@/components/leftSidebar/LeftSidebar";

interface MainLayoutProps {
  isAdmin?: boolean;
}

export default function MainLayout({ isAdmin: isAdminProp }: MainLayoutProps) {
  const isMobile = useIsMobile();
  const pathname = usePathname();
  const isAdmin = isAdminProp ?? (pathname?.endsWith("/config") ?? false);

  const sidebarWidth = 256;

  const [leftSidebarWidth, setLeftSidebarWidth] = useState(sidebarWidth);
  const [rightSidebarWidth, setRightSidebarWidth] = useState(320);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);


  const [showRightSidebar, setShowRightSidebar] = useState(false);
  const [checkedPdfs, setCheckedPdfs] = useState<string[]>([]);
  const [isPDFEnabled, setIsPDFEnabled] = useState(false);
  const [selectedFilename, setSelectedFilename] = useState<string | null>(null);
  const [sources, setSources] = useState<SidebarItem[]>([]);
  const uploadTriggerRef = useRef<(() => void) | undefined>(undefined);


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

    {/* LEFT SIDEBAR – DESKTOP ONLY */}
    {!isMobile && (
      <div
        className="h-full"
        style={{ width: leftSidebarWidth, minWidth: leftSidebarWidth }}
      >
        <LeftSidebar
          width={leftSidebarWidth}
          defaultWidth={sidebarWidth}
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
            onExposeUploadTrigger={(fn) => {
    uploadTriggerRef.current = fn;
  }}
        />
      </div>
    )}

    {/* LEFT SIDEBAR – MOBILE DRAWER (FIXED OVERLAY) */}
    {isMobile && (
      <>
        {/* Backdrop */}
        {mobileSidebarOpen && (
          <div
            className="fixed inset-0 bg-black/40 z-40"
            onClick={() => setMobileSidebarOpen(false)}
          />
        )}

        {/* Drawer */}
        <div
          className={`
            fixed top-0 left-0 h-full w-[280px] bg-slate-50 z-50
            transform transition-transform duration-300 ease-in-out
            ${mobileSidebarOpen ? "translate-x-0" : "-translate-x-full"}
          `}
        >
          <LeftSidebar
            width={280}
            defaultWidth={280}
            onWidthChange={() => {}}
            checkedPdfs={checkedPdfs}
            setCheckedPdfs={setCheckedPdfs}
            sources={sources}
            setSources={setSources}
            selectedFilename={selectedFilename}
            setSelectedFilename={(name) => {
              setSelectedFilename(name);
              setMobileSidebarOpen(false);
            }}
            setIsPDFEnabled={setIsPDFEnabled}
            setShowRightSidebar={setShowRightSidebar}
            onFileSelect={(filename) => {
              handleFileSelect(filename);
              setMobileSidebarOpen(false);
            }}
            isMobile
            onMobileClose={() => setMobileSidebarOpen(false)}
              onExposeUploadTrigger={(fn) => {
    uploadTriggerRef.current = fn;
  }}
          />
        </div>
      </>
    )}

    {/* CHAT SECTION */}
    <div className="flex-1 min-w-0 h-full flex flex-col">
      <ChatSection
        checkedPdfs={checkedPdfs}
        sources={sources}
        onOpenSidebar={() => setMobileSidebarOpen(true)}
          onAttach={() => {
    if (isMobile) setMobileSidebarOpen(true);
    uploadTriggerRef.current?.();
  }}
      />
    </div>

  </main>
</AdminProvider>

  );
}