"use client";

import React from "react";
import { MdSend } from "react-icons/md";

interface Props {
  onClick: () => void;
  disabled: boolean;
}

const SendButton: React.FC<Props> = ({ onClick, disabled }) => {
  return (
    <button
    aria-label="button"
      onClick={onClick}
      disabled={disabled}
      className="w-9 h-9 rounded-full flex items-center justify-center bg-indigo-100 hover:opacity-80 transition disabled:opacity-50"
    >
      <MdSend className="w-5 h-5 text-blue-800" />
    </button>
  );
};

export default SendButton;