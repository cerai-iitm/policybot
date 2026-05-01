"use client";

import React, { useRef } from "react";
import { HiOutlineDotsVertical } from "react-icons/hi";
import { FiTrash2 } from "react-icons/fi";

import DropdownPortal from "@/features/chat/components/chatmenu/menu/DropdownPortal";
import DropdownMenu, {
  DropdownItem,
} from "@/features/chat/components/chatmenu/menu/DropdownMenu";

interface Props {
  open: boolean;
  onToggle: (e: React.MouseEvent) => void;
  onClose: () => void;
  onDeleteChat: () => void;
}

const ChatMenu: React.FC<Props> = ({
  open,
  onToggle,
  onClose,
  onDeleteChat,
}) => {
  const buttonRef = useRef<HTMLButtonElement>(null);

  const menuItems: DropdownItem[] = [
    {
      label: "Delete chat history",
      icon: <FiTrash2 size={16} />,
      onClick: onDeleteChat,
      className: "text-red-600 hover:bg-red-50",
    },
  ];

  return (
    <>
      {/* BUTTON */}
      <button
        ref={buttonRef}
        aria-label="Chat menu"
        onClick={onToggle}
        className="
          w-8 h-8
          flex items-center justify-center
          rounded-lg
          text-slate-500
          hover:bg-slate-100
          hover:text-slate-700
          transition
        "
      >
        <HiOutlineDotsVertical size={18} />
      </button>

      {/* MENU */}
      <DropdownPortal
        anchorRef={buttonRef}
        open={open}
        onClose={onClose}
      >
        <DropdownMenu items={menuItems} />
      </DropdownPortal>
    </>
  );
};

export default ChatMenu;