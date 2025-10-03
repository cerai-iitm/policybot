"use client";
import LeftSidebar from "@/components/leftSidebar/LeftSidebar";
import { useState } from "react";

export default function Home() {
  const sidebarWidth = 256;
  const [leftSidebarWidth, setLeftSidebarWidth] = useState(sidebarWidth);
  const [checkedPdfs, setCheckedPdfs] = useState<string[]>([]);

  return (
    <main className="flex h-screen">
      {/* Left Sidebar */}
      <div style={{ width: leftSidebarWidth, minWidth: leftSidebarWidth }}>
        <LeftSidebar
          width={leftSidebarWidth}
          onWidthChange={setLeftSidebarWidth}
          checkedPdfs={checkedPdfs}
          setCheckedPdfs={setCheckedPdfs}
        />
      </div>
    </main>
  );
}
