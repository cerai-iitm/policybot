"use clinet";
import React, { useState } from "react";
import MarkdownRenderer from "../common/Markdown";

interface AIMessageProps {
  content: string;
  sourceChunks?: string[];
}

const AIMessage: React.FC<AIMessageProps> = ({ content, sourceChunks }) => {
  const [showChunks, setShowChunks] = useState(false);

  return (
    <div className="p-4 rounded-xl bg-bg-dark text-text text-base max-w-4xl break-words mx-4 my-3 shadow-sm hover:shadow-md transition-all duration-200 border border-border-muted">
      {/* Loader if content is empty */}
      {content ? (
        <div className="prose prose-base max-w-none text-text">
          <MarkdownRenderer text={content} />
        </div>
      ) : (
        <div className="flex items-center space-x-3 py-2">
          <div className="animate-spin rounded-full h-4 w-4 border-2 border-text-muted border-t-transparent"></div>
          <span className="text-text-muted text-base">
            Generating response...
          </span>
        </div>
      )}

      {/* Source chunks section */}
      {content && sourceChunks && sourceChunks.length > 0 && (
        <div className="mt-4 pt-4 border-t border-border-muted">
          <button
            onClick={() => setShowChunks((prev) => !prev)}
            className="bg-bg text-text-muted border border-border-muted rounded-lg px-4 py-2 text-sm font-medium hover:bg-bg-light hover:text-text transition-all duration-200 focus:outline-none"
          >
            {showChunks ? "Hide Source Chunks" : "Show Source Chunks"}{" "}
            <span className="ml-2 text-text-muted">
              ({sourceChunks.length})
            </span>
          </button>

          {showChunks && (
            <div className="mt-4 space-y-3">
              <div className="flex items-center gap-2 pb-2">
                <span className="text-base">📄</span>
                <h4 className="text-text font-semibold text-base m-0">
                  Source Chunks:
                </h4>
              </div>

              <div className="space-y-2">
                {sourceChunks.map((chunk, idx) => (
                  <div
                    key={idx}
                    className="bg-bg-light rounded-lg p-3 border border-border"
                  >
                    <div className="flex items-center gap-2 mb-3">
                      <span className="text-text font-bold text-lg tracking-wide">
                        Chunk {idx + 1}
                      </span>
                    </div>
                    <div className="text-text text-base leading-relaxed">
                      {chunk}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AIMessage;
