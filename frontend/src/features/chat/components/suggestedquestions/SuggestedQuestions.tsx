"use client";
import React from "react";

interface SuggestedQuestionsProps {
  questions: string[];
  onSelect: (question: string) => void;
}

const SuggestedQuestions: React.FC<SuggestedQuestionsProps> = ({
  questions,
  onSelect,
}) => {
  if (!questions || questions.length === 0) return null;

  return (
    <div className="w-full flex justify-start px-3 mt-3 mb-6 animate-fadeIn">
      
      {/* 👉 Container aligned like AI message */}
      <div className="w-full max-w-2xl flex flex-col gap-2">

        {questions.map((question, index) => (
          <button
            key={index}
            onClick={() => onSelect(question)}
            className="
              text-left
              px-4 py-3

              /* 🔥 CHAT-BUBBLE STYLE */
              rounded-xl
              rounded-tl-sm   /* 👈 remove top-left curve */

              /* 🔥 AI LOOK */
              bg-slate-100
              text-slate-700
              border border-slate-200

              /* 🔥 INTERACTION */
              hover:bg-slate-200
              hover:border-slate-300

              transition-all duration-200

              text-[14px] leading-5
            "
          >
            {question}
          </button>
        ))}

      </div>
    </div>
  );
};

export default SuggestedQuestions;