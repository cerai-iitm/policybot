"use client";

import React from "react";

export interface NotebookDropdownItem {
  label: string;
  onClick: () => void;
  icon?: React.ReactNode;
  className?: string;
}

interface Props {
  items: NotebookDropdownItem[];
}

const NotebookDropdownMenu: React.FC<Props> = ({ items }) => {
  return (
    <div className="w-44 bg-white border border-gray-300 rounded-lg shadow-md py-1">
      {items.map((item, index) => (
        <button
          key={index}
          onClick={item.onClick}
          className={`w-full flex items-center gap-3 px-4 py-2 text-sm hover:bg-slate-100 ${item.className || ""}`}
        >
          {item.icon && <span className="text-base">{item.icon}</span>}
          <span>{item.label}</span>
        </button>
      ))}
    </div>
  );
};

export default NotebookDropdownMenu;