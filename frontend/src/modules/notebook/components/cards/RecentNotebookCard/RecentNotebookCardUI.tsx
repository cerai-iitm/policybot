"use client";

import React from "react";
import { MoreVertical } from "lucide-react";

type Props = {
  title: string;
  desc: string;
  createdAt: string;
  sourceCount: number; // ✅ ADD
  onCardClick?: () => void;
  onMenuClick?: (e: React.MouseEvent) => void;
  buttonRef?: React.RefObject<HTMLButtonElement | null>;
};

const RecentNotebookCardUI: React.FC<Props> = ({
  title,
  desc,
  createdAt,
  sourceCount,
  onCardClick,
  onMenuClick,
  buttonRef,
}) => {

  // 🔹 Format date → April 1, 2026
  const formattedDate = new Date(createdAt).toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  });

  // 🔹 Get initials (like "IN")
  const initials = title
    .split(" ")
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase();

  return (
    <div
      onClick={onCardClick}
      className="
        relative
        w-80 h-56
        rounded-2xl
        bg-[#f3f4f6]
        p-5
        flex flex-col justify-between
        cursor-pointer
        transition-all duration-300 ease-out
        hover:shadow-md
      "
    >
      {/* 🔹 TOP SECTION */}
      <div className="flex items-start justify-between">

        {/* INITIALS BLOCK */}
        <div className="text-3xl font-semibold text-gray-700 tracking-wide">
          {initials}
        </div>

        {/* MENU */}
        <button
          ref={buttonRef}
          onClick={onMenuClick}
          className="
            p-1.5 rounded-md
            text-gray-500
            hover:bg-gray-200
            transition
          "
          aria-label="More options"
        >
          <MoreVertical size={18} />
        </button>
      </div>

      {/* 🔹 BOTTOM CONTENT */}
      <div className="flex flex-col gap-2">

        <h3
          className="
            text-xl font-semibold text-gray-900
            leading-snug
            line-clamp-2
          "
        >
          {title}
        </h3>

        <p className="text-sm text-gray-600">
  {formattedDate} • {sourceCount} {sourceCount === 1 ? "source" : "sources"}
</p>

      </div>
    </div>
  );
};

export default RecentNotebookCardUI;