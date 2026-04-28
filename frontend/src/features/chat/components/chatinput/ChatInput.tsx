"use client";

import React, { useRef } from "react";
import ChatInputUI from "./components/ChatInputUI";

interface ChatInputProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onSend: () => void;

  disabled: boolean;
  placeholder?: string;
  selectedCount: number;
  onOpenSidebar?: () => void;
  onAttach?: () => void;
}

const MAX_HEIGHT = 144;

const ChatInput: React.FC<ChatInputProps> = ({
  value,
  onChange,
  onSend,
  disabled,
  placeholder = "Select a source to continue",
  selectedCount,
  onOpenSidebar,
  onAttach,
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

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

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <ChatInputUI
      value={value}
      textareaRef={textareaRef}
      onChange={handleChange}
      onKeyDown={handleKeyDown}
      onSend={onSend}
      onAttach={onAttach}
      onOpenSidebar={onOpenSidebar}
      disabled={disabled}
      placeholder={placeholder}
      selectedCount={selectedCount}
    />
  );
};

export default ChatInput;