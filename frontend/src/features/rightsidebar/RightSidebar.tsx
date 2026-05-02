"use client";

import React, { useRef, useState } from "react";
import sidebaricon from "@/assets/sidebar.png";

import BaseSideContainer from "@/features/layout/components/BaseSideContainer";
import CitationCard from "./components/CitationCard";
import Image from "next/image";
import citation from "@/assets/greycitation.png";
import TooltipPortal from "./components/TooltipPortal"; // ✅ IMPORT

interface Props {
  collapsed: boolean;
  onToggleCollapse: () => void;
  citations: any[];
  onOpen: () => void;
}

const RightSidebar: React.FC<Props> = ({
  collapsed,
  onToggleCollapse,
  citations,
  onOpen
}) => {
  const iconRef = useRef<HTMLDivElement>(null);
  const [hovered, setHovered] = useState(false);

  return (
    <BaseSideContainer
      title="Citations"
      icon={sidebaricon}
      collapsed={collapsed}
      onToggle={onToggleCollapse}
    >
      <div
        className={`h-full overflow-y-auto custom-scrollbar ${
          collapsed
            ? "flex flex-col items-center gap-3 py-4"
            : "p-4"
        }`}
      >
        {/* ✅ EMPTY STATE (EXPANDED) */}
        {!collapsed && citations.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center px-6">
            <p className="text-sm text-slate-500">
              No citations yet
            </p>
            <p className="text-sm text-slate-400 mt-1">
              Ask a question to see referenced sources here
            </p>
          </div>
        )}

        {/* ✅ COLLAPSED EMPTY STATE (🔥 FIXED WITH PORTAL) */}
        {collapsed && citations.length === 0 && (
          <div className="flex flex-col h-full items-center">
            <div
              ref={iconRef}
              className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center cursor-default"
              onMouseEnter={() => setHovered(true)}
              onMouseLeave={() => setHovered(false)}
            >
              <Image
                src={citation}
                alt="citation"
                width={14}
                height={14}
                className="opacity-50"
              />
            </div>

            {/* ✅ TOOLTIP VIA PORTAL */}
            <TooltipPortal anchorRef={iconRef} open={hovered}>
              <div className="text-xs bg-black text-white px-2 py-1 rounded shadow">
                Citations
              </div>
            </TooltipPortal>
          </div>
        )}

        {/* ✅ LIST */}
        {!(collapsed && citations.length === 0) && (
          <div className="space-y-4">
            {citations.map((item, index) => (
              <CitationCard
                key={index}
                title={item.original_filename || "Document"}
                subtitle="Referenced document"
                pageNo={item.page_number || "-"}
                content={item.text}
                collapsed={collapsed}
                 onClick={onOpen}
              />
            ))}
          </div>
        )}
      </div>
    </BaseSideContainer>
  );
};

export default RightSidebar;