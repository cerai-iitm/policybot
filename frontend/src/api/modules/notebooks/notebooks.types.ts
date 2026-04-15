import { ISODateString } from "../../shared/common.types"

export interface Notebook {
  id: number
  notebook_id: string
  title: string
  description?: string | null
  created_at: ISODateString
}

export interface NotebookListResponse {
  notebooks: Notebook[]
}