"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import AuthPage from "@/features/login/Login";

export default function LoginPage() {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      router.replace("/notebook");
    }
  }, []);

  return <AuthPage />;
}