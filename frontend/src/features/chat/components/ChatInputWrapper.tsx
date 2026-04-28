"use client";

import React from "react";
import ChatInput from "./chatinput/ChatInput";

interface Props {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onSend: () => void;
}

const ChatInputWrapper: React.FC<Props> = ({
  value,
  onChange,
  onSend,
}) => {
  return (
    <div >
      <ChatInput
        value={value}
        onChange={onChange}
        onSend={onSend}
        disabled={false}
        selectedCount={0}
      />
    </div>
  );
};

export default ChatInputWrapper;