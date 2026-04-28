"use client";

import React from "react";
import Image, { StaticImageData } from "next/image";

interface BaseSideContainerProps {
  title: string;
  icon?: StaticImageData | string;
  children: React.ReactNode;
  className?: string;

  collapsed?: boolean;          // ✅ NEW
  onToggle?: () => void;        // ✅ NEW

  rightAction?: React.ReactNode;
}

const BaseSideContainer: React.FC<BaseSideContainerProps> = ({
  title,
  icon,
  children,
  className = "",
  collapsed = false,
  onToggle,
  rightAction,
}) => {
  return (
    <section
      className={`h-full rounded-2xl bg-white overflow-hidden flex flex-col transition-all duration-300 ${className}`}
    >
      {/* HEADER */}
      <div
        className={`
          ${collapsed ? "h-14.5 justify-center px-2" : "h-14.5 px-6 justify-between"}
          flex items-center border-b border-[#EEF1F4]
        `}
      >
        {!collapsed && (
          <h2 className="text-[15px] font-medium text-[#1F2937]">
            {title}
          </h2>
        )}

        {/* RIGHT ACTION / TOGGLE */}
        {onToggle && icon && (
          <button
            aria-label={`${title} toggle`}
            onClick={onToggle}
            className="hover:opacity-80 transition"
          >
            <Image
              src={icon}
              alt="toggle"
              width={16}
              height={16}
            />
          </button>
        )}

        {!onToggle && rightAction && rightAction}
      </div>

      {/* BODY */}
      {!collapsed && (
        <div className="flex-1 overflow-hidden">
          {children}
        </div>
      )}
    </section>
  );
};

export default BaseSideContainer;