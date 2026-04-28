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
    <div className="w-full max-w-3xl px-3 sm:mx-4 sm:px-0 mt-6 animate-fadeIn">
      <div className="flex flex-col gap-3">

        {questions.map((question, index) => (
          <button
            key={index}
            onClick={() => onSelect(question)}
            className="
              text-left
              px-4 py-3
              rounded-xl
              border border-slate-200
              bg-slate-50
              text-slate-700
              hover:bg-slate-100
              hover:border-slate-300
              transition-all
              duration-200
              text-sm sm:text-base
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
