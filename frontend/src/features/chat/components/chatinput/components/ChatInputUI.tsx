"use client";

import React from "react";

import SendButton from "./sendbutton/SendButton";
import SourceCount from "./SourceCount";

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


  const noSources = selectedCount === 0;
const noMessage = !value.trim();

const isDisabled = disabled || noSources || noMessage;

let tooltipText = "";

if (noSources) {
  tooltipText = "Select a source to continue";
} else if (noMessage) {
  tooltipText = "Type a message to send";
} else {
  tooltipText = "Send prompt";
}


  return (
    <div className="w-full flex justify-center px-4 pb-4">
      <div className="w-full md:w-[90%] max-w-4xl">
        <div className="rounded-3xl border border-slate-200 bg-white px-3 py-2 transition-all duration-200 flex flex-col">

          {/* 🔥 ROW 1 → TEXTAREA */}
          <div className="mb-2">
            <textarea
              ref={textareaRef}
              value={value}
              onChange={onChange}
              onKeyDown={onKeyDown}
              placeholder={placeholder}
              rows={1}
              className="
                w-full
                p-2
                resize-none
                bg-transparent
                outline-none
                text-md
                leading-6
                text-slate-700
                placeholder:text-slate-400
                custom-scrollbar
                overflow-y-auto
                max-h-35
              "
            />
          </div>

          {/* 🔥 ROW 2 → CONTROLS (ALWAYS FIXED POSITION) */}
          <div className="flex items-center justify-between">
            <SourceCount
              count={selectedCount}
              onClick={() => {
                if (onOpenSidebar && window.innerWidth < 768) {
                  onOpenSidebar();
                }
              }}
            />

            <SendButton
  onClick={onSend}
  disabled={isDisabled}
  tooltipText={tooltipText}
/>
          </div>

        </div>
      </div>
    </div>
  );
};

export default ChatInputUI;