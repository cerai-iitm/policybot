import api from "@/lib/axios";
import { CreateNotebookPayload,NotebookListItem  } from "@/lib/types/notebook";

export const createNotebook = async (data: CreateNotebookPayload) => {
  const res = await api.post("/notebooks", data);
  return res.data;
};

export const getNotebooks = async (): Promise<NotebookListItem[]> => {
  const res = await api.get("/notebooks");

  // ✅ normalize API response here (VERY IMPORTANT)
  return res.data.notebooks;
};

export const getNotebook = async (notebookId: string) => {
  const res = await api.get(`/notebooks?notebook_id=${notebookId}`);
  return res.data;
};

export const deleteNotebook = async (notebookId: string) => {
  const res = await api.delete(`/notebooks?notebook_id=${notebookId}`);
  return res.data;
};
