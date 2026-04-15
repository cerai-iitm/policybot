import api from "@/lib/axios";
import { LoginPayload, RegisterPayload } from "@/lib/types/auth";

export const registerUser = async (data: RegisterPayload) => {
  const res = await api.post("/auth/register", data);
  return res.data;
};

export const loginUser = async (data: LoginPayload) => {
  const formData = new URLSearchParams();
  formData.append("username", data.username);
  formData.append("password", data.password);

  const res = await api.post("/auth/login/", formData, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });

  return res.data;
};

export const getMe = async () => {
  const res = await api.get("/auth/me");
  return res.data;
};

export const logoutUser = async () => {
  const res = await api.post("/auth/logout");
  return res.data;
};