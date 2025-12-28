"use client";
import React from "react";
import { MdSend } from "react-icons/md";

interface ChatInputProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onSend: () => void;
  suggestedQuestions?: string[];
  onSuggestionClick?: (question: string) => void;
  disabled: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({
  value,
  onChange,
  onSend,
  suggestedQuestions = [],
  onSuggestionClick,
  disabled,
}) => {
  return (
    <div className="flex flex-col border-t mx-8 border-border-muted">
      {/* Input Row */}
      <div className="flex flex-row  justify-center items-center w-full border rounded-3xl bg-bg-light py-0 px-0 border-border">
        <textarea
          value={value}
          onChange={onChange}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              onSend();
            }
          }}
          className="flex-grow px-5 m-0 text-base resize-none border-none focus:outline-none py-2 max-h-32 bg-none text-text placeholder:text-text-muted transition-colors duration-300 "
          placeholder="Type your message here..."
        />
        <button
          className="flex items-center justify-center mr-2 w-8 h-8 bg-blue-600 text-bg-light  rounded-full hover:opacity-75 transition-colors duration-300"
          onClick={onSend}
          type="button"
          disabled={disabled}
        >
          <MdSend className="w-5 h-5 text-white hover:text-white hover: opacity-75" />
        </button>
      </div>
      {/* Suggestions Row */}
      {suggestedQuestions.length > 0 && (
        <div className="flex flex-row gap-2 overflow-x-auto whitespace-nowrap scrollbar-hide text-sm mt-2 py-2  ">
          {suggestedQuestions.map((q, idx) => (
            <button
              key={idx}
              className="px-3 py-1 rounded-full text-sm transition mr-2 mb-2 bg-bg hover:bg-primary hover:text-bg-light"
              onClick={() => onSuggestionClick && onSuggestionClick(q)}
              type="button"
            >
              {q}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default ChatInput;
