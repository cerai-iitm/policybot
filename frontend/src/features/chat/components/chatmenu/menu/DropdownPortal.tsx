"use client";

import React, { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

interface Props {
  anchorRef: React.RefObject<HTMLElement | null>;
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

const DropdownPortal: React.FC<Props> = ({
  anchorRef,
  open,
  onClose,
  children,
}) => {
  const menuRef = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState({ top: 0, left: 0 });

  // 📌 Positioning
  useEffect(() => {
    if (open && anchorRef.current) {
      const rect = anchorRef.current.getBoundingClientRect();

      const DROPDOWN_WIDTH = 220;

setPos({
  top: rect.bottom + 6,
  left: rect.right - DROPDOWN_WIDTH,
});
    }
  }, [open, anchorRef]);

  // 📌 Outside click + ESC
  useEffect(() => {
    if (!open) return;

    const handleClick = (e: MouseEvent) => {
      if (
        menuRef.current &&
        !menuRef.current.contains(e.target as Node) &&
        anchorRef.current &&
        !anchorRef.current.contains(e.target as Node)
      ) {
        onClose();
      }
    };

    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };

    window.addEventListener("mousedown", handleClick);
    window.addEventListener("keydown", handleEsc);

    return () => {
      window.removeEventListener("mousedown", handleClick);
      window.removeEventListener("keydown", handleEsc);
    };
  }, [open, onClose, anchorRef]);

  if (!open || typeof window === "undefined") return null;

  return createPortal(
    <div
      ref={menuRef}
      style={{
        position: "fixed",
        top: pos.top,
        left: pos.left,
      }}
      className="z-9999 animate-fadeIn"
    >
      {children}
    </div>,
    document.body
  );
};

export default DropdownPortal;