"use client";

import React from "react";
import { FiMoreVertical } from "react-icons/fi";
import Image from "next/image";

import docicon from "@/assets/doc.png";

import SourceItemIcon from "./components/SourceItemIcon";
import SourceItemFilename from "./components/SourceItemFilename";
import SourceItemCheckbox from "./components/SourceItemCheckbox";

interface UIProps {
  filename: string;
  isLongName: boolean;
  displayName: string;

  isHovered: boolean;
  showMenu: boolean;
  checked: boolean;
  isCollapsedSidebar?: boolean;

  onMouseEnter: () => void;
  onMouseLeave: () => void;

  onMainClick?: () => void;
  onToggle: () => void;

  onMenuToggle: (e: React.MouseEvent) => void;
  onDeleteClick: () => void;
  onMenuClose: () => void;
}

const SourceItemUI: React.FC<UIProps> = (props) => {
  const {
    filename,
    isLongName,
    displayName,
    isHovered,
    showMenu,
    checked,
    isCollapsedSidebar,
    onMouseEnter,
    onMouseLeave,
    onMainClick,
    onToggle,
    onMenuToggle,
    onDeleteClick,
    onMenuClose
  } = props;

  /* COLLAPSED */
if (isCollapsedSidebar) {
  return (
    <div
      className="flex justify-center items-center p-2"
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      onClick={onMainClick}
    >
      <SourceItemIcon
        isHovered={isHovered}
        showMenu={showMenu}
        onMenuToggle={onMenuToggle}
        onDeleteClick={onDeleteClick}
        onMenuClose={onMenuClose}
      />
    </div>
  );
}

  return (
    <>
      <style jsx>{`
  @keyframes marqueeScroll {
    0% { transform: translateX(0); }
    100% { transform: translateX(-100%); }
  }

  :global(.marquee) {
    display: inline-block;
    white-space: nowrap;
  }

  :global(.group:hover .animate-marquee) {
    animation: marqueeScroll 8s linear infinite;
  }
`}</style>

      <div
        className="group h-12 px-6 rounded-lg flex items-center justify-between hover:bg-slate-100 overflow-visible"
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
        onClick={onMainClick}
      >
        <div className="flex items-center gap-3 min-w-0 flex-1 overflow-hidden">
          
          <SourceItemIcon
            isHovered={isHovered}
            showMenu={showMenu}
            onMenuToggle={onMenuToggle}
            onDeleteClick={onDeleteClick}
            onMenuClose={onMenuClose}
          />

          <SourceItemFilename
            filename={filename}
            displayName={displayName}
            isLongName={isLongName}
            onToggle={onToggle}
          />
        </div>

        <SourceItemCheckbox
          checked={checked}
          onToggle={onToggle}
        />
      </div>
    </>
  );
};

export default SourceItemUI;