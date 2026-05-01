import CreateWorkspaceCard from "../components/cards/CreateWorkspaceCard";
import RecentNotebookCard from "../components//cards/RecentNotebookCard/RecentNotebookCard";
import { NotebookListItem } from "@/lib/types/notebook";
import { useState } from "react"
import CommonModal from "@/components/popup"


type Props = {
  recentNotebooks?: NotebookListItem[]; // 👈 make optional
  onSelect: (id: string) => void;
};

const RecentSection = ({ recentNotebooks = [], onSelect }: Props) => {

  const [modalType, setModalType] = useState<"rename" | "delete" | null>(null)
  const [selectedNotebook, setSelectedNotebook] = useState<NotebookListItem | null>(null)
  const [inputValue, setInputValue] = useState("")

  const handleRename = (nb: NotebookListItem) => {
    setSelectedNotebook(nb)
    setInputValue(nb.title)
    setModalType("rename")
  }

  const handleDelete = (nb: NotebookListItem) => {
    setSelectedNotebook(nb)
    setModalType("delete")
  }

  const closeModal = () => {
    setModalType(null)
    setSelectedNotebook(null)
  }

  const handleConfirm = () => {
    if (!selectedNotebook) return

    if (modalType === "rename") {
      console.log("Renaming:", selectedNotebook.notebook_id, inputValue)
    }

    if (modalType === "delete") {
      console.log("Deleting:", selectedNotebook.notebook_id)
    }

    closeModal()
  }

  return (
    <>
      <h2 className="text-xl font-semibold mb-6">
        Recent Workspaces
      </h2>

      <div className="flex gap-6 mb-12 overflow-x-auto no-scrollbar">

        <CreateWorkspaceCard />

        {recentNotebooks.map((nb) => (
          <div key={nb.notebook_id} className="shrink-0">
            <RecentNotebookCard
              title={nb.title}
              desc={nb.description || "No description available"}
              createdAt={nb.created_at}
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
      />
    </>
  );
};

export default RecentSection;