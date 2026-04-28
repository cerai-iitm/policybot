"use client";

import React, { useState } from "react";
import { usePathname } from "next/navigation";

import Topbar from "@/features/topbar/Topbar";
import LeftSidebar from "@/features/leftsidebar/LeftSidebar";
import ChatView from "@/features/chat/ChatView";
import RightSidebar from "@/features/rightsidebar/RightSidebar";

import { AdminProvider } from "../chat/context/AdminContext";
import { useEffect } from "react";
import { listPdfs } from "@/lib/api/pdf.api";
import { PdfItem } from "@/lib/types/pdf";
import { useSearchParams } from "next/navigation";
import { uploadPdf } from "@/lib/api/pdf.api";

interface MainLayoutProps {
  isAdmin?: boolean;
  notebookId?: string | null;
}

export default function MainLayout({
  isAdmin: isAdminProp,
}: MainLayoutProps) {
  const pathname = usePathname();

  const isAdmin =
    isAdminProp ?? (pathname?.endsWith("/config") ?? false);

  /* ---------------- STATE ---------------- */

  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);

  const [checkedPdfs, setCheckedPdfs] = useState<string[]>([]);
  const [selectedFilename, setSelectedFilename] =
    useState<string | null>(null);

  const [sources, setSources] = useState<PdfItem[]>([]);
const [loadingPdfs, setLoadingPdfs] = useState(false);

const searchParams = useSearchParams();
const notebookId = searchParams.get("notebook_id");

useEffect(() => {
  if (!notebookId) return;

  const fetchPdfs = async () => {
    setLoadingPdfs(true);
    try {
      const data = await listPdfs(notebookId);

      const mapped: PdfItem[] = data.pdfs.map((pdf: any) => ({
        pdf_id: pdf.stored_filename,
        filename: pdf.original_filename,
        notebook_id: pdf.notebook_id,
        processing_status: pdf.processing_status,
        summary: pdf.summary,
        uploaded_at: pdf.uploaded_at,
        suggested_queries: pdf.suggested_queries || [],
      }));

      setSources(mapped);
    } catch (err) {
      console.error("Failed to fetch PDFs", err);
    } finally {
      setLoadingPdfs(false);
    }
  };

  fetchPdfs();
}, [notebookId]);

  /* ---------------- HANDLERS ---------------- */

  const handleUploadPdf = async (file: File) => {
  if (!notebookId) return;

  try {
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

    // ✅ optimistic UI update
    setSources((prev) => [newPdf, ...prev]);

  } catch (err) {
    console.error("Upload failed", err);
  }
};



  const handleTogglePdf = (pdfId: string) => {
  setCheckedPdfs((prev) =>
    prev.includes(pdfId)
      ? prev.filter((id) => id !== pdfId)
      : [...prev, pdfId]
  );
};
  const handleSelectPdf = (filename: string) => {
    setSelectedFilename(filename);
  };

 const handleDeletePdf = (pdfId: string) => {
  setCheckedPdfs((prev) =>
    prev.filter((id) => id !== pdfId)
  );
};

const handleSelectAll = () => {
  const all = sources.map((s) => s.pdf_id);

  const areAllSelected = all.every((id) =>
    checkedPdfs.includes(id)
  );

  setCheckedPdfs(areAllSelected ? [] : all);
};

  /* ---------------- GRID WIDTH LOGIC ---------------- */

  const leftWidth = leftCollapsed ? "72px" : "285px";
  const rightWidth = rightCollapsed ? "72px" : "420px";

  const gridTemplate = `${leftWidth} 1fr ${rightWidth}`;

  /* ---------------- UI ---------------- */

  return (
    <AdminProvider isAdmin={isAdmin}>
      <div className="h-screen w-full bg-[#F1F5F9] flex flex-col overflow-hidden">

        <Topbar />

        <main className="flex-1 px-6 pb-5 overflow-hidden">
          <div
            className="h-full grid gap-3 transition-all duration-300"
            style={{ gridTemplateColumns: gridTemplate }}
          >

            {/* LEFT */}
           <LeftSidebar
  collapsed={leftCollapsed}
  onToggleCollapse={() => setLeftCollapsed((prev) => !prev)}
  sources={sources}
  checkedPdfs={checkedPdfs}
  onTogglePdf={handleTogglePdf}
  onSelectPdf={(pdfId) => setSelectedFilename(pdfId)}
  onDeletePdf={handleDeletePdf}
  onSelectAll={handleSelectAll}
  onUploadPdf={handleUploadPdf}
/>

            {/* CENTER */}
            <ChatView />

            {/* RIGHT */}
            <RightSidebar
              collapsed={rightCollapsed}
              onToggleCollapse={() =>
                setRightCollapsed((prev) => !prev)
              }
            />

          </div>
        </main>
      </div>
    </AdminProvider>
  );
}