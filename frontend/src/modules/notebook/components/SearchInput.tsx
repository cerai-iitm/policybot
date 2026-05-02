"use client";

import { Search, X } from "lucide-react";
import { useState, useRef, useEffect } from "react";

type Props = {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
};

const SearchInput = ({
  value,
  onChange,
  placeholder = "Search workspaces...",
}: Props) => {
  const [open, setOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // 🔹 Auto focus when opened
  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);

  return (
    <div
      className={`
        flex items-center
        border border-gray-300
        rounded-full
        bg-white
        transition-all duration-300 ease-in-out
        px-3 py-2
        
        ${open ? "w-64 gap-3" : "w-11 justify-center cursor-pointer"}
       
      `}
      onClick={() => {
        if (!open) setOpen(true);
      }}
    >
      {/* 🔍 Icon */}
      <Search size={18} className="text-gray-500 shrink-0" />

      {/* 🔹 Input */}
      <input
        ref={inputRef}
        type="text"
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onBlur={() => {
          if (!value) setOpen(false);
        }}
        className={`
          bg-transparent outline-none
          text-sm text-gray-800 placeholder-gray-400
          w-full
          transition-all duration-200
          ${open ? "opacity-100" : "opacity-0 w-0"}
        `}
      />

      {/* ❌ Clear Button */}
      {open && value && (
        <button
        aria-label="button"
          onClick={(e) => {
            e.stopPropagation();
            onChange("");
            inputRef.current?.focus();
          }}
          className="text-gray-400 hover:text-gray-600 transition"
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
};

export default SearchInput;