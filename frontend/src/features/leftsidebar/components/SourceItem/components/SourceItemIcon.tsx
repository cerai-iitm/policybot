"use client";

import React, { useRef } from "react";
import { FiMoreVertical, FiTrash2, FiEdit2 } from "react-icons/fi";
import Image from "next/image";

import docicon from "@/assets/doc.png";
import DropdownPortal from "@/features/leftsidebar/components/SourceItem/menu/DropdownPortal";
import DropdownMenu, { DropdownItem } from "@/features/leftsidebar/components/SourceItem/menu/DropdownMenu";

interface Props {
  isHovered: boolean;
  showMenu: boolean;
  onMenuToggle: (e: React.MouseEvent) => void;
  onDeleteClick: () => void;
  onMenuClose: () => void;
}

const SourceItemIcon: React.FC<Props> = ({
  showMenu,
  onMenuToggle,
  onDeleteClick,
  onMenuClose
}) => {
  const buttonRef = useRef<HTMLButtonElement>(null);

const menuItems: DropdownItem[] = [
  {
    label: "Delete",
    icon: <FiTrash2 size={16} />, // ✅ icon added
    onClick: onDeleteClick,
    className: "text-red-600 hover:bg-red-50",
  },

  // 👉 Future ready
  {
    label: "Rename",
    icon: <FiEdit2 size={16} />,
    onClick: () => {},
    className: "text-slate-700",
  },
];

  return (
    <>
      {/* BUTTON */}
      <div className="relative group">
        <button
          ref={buttonRef}
          aria-label="menu"
          onClick={onMenuToggle}
          className="w-8 h-8 flex items-center justify-center rounded hover:bg-slate-200"
        >
          <span className="group-hover:hidden">
            <Image src={docicon} alt="document" width={16} height={16} />
          </span>

          <span className="hidden group-hover:block">
            <FiMoreVertical size={18} />
          </span>
        </button>
      </div>

      {/* MENU */}
      <DropdownPortal
        anchorRef={buttonRef}
        open={showMenu}
        onClose={onMenuClose} 
      >
        <DropdownMenu items={menuItems} />
      </DropdownPortal>
    </>
  );
};

export default SourceItemIcon;