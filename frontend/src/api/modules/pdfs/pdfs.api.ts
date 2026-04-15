import { apiClient, buildUrl } from "../../core/client"
import {
  PDFListResponse,
  PDFUploadResponse,
} from "./pdfs.types"

export const pdfsApi = {
  upload: async (notebookId: number, file: File): Promise<PDFUploadResponse> => {
    const form = new FormData()
    form.append("notebook_id", String(notebookId))
    form.append("file", file)

    const res = await apiClient.post(
      buildUrl("/pdfs/"), // ✅ FIXED
      form,
      {
        headers: { "Content-Type": "multipart/form-data" },
      }
    )

    return res.data
  },

  list: async (notebookId: number): Promise<PDFListResponse> => {
    const res = await apiClient.get(
      buildUrl("/pdfs/"), // ✅ FIXED
      {
        params: { notebook_id: notebookId },
      }
    )
    return res.data
  },

  delete: async (pdfId: number) => {
    await apiClient.delete(buildUrl(`/pdfs/${pdfId}`)) // ✅ FIXED
  },

  viewUrl: (pdfId: number) => {
    return buildUrl(`/pdfs/${pdfId}/view`) // ✅ FIXED
  },
}