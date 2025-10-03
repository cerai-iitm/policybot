"use client";
import React from "react";
import { MdSend } from "react-icons/md";

interface ChatInputProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onSend: () => void;
}

const ChatInput: React.FC<ChatInputProps> = ({ value, onChange, onSend }) => {
  return (
    <div className="flex items-center p-4 border-t mx-8">
      <div className="flex items-center w-full h-full border rounded-4xl bg-gray-100 py-2">
        <textarea
          value={value}
          onChange={onChange}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              onSend();
            }
          }}
          className="flex-grow px-5 text-lg resize-none border-none focus:outline-none min-h-[2rem]"
          placeholder="Type your message here..."
        />
        <button
          className="flex items-center justify-center mr-3 w-7 h-7 bg-blue-500 text-white rounded-full hover:bg-blue-600"
          onClick={onSend}
        >
          <MdSend className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default ChatInput;
