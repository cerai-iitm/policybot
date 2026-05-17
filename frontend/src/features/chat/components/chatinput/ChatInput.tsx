"use client";

import React, { useRef, useState, useEffect } from "react";
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

const MAX_HEIGHT = 140;

const ChatInput: React.FC<ChatInputProps> = ({
  value,
  onChange,
  onSend,
  disabled,
  placeholder,
  selectedCount,
  onOpenSidebar,
  onAttach,
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);


  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    textarea.style.height = "auto";

    const scrollHeight = textarea.scrollHeight;
    const newHeight = Math.min(scrollHeight, MAX_HEIGHT);

    textarea.style.height = `${newHeight}px`;
    textarea.style.overflowY = scrollHeight > MAX_HEIGHT ? "auto" : "hidden";

   
  }, [value]);

const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();

    /**
     * 🚫 DO NOT TRUST UI
     * Controller will validate everything
     */
    onSend();
  }
};

  return (
    <ChatInputUI
      value={value}
      textareaRef={textareaRef}
      onChange={onChange}
      onKeyDown={handleKeyDown}
      onSend={onSend}
      onAttach={onAttach}
      onOpenSidebar={onOpenSidebar}
      disabled={disabled}
      placeholder={
  selectedCount === 0
    ? "Select at least one PDF to continue"
    : "Ask something about your documents..."
}
      selectedCount={selectedCount}
      
    />
  );
};

export default ChatInput;