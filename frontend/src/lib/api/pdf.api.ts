import api from "@/lib/axios";

export const uploadPdf = async (notebookId: string, file: File) => {
  const formData = new FormData();
  formData.append("notebook_id", notebookId);
  formData.append("file", file);

  const res = await api.post("/pdfs/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return res.data;
};

export const listPdfs = async (notebookId: string) => {
  const res = await api.post(`/pdfs/?notebook_id=${notebookId}`);
  return res.data;
};

export const deletePdf = async (pdfId: string) => {
  const res = await api.delete(`/pdfs/?pdf_id=${pdfId}`);
  return res.data;
};

export const getPdf = async (pdfIds: string) => {
  const res = await api.post(`/pdfs/?pdf_ids=${pdfIds}`);
  return res.data;
};

export const getPdfProcess = async (notebookId: string, pdfId: string) => {
  const res = await api.get(`/pdfs/process?notebook_id=${notebookId}&pdf_id=${pdfId}`);
  return res.data;
};