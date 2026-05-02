"use client";

import { useEffect, useRef, useState } from "react";
import { getPdfDetails } from "@/lib/api/notebook.api";

export const useSummary = (notebookId: string, selectedPdfIds: string[]) => {
  const [summary, setSummary] = useState("");
  const [suggestedQueries, setSuggestedQueries] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const hasStartedRef = useRef(false);

  useEffect(() => {
    let retryTimer: NodeJS.Timeout;

    const fetchSummary = async (retry = 0) => {
      if (!selectedPdfIds.length) {
        setSummary("");
        setSuggestedQueries([]);
        return;
      }

      if (hasStartedRef.current) return;

      try {
        setIsLoading(true);

        const res = await getPdfDetails(notebookId, selectedPdfIds);

        setSummary(res.summary || "");
        setSuggestedQueries(res.suggested_queries || []);

        if ((res.suggested_queries || []).length === 0 && retry < 5) {
          retryTimer = setTimeout(() => fetchSummary(retry + 1), 1500);
        }
      } catch {
        setSummary("");
        setSuggestedQueries([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSummary();
    return () => clearTimeout(retryTimer);
  }, [notebookId, selectedPdfIds]);

  return {
    summary,
    suggestedQueries,
    isSummaryLoading: isLoading,
    hasStartedRef,
  };
};