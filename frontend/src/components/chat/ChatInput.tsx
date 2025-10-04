"use client";
import React from "react";
import { MdSend } from "react-icons/md";

interface ChatInputProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onSend: () => void;
  suggestedQuestions?: string[];
  onSuggestionClick?: (question: string) => void;
}

const ChatInput: React.FC<ChatInputProps> = ({
  value,
  onChange,
  onSend,
  suggestedQuestions = [],
  onSuggestionClick,
}) => {
  return (
    <div className="flex flex-col p-4 border-t mx-8">
      {/* Input Row */}
      <div className="flex flex-row items-end w-full h-full border rounded-4xl bg-gray-100 py-2">
        <textarea
          value={value}
          onChange={onChange}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              onSend();
            }
          }}
          className="flex-grow px-5 text-lg resize-none border-none focus:outline-none min-h-[2.5rem] max-h-32 bg-gray-100"
          placeholder="Type your message here..."
        />
        <button
          className="flex items-center justify-center ml-2 w-10 h-10 bg-blue-500 text-white rounded-full hover:bg-blue-600"
          onClick={onSend}
          type="button"
        >
          <MdSend className="w-5 h-5" />
        </button>
      </div>
      {/* Suggestions Row */}
      {suggestedQuestions.length > 0 && (
        <div className="flex flex-row gap-2 mt-2 overflow-x-auto whitespace-nowrap scrollbar-hide">
          {suggestedQuestions.map((q, idx) => (
            <button
              key={idx}
              className="px-3 py-1 bg-gray-200 rounded-full text-sm hover:bg-blue-200 transition mr-2"
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
