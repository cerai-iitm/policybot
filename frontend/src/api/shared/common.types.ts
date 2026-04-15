export type ISODateString = string

export interface ErrorResponse {
  detail: string
}

export function parseBackendError(err: unknown): ErrorResponse | null {
  const anyErr = err as any
  if (anyErr?.response?.data?.detail) {
    return { detail: anyErr.response.data.detail }
  }
  return null
}