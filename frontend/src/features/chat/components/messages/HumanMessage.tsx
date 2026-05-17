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
    // Primary modern API
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(content);
    } 
    else {
      // 🔥 Fallback for older / unsupported browsers
      const textArea = document.createElement("textarea");
      textArea.value = content;
      textArea.style.position = "fixed";
      textArea.style.left = "-9999px";
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      document.execCommand("copy");
      document.body.removeChild(textArea);
    }

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