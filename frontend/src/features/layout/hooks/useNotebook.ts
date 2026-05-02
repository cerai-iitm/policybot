"use client";

import { useEffect, useState, useCallback } from "react";
import {
  getNotebook,
  updateNotebook,
} from "@/lib/api/notebook.api";
import { NotebookResponse } from "@/lib/types/notebook";

export const useNotebook = (notebookId: string | null) => {
  const [notebook, setNotebook] =
    useState<NotebookResponse | null>(null);

  const [loading, setLoading] = useState(false);
  const [updating, setUpdating] = useState(false); // ✅ NEW

  /* ---------------- FETCH ---------------- */
  const fetchNotebook = useCallback(async () => {
    if (!notebookId) return;

    setLoading(true);
    try {
      const res = await getNotebook(notebookId);

      const nb = res?.notebooks?.[0];

      if (nb) {
        setNotebook(nb);
      }
    } catch (err) {
      console.error("Failed to fetch notebook", err);
    } finally {
      setLoading(false);
    }
  }, [notebookId]);

  useEffect(() => {
    fetchNotebook();
  }, [fetchNotebook]);

  /* ---------------- UPDATE TITLE ---------------- */
  const updateTitle = useCallback(
    async (newTitle: string) => {
      if (!notebookId || !notebook) return;

      const trimmed = newTitle.trim();
      if (!trimmed || trimmed === notebook.title) return;

      try {
        setUpdating(true);

        // ✅ Optimistic update (instant UI)
        setNotebook((prev) =>
          prev ? { ...prev, title: trimmed } : prev
        );

        await updateNotebook({
          notebook_id: notebookId,
          title: trimmed,
          description: notebook.description || "",
        });

        // ✅ Sync with backend
        await fetchNotebook();
      } catch (err) {
        console.error("Failed to update notebook title", err);

        // ❌ rollback on error
        await fetchNotebook();
      } finally {
        setUpdating(false);
      }
    },
    [notebookId, notebook, fetchNotebook]
  );

  return {
    notebook,
    loading,
    updating, // optional (for future UI)
    refetch: fetchNotebook,
    updateTitle, // ✅ exposed
  };
};