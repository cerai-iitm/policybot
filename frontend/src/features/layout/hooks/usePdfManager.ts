"use client";

import { useEffect, useState, useCallback } from "react";
import { listPdfs, uploadPdf, deletePdf } from "@/lib/api/pdf.api";
import { PdfItem } from "@/lib/types/pdf";

export const usePdfManager = (notebookId: string | null) => {
  const [sources, setSources] = useState<PdfItem[]>([]);
  const [checkedPdfs, setCheckedPdfs] = useState<string[]>([]);
  const [selectedFilename, setSelectedFilename] = useState<string | null>(null);
  const [loadingPdfs, setLoadingPdfs] = useState(false);
  const [hasAutoSelected, setHasAutoSelected] = useState(false);
  const [hasFetched, setHasFetched] = useState(false);


  useEffect(() => {
  // 🔥 reset when switching notebook
  setCheckedPdfs([]);
  setHasAutoSelected(false);
}, [notebookId]);


const fetchPdfs = useCallback(async () => {
  if (!notebookId) return;

  setLoadingPdfs(true);
  try {
    const data = await listPdfs(notebookId);

    const mapped: PdfItem[] = data.pdfs.map((pdf: any) => ({
      pdf_id: pdf.stored_filename,
      filename: pdf.original_filename,
      notebook_id: pdf.notebook_id,
      processing_status: pdf.processing_status,
      summary: pdf.summary || "",
      uploaded_at: pdf.uploaded_at,
      suggested_queries: pdf.suggested_queries || [],
    }));

    // ✅ build merged list
    let finalList: PdfItem[] = [];

    setSources((prev) => {
      const map = new Map<string, PdfItem>();

      mapped.forEach((item) => map.set(item.pdf_id, item));
      prev.forEach((item) => {
        if (!map.has(item.pdf_id)) map.set(item.pdf_id, item);
      });

      finalList = Array.from(map.values());
      return finalList;
    });

    setHasFetched(true);

    /* ✅ SAFE AUTO SELECT (OUTSIDE setSources) */
  const completedIds = mapped
  .filter((s) => s.processing_status === "complete")
  .map((s) => s.pdf_id);

/* 🔥 FIRST LOAD → SELECT ALL */
if (!hasAutoSelected && completedIds.length > 0) {
  setCheckedPdfs(completedIds);
  setHasAutoSelected(true);
}

/* 🔥 AFTER UPLOAD → ADD NEW ONES */
else if (hasAutoSelected && completedIds.length > 0) {
  setCheckedPdfs((prev) => {
    const newOnes = completedIds.filter((id) => !prev.includes(id));
    return newOnes.length ? [...prev, ...newOnes] : prev;
  });
}

  } catch (err) {
    console.error("Failed to fetch PDFs", err);
  } finally {
    setLoadingPdfs(false);
  }
}, [notebookId, hasAutoSelected]); // ✅ add dependency


  /* ✅ FIX: now dependency is safe */
  useEffect(() => {
    fetchPdfs();
  }, [fetchPdfs]);

  /* ---------------- RENAME ---------------- */
  const handleRenamePdf = async (pdfId: string, newName: string) => {
    setSources((prev) =>
      prev.map((item) =>
        item.pdf_id === pdfId
          ? { ...item, filename: newName }
          : item
      )
    );

    try {
      // TODO: real API
      await fetchPdfs();
    } catch (err) {
      console.error("Rename failed", err);
      await fetchPdfs();
    }
  };

  /* ---------------- UPLOAD ---------------- */
  const handleUploadPdf = async (file: File) => {
    if (!notebookId) return null;

    const res = await uploadPdf(notebookId, file);

    const newPdf: PdfItem = {
      pdf_id: res.stored_filename,
      filename: res.original_filename,
      notebook_id: res.notebook_id,
      processing_status: res.processing_status,
      summary: "",
      uploaded_at: res.uploaded_at,
      suggested_queries: [],
    };

    setSources((prev) => {
      const exists = prev.some((p) => p.pdf_id === newPdf.pdf_id);
      if (exists) return prev;
      return [newPdf, ...prev];
    });

    return res;
  };

  /* ---------------- DELETE ---------------- */
  const handleDeletePdf = async (pdfId: string) => {
    setSources((prev) => prev.filter((s) => s.pdf_id !== pdfId));
    setCheckedPdfs((prev) => prev.filter((id) => id !== pdfId));

    try {
      await deletePdf(pdfId);
      await fetchPdfs();
    } catch (err) {
      console.error("Delete failed", err);
      await fetchPdfs();
    }
  };

  /* ---------------- SELECTION ---------------- */
  const handleTogglePdf = (pdfId: string) => {
    setCheckedPdfs((prev) =>
      prev.includes(pdfId)
        ? prev.filter((id) => id !== pdfId)
        : [...prev, pdfId]
    );
  };

const handleSelectAll = () => {
  const all = sources
    .filter((s) => s.processing_status === "complete")
    .map((s) => s.pdf_id);

  const areAllSelected = all.every((id) =>
    checkedPdfs.includes(id)
  );

  setCheckedPdfs(areAllSelected ? [] : all);
};

  return {
    sources,
    checkedPdfs,
    selectedFilename,
    setSelectedFilename,
    fetchPdfs,
    handleUploadPdf,
    handleDeletePdf,
    handleTogglePdf,
    handleSelectAll,
    handleRenamePdf,
    loadingPdfs,
    hasFetched
  };
};