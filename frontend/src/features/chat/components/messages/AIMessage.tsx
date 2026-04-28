"use client";

import React, { useState, useEffect, useRef } from "react";

import MessageLoader from "./components/MessageLoader";
import MessageError from "./components/MessageError";
import MessageContent from "./components/MessageContent";
import MessageActions from "./components/MessageActions";
import SourcesButton from "./components/SourcesButton";
import SourcePanel from "./components/SourcePanel";

interface SourceChunk {
  text: string;
  source: string;
  page_number: number | null;
}

interface Props {
  content: string;
  sourceChunks?: SourceChunk[];
  loadingType?: "thinking" | "summary";
}

const AIMessage: React.FC<Props> = ({
  content,
  sourceChunks,
  loadingType,
}) => {
  const [showChunks, setShowChunks] = useState(false);
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] =
    useState<"like" | "dislike" | null>(null);

  const sourceRef = useRef<HTMLDivElement>(null);

  const isError = content?.startsWith("Error:");
  const isGenerating = loadingType === "thinking";
  const showActions = content && !isError && !isGenerating;

  useEffect(() => {
    if (showChunks && sourceRef.current) {
      sourceRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [showChunks]);

const shouldShowChunks = showChunks && !isGenerating;

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="w-full max-w-3xl px-3 my-4">

      {!content && <MessageLoader type={loadingType} />}

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

          {showActions && sourceChunks?.length ? (
            <SourcesButton
              onClick={() =>
                setShowChunks((prev) => !prev)
              }
            />
          ) : null}
        </>
      )}

      {shouldShowChunks && sourceChunks && showActions && (
  <SourcePanel ref={sourceRef} chunks={sourceChunks} />
)}
    </div>
  );
};

export default AIMessage;