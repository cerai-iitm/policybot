import { useState } from "react";
import { loginUser, registerUser } from "@/lib/api/auth.api";
import { LoginResponse, RegisterPayload } from "@/lib/types/auth";

export const useAuth = () => {
  const [loading, setLoading] = useState(false);

  const login = async (username: string, password: string) => {
    setLoading(true);
    try {
      const data: LoginResponse = await loginUser({ username, password });

      localStorage.setItem("token", data.access_token);

      return data;
    } catch (err: any) {
      throw err?.response?.data || err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (payload: RegisterPayload) => {
    setLoading(true);
    try {
      const data = await registerUser(payload);
      return data;
    } catch (err: any) {
      throw err?.response?.data || err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    window.location.href = "/login";
  };

  return { login, register, logout, loading };
};