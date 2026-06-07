import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { loginUser, registerUser, loginDemoUser } from "@/lib/api/auth.api";
import { LoginResponse, RegisterPayload } from "@/lib/types/auth";
import Cookies from "js-cookie";

export const useAuth = () => {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [isDemoUser, setIsDemoUser] = useState(false);

  useEffect(() => {
    setIsDemoUser(Cookies.get("isDemoUser") === "true");
  }, []);

  const login = async (username: string, password: string) => {
    setLoading(true);
    try {
      const data: LoginResponse = await loginUser({ username, password });

      Cookies.set("token", data.access_token, {
        expires: 7,
        path: "/",
        sameSite: "lax",
      });

      Cookies.remove("isDemoUser"); // ✅ clear demo

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

  const loginDemo = async () => {
    setLoading(true);
    try {
      const data = await loginDemoUser();

      Cookies.set("token", data.access_token, {
        expires: 7,
        path: "/",
        sameSite: "lax",
      });

      Cookies.set("isDemoUser", "true", {
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

  const logout = () => {
    Cookies.remove("token");
    Cookies.remove("isDemoUser");
    router.push("/login");
  };

  const startRealUserFlow = () => {
  const isDemo = Cookies.get("isDemoUser") === "true";

  if (isDemo) {
    Cookies.remove("token");
    Cookies.remove("isDemoUser");
  }
};

  return { login, register, logout, loginDemo, loading, isDemoUser,startRealUserFlow };
};