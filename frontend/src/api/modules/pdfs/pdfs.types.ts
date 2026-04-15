import { ISODateString } from "../../shared/common.types"

export interface PDF {
  id: number
  original_filename: string
  stored_filename: string
  notebook_id: number
  processing_status: string
  uploaded_at: ISODateString
  summary?: string | null
}

export interface PDFUploadResponse {
  pdf_id: number
  original_filename: string
  stored_filename: string
  notebook_id: number
  file_path: string
  processing_status: string
  uploaded_at: ISODateString
}

export interface PDFListResponse {
  notebook_id: string
  pdfs: PDF[]
}