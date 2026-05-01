"use client";

import { useState, useEffect } from "react";

import CreateWorkspaceCard from "../components/cards/CreateWorkspaceCard";
import RecentNotebookCard from "../components/cards/RecentNotebookCard/RecentNotebookCard";
import CommonModal from "@/components/popup";

import { NotebookListItem } from "@/lib/types/notebook";
import { updateNotebook, deleteNotebook } from "@/lib/api/notebook.api";
import { createNotebook } from "@/lib/api/notebook.api";
import { DEFAULT_NOTEBOOK } from "@/lib/constants/notebook";
import { useRouter } from "next/navigation";

type Props = {
  recentNotebooks?: NotebookListItem[];
  onSelect: (id: string) => void;
};

const RecentSection = ({ recentNotebooks = [], onSelect }: Props) => {
  const router = useRouter();


  const [modalType, setModalType] = useState<"rename" | "delete" | null>(null);
  const [selectedNotebook, setSelectedNotebook] =
    useState<NotebookListItem | null>(null);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);

  const [localNotebooks, setLocalNotebooks] = useState<NotebookListItem[]>([]);


  const handleCreateWorkspace = async () => {
  if (loading) return;

  try {
    setLoading(true);

    const res = await createNotebook(DEFAULT_NOTEBOOK);

    const notebookId = res.notebook_id;

    if (!notebookId) throw new Error("Notebook ID missing");

    // 🚀 redirect to chat
    router.push(`/chat?notebook_id=${notebookId}`);

  } catch (err) {
    console.error("Create notebook failed", err);
  } finally {
    setLoading(false);
  }
};



  // ✅ Sync props → state
  useEffect(() => {
    setLocalNotebooks(recentNotebooks);
  }, [recentNotebooks]);

  // -----------------------------
  // ACTION HANDLERS
  // -----------------------------

  const handleRename = (nb: NotebookListItem) => {
    setSelectedNotebook(nb);
    setInputValue(nb.title);
    setModalType("rename");
  };

  const handleDelete = (nb: NotebookListItem) => {
    setSelectedNotebook(nb);
    setModalType("delete");
  };

  const closeModal = () => {
    if (loading) return; // ✅ prevent closing during API call
    setModalType(null);
    setSelectedNotebook(null);
  };

  // -----------------------------
  // CONFIRM HANDLER
  // -----------------------------

  const handleConfirm = async () => {
    if (!selectedNotebook || loading) return; // ✅ double-click guard

    try {
      setLoading(true);

      // ✅ RENAME
      if (modalType === "rename") {
        if (!inputValue.trim()) return;

        const updated = await updateNotebook({
          notebook_id: selectedNotebook.notebook_id,
          title: inputValue.trim(),
          description: selectedNotebook.description ?? "Default Description", // ✅ FIXED
        });

        setLocalNotebooks((prev) =>
          prev.map((nb) =>
            nb.notebook_id === selectedNotebook.notebook_id
              ? { ...nb, title: updated.title }
              : nb
          )
        );
      }

      // ✅ DELETE
      if (modalType === "delete") {
        await deleteNotebook(selectedNotebook.notebook_id);

        setLocalNotebooks((prev) =>
          prev.filter(
            (nb) => nb.notebook_id !== selectedNotebook.notebook_id
          )
        );
      }

      closeModal();
    } catch (err) {
      console.error("Operation failed", err);
    } finally {
      setLoading(false);
    }
  };

  // -----------------------------
  // UI
  // -----------------------------

  return (
    <>
      <h2 className="text-xl font-semibold mb-6">
        Recent Workspaces
      </h2>

      <div className="flex gap-6 mb-12 overflow-x-auto no-scrollbar">
       <CreateWorkspaceCard
  onClick={handleCreateWorkspace}
  disabled={loading}
/>

        {localNotebooks.map((nb) => (
          <div key={nb.notebook_id} className="shrink-0">
            <RecentNotebookCard
  title={nb.title}
  desc={nb.description || "No description available"}
  createdAt={nb.created_at}
  sourceCount={nb.processed_pdf_count} // ✅ ADD THIS
  onClick={() => onSelect(nb.notebook_id)}
  onRename={() => handleRename(nb)}
  onDelete={() => handleDelete(nb)}
/>
          </div>
        ))}
      </div>

      {/* ✅ MODAL */}
      <CommonModal
        isOpen={modalType !== null}
        title={
          modalType === "rename"
            ? "Edit Notebook"
            : `Delete ${selectedNotebook?.title}?`
        }
        description={
          modalType === "delete"
            ? "This notebook will be permanently deleted. This action cannot be undone."
            : undefined
        }
        showInput={modalType === "rename"}
        inputValue={inputValue}
        onInputChange={setInputValue}
        confirmText={modalType === "rename" ? "Save" : "Delete"}
        isDanger={modalType === "delete"}
        onConfirm={handleConfirm}
        onCancel={closeModal}
        isLoading={loading}
      />
    </>
  );
};

export default RecentSection;