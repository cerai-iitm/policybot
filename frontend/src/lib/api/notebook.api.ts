import api from "@/lib/axios";
import { CreateNotebookPayload } from "@/lib/types/notebook";

export const createNotebook = async (data: CreateNotebookPayload) => {
  const res = await api.post("/notebooks", data);
  return res.data;
};

export const getNotebooks = async () => {
  const res = await api.get("/notebooks");
  return res.data;
};

export const getNotebook = async (notebookId: string) => {
  const res = await api.get(`/notebooks?notebook_id=${notebookId}`);
  return res.data;
};

export const deleteNotebook = async (notebookId: string) => {
  const res = await api.delete(`/notebooks?notebook_id=${notebookId}`);
  return res.data;
};
