"use client";

import React from "react";

/* ---------------- ASSETS ---------------- */
import selectAllChecked from "@/assets/marked.png";
import selectAllUnchecked from "@/assets/unmarked.png";
import selectAllIndeterminate from "@/assets/partialmarked.png";
import sidebaricon from "@/assets/sidebar.png";

/* ---------------- LAYOUT ---------------- */
import BaseSideContainer from "@/features/layout/components/BaseSideContainer";

/* ---------------- COMPONENTS ---------------- */
import FileUpload from "./components/fileupload/FileUpload";
import SourceItem from "./components/SourceItem/SourceItem";
import SelectAllRow from "./components/SelectAllRow";
import Title from "./components/Title";

/* ---------------- TYPES ---------------- */
import { SidebarProps } from "./types";

const LeftSidebar: React.FC<SidebarProps & {
  title: string;
  notebookId: string;
  onUpdateTitle: (newTitle: string) => Promise<void>;
}> = ({
  title,
  sources,
  checkedPdfs,
  onTogglePdf,
  onSelectPdf,
  onDeletePdf,
  onSelectAll,
  collapsed,
  onToggleCollapse,
  onUploadPdf,
  onOpenProcessing,
  onRenamePdf,
  notebookId,
  onUpdateTitle
  
}) => {
  /* ---------------- DERIVED STATE ---------------- */

  const allIds = sources.map((s) => s.pdf_id);

  const areAllSelected =
    allIds.length > 0 &&
    allIds.every((id) => checkedPdfs.includes(id));

  const areNoneSelected = allIds.every(
    (id) => !checkedPdfs.includes(id)
  );

  const selectAllIconSrc = areAllSelected
    ? selectAllChecked.src
    : areNoneSelected
    ? selectAllUnchecked.src
    : selectAllIndeterminate.src;

  /* ---------------- RENDER ---------------- */

  return (
    <BaseSideContainer
      title="Policies"
      icon={sidebaricon}
      collapsed={collapsed}
      onToggle={onToggleCollapse}
    >
      <div className="h-full flex flex-col bg-white">

        {/* ---------- TITLE ---------- */}
       {!collapsed && (
  <Title
  title={
    title === "Loading..."
      ? "Loading..." // keep raw text
      : title
  }
  notebookId={notebookId}
  onUpdate={onUpdateTitle}
/>
)}

        {/* ---------- UPLOAD ---------- */}
        <div className="px-6 pt-2">
          <FileUpload
            onFileSelect={onUploadPdf}
            collapsed={collapsed}
          />
        </div>

        {/* ---------- SELECT ALL ---------- */}
        {!collapsed && sources.length > 0 && (
          <SelectAllRow
            iconSrc={selectAllIconSrc}
            onToggle={onSelectAll}
          />
        )}

        {/* ---------- SOURCE LIST ---------- */}
       {/* ---------- SOURCE LIST ---------- */}
<div className="flex-1 overflow-y-auto pt-2 px-2 pb-4 custom-scrollbar">

  {/* ✅ EMPTY STATE */}
  {!collapsed && sources.length === 0 && (
    <div className="h-full flex flex-col items-center justify-center text-center px-6">
      <p className="text-sm text-slate-500">
        Saved sources will appear here
      </p>
      <p className="text-sm text-slate-400 mt-1">
        Click <span className="font-medium text-slate-600">Add source</span> above to add PDF
      </p>
    </div>
  )}

  {/* ✅ LIST */}
  <div className="space-y-1">
    {sources.map((item) => (
      <SourceItem
        key={item.pdf_id}
        item={item}
        checked={checkedPdfs.includes(item.pdf_id)}
        onToggle={onTogglePdf}
        onClick={() => {
          if (item.processing_status !== "complete") {
            onOpenProcessing(item);
          } else {
            onSelectPdf(item.pdf_id);
          }
        }}
        onDelete={onDeletePdf}
        onRename={onRenamePdf}
        isCollapsedSidebar={collapsed}
      />
    ))}
  </div>

</div>

      </div>
    </BaseSideContainer>
  );
};

export default LeftSidebar;