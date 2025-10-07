import React from "react";
import ReactMarkdown from "react-markdown";
// import rehype plugins or remark plugins if you use them
// import rehypeRaw from "rehype-raw"; // example

type MarkdownRendererProps = {
  text: string;
  className?: string;
};

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({
  text,
  className,
}) => (
  <div
    className={className ?? "prose prose-neutral dark:prose-invert break-words"}
  >
    <ReactMarkdown
      // rehypePlugins={[rehypeRaw]} // add plugins if you use them
      // remarkPlugins={[]} // add plugins if you use them
      components={{
        h1: ({ node, ...props }) => (
          <h1 className="text-3xl font-bold my-4" {...props} />
        ),
        h2: ({ node, ...props }) => (
          <h2 className="text-2xl font-semibold my-3" {...props} />
        ),
        ul: ({ node, ...props }) => (
          <ul className="list-disc pl-6 my-2" {...props} />
        ),
        ol: ({ node, ...props }) => (
          <ol className="list-decimal pl-6 my-2" {...props} />
        ),
        code: ({ node, ...props }) => (
          <code className="bg-gray-200 rounded px-1" {...props} />
        ),
        // ...add more as needed
      }}
    >
      {text}
    </ReactMarkdown>
  </div>
);

export default MarkdownRenderer;
