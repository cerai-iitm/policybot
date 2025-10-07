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
    <div className="flex flex-col border-t mx-8">
      {/* Input Row */}
      <div className="flex flex-row  justify-center items-center w-full border rounded-3xl bg-gray-100 py-0 px-0">
        <textarea
          value={value}
          onChange={onChange}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              onSend();
            }
          }}
          className="flex-grow px-5 m-0 text-base resize-none border-none focus:outline-none py-2 max-h-32 bg-none "
          placeholder="Type your message here..."
        />
        <button
          className="flex items-center justify-center mr-2 w-8 h-8 bg-blue-500 text-white rounded-full hover:bg-blue-600"
          onClick={onSend}
          type="button"
          disabled={disabled}
        >
          <MdSend className="w-5 h-5" />
        </button>
      </div>
      {/* Suggestions Row */}
      {suggestedQuestions.length > 0 && (
        <div className="flex flex-row gap-2 overflow-x-auto whitespace-nowrap scrollbar-hide text-sm mt-2 py-2  ">
          {suggestedQuestions.map((q, idx) => (
            <button
              key={idx}
              className="px-3 py-1 bg-gray-200 rounded-full text-sm hover:bg-blue-200 transition mr-2 mb-2"
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
