"use client";

import { useEffect, useState } from "react";
import Navbar from "@/modules/notebook/components/layout/Navbar";
import PolicyCollectionsSection from "@/modules/notebook/PolicyCollectionsSection";
import { NotebookListItem } from "@/lib/types/notebook";
import { getNotebooks } from "@/lib/api";
import { useRouter } from "next/navigation";

function NotebookContent() {

  const router = useRouter();

 


  // ✅ STATIC FEATURED NOTEBOOKS
  const featuredNotebooks: NotebookListItem[] = [
    {
      notebook_id: "1",
      title: "Education Policy",
      description: "Explore India's education policies and reforms",
      created_at: new Date().toISOString(), // required by type
    },
    {
      notebook_id: "2",
      title: "Digital Governance",
      description: "Understand digital India initiatives and IT laws",
      created_at: new Date().toISOString(),
    },
    {
      notebook_id: "3",
      title: "Union Budget",
      description: "Dive into financial policies and budget insights",
      created_at: new Date().toISOString(),
    },
  ];

  // ✅ API STATE (RECENT)
  const [recentNotebooks, setRecentNotebooks] = useState<NotebookListItem[]>([]);
  const [loading, setLoading] = useState(true);

  const [active, setActive] = useState("");

  useEffect(() => {
    const fetchRecent = async () => {
      try {
        const data = await getNotebooks();

        // ✅ sort latest first (real "recent")
        const sorted = [...data].sort(
          (a, b) =>
            new Date(b.created_at).getTime() -
            new Date(a.created_at).getTime()
        );

        setRecentNotebooks(sorted);

        if (sorted.length > 0) {
          setActive(sorted[0].notebook_id);
        }
      } catch (err) {
        console.error("Failed to fetch recent notebooks");
      } finally {
        setLoading(false);
      }
    };

    fetchRecent();
  }, []);

 

  if (loading) {
    return <div className="p-10">Loading workspaces...</div>;
  }


   const handleSelect = (id: string) => {
  setActive(id);

  // ✅ redirect with notebook_id
  router.push(`/chat?notebook_id=${id}`);
};

  return (
    <div className="min-h-screen bg-white">
      <Navbar />

      <PolicyCollectionsSection
        notebooks={featuredNotebooks}       // ✅ static (featured)
        recentNotebooks={recentNotebooks}   // ✅ API (recent)
        active={active}
        onSelect={handleSelect}
      />
    </div>
  );
}

export default function NotebookPage() {
  return <NotebookContent />;
}