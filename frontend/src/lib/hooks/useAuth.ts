import { useState } from "react";
import { loginUser, registerUser, loginDemoUser } from "@/lib/api/auth.api";
import { LoginResponse, RegisterPayload } from "@/lib/types/auth";
import Cookies from "js-cookie";

export const useAuth = () => {
  const [loading, setLoading] = useState(false);

  const login = async (username: string, password: string) => {
    setLoading(true);
    try {
      const data: LoginResponse = await loginUser({ username, password });

      // ✅ Store token in cookie
      Cookies.set("token", data.access_token, {
        expires: 7, // days
        path: "/",
        sameSite: "lax",
      });

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
    Cookies.remove("token");
    window.location.href = "/login";
  };


   const loginDemo = async () => {
  setLoading(true);
  try {
    const data = await loginDemoUser();

    Cookies.set("token", data.access_token, {
      expires: 7,
      path: "/",
      sameSite: "lax",
    });

    return data;
  } catch (err: any) {
    throw err?.response?.data || err;
  } finally {
    setLoading(false);
  }
};



  return { login, register, logout,loginDemo, loading };

 


};

