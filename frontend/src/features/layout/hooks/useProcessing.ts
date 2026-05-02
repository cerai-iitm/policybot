"use client";

import { useState } from "react";
import { processPdfStream } from "@/lib/api/pdf.api";
import { PdfItem } from "@/lib/types/pdf";

export const useProcessing = (fetchPdfs: () => Promise<void>) => {
  const [processingLogs, setProcessingLogs] = useState<string[]>([]);
  const [processingOpen, setProcessingOpen] = useState(false);
  const [processingFile, setProcessingFile] = useState<string | null>(null);

  const startProcessing = async (
    notebookId: string,
    pdfId: string,
    filename: string,
    onDone?: () => void
  ) => {
    setProcessingLogs([]);
    setProcessingOpen(true);
    setProcessingFile(filename);

    processPdfStream(notebookId, pdfId, (msg) => {
      setProcessingLogs((prev) => [...prev, msg]);
    })
      .then(async () => {
        await fetchPdfs();
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