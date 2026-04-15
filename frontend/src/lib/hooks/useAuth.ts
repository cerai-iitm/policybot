import { useState } from "react";
import { loginUser } from "@/lib/api/auth.api";
import { LoginResponse } from "@/lib/types/auth";

export const useAuth = () => {
  const [loading, setLoading] = useState(false);

  const login = async (username: string, password: string) => {
    setLoading(true);
    try {
      const data: LoginResponse = await loginUser({ username, password });
      localStorage.setItem("token", data.access_token);
      return data;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
  localStorage.removeItem("token");
  window.location.href = "/login";
};

  return { login, logout, loading };
};
