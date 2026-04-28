"use client";

import { useState } from "react";
import logo from "@/assets/logo.png";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/hooks/useAuth";
import Link from "next/link";

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
    <div className="h-screen w-screen bg-white flex flex-col">

      {/* LOGO */}
      <div className="absolute top-8 left-10">
        <Link href="/">
          <img
            src={logo.src}
            alt="Logo"
            className="h-6 w-auto cursor-pointer opacity-90 hover:opacity-70 transition"
          />
        </Link>
      </div>

      {/* CENTER */}
      <div className="flex flex-1 items-center justify-center px-6">
        <div className="w-full max-w-md">

          {/* TITLE */}
          <h1 className="text-2xl font-semibold text-gray-900 mb-2">
            {mode === "signin" ? "Sign in" : "Create your account"}
          </h1>

          <p className="text-sm text-gray-500 mb-8">
            {mode === "signin" ? "Welcome back" : "Start using PolicyBot"}
          </p>

          {/* FORM */}
          <div className="flex flex-col gap-4" onKeyDown={handleKeyDown}>

            {/* FULL NAME */}
            {mode === "signup" && (
              <div>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Full name"
                  className={`h-11 w-full px-4 rounded-lg border bg-gray-50 
                  focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#1e40af]/20 transition
                  ${fieldErrors.name ? "border-red-400" : "border-gray-300"}`}
                />
                {fieldErrors.name && (
                  <p className="text-xs text-red-500 mt-1">{fieldErrors.name}</p>
                )}
              </div>
            )}

            {/* EMAIL */}
            <div>
              <input
                type="email"
                value={mode === "signin" ? loginEmail : email}
                onChange={(e) =>
                  mode === "signin"
                    ? setLoginEmail(e.target.value)
                    : setEmail(e.target.value)
                }
                placeholder="Email"
                autoComplete="email"
                className={`h-11 w-full px-4 rounded-lg border bg-gray-50 
                focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#1e40af]/20 transition
                ${fieldErrors.email ? "border-red-400" : "border-gray-300"}`}
              />
              {fieldErrors.email && (
                <p className="text-xs text-red-500 mt-1">{fieldErrors.email}</p>
              )}
            </div>

            {/* PASSWORD */}
            <div>
              <input
                type="password"
                value={mode === "signin" ? loginPassword : password}
                onChange={(e) =>
                  mode === "signin"
                    ? setLoginPassword(e.target.value)
                    : setPassword(e.target.value)
                }
                placeholder="Password"
                autoComplete="current-password"
                className={`h-11 w-full px-4 rounded-lg border bg-gray-50 
                focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#1e40af]/20 transition
                ${fieldErrors.password ? "border-red-400" : "border-gray-300"}`}
              />
              {fieldErrors.password && (
                <p className="text-xs text-red-500 mt-1">{fieldErrors.password}</p>
              )}
            </div>

            {/* ✅ GLOBAL ERROR (IMPROVED UI) */}
            {error && (
              <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2">
                {error}
              </div>
            )}

            {/* BUTTON */}
          <button
  onClick={mode === "signin" ? handleLogin : handleSignup}
  disabled={loading}
  className="h-11 rounded-lg bg-primary text-white font-medium 
  hover:opacity-95 active:scale-[0.99] transition 
  disabled:opacity-60 disabled:cursor-not-allowed 
  flex items-center justify-center gap-2"
>
  {loading && (
    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
  )}

  {loading
    ? mode === "signin"
      ? "Signing in..."
      : "Creating account..."
    : mode === "signin"
    ? "Sign in"
    : "Create account"}
</button>
          </div>

          {/* SWITCH */}
          <p className="text-sm text-gray-500 mt-6">
            {mode === "signin"
              ? "Don’t have an account?"
              : "Already have an account?"}{" "}
            <span
              onClick={() =>
                switchMode(mode === "signin" ? "signup" : "signin")
              }
              className="text-[#1e40af] cursor-pointer font-medium hover:underline"
            >
              {mode === "signin" ? "Sign up" : "Sign in"}
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}