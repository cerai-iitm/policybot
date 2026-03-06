"use client";
import React, { useRef } from "react";
import { MdSend } from "react-icons/md";
import { FiPaperclip } from "react-icons/fi";

interface ChatInputProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onSend: () => void;

  disabled: boolean;
  placeholder?: string;
  selectedCount: number;  
  onOpenSidebar?: () => void;   // ✅ ADD THIS
   onAttach?: () => void;
}

const MAX_HEIGHT = 144; // ~6 lines

const ChatInput: React.FC<ChatInputProps> = ({
  value,
  onChange,
  onSend,

  disabled,
  placeholder = "Select a source to continue",
  selectedCount,
  onOpenSidebar,   // ✅ ADD THIS
  onAttach,
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto resize logic
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e);

    const textarea = textareaRef.current;
    if (!textarea) return;

    textarea.style.height = "auto";

    if (textarea.scrollHeight > MAX_HEIGHT) {
      textarea.style.height = `${MAX_HEIGHT}px`;
      textarea.style.overflowY = "auto";
    } else {
      textarea.style.height = `${textarea.scrollHeight}px`;
      textarea.style.overflowY = "hidden";
    }
  };

  return (
    <div className="w-full flex flex-col items-center px-4 pt-2 sm:pt-3 pb-5 sm:pb-6">
      
      {/* Main Input Container */}
     <div
className="w-full max-w-[760px] rounded-[32px] border p-3 transition-all duration-200 bg-white border-slate-200 shadow-[0px_2px_8px_-2px_rgba(0,0,0,0.16)]"

>


        {/* Textarea */}
        <div className="pr-4">
          <textarea
            ref={textareaRef}
            value={value}
            
            onChange={handleChange}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                onSend();
              }
            }}
            placeholder={placeholder}  // ⭐ dynamic placeholder
            rows={1}
 className="mx-4 mt-2 w-full resize-none text-sm sm:text-base outline-none bg-transparent leading-5 sm:leading-6 transition-all duration-150 overflow-y-auto custom-scrollbar text-slate-700 placeholder:text-slate-400"

          />
        </div>

        {/* Bottom Row */}
        <div className="flex items-center justify-between mt-3">
          
          {/* Attach Button */}
          <button
            type="button"
            onClick={onAttach}
            className="flex items-center gap-1 px-3 py-1.5 sm:py-2 rounded-full border border-black/10 text-zinc-600 text-xs sm:text-sm font-semibold hover:bg-slate-50 transition"
          >
            <FiPaperclip className="w-3 h-3" />
            Attach
          </button>

          {/* Send Button */}
        <div className="flex items-center gap-3">
  
<div
  onClick={() => {
    if (onOpenSidebar && window.innerWidth < 768) {
      onOpenSidebar();
    }
  }}
  className={`cursor-pointer px-2.5 py-1 text-[10px] sm:text-xs font-medium rounded-full border transition
    ${
      selectedCount === 0
        ? "bg-slate-100 text-slate-500 border-slate-200"
        : "bg-indigo-50 text-indigo-700 border-indigo-200"
    }
  `}
>
  {selectedCount} source{selectedCount !== 1 ? "s" : ""}
</div>



  <button
    aria-label="button"
    type="button"
    onClick={onSend}
    
className="w-9 h-9 rounded-full flex items-center justify-center transition bg-indigo-100 hover:opacity-80"

  >
    <MdSend
     className="w-5 h-5 text-blue-800 opacity-80"

    />
  </button>

</div>


        </div>
      </div>

      {/* Suggested Questions */}

    </div>
  );
};

export default ChatInput;
