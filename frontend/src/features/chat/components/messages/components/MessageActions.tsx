"use client";
import React from "react";
import { FiCopy, FiCheck } from "react-icons/fi";
import {
  AiOutlineLike,
  AiOutlineDislike,
  AiFillLike,
  AiFillDislike,
} from "react-icons/ai";

interface Props {
  copied: boolean;
  feedback: "like" | "dislike" | null;
  onCopy: () => void;
  onLike: () => void;
  onDislike: () => void;
}

const MessageActions: React.FC<Props> = ({
  copied,
  feedback,
  onCopy,
  onLike,
  onDislike,
}) => {
  return (
    <div className="flex items-center gap-2 mt-3 text-slate-400 animate-fadeIn">

      <button onClick={onCopy} className="p-2 -m-2 hover:text-slate-700 cursor-pointer">
        {copied ? <FiCheck size={16} /> : <FiCopy size={16} />}
      </button>

      <button
        onClick={onLike}
        className={`${
          feedback === "like"
            ? "text-green-600"
            : "hover:text-green-600 cursor-pointer"
        }`}
      >
        {feedback === "like" ? (
          <AiFillLike size={16} />
        ) : (
          <AiOutlineLike size={16} />
        )}
      </button>

      <button
        onClick={onDislike}
        className={`${
          feedback === "dislike"
            ? "text-red-600"
            : "hover:text-red-500 cursor-pointer"
        }`}
      >
        {feedback === "dislike" ? (
          <AiFillDislike size={16} />
        ) : (
          <AiOutlineDislike size={16} />
        )}
      </button>
    </div>
  );
};

export default MessageActions;