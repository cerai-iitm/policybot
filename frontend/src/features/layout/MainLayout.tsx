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
import { deletePdf } from "@/lib/api/pdf.api";
import { processPdfStream } from "@/lib/api/pdf.api";
import ProcessingModal from "@/features/leftsidebar/components/processing/ProcessingModal";

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
const [processingLogs, setProcessingLogs] = useState<string[]>([]);
const [processingOpen, setProcessingOpen] = useState(false);
const [processingFile, setProcessingFile] = useState<string | null>(null);


const fetchPdfs = async () => {
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

    setSources((prev) => {
  const map = new Map<string, PdfItem>();

  // ✅ Put latest backend data first
  mapped.forEach((item) => {
    map.set(item.pdf_id, item);
  });

  // ✅ Preserve any optimistic items not yet in backend
  prev.forEach((item) => {
    if (!map.has(item.pdf_id)) {
      map.set(item.pdf_id, item);
    }
  });

  return Array.from(map.values());
});
  } catch (err) {
    console.error("Failed to fetch PDFs", err);
  } finally {
    setLoadingPdfs(false);
  }
};


useEffect(() => {
  fetchPdfs();
}, [notebookId]);

  /* ---------------- HANDLERS ---------------- */

const handleUploadPdf = async (file: File) => {
  if (!notebookId) return;

  try {
    // 1️⃣ Upload
    const res = await uploadPdf(notebookId, file);

    const newPdf: PdfItem = {
      pdf_id: res.stored_filename,
      filename: res.original_filename,
      notebook_id: res.notebook_id,
      processing_status: res.processing_status, // "uploaded"
      summary: "",
      uploaded_at: res.uploaded_at,
      suggested_queries: [],
    };

    // 2️⃣ Optimistic UI
    setSources((prev) => {
  const exists = prev.some((p) => p.pdf_id === newPdf.pdf_id);
  if (exists) return prev;

  return [newPdf, ...prev];
});

    // 3️⃣ Start processing (🔥 IMPORTANT)
    setProcessingLogs([]);
setProcessingOpen(true);
setProcessingFile(res.original_filename);

processPdfStream(
  res.notebook_id,
  res.stored_filename,
  (msg) => {
    setProcessingLogs((prev) => [...prev, msg]);
  }
)
  .then(async () => {
    setProcessingLogs((prev) => [...prev, "Completed ✅"]);

    await fetchPdfs(); // backend sync

    setSelectedFilename(res.stored_filename);

    setProcessingOpen(false);
  })
  .catch(console.error);
 

   

  } catch (err) {
    console.error("Upload/Process failed", err);
  }
};


const handleOpenProcessing = (item: PdfItem) => {
  if (item.processing_status === "complete") return;

  setProcessingLogs([]);
  setProcessingOpen(true);
  setProcessingFile(item.filename);


  processPdfStream(
  item.notebook_id,
  item.pdf_id,
  (msg) => {
    setProcessingLogs((prev) => [...prev, msg]);
  }
)
  .then(async () => {
    await fetchPdfs();

    // ✅ auto select after processing
    setSelectedFilename(item.pdf_id);

    // ✅ close modal
    setProcessingOpen(false);
  })
  .catch(console.error);
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

const handleDeletePdf = async (pdfId: string) => {
  if (!notebookId) return;

  // ✅ Optimistic UI update
  setSources((prev) => prev.filter((s) => s.pdf_id !== pdfId));
  setCheckedPdfs((prev) => prev.filter((id) => id !== pdfId));

  try {
    await deletePdf(pdfId);

    // ✅ Re-sync with backend (important)
    await fetchPdfs();

  } catch (err) {
    console.error("Delete failed", err);

    // ❗ Rollback (optional but professional)
    await fetchPdfs();
  }
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
  onOpenProcessing={handleOpenProcessing}
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

            <ProcessingModal
  open={processingOpen}
  onClose={() => setProcessingOpen(false)}
  logs={processingLogs}
  filename={processingFile || ""}
/>

          </div>
        </main>
      </div>
    </AdminProvider>
  );
}