"use client";
import React from "react";

const MessageError = ({ content }: { content: string }) => {
  return (
    <div className="text-red-600 bg-red-50 px-4 py-3 rounded-xl border border-red-200">
      {content}
    </div>
  );
};

export default MessageError;