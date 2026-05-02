"use client";

import React, { useState } from "react";
import HumanMessageUI from "./components/HumanMessageUI";

interface HumanMessageProps {
  content: string;
}

const HumanMessage: React.FC<HumanMessageProps> = ({ content }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);

      setTimeout(() => {
        setCopied(false);
      }, 2000);
    } catch (err) {
      console.error("Copy failed", err);
    }
  };

  return (
    <HumanMessageUI
      content={content}
      copied={copied}
      onCopy={handleCopy}
    />
  );
};

export default HumanMessage;