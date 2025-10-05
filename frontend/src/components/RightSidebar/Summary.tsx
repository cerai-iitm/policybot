import React, { useEffect, useState } from "react";
import MarkdownRenderer from "../common/Markdown";

interface SummaryProps {
  filename: string | null;
}

const Summary: React.FC<SummaryProps> = ({ filename }) => {
  const [summary, setSummary] = useState<string>("No summary available.");
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (!filename) {
      setSummary("");
      return;
    }
    setLoading(true);
    fetch(`http://localhost:8000/pdf/summary/${encodeURIComponent(filename)}`)
      .then((res) => res.json())
      .then((data) => setSummary(data.summary))
      .catch(() => setSummary("No summary available."))
      .finally(() => setLoading(false));
  }, [filename]);

  if (!filename) return null;

  return (
    <div className="mb-4 p-2 bg-gray-100 rounded">
      <h3 className="font-semibold mb-2">Summary</h3>
      <MarkdownRenderer text={loading ? "Loading summary..." : summary} />
    </div>
  );
};

export default Summary;
