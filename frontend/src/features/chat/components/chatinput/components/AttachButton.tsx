"use client";

import React from "react";
import { FiPaperclip } from "react-icons/fi";

interface Props {
  onClick?: () => void;
}

const AttachButton: React.FC<Props> = ({ onClick }) => {
  return (
    <button
    aria-label="button"
      onClick={onClick}
      className="w-9 h-9 flex items-center justify-center rounded-full hover:bg-slate-100"
    >
      <FiPaperclip className="w-4 h-4 text-slate-600" />
    </button>
  );
};

export default AttachButton;