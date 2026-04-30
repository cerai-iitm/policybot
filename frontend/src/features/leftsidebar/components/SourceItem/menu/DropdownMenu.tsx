"use client";

import React from "react";

export interface DropdownItem {
  label: string;
  onClick: () => void;
  icon?: React.ReactNode;   // ✅ NEW
  className?: string;
}

interface Props {
  items: DropdownItem[];
}

const DropdownMenu: React.FC<Props> = ({ items }) => {
  return (
    <div className="w-44 bg-white border rounded-lg shadow-md py-1">
      {items.map((item, index) => (
        <button
          key={index}
          onClick={item.onClick}
          className={`w-full flex items-center gap-3 px-4 py-2 text-sm hover:bg-slate-100 ${item.className || ""}`}
        >
          {/* ✅ ICON */}
          {item.icon && (
            <span className="text-base">{item.icon}</span>
          )}

          {/* ✅ TEXT */}
          <span>{item.label}</span>
        </button>
      ))}
    </div>
  );
};

export default DropdownMenu;