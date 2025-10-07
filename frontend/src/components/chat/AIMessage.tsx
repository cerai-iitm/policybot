import React, { useState } from "react";
import MarkdownRenderer from "../common/Markdown";

interface AIMessageProps {
  content: string;
  sourceChunks?: string[];
}

const AIMessage: React.FC<AIMessageProps> = ({ content, sourceChunks }) => {
  const [showChunks, setShowChunks] = useState(false);

  return (
    <div className="p-2 rounded-md bg-bg-dark text-text text-base max-w-[70%] break-words mx-8 whitespace-pre-wrap">
      {/* Loader if content is empty */}
      {content ? (
        <MarkdownRenderer text={content} />
      ) : (
        <div className="flex items-center">
          {/* Replace with your preferred spinner/loader */}
          <span className="loader mr-2"></span>
          Generating response...
        </div>
      )}
      {/* Dropdown for source chunks, only if response is available and chunks exist */}
      {content && sourceChunks && sourceChunks.length > 0 && (
        <div>
          <button
            onClick={() => setShowChunks((prev) => !prev)}
            className="bg-gray-200 rounded px-3 py-1 mt-2 mb-2 text-sm hover:bg-blue-200 transition"
          >
            {showChunks ? "Hide Source Chunks" : "Show Source Chunks"}
          </button>
          {showChunks && (
            <div className="border rounded p-2 mt-2 bg-gray-50">
              <h4 className="font-semibold mb-2">Source Chunks:</h4>
              <ul>
                {sourceChunks.map((chunk, idx) => (
                  <>
                    <h6>Chunk {idx + 1}:</h6>
                    <li key={idx} className="mb-1">
                      {chunk}
                    </li>
                  </>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AIMessage;
