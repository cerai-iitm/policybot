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
  if (!open) return;

  const update = () => {
    if (!anchorRef.current) return;

    const rect = anchorRef.current.getBoundingClientRect();

    const tooltipWidth = 180;
    const padding = 8;

    let left = rect.left + rect.width / 2;

    const minLeft = tooltipWidth / 2 + padding;
    const maxLeft = window.innerWidth - tooltipWidth / 2 - padding;

    if (left < minLeft) left = minLeft;
    if (left > maxLeft) left = maxLeft;

    setPos({
      top: rect.top - 8,
      left,
    });
  };

  window.addEventListener("scroll", update);
  window.addEventListener("resize", update);

  return () => {
    window.removeEventListener("scroll", update);
    window.removeEventListener("resize", update);
  };
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