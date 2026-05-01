import api from "@/lib/axios";
import { CreateNotebookPayload,NotebookListItem  } from "@/lib/types/notebook";

export interface UpdateNotebookPayload {
  notebook_id: string;
  title: string;
  description: string;
}


export const createNotebook = async (data: CreateNotebookPayload) => {
  const res = await api.post("/notebooks", data);
  return res.data;
};

export const getNotebooks = async (): Promise<NotebookListItem[]> => {
  const res = await api.get("/notebooks");

  // ✅ normalize API response here (VERY IMPORTANT)
  return res.data.notebooks.map((nb: any) => ({
  notebook_id: nb.notebook_id,
  title: nb.title,
  description: nb.description,
  created_at: nb.created_at,
  processed_pdf_count: nb.processed_pdf_count ?? 0, // ✅ safe fallback
}));

};

export const getNotebook = async (notebookId: string) => {
  const res = await api.get(`/notebooks?notebook_id=${notebookId}`);
  return res.data;
};

export const deleteNotebook = async (notebookId: string) => {
  await api.delete(`/notebooks/${notebookId}`);
};


export const updateNotebook = async (data: UpdateNotebookPayload) => {
  const res = await api.post(
    `/notebooks/update/?notebook_id=${data.notebook_id}`,
    {
      title: data.title,
      description: data.description,
    }
  );

  return res.data;
};