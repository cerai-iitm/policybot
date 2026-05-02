"use client";

import React from "react";
import Image from "next/image";

import uncheckedicon from "@/assets/unmarked.png";
import checkedicon from "@/assets/marked.png";

interface Props {
  checked: boolean;
  onToggle: () => void;
}

const SourceItemCheckbox: React.FC<Props> = ({ checked, onToggle }) => {
  return (
    <div className="flex items-center gap-2 shrink-0">
      <button
        aria-label="toggle source"
        onClick={(e) => {
          e.stopPropagation();
          onToggle();
        }}
      >
        <Image
          src={checked ? checkedicon : uncheckedicon}
          alt="checkbox"
          width={20}
          height={20}
        />
      </button>
    </div>
  );
};

export default SourceItemCheckbox;