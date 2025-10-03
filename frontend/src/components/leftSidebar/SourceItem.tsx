import React from "react";
import { FiCheckCircle, FiFileText, FiCircle } from "react-icons/fi";
import { SidebarItem } from "./LeftSidebar";

interface SourceItemProps {
  item: SidebarItem;
  checked: boolean;
  onToggle: (id: string) => void;
  isCollapsedSidebar: boolean;
  onClick: () => void;
}

const SourceItem: React.FC<SourceItemProps> = ({
  item,
  checked,
  onToggle,
  isCollapsedSidebar: isCollapsed,
  onClick,
}) => {
  if (isCollapsed) {
    return (
      <div className="flex justify-center items-center p-2">
        <FiFileText className="text-red-500" size={20} aria-hidden="true" />
      </div>
    );
  }
  return (
    <div
      className="p-2 text-white hover:bg-gray-700 rounded cursor-pointer flex justify-between items-center"
      onClick={onClick} // Add the onClick handler here
    >
      <FiFileText className="text-red-500 mr-2 flex-shrink-0" size={20} />
      <span className="truncate flex-grow min-w-0 mr-2">{item.name}</span>
      <button
        onClick={(e) => {
          e.stopPropagation(); // Prevent the parent onClick from being triggered
          onToggle(item.name);
        }}
        className="ml-2 flex-shrink-0"
        aria-label={checked ? "Uncheck" : "Check"}
      >
        {checked ? <FiCheckCircle size={20} /> : <FiCircle size={20} />}
      </button>
    </div>
  );
};

export default SourceItem;
