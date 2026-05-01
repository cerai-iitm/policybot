"use client";

import React, { useState, useRef, useEffect } from "react";

type Props = {
  title: string;
  notebookId: string;
  onUpdate: (newTitle: string) => Promise<void>;
};

const Title = ({ title, notebookId, onUpdate }: Props) => {
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(title);

  // ✅ FIX: correct ref type for textarea
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // sync with backend
  useEffect(() => {
    setValue(title);
  }, [title]);

  // focus when editing
  useEffect(() => {
    if (editing) {
      inputRef.current?.focus();

      // optional: place cursor at end instead of select all
      const length = inputRef.current?.value.length || 0;
      inputRef.current?.setSelectionRange(length, length);
    }
  }, [editing]);

  // auto height resize
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = "auto";
      inputRef.current.style.height =
        inputRef.current.scrollHeight + "px";
    }
  }, [value, editing]);

  const handleSave = async () => {
    const trimmed = value.trim();

    if (!trimmed || trimmed === title) {
      setValue(title);
      setEditing(false);
      return;
    }

    try {
      await onUpdate(trimmed);
    } catch (err) {
      console.error("Failed to update title", err);
      setValue(title);
    } finally {
      setEditing(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); // prevent newline
      handleSave();
    }

    if (e.key === "Escape") {
      setValue(title);
      setEditing(false);
    }
  };

  return (
    <div className="px-6 pt-6 pb-4">
      <div className="inline-block max-w-full">
        {editing ? (
       <textarea
  ref={inputRef}
  value={value}
  onChange={(e) => setValue(e.target.value)}
  onBlur={handleSave}
  onKeyDown={handleKeyDown}
  rows={1}
  maxLength={50} 
  placeholder="Enter title"
  aria-label="Notebook title"
  className="
    text-lg font-semibold text-gray-800
    bg-transparent outline-none

    px-2 py-1

    border border-black/60
    rounded-md

    inline-block
    max-w-full

    resize-none
    overflow-hidden

    whitespace-pre-wrap
    break-all   /* 🔥 THIS IS THE KEY FIX */
    
    leading-snug
  "
/>
        ) : (
          <h2
  onClick={() => setEditing(true)}
  className="
    inline-block
    max-w-full

    text-lg font-semibold text-gray-800
    leading-snug

    cursor-pointer

    px-1 py-0.5
    rounded-md

    transition-all

    hover:border hover:border-black/40
    hover:bg-gray-50

    break-all          /* 🔥 add this */
    whitespace-pre-wrap /* 🔥 and this */
  "
  title="Click to edit"
>
  {title}
</h2>
        )}
      </div>
    </div>
  );
};

export default Title;