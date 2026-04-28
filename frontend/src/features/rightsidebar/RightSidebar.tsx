// FILE: D:\buddi\Policybot\frontend\src\features\rightsidebar\RightSidebar.tsx

"use client";

import React from "react";
import sidebaricon from "@/assets/sidebar.png";

import BaseSideContainer from "@/features/layout/components/BaseSideContainer";

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
        <div className="h-full p-5 overflow-y-auto">
          <div className="h-full rounded-2xl bg-[#F4F6F8] border border-[#E7EBF0] flex items-center justify-center">
            <p className="text-sm text-[#94A3B8]">
              Citation container placeholder
            </p>
          </div>
        </div>
      )}
    </BaseSideContainer>
  );
};

export default RightSidebar;