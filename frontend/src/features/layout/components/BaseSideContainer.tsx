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
  showMobileHeader?: boolean;
}

const BaseSideContainer: React.FC<BaseSideContainerProps> = ({
  title,
  icon,
  children,
  className = "",
  collapsed = false,
  onToggle,
  rightAction,
  showMobileHeader = false,
}) => {
  return (
    <section
      className={`h-full md:rounded-2xl bg-white overflow-hidden flex flex-col transition-all duration-300 ${className}`}
    >
      {/* HEADER */}
      <div
        className={`
          ${
            showMobileHeader
              ? "flex"
              : "hidden"
          }

          md:flex

         ${
  collapsed
    ? "h-14.5 justify-center px-2"
    : `
        
        px-4 md:px-6

        ${
          showMobileHeader
            ? "h-12 md:h-14.5 justify-end md:justify-between"
            : " h-14.5 justify-between"
        }
      `
}

          items-center
          border-b
          border-[#EEF1F4]
        `}
      >
      {!collapsed && (
  <h2
    className={`
      text-[15px]
      font-medium
      text-[#1F2937]

      ${
        showMobileHeader
          ? "hidden md:block"
          : ""
      }
    `}
  >
    {title}
  </h2>
)}

        {/* RIGHT ACTION / TOGGLE */}
        {onToggle && icon && (
          <button
            aria-label={`${title} toggle`}
            onClick={onToggle}
            className="hover:opacity-80 transition cursor-pointer"
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
     
        <div className="flex-1 overflow-hidden">
          {children}
        </div>
    
    </section>
  );
};

export default BaseSideContainer;