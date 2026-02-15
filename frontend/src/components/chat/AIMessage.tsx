"use client";
import React, { useState, useEffect } from "react";
import MarkdownRenderer from "../common/Markdown";
import { FiFile, FiCopy } from "react-icons/fi";
import { AiOutlineLike, AiOutlineDislike } from "react-icons/ai";
import { FiCheck } from "react-icons/fi";
import { AiFillLike, AiFillDislike } from "react-icons/ai";

interface SourceChunk {
  text: string;
  source: string;
  page_number: number | null;
}

interface AIMessageProps {
  content: string;
  sourceChunks?: SourceChunk[];
  loadingType?: "thinking" | "summary";
}

const AIMessage: React.FC<AIMessageProps> = ({
  content,
  sourceChunks,
  loadingType,
}) => {
  const [showChunks, setShowChunks] = useState(false);
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState<"like" | "dislike" | null>(null);

  const isError = content?.startsWith("Error:");
  const isGenerating = loadingType === "thinking";
  const showActions = content && !isError && !isGenerating;
  const sourcePanelRef = React.useRef<HTMLDivElement>(null);

  useEffect(() => {
  if (showChunks && sourcePanelRef.current) {
    sourcePanelRef.current.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }
}, [showChunks]);


  // ✅ Auto-close sources if new generation starts
  useEffect(() => {
    if (isGenerating) {
      setShowChunks(false);
    }
  }, [isGenerating]);

  const handleLike = () => {
    setFeedback((prev) => (prev === "like" ? null : "like"));
  };

  const handleDislike = () => {
    setFeedback((prev) => (prev === "dislike" ? null : "dislike"));
  };

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
    <div className="w-full max-w-3xl px-3 sm:mx-4 sm:px-0 my-4 animate-fadeIn">


      {/* ================= LOADER ================= */}
      {!content && (
        <div className="flex items-center gap-2 py-2">
          <div className="flex gap-1">
            <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></span>
            <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-150"></span>
            <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-300"></span>
          </div>
          <span className="text-slate-500 text-sm">
            {loadingType === "summary" ? "Generating summary" : "Thinking"}
          </span>
        </div>
      )}

      {/* ================= ERROR MESSAGE ================= */}
      {content && isError && (
        <div className="text-red-600 bg-red-50 px-4 py-3 rounded-xl border border-red-200">
          {content}
        </div>
      )}

      {/* ================= NORMAL MESSAGE ================= */}
      {content && !isError && (
        <>
          {/* Message Text */}
          <div className="text-slate-700">
            <div className="relative">
              <MarkdownRenderer text={content} />
              {isGenerating && (
                <span className="inline-block w-2 ml-1 bg-black animate-pulse align-middle" />
              )}
            </div>
          </div>

          {/* ================= ACTION ICONS ================= */}
          {showActions && (
            <div className="flex items-center gap-5 mt-3 text-slate-400 animate-fadeIn">

              <button
                onClick={handleCopy}
                className=" p-2 -m-2 hover:text-slate-700 transition"
                title="Copy"
              >
                {copied ? <FiCheck size={18} /> : <FiCopy size={18} />}
              </button>

              <button
                onClick={handleLike}
                className={`transition ${
                  feedback === "like"
                    ? "text-green-600"
                    : "text-slate-400 hover:text-green-600"
                }`}
                title="Helpful"
              >
                {feedback === "like" ? (
                  <AiFillLike size={18} />
                ) : (
                  <AiOutlineLike size={18} />
                )}
              </button>

              <button
                onClick={handleDislike}
                className={`transition ${
                  feedback === "dislike"
                    ? "text-red-600"
                    : "text-slate-400 hover:text-red-500"
                }`}
                title="Not Helpful"
              >
                {feedback === "dislike" ? (
                  <AiFillDislike size={18} />
                ) : (
                  <AiOutlineDislike size={18} />
                )}
              </button>
            </div>
          )}

          {/* ================= SOURCES BUTTON ================= */}
          {showActions && sourceChunks && sourceChunks.length > 0 && (
            <button
              onClick={() => setShowChunks((prev) => !prev)}
              className="mt-6 flex items-center gap-2 px-3  py-2 rounded-full border border-slate-300 bg-white text-sm text-slate-600 hover:bg-slate-100 transition animate-fadeIn"
            >
              <FiFile size={14} />
              Sources
            </button>
          )}
        </>
      )}

      {/* ================= SOURCE PANEL ================= */}
     {showChunks && sourceChunks && showActions && (
  <div
    ref={sourcePanelRef}
    className="mt-6 space-y-4 animate-fadeIn"
  >

          <div className="text-xs font-semibold tracking-wide text-slate-500 uppercase">
            Source References
          </div>

          {sourceChunks.map((chunk, idx) => (
            <div
              key={idx}
              className="group bg-white border border-slate-200 rounded-2xl p-3 sm:p-4 transition-all duration-200"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2 min-w-0">
                  <div className="p-2 bg-slate-100 rounded-lg">
                    <FiFile className="text-slate-600" size={14} />
                  </div>

                  <div className="flex flex-col min-w-0">

                    <span className="text-sm font-medium text-slate-800 truncate">
                      {chunk.source}
                    </span>
                    <span className="text-xs text-slate-500">
                      Referenced document
                    </span>
                  </div>
                </div>

                {chunk.page_number !== null && (
                  <div className="px-2.5 py-1 text-xs font-medium bg-slate-100 text-slate-600 rounded-full border border-slate-200">
                    Page {chunk.page_number}
                  </div>
                )}
              </div>

              <div className="h-px bg-slate-100 mb-3" />

              <p className="text-sm text-slate-700 leading-relaxed">
                {chunk.text}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AIMessage;
