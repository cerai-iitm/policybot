"use client";

import { useState } from "react";
import { processPdfStream } from "@/lib/api/pdf.api";

export const useProcessing = (
  fetchPdfs: () => Promise<void>,
  refetchNotebook?: () => Promise<void>
) => {
  const [processingLogs, setProcessingLogs] = useState<string[]>([]);
  const [processingOpen, setProcessingOpen] = useState(false);
  const [processingFile, setProcessingFile] = useState<string | null>(null);

  const startProcessing = async (
    notebookId: string,
    pdfId: string,
    filename: string,
    onTitleUpdate?: (title: string) => void,
    onDone?: () => void
  ) => {
    setProcessingLogs([]);
    setProcessingOpen(true);
    setProcessingFile(filename);

    processPdfStream(notebookId, pdfId, (msg) => {
      // Check if this is a notebook title update from SSE
      if (msg.startsWith('{"type":"notebook_title"')) {
        try {
          const parsed = JSON.parse(msg);
          if (parsed.type === "notebook_title" && parsed.title) {
            console.log("NOTEBOOK TITLE FROM SSE:", parsed.title);
            onTitleUpdate?.(parsed.title);
          }
        } catch {
          console.error("Failed to parse notebook title from SSE:", msg);
        }
      }
      setProcessingLogs((prev) => [...prev, msg]);
    })
      .then(async () => {
        await fetchPdfs();
        await refetchNotebook?.();
        onDone?.();
        setProcessingOpen(false);
      })
      .catch(console.error);
  };

  return {
    processingLogs,
    processingOpen,
    processingFile,
    setProcessingOpen,
    startProcessing,
  };
};