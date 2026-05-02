import TopBar from "./sections/TopBar";
import RecentSection from "./sections/RecentSection";

import { NotebookListItem } from "@/lib/types/notebook";
import { createNotebook } from "@/lib/api/notebook.api";
import { DEFAULT_NOTEBOOK } from "@/lib/constants/notebook";
import { useState, useMemo } from "react";
import { getNotebooks } from "@/lib/api/notebook.api";
import { useEffect } from "react";

type Props = {
  notebooks: NotebookListItem[];
  recentNotebooks: NotebookListItem[];
  active: string;
  onSelect: (id: string) => void;
};

const PolicyCollectionsSection = ({
  notebooks,
  active,
  onSelect,
  recentNotebooks,
}: Props) => {
  const [loading, setLoading] = useState(false);
  const [localNotebooks, setLocalNotebooks] = useState<NotebookListItem[]>([]);

  const fetchNotebooks = async () => {
  try {
    const data = await getNotebooks();
    setLocalNotebooks(data);
  } catch (err) {
    console.error("Failed to fetch notebooks", err);
  }
};

useEffect(() => {
  fetchNotebooks();
}, []);



  // 🔍 SEARCH STATE
  const [searchQuery, setSearchQuery] = useState("");

  // ✅ CREATE
  const handleCreateWorkspace = async () => {
    if (loading) return;

    try {
      setLoading(true);

      const res = await createNotebook(DEFAULT_NOTEBOOK);
      const notebookId = res.notebook_id;

      if (!notebookId) throw new Error("Notebook ID missing");

      onSelect(notebookId);
    } catch (err) {
      console.error("Create notebook failed", err);
    } finally {
      setLoading(false);
    }
  };

  // 🔍 FILTER LOGIC (clean + memoized)
const filteredNotebooks = useMemo(() => {
  if (!searchQuery.trim()) return localNotebooks;

  return localNotebooks.filter((nb) =>
    nb.title.toLowerCase().includes(searchQuery.toLowerCase())
  );
}, [searchQuery, localNotebooks]);

  return (
    <div className="mt-10 mx-30">
      <TopBar
        onCreateWorkspace={handleCreateWorkspace}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
      />

      <RecentSection
        recentNotebooks={filteredNotebooks} // ✅ filtered here
        onSelect={onSelect}
        onCreateWorkspace={handleCreateWorkspace}
         onRefresh={fetchNotebooks} 
      />
    </div>
  );
};

export default PolicyCollectionsSection;