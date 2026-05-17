"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/hooks/useAuth";
import LoginUI from "./LoginUI";

export default function AuthPage() {
  const [mode, setMode] = useState<"signin" | "signup">("signin");

  // Signin
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  // Signup
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<any>({});

  const router = useRouter();
  const { login, register, loading } = useAuth();

  // ✅ RESET WHEN SWITCHING
  const switchMode = (newMode: "signin" | "signup") => {
    setMode(newMode);
    setError("");
    setFieldErrors({});
    setLoginEmail("");
    setLoginPassword("");
    setName("");
    setEmail("");
    setPassword("");
  };

  // ✅ VALIDATION
  const validate = () => {
    const errors: any = {};

    if (mode === "signup" && !name.trim()) {
      errors.name = "Full name is required";
    }

    const currentEmail = mode === "signin" ? loginEmail : email;

    if (!currentEmail.trim()) {
      errors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(currentEmail)) {
      errors.email = "Enter a valid email";
    }

    const currentPassword = mode === "signin" ? loginPassword : password;

    if (!currentPassword) {
      errors.password = "Password is required";
    } else if (currentPassword.length < 6) {
      errors.password = "Minimum 6 characters";
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // ✅ LOGIN
  const handleLogin = async () => {
    setError("");

    if (!validate()) return;

    try {
      await login(loginEmail, loginPassword);
      router.push("/notebook");
    } catch (err: any) {
      const message =
        err?.response?.data?.detail ||
        err?.message ||
        "Invalid credentials";

      setError(message);
    }
  };

  // ✅ SIGNUP
  const handleSignup = async () => {
    setError("");

    if (!validate()) return;

    try {
      await register({
        full_name: name,
        email,
        password,
        username: email,
      });

      await login(email, password);
      router.push("/notebook");
    } catch (err: any) {
      const message =
        err?.response?.data?.detail ||
        err?.message ||
        "Signup failed";

      setError(message);
    }
  };

  // ✅ FIX ENTER DOUBLE TRIGGER
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      mode === "signin" ? handleLogin() : handleSignup();
    }
  };

  return (
    <LoginUI
      mode={mode}
      loading={loading}
      error={error}
      fieldErrors={fieldErrors}
      name={name}
      email={email}
      password={password}
      loginEmail={loginEmail}
      loginPassword={loginPassword}
      onNameChange={setName}
      onEmailChange={setEmail}
      onPasswordChange={setPassword}
      onLoginEmailChange={setLoginEmail}
      onLoginPasswordChange={setLoginPassword}
      onSwitchMode={switchMode}
      onSubmit={mode === "signin" ? handleLogin : handleSignup}
      onKeyDown={handleKeyDown}
    />
  );
}