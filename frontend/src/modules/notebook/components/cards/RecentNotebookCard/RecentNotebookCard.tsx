"use client";

import { useRef, useState } from "react";
import { FiTrash2, FiEdit2 } from "react-icons/fi";

import NotebookDropdownPortal from "../../menu/NotebookDropdownPortal";
import NotebookDropdownMenu, {
  NotebookDropdownItem,
} from "../../menu/NotebookDropdownMenu";

import RecentNotebookCardUI from "./RecentNotebookCardUI";

type Props = {
  title: string;
  desc: string;
  createdAt: string;
  sourceCount: number; // ✅ ADD
  onClick?: () => void;
  onRename?: () => void;
  onDelete?: () => void;
};

const RecentNotebookCard = ({
  title,
  desc,
  createdAt,
  sourceCount,
  onClick,
  onRename,
  onDelete
}: Props) => {
  const [open, setOpen] = useState(false);
  const buttonRef = useRef<HTMLButtonElement>(null);

  const handleMenuToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    setOpen((prev) => !prev);
  };

const menuItems: NotebookDropdownItem[] = [
  {
    label: "Rename",
    icon: <FiEdit2 size={16} />,
    onClick: () => {
      onRename?.()
      setOpen(false)
    },
  },
  {
    label: "Delete",
    icon: <FiTrash2 size={16} />,
    onClick: () => {
      onDelete?.()
      setOpen(false)
    },
    className: "text-red-600 hover:bg-red-50",
  },
]

  return (
    <>
      <RecentNotebookCardUI
  title={title}
  desc={desc}
  createdAt={createdAt}
  sourceCount={sourceCount} // ✅ ADD
  onCardClick={onClick}
  onMenuClick={handleMenuToggle}
  buttonRef={buttonRef}
/>

      <NotebookDropdownPortal
        anchorRef={buttonRef}
        open={open}
        onClose={() => setOpen(false)}
      >
        <NotebookDropdownMenu items={menuItems} />
      </NotebookDropdownPortal>
    </>
  );
};

export default RecentNotebookCard;