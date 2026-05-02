import axios from "axios";
import { API_URL } from "@/lib/config/env";
import { getToken } from "@/lib/utils/token";
import Cookies from "js-cookie"; // ✅ ADD THIS

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    (config.headers as any).Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const url = error.config?.url;

    const isLoginRequest = url?.includes("/auth/login");

    // ✅ Only redirect for protected API failures
    if (status === 401 && !isLoginRequest) {
      if (typeof window !== "undefined") {
        Cookies.remove("token"); // ✅ FIXED
        window.location.href = "/policybot/login";
      }
    }

    return Promise.reject(error);
  }
);

export default api;