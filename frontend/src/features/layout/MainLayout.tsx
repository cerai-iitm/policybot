"use client";

import React, { useState } from "react";
import { usePathname, useSearchParams } from "next/navigation";

import Topbar from "@/features/topbar/Topbar";
import LeftSidebar from "@/features/leftsidebar/LeftSidebar";
import ChatView from "@/features/chat/ChatView";
import RightSidebar from "@/features/rightsidebar/RightSidebar";

import { AdminProvider } from "../chat/context/AdminContext";
import ProcessingModal from "@/features/leftsidebar/components/processing/ProcessingModal";
import CommonModal from "@/components/popup";

/* 🔥 HOOKS */
import { usePdfManager } from "./hooks/usePdfManager";
import { useProcessing } from "./hooks/useProcessing";
import { usePdfModal } from "./hooks/usePdfModal";
import { useNotebook } from "./hooks/useNotebook";



export default function MainLayout() {
  const pathname = usePathname();
  const isAdmin = pathname?.endsWith("/config");

  const searchParams = useSearchParams();
  const notebookId = searchParams.get("notebook_id");

  /* ✅ SAME STATE (unchanged) */
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);

  /* 🔥 HOOKS */
  const pdf = usePdfManager(notebookId);
  const processing = useProcessing(pdf.fetchPdfs);
  const notebookData = useNotebook(notebookId);

 const modal = usePdfModal(
  async (id) => {
    await pdf.handleDeletePdf(id);
  },
  async (id, name) => {
    await pdf.handleRenamePdf(id, name); // ✅ CLEAN
  }
);



  /* 🔥 UPLOAD (same flow preserved) */
  const handleUpload = async (file: File) => {
    const res = await pdf.handleUploadPdf(file);
    if (!res) return;

    processing.startProcessing(
      res.notebook_id,
      res.stored_filename,
      res.original_filename,
      () => pdf.setSelectedFilename(res.stored_filename)
    );
  };

  /* 🔥 EXACT SAME GRID LOGIC */
  const leftWidth = leftCollapsed ? "72px" : "285px";
  const rightWidth = rightCollapsed ? "72px" : "420px";
  const gridTemplate = `${leftWidth} 1fr ${rightWidth}`;

  return (
    <AdminProvider isAdmin={isAdmin}>
      {/* ✅ SAME WRAPPER (CRITICAL) */}
      <div className="h-screen w-full bg-[#F1F5F9] flex flex-col overflow-hidden">

        <Topbar />

        {/* ✅ SAME MAIN WRAPPER */}
        <main className="flex-1 px-6 pb-5 overflow-hidden">
          <div
            className="h-full grid gap-3 transition-all duration-300"
            style={{ gridTemplateColumns: gridTemplate }}
          >

            {/* LEFT */}
            <LeftSidebar
            title={notebookData.notebook?.title || "Loading..."}
            notebookId={notebookId || ""}
            onUpdateTitle={notebookData.updateTitle}
              collapsed={leftCollapsed}
              onToggleCollapse={() => setLeftCollapsed((p) => !p)}
              sources={pdf.sources}
              checkedPdfs={pdf.checkedPdfs}
              onTogglePdf={pdf.handleTogglePdf}
              onSelectPdf={pdf.setSelectedFilename}
              onDeletePdf={modal.openDelete}
              onRenamePdf={modal.openRename}
              onSelectAll={pdf.handleSelectAll}
              onUploadPdf={handleUpload}
              onOpenProcessing={(item) =>
                processing.startProcessing(
                  item.notebook_id,
                  item.pdf_id,
                  item.filename,
                  () => pdf.setSelectedFilename(item.pdf_id)
                )
              }
            />

            {/* CENTER */}
            <ChatView
  notebookId={notebookId || ""}
  selectedPdfIds={pdf.checkedPdfs}
/>

            {/* RIGHT */}
            <RightSidebar
              collapsed={rightCollapsed}
              onToggleCollapse={() => setRightCollapsed((p) => !p)}
            />

            {/* ✅ SAME MODALS POSITION */}
            <ProcessingModal
              open={processing.processingOpen}
              onClose={() => processing.setProcessingOpen(false)}
              logs={processing.processingLogs}
              filename={processing.processingFile || ""}
            />

            <CommonModal
              isOpen={modal.modalOpen}
              title={
                modal.modalType === "delete"
                  ? "Delete File"
                  : "Rename File"
              }
              description={
                modal.modalType === "delete"
                  ? "Are you sure you want to delete this file? This action cannot be undone."
                  : "Enter a new name for this file."
              }
              showInput={modal.modalType === "rename"}
              inputValue={modal.renameValue}
              onInputChange={modal.setRenameValue}
              confirmText={
                modal.modalType === "delete" ? "Delete" : "Rename"
              }
              cancelText="Cancel"
              isDanger={modal.modalType === "delete"}
              isLoading={modal.loading}
              onCancel={() => {
                if (modal.loading) return;
                modal.setModalOpen(false);
              }}
              onConfirm={modal.confirm}
            />

          </div>
        </main>
      </div>
    </AdminProvider>
  );
}