import axios from "axios"
import { withBase } from "./url"

const BASE = process.env.NEXT_PUBLIC_API_BASE || ""

export const apiClient = axios.create({
  baseURL: BASE,
  headers: {
    Accept: "application/json",
  },
})

// 🔐 Attach JWT
apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("jwt")
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

// 🚨 Global error handler
apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("jwt")
        window.location.href = "/login"
      }
    }
    return Promise.reject(err)
  }
)

export const buildUrl = (path: string) => withBase(`/api${path}`)