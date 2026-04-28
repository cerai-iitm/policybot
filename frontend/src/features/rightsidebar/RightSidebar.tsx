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
      {!collapsed && (
        <div className="h-full p-4 overflow-y-auto space-y-4">
          
          {mockCitations.map((item) => (
            <CitationCard
              key={item.id}
              title={item.title}
              subtitle={item.subtitle}
              pageNo={item.pageNo}
              content={item.content}
            />
          ))}

        </div>
      )}
    </BaseSideContainer>
  );
};

export default RightSidebar;