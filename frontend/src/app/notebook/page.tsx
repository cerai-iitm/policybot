"use client";

import Navbar from "@/features/notebook/components/Navbar";
import PolicyCollectionsSection from "@/features/notebook/PolicyCollectionsSection";
import { NotebookListItem } from "@/types";

function NotebookContent() {
  // ✅ STATIC NOTEBOOK DATA
  const notebooks: NotebookListItem[] = [
    {
      notebook_id: "1",
      title: "Education Policy",
      description: "Explore India's education policies and reforms",
    },
    {
      notebook_id: "2",
      title: "Digital Governance",
      description: "Understand digital India initiatives and IT laws",
    },
    {
      notebook_id: "3",
      title: "Union Budget",
      description: "Dive into financial policies and budget insights",
    },
  ];

  const activeCollection = "1";

  return (
    <div className="min-h-screen bg-white">
      <Navbar />

      <PolicyCollectionsSection
        notebooks={notebooks}
        active={activeCollection}
        onSelect={() => {}} // no-op (UI only)
      />
    </div>
  );
}

export default function NotebookPage() {
  return <NotebookContent />;
}