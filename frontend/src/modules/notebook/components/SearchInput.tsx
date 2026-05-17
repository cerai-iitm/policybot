"use client";

import { Search, X } from "lucide-react";
import { useState, useRef, useEffect } from "react";

type Props = {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;

  // ✅ Added for mobile responsive control
  onOpenChange?: (open: boolean) => void;
};

const SearchInput = ({
  value,
  onChange,
  placeholder = "Search workspaces...",
  onOpenChange,
}: Props) => {
  const [open, setOpen] = useState(false);

  const inputRef = useRef<HTMLInputElement>(null);

  // 🔹 Auto focus when opened
  useEffect(() => {
    if (open) {
      inputRef.current?.focus();
    }
  }, [open]);

  // ✅ Notify parent
  useEffect(() => {
    onOpenChange?.(open);
  }, [open, onOpenChange]);

  const handleOpen = () => {
    if (!open) {
      setOpen(true);
    }
  };

  const handleClose = () => {
    if (!value) {
      setOpen(false);
    }
  };

  return (
    <div
      className={`
        flex items-center
        border border-gray-300
        rounded-full
        bg-white
        transition-all duration-300 ease-in-out
        px-3 py-2
        overflow-hidden

        ${
          open
            ? "w-full max-w-[220px] md:w-64 md:max-w-none gap-3"
            : "w-11 justify-center cursor-pointer"
        }
      `}
      onClick={handleOpen}
    >
      {/* 🔍 Icon */}
      <Search
        size={18}
        className="text-gray-500 shrink-0"
      />

      {/* 🔹 Input */}
      <input
        ref={inputRef}
        type="text"
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onBlur={handleClose}
        className={`
          bg-transparent outline-none
          text-sm text-gray-800 placeholder-gray-400
          min-w-0
          w-full
          transition-all duration-200

          ${
            open
              ? "opacity-100"
              : "opacity-0 w-0"
          }
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
          className="
            text-gray-400
            hover:text-gray-600
            transition
            shrink-0
          "
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
};

export default SearchInput;