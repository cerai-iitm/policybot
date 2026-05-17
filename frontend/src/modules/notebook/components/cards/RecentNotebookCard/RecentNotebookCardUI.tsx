"use client";

import React from "react";
import { MoreVertical } from "lucide-react";
import { useAuth } from "@/lib/hooks/useAuth";

type Props = {
  title: string;
  desc: string;
  createdAt: string;
  sourceCount: number;
  onCardClick?: () => void;
  onMenuClick?: (
    e: React.MouseEvent
  ) => void;
  buttonRef?: React.RefObject<
    HTMLButtonElement | null
  >;
};

const RecentNotebookCardUI: React.FC<Props> = ({
  title,
  createdAt,
  sourceCount,
  onCardClick,
  onMenuClick,
  buttonRef,
}) => {
  const { isDemoUser } = useAuth();

  // ✅ Format date
  const formattedDate =
    new Date(createdAt).toLocaleDateString(
      "en-US",
      {
        month: "short",
        day: "numeric",
        year: "numeric",
      }
    );

  return (
    <div
      onClick={onCardClick}
      className="
        w-full

        md:grid
        md:grid-cols-[1.8fr_0.8fr_0.8fr_40px]
        md:items-center
        md:gap-6

        flex
        items-center
        justify-between

        px-4 md:px-6
        py-4 md:py-5

        border-b
        border-[#F1F5F9]

        hover:bg-[#F8FAFC]
        transition
        cursor-pointer
      "
    >
      {/* MOBILE TITLE */}
      <div
        className="
          flex-1
          min-w-0

          text-[14px]
          md:text-[17px]

          font-normal
          text-black

          truncate
        "
      >
        {title}
      </div>

      {/* DESKTOP SOURCES */}
      <div
        className="
          hidden md:block

          text-[16px]
          text-gray-700
          whitespace-nowrap
        "
      >
        {sourceCount}{" "}
        {sourceCount === 1
          ? "Source"
          : "Sources"}
      </div>

      {/* DESKTOP CREATED */}
      <div
        className="
          hidden md:block

          text-[16px]
          text-gray-700
          whitespace-nowrap
        "
      >
        {formattedDate}
      </div>

      {/* MENU */}
      <div className="flex justify-end shrink-0">
        {!isDemoUser && (
          <button
            ref={buttonRef}
            onClick={onMenuClick}
            className="
              p-2
              rounded-md
              text-gray-500
              hover:bg-gray-200
              transition
            "
            aria-label="More options"
          >
            <MoreVertical size={18} />
          </button>
        )}
      </div>
    </div>
  );
};

export default RecentNotebookCardUI;