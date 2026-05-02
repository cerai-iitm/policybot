import api from "@/lib/axios";
import { API_URL } from "@/lib/config/env";
import { getToken } from "@/lib/utils/token";
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
  const res = await api.get(`/pdfs/?notebook_id=${notebookId}`);
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

export const renamePdf = async (
  pdfId: string,
  newFilename: string
) => {
  const res = await api.patch(
    `/pdfs/filename?pdf_id=${pdfId}`,
    {
      original_filename: newFilename,
    }
  );

  return res.data;
};

export const processPdfStream = async (
  notebookId: string,
  pdfId: string,
  onMessage?: (msg: string) => void
): Promise<void> => {
  const token = getToken();

  if (!token) {
    throw new Error("No auth token");
  }

  const url = `${API_URL}/pdfs/process?notebook_id=${notebookId}&pdf_id=${pdfId}`;

  const response = await fetch(url, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`, // ✅ NOW WORKS
      Accept: "text/event-stream",      // important for SSE backend
    },
  });

  if (!response.ok) {
    throw new Error(`Stream failed: ${response.status}`);
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder("utf-8");

  if (!reader) {
    throw new Error("No stream reader");
  }

  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();

    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // 🔥 Split SSE messages
    const parts = buffer.split("\n\n");

    for (let i = 0; i < parts.length - 1; i++) {
      const line = parts[i].trim();

      if (line.startsWith("data:")) {
        const msg = line.replace("data:", "").trim();

        console.log("STREAM:", msg);

        onMessage?.(msg);

        if (msg === "done") {
          return;
        }
      }
    }

    buffer = parts[parts.length - 1];
  }
};