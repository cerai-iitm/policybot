import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github.css";
import type { Components } from "react-markdown";

type MarkdownRendererProps = {
  text: string;
  className?: string;
};

const components: Components = {
  /* =========================
     HEADINGS
  ========================== */

  h1: ({ ...props }) => (
    <h1
      className="
        text-2xl sm:text-3xl
        font-semibold
        mt-8 sm:mt-12
        mb-4 sm:mb-6
        tracking-tight
        text-black
        border-b border-gray-200
        pb-2 sm:pb-3
      "
      {...props}
    />
  ),

  h2: ({ ...props }) => (
    <h2
      className="
        text-xl sm:text-2xl
        font-semibold
        mt-8 sm:mt-10
        mb-3 sm:mb-4
        tracking-tight
        text-black
      "
      {...props}
    />
  ),

  h3: ({ ...props }) => (
    <h3
      className="
        text-lg sm:text-xl
        font-semibold
        mt-6 sm:mt-8
        mb-2 sm:mb-3
        text-black
      "
      {...props}
    />
  ),

  h4: ({ ...props }) => (
    <h4
      className="
        text-base sm:text-lg
        font-semibold
        mt-5 sm:mt-6
        mb-2
        text-black
      "
      {...props}
    />
  ),

  /* =========================
     PARAGRAPH
  ========================== */

  p: ({ ...props }) => (
    <p
      className="
        my-4 sm:my-5
        text-black
        leading-7 sm:leading-8
      "
      {...props}
    />
  ),

  /* =========================
     LISTS
  ========================== */

  ul: ({ ...props }) => (
    <ul
      className="
        list-disc
        pl-5 sm:pl-6
        my-4 sm:my-5
        space-y-1.5 sm:space-y-2
        text-black
      "
      {...props}
    />
  ),

  ol: ({ ...props }) => (
    <ol
      className="
        list-decimal
        pl-5 sm:pl-6
        my-4 sm:my-5
        space-y-1.5 sm:space-y-2
        text-black
      "
      {...props}
    />
  ),

  li: ({ ...props }) => (
    <li
      className="
        leading-7 sm:leading-8
      "
      {...props}
    />
  ),

  /* =========================
     BLOCKQUOTE
  ========================== */

  blockquote: ({ ...props }) => (
    <blockquote
      className="
        border-l-4 border-gray-300
        pl-4 sm:pl-5
        italic
        text-gray-700
        my-6 sm:my-8
      "
      {...props}
    />
  ),

  /* =========================
     CODE
  ========================== */

  code({ className, children, ...props }) {
    const isInline = !className;

    return isInline ? (
      <code
        className="
          bg-gray-100
          text-black
          px-1.5
          py-0.5
          rounded-md
          text-[0.8em] sm:text-[0.85em]
          font-mono
        "
        {...props}
      >
        {children}
      </code>
    ) : (
      <div className="my-6 sm:my-8">
        <pre
          className="
            bg-gray-900
            text-white
            p-4 sm:p-5
            rounded-xl
            overflow-x-auto
            text-xs sm:text-sm
            leading-6
            shadow-sm
          "
        >
          <code className={className} {...props}>
            {children}
          </code>
        </pre>
      </div>
    );
  },

  /* =========================
     LINKS
  ========================== */

  a: ({ ...props }) => (
    <a
      className="
        text-blue-600
        font-medium
        underline
        underline-offset-4
        hover:opacity-80
        transition
      "
      target="_blank"
      rel="noopener noreferrer"
      {...props}
    />
  ),

  /* =========================
     TABLES
  ========================== */

  table: ({ ...props }) => (
    <div className="my-6 sm:my-8 overflow-x-auto">
      <table
        className="
          w-full
          border-collapse
          text-xs sm:text-sm
          text-black
        "
        {...props}
      />
    </div>
  ),

  th: ({ ...props }) => (
    <th
      className="
        border border-gray-200
        px-3 sm:px-4
        py-2
        bg-gray-100
        text-left
        font-semibold
      "
      {...props}
    />
  ),

  td: ({ ...props }) => (
    <td
      className="
        border border-gray-200
        px-3 sm:px-4
        py-2
        align-top
      "
      {...props}
    />
  ),

  /* =========================
     HORIZONTAL RULE
  ========================== */

  hr: () => (
    <hr className="my-8 sm:my-10 border-gray-200" />
  ),
};

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({
  text,
  className,
}) => (
  <div
    className={
      className ??
      `
      max-w-none
      text-[15px] sm:text-[16px]
      leading-7 sm:leading-8
      tracking-[0.01em]
      break-words
      text-black
      `
    }
  >
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeHighlight]}
      components={components}
    >
      {text}
    </ReactMarkdown>
  </div>
);

export default React.memo(MarkdownRenderer);
