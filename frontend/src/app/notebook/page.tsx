"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import Navbar from "@/components/notebook/Navbar";
import PolicyCollectionsSection from "@/components/notebook//PolicyCollectionsSection";
import PolicyTopicsSection from "@/components/notebook/PolicyTopicsSection";

import { listNotebooks, listPdfs } from "@/lib/router";
import { NotebookListItem, FirstNotebookPDFItem } from "@/lib/interfaces";

export default function NotebookPage() {
  const [notebooks, setNotebooks] = useState<NotebookListItem[]>([]);
  const [activeCollection, setActiveCollection] = useState<string>("");
  const [pdfs, setPdfs] = useState<FirstNotebookPDFItem[]>([]);
  const [loading, setLoading] = useState(false);

  const router = useRouter();
  const searchParams = useSearchParams();

  // 🔹 Load notebooks
  useEffect(() => {
    const preferred = searchParams.get("preferred");

    const fetchNotebooks = async () => {
      try {
        const data = await listNotebooks();
        setNotebooks(data.notebooks);

        if (preferred) {
          const pref = preferred.toLowerCase();

          const match = data.notebooks.find((n) =>
            n.title.toLowerCase().includes(pref)
          );

          if (match) setActiveCollection(match.notebook_id);
          else if (data.first_notebook_id)
            setActiveCollection(data.first_notebook_id);

          router.replace("/notebook");
          return;
        }

        if (data.first_notebook_id) {
          setActiveCollection(data.first_notebook_id);
        }
      } catch (err) {
        console.error(err);
      }
    };

    fetchNotebooks();
  }, []);

  // 🔹 Load PDFs
  useEffect(() => {
    if (!activeCollection) return;

    const fetchPdfs = async () => {
      try {
        setLoading(true);
        const data = await listPdfs(activeCollection);

        setPdfs(data.pdfs);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchPdfs();
  }, [activeCollection]);

  const activeNotebookTitle =
    notebooks.find((n) => n.notebook_id === activeCollection)?.title || "";

  return (
    <div className="min-h-screen bg-white">
      <Navbar />

      <PolicyCollectionsSection
        notebooks={notebooks}
        active={activeCollection}
        onSelect={setActiveCollection}
      />

      <PolicyTopicsSection
        pdfs={pdfs}
        loading={loading}
        title={activeNotebookTitle}
        notebookId={activeCollection}
      />
    </div>
  );
}