"use client";

import React, { useState, useEffect, useRef } from "react";

import MessageLoader from "./components/MessageLoader";
import MessageError from "./components/MessageError";
import MessageContent from "./components/MessageContent";
import MessageActions from "./components/MessageActions";
import SourcesButton from "./components/SourcesButton";


interface SourceChunk {
  text: string;
  source: string;
  page_number: number | null;
}

interface Props {
  content: string;
  sourceChunks?: SourceChunk[];
  loadingType?: "thinking" | "summary";
  onSourcesClick?: () => void;
}

const AIMessage: React.FC<Props> = ({
  content,
  sourceChunks,
  loadingType,
  onSourcesClick
}) => {
  const [showChunks, setShowChunks] = useState(false);
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] =
    useState<"like" | "dislike" | null>(null);

  const sourceRef = useRef<HTMLDivElement>(null);

  const isError = content?.startsWith("Error:");
  const isGenerating = !content;
  const showActions = content && !isError && !isGenerating;

  useEffect(() => {
    if (showChunks && sourceRef.current) {
      sourceRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [showChunks]);

const shouldShowChunks = showChunks && !isGenerating;
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
    <div className="w-full max-w-3xl px-3 my-4">

      {!content && <MessageLoader type="thinking" />}

      {content && isError && <MessageError content={content} />}

      {content && !isError && (
        <>
          <MessageContent
            content={content}
            isGenerating={isGenerating}
          />

          {showActions && (
            <MessageActions
              copied={copied}
              feedback={feedback}
              onCopy={handleCopy}
              onLike={() =>
                setFeedback((f) => (f === "like" ? null : "like"))
              }
              onDislike={() =>
                setFeedback((f) =>
                  f === "dislike" ? null : "dislike"
                )
              }
            />
          )}

          {showActions && Array.isArray(sourceChunks) && sourceChunks.length > 0 && (
 <SourcesButton
  onClick={() => {
    setShowChunks((prev) => !prev);
    onSourcesClick?.(); // 🔥 trigger sidebar
  }}
/>
)}
        </>
      )}

     
    </div>
  );
};

export default AIMessage;