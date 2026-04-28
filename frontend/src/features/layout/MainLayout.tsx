"use client";

import React, { useState } from "react";
import { usePathname } from "next/navigation";

import Topbar from "@/features/topbar/Topbar";
import LeftSidebar from "@/features/leftsidebar/LeftSidebar";
import ChatView from "@/features/chat/ChatView";
import RightSidebar from "@/features/rightsidebar/RightSidebar";

import { AdminProvider } from "../chat/context/AdminContext";
import { SidebarItem } from "@/features/leftsidebar/types";
import { mockPdfs } from "@/features/leftsidebar/data/mockData";

interface MainLayoutProps {
  isAdmin?: boolean;
  notebookId?: string | null;
}

export default function MainLayout({
  isAdmin: isAdminProp,
}: MainLayoutProps) {
  const pathname = usePathname();

  const isAdmin =
    isAdminProp ?? (pathname?.endsWith("/config") ?? false);

  /* ---------------- STATE ---------------- */

  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);

  const [checkedPdfs, setCheckedPdfs] = useState<string[]>([]);
  const [selectedFilename, setSelectedFilename] =
    useState<string | null>(null);

  const [sources] = useState<SidebarItem[]>(mockPdfs);

  /* ---------------- HANDLERS ---------------- */

  const handleTogglePdf = (filename: string) => {
    setCheckedPdfs((prev) =>
      prev.includes(filename)
        ? prev.filter((f) => f !== filename)
        : [...prev, filename]
    );
  };

  const handleSelectPdf = (filename: string) => {
    setSelectedFilename(filename);
  };

  const handleDeletePdf = (_id: string, filename: string) => {
    setCheckedPdfs((prev) =>
      prev.filter((f) => f !== filename)
    );
  };

  const handleSelectAll = () => {
    const all = sources.map((s) => s.filename);

    const areAllSelected = all.every((file) =>
      checkedPdfs.includes(file)
    );

    setCheckedPdfs(areAllSelected ? [] : all);
  };

  /* ---------------- GRID WIDTH LOGIC ---------------- */

  const leftWidth = leftCollapsed ? "72px" : "285px";
  const rightWidth = rightCollapsed ? "72px" : "420px";

  const gridTemplate = `${leftWidth} 1fr ${rightWidth}`;

  /* ---------------- UI ---------------- */

  return (
    <AdminProvider isAdmin={isAdmin}>
      <div className="h-screen w-full bg-[#F1F5F9] flex flex-col overflow-hidden">

        <Topbar />

        <main className="flex-1 px-6 pb-5 overflow-hidden">
          <div
            className="h-full grid gap-3 transition-all duration-300"
            style={{ gridTemplateColumns: gridTemplate }}
          >

            {/* LEFT */}
            <LeftSidebar
              collapsed={leftCollapsed}
              onToggleCollapse={() =>
                setLeftCollapsed((prev) => !prev)
              }
              sources={sources}
              checkedPdfs={checkedPdfs}
              onTogglePdf={handleTogglePdf}
              onSelectPdf={handleSelectPdf}
              onDeletePdf={handleDeletePdf}
              onSelectAll={handleSelectAll}
            />

            {/* CENTER */}
            <ChatView />

            {/* RIGHT */}
            <RightSidebar
              collapsed={rightCollapsed}
              onToggleCollapse={() =>
                setRightCollapsed((prev) => !prev)
              }
            />

          </div>
        </main>
      </div>
    </AdminProvider>
  );
}