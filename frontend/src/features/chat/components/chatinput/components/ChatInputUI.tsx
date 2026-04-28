"use client";

import React from "react";
import { MdSend } from "react-icons/md";
import { FiPaperclip } from "react-icons/fi";

interface Props {
  value: string;
  textareaRef: React.Ref<HTMLTextAreaElement>;

  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void;

  onSend: () => void;
  onAttach?: () => void;
  onOpenSidebar?: () => void;

  disabled: boolean;
  placeholder: string;
  selectedCount: number;
}

const ChatInputUI: React.FC<Props> = ({
  value,
  textareaRef,
  onChange,
  onKeyDown,
  onSend,
  onAttach,
  onOpenSidebar,
  disabled,
  placeholder,
  selectedCount,
}) => {
  return (
    <div className="w-full flex flex-col items-center px-4 pt-2 sm:pt-3 pb-5 sm:pb-6">

      <div className="w-full max-w-190 rounded-4xl border p-3 bg-white border-slate-200 shadow-[0px_2px_8px_-2px_rgba(0,0,0,0.16)]">

        {/* TEXTAREA */}
        <div className="pr-4">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={onChange}
            onKeyDown={onKeyDown}
            placeholder={placeholder}
            rows={1}
            className="mx-4 mt-2 w-full resize-none text-sm sm:text-base outline-none bg-transparent leading-5 sm:leading-6 overflow-y-auto custom-scrollbar text-slate-700 placeholder:text-slate-400"
          />
        </div>

        {/* BOTTOM ROW */}
        <div className="flex items-center justify-between mt-3">

          {/* ATTACH */}
          <button
            type="button"
            onClick={onAttach}
            className="flex items-center gap-1 px-3 py-1.5 sm:py-2 rounded-full border border-black/10 text-zinc-600 text-xs sm:text-sm font-semibold hover:bg-slate-50 transition"
          >
            <FiPaperclip className="w-3 h-3" />
            Attach
          </button>

          {/* RIGHT SIDE */}
          <div className="flex items-center gap-3">

            {/* SOURCE COUNT */}
            <div
              onClick={() => {
                if (onOpenSidebar && window.innerWidth < 768) {
                  onOpenSidebar();
                }
              }}
              className={`cursor-pointer px-2.5 py-1 text-[10px] sm:text-xs font-medium rounded-full border
                ${
                  selectedCount === 0
                    ? "bg-slate-100 text-slate-500 border-slate-200"
                    : "bg-indigo-50 text-indigo-700 border-indigo-200"
                }`}
            >
              {selectedCount} source{selectedCount !== 1 ? "s" : ""}
            </div>

            {/* SEND */}
            <button
              type="button"
              onClick={onSend}
              disabled={disabled}
              className="w-9 h-9 rounded-full flex items-center justify-center bg-indigo-100 hover:opacity-80 transition disabled:opacity-50"
              aria-label="Send message"
            >
              <MdSend className="w-5 h-5 text-blue-800 opacity-80" />
            </button>

          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInputUI;