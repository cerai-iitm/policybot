import { apiClient, buildUrl } from "../../core/client"
import { Notebook, NotebookListResponse } from "./notebooks.types"

export const notebooksApi = {
  create: async (title: string, description?: string): Promise<Notebook> => {
  const res = await apiClient.post(
    buildUrl("/notebooks"),
    {
      title,
      description,
    }
  )
  return res.data
},

  list: async (): Promise<NotebookListResponse> => {
    const res = await apiClient.get(buildUrl("/notebooks"))
    return res.data
  },

  get: async (id: string): Promise<Notebook> => {
    const res = await apiClient.get(buildUrl(`/notebooks/${id}`))
    return res.data
  },

  delete: async (id: string) => {
    await apiClient.delete(buildUrl(`/notebooks/${id}`))
  },
}