// FILE: D:\buddi\Policybot\frontend\src\features\leftsidebar\LeftSidebar.tsx

"use client";

import React from "react";

import selectAllChecked from "@/assets/marked.png";
import selectAllUnchecked from "@/assets/unmarked.png";
import selectAllIndeterminate from "@/assets/partialmarked.png";
import sidebaricon from "@/assets/sidebar.png";

import BaseSideContainer from "@/features/layout/components/BaseSideContainer";

import FileUpload from "./components/FileUpload";
import SourceItem from "./components/SourceItem";
import SelectAllRow from "./components/SelectAllRow";
import Title from "./components/Title";

import { SidebarProps } from "./types";



const LeftSidebar: React.FC<SidebarProps> = ({
  sources,
  checkedPdfs,
  onTogglePdf,
  onSelectPdf,
  onDeletePdf,
  onSelectAll,
  collapsed,
  onToggleCollapse
}) => {
  const allNames = sources.map((s) => s.filename);

  const areAllSelected =
    allNames.length > 0 &&
    allNames.every((n) => checkedPdfs.includes(n));

  const areNoneSelected = allNames.every(
    (n) => !checkedPdfs.includes(n)
  );

  const selectAllIconSrc = areAllSelected
    ? selectAllChecked.src
    : areNoneSelected
    ? selectAllUnchecked.src
    : selectAllIndeterminate.src;

  return (
  <BaseSideContainer
  title="Policies"
  icon={sidebaricon}
  collapsed={collapsed}
  onToggle={onToggleCollapse}
>
  <div className="h-full flex flex-col bg-white">

    {/* SECTION TITLE */}
   {!collapsed && <Title title="Education & Academic Policies" />}

    {/* UPLOAD BLOCK */}
    <div className="px-6 pt-2 ">
     <FileUpload collapsed={collapsed} />
    </div>

    {/* SELECT ALL */}
    {!collapsed && sources.length > 0 && (
  <SelectAllRow
    iconSrc={selectAllIconSrc}
    onToggle={onSelectAll}
  />
)}

    {/* LIST */}
    <div className="flex-1 overflow-y-auto pt-2 space-y-1 px-2 pb-4">
      {sources.map((item) => (
       <SourceItem
  key={item.pdf_id}
  item={item}
  checked={checkedPdfs.includes(item.filename)}
  onToggle={onTogglePdf}
  onClick={() => onSelectPdf(item.filename)}
  onDelete={onDeletePdf}
  isCollapsedSidebar={collapsed}   // ✅ FIX HERE
/>
      ))}
    </div>

  </div>
</BaseSideContainer>
  );
};

export default LeftSidebar;