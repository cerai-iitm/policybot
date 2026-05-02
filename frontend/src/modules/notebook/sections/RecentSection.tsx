"use client";

import { useState } from "react";

import CreateWorkspaceCard from "../components/cards/CreateWorkspaceCard";
import RecentNotebookCard from "../components/cards/RecentNotebookCard/RecentNotebookCard";
import CommonModal from "@/components/popup";

import { NotebookListItem } from "@/lib/types/notebook";
import { updateNotebook, deleteNotebook } from "@/lib/api/notebook.api";
import { useAuth } from "@/lib/hooks/useAuth";

type Props = {
  recentNotebooks?: NotebookListItem[];
  onSelect: (id: string) => void;
  onCreateWorkspace: () => void;
   onRefresh: () => void;
};

const RecentSection = ({
  recentNotebooks = [],
  onSelect,
  onCreateWorkspace,
  onRefresh
}: Props) => {
  const { isDemoUser } = useAuth();

  const [modalType, setModalType] = useState<"rename" | "delete" | null>(null);
  const [selectedNotebook, setSelectedNotebook] =
    useState<NotebookListItem | null>(null);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);

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
    if (loading) return;
    setModalType(null);
    setSelectedNotebook(null);
  };

  // -----------------------------
  // CONFIRM HANDLER
  // -----------------------------

const handleConfirm = async () => {
  if (!selectedNotebook || loading) return;

  try {
    setLoading(true);

    if (modalType === "rename") {
      if (!inputValue.trim()) return;

      await updateNotebook({
        notebook_id: selectedNotebook.notebook_id,
        title: inputValue.trim(),
        description:
          selectedNotebook.description ?? "Default Description",
      });
    }

    if (modalType === "delete") {
      await deleteNotebook(selectedNotebook.notebook_id);
    }

    onRefresh(); // ✅ KEY LINE
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
        {isDemoUser ? "Featured Workspaces" : "Recent Workspaces"}
      </h2>

      <div className="flex gap-6 mb-12 overflow-x-auto no-scrollbar">
        {!isDemoUser && (
          <CreateWorkspaceCard
            onClick={onCreateWorkspace}
            disabled={loading}
          />
        )}

        {recentNotebooks.map((nb) => (
          <div key={nb.notebook_id} className="shrink-0">
            <RecentNotebookCard
              title={nb.title}
              desc={nb.description || "No description available"}
              createdAt={nb.created_at}
              sourceCount={nb.processed_pdf_count}
              onClick={() => onSelect(nb.notebook_id)}
              onRename={() => handleRename(nb)}
              onDelete={() => handleDelete(nb)}
            />
          </div>
        ))}
      </div>

      <CommonModal
        isOpen={modalType !== null}
        title={
          modalType === "rename"
            ? "Edit Workspace"
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