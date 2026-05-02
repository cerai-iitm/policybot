"use client";

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";

interface Props {
  anchorRef: React.RefObject<HTMLElement | null>;
  open: boolean;
  children: React.ReactNode;
}

export default function TooltipPortal({
  anchorRef,
  open,
  children,
}: Props) {
  const [pos, setPos] = useState({ top: 0, left: 0 });

  useEffect(() => {
    if (open && anchorRef.current) {
      const rect = anchorRef.current.getBoundingClientRect();

      setPos({
        top: rect.top - 8, // 👈 ABOVE element
        left: rect.left + rect.width / 2, // 👈 CENTER horizontally
      });
    }
  }, [open, anchorRef]);

  if (!open || typeof window === "undefined") return null;

  return createPortal(
    <div
      style={{
        position: "fixed",
        top: pos.top,
        left: pos.left,
        transform: "translate(-50%, -100%)", // 👈 center + move above
      }}
      className="z-9999"
    >
      {children}
    </div>,
    document.body
  );
}