"use client";

import React from "react";
import sidebaricon from "@/assets/sidebar.png";

import BaseSideContainer from "@/features/layout/components/BaseSideContainer";
import CitationCard from "./components/CitationCard";
import { mockCitations } from "./data/mockCitations";

interface Props {
  collapsed: boolean;
  onToggleCollapse: () => void;
}

const RightSidebar: React.FC<Props> = ({
  collapsed,
  onToggleCollapse,
}) => {
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
            : "p-4 space-y-4"
        }`}
      >
        {mockCitations.map((item) => (
          <CitationCard
            key={item.id}
            title={item.title}
            subtitle={item.subtitle}
            pageNo={item.pageNo}
            content={item.content}
            collapsed={collapsed}
          />
        ))}
      </div>
    </BaseSideContainer>
  );
};

export default RightSidebar;