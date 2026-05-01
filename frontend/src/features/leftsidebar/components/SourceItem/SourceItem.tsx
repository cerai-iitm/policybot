"use client";

import React, { useState } from "react";
import SourceItemUI from "./SourceItemUI";

interface SourceItemData {
  pdf_id: string;
  filename: string;
  processing_status?: string;
}


interface Props {
  item: SourceItemData;
  checked: boolean;
  onToggle: (id: string) => void;
  onDelete?: (id: string) => void;
  onClick?: () => void;
  isCollapsedSidebar?: boolean;
}

const SourceItem: React.FC<Props> = ({
  item,
  checked,
  onToggle,
  onClick,
  isCollapsedSidebar,
  onDelete,
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  const filename = item.filename || "";

  const isLongName = filename.length > 22;

 const getDisplayName = (name: string) => {
  const isLong = name.length > 22;

  if (!isLong) return name;

  const lastDot = name.lastIndexOf(".");
  if (lastDot === -1) {
    return name.slice(0, 18) + "...";
  }

  const base = name.slice(0, lastDot);
  const ext = name.slice(lastDot);

  return `${base.slice(0, 16)}...${ext}`;
};

  return (
    <SourceItemUI
    
      filename={filename}
      isLongName={isLongName}
      displayName={getDisplayName(filename)}
      isHovered={isHovered}
      showMenu={showMenu}
      checked={checked}
      isCollapsedSidebar={isCollapsedSidebar}

      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}

      onMainClick={onClick}
      onToggle={() => onToggle(item.pdf_id)}

      onMenuToggle={(e) => {
  e.stopPropagation();
  setShowMenu(true);   // ✅ ALWAYS OPEN
}}

      onMenuClose={() => setShowMenu(false)}

      onDeleteClick={() => {
  setShowMenu(false);
  onDelete?.(item.pdf_id);

}}
     processingStatus={item.processing_status}
    />

    
  );
};

export default SourceItem;