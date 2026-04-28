"use client";

import React from "react";
import AttachButton from "./AttachButton";
import SendButton from "./SendButton";
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
  isMultiline: boolean;
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
  isMultiline,
}) => {
  return (
    <div className="w-full flex justify-center px-4 pb-4">
      <div className="w-full md:w-[90%] max-w-4xl">
        <div className="rounded-3xl border border-slate-200 bg-white px-3 py-2 transition-all duration-200">

          {/* 🔥 TEXTAREA (always full width in multiline) */}
          <div className={`${isMultiline ? "mb-2" : ""}`}>
            <textarea
              ref={textareaRef}
              value={value}
              onChange={onChange}
              onKeyDown={onKeyDown}
              placeholder={placeholder}
              rows={1}
              className="
              p-2
                w-full
                resize-none
                bg-transparent
                outline-none
                text-sm
                leading-6
                text-slate-700
                placeholder:text-slate-400
                custom-scrollbar
                overflow-y-auto
                max-h-[140px]
              "
            />
          </div>

          {/* 🔥 CONTROLS */}
          {!isMultiline ? (
            // SINGLE LINE → inline layout
            <div className="flex items-center gap-2">
              <AttachButton onClick={onAttach} />

              <div className="flex-1" />

              <SourceCount
                count={selectedCount}
                onClick={() => {
                  if (onOpenSidebar && window.innerWidth < 768) {
                    onOpenSidebar();
                  }
                }}
              />

              <SendButton onClick={onSend} disabled={disabled} />
            </div>
          ) : (
            // MULTILINE → bottom row
            <div className="flex items-center justify-between">
              <AttachButton onClick={onAttach} />

              <div className="flex items-center gap-3">
                <SourceCount
                  count={selectedCount}
                  onClick={() => {
                    if (onOpenSidebar && window.innerWidth < 768) {
                      onOpenSidebar();
                    }
                  }}
                />

                <SendButton onClick={onSend} disabled={disabled} />
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default ChatInputUI;