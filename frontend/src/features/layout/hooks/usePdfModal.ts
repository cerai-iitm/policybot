"use client";

import { useState } from "react";

export const usePdfModal = (
  onDelete: (id: string) => Promise<void>,
  onRename: (id: string, name: string) => Promise<void>
) => {
  const [modalOpen, setModalOpen] = useState(false);
  const [modalType, setModalType] = useState<"delete" | "rename" | null>(null);
  const [activePdfId, setActivePdfId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState("");
  const [loading, setLoading] = useState(false);

  const openDelete = (id: string) => {
    setActivePdfId(id);
    setModalType("delete");
    setModalOpen(true);
  };

  const openRename = (id: string, name: string) => {
    setActivePdfId(id);
    setRenameValue(name);
    setModalType("rename");
    setModalOpen(true);
  };

  const confirm = async () => {
    if (!activePdfId) return;

    setLoading(true);

    try {
      if (modalType === "delete") {
        await onDelete(activePdfId);
      } else {
        await onRename(activePdfId, renameValue);
      }
    } finally {
      setLoading(false);
      setModalOpen(false);
      setActivePdfId(null);
    }
  };

  return {
    modalOpen,
    modalType,
    renameValue,
    setRenameValue,
    loading,
    openDelete,
    openRename,
    confirm,
    setModalOpen,
  };
};