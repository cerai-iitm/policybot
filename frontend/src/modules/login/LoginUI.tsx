"use client";

import logo from "@/assets/logo.png";
import Link from "next/link";

type Props = {
  mode: "signin" | "signup";
  loading: boolean;
  error: string;
  fieldErrors: any;

  name: string;
  email: string;
  password: string;

  loginEmail: string;
  loginPassword: string;

  onNameChange: (value: string) => void;
  onEmailChange: (value: string) => void;
  onPasswordChange: (value: string) => void;

  onLoginEmailChange: (value: string) => void;
  onLoginPasswordChange: (value: string) => void;

  onSwitchMode: (mode: "signin" | "signup") => void;
  onSubmit: () => void;

  onKeyDown: (e: React.KeyboardEvent) => void;
};

export default function LoginUI({
  mode,
  loading,
  error,
  fieldErrors,

  name,
  email,
  password,

  loginEmail,
  loginPassword,

  onNameChange,
  onEmailChange,
  onPasswordChange,

  onLoginEmailChange,
  onLoginPasswordChange,

  onSwitchMode,
  onSubmit,

  onKeyDown,
}: Props) {
  return (
    <div
      className="
        min-h-screen
        w-screen
        bg-white
        flex
        flex-col
        overflow-y-auto
        md:h-screen
        md:overflow-hidden
      "
    >

      {/* LOGO */}
      <div
        className="
          absolute
          top-6
          left-5
          md:top-8
          md:left-10
          z-10
        "
      >
        <Link href="/">
          <img
            src={logo.src}
            alt="Logo"
            className="
              h-5
              md:h-6
              w-auto
              cursor-pointer
              opacity-90
              hover:opacity-70
              transition
            "
          />
        </Link>
      </div>

      {/* CENTER */}
      <div
        className="
          flex
          flex-1
          justify-center
          px-5
          pt-28
          pb-10
          md:items-center
          md:px-6
          md:pt-0
          md:pb-0
        "
      >
        <div className="w-full max-w-md">

          {/* TITLE */}
          <h1 className="text-2xl font-semibold text-gray-900 mb-2">
            {mode === "signin" ? "Sign in" : "Create your account"}
          </h1>

          <p className="text-sm text-gray-500 mb-8">
            {mode === "signin" ? "Welcome back" : "Start using PolicyBot"}
          </p>

          {/* FORM */}
          <div className="flex flex-col gap-4" onKeyDown={onKeyDown}>

            {/* FULL NAME */}
            {mode === "signup" && (
              <div>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => onNameChange(e.target.value)}
                  placeholder="Full name"
                  className={`h-11 w-full px-4 rounded-lg border bg-gray-50
                  focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#1e40af]/20 transition
                  ${fieldErrors.name ? "border-red-400" : "border-gray-300"}`}
                />

                {fieldErrors.name && (
                  <p className="text-xs text-red-500 mt-1">
                    {fieldErrors.name}
                  </p>
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
                    ? onLoginEmailChange(e.target.value)
                    : onEmailChange(e.target.value)
                }
                placeholder="Email"
                autoComplete="email"
                className={`h-11 w-full px-4 rounded-lg border bg-gray-50
                focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#1e40af]/20 transition
                ${fieldErrors.email ? "border-red-400" : "border-gray-300"}`}
              />

              {fieldErrors.email && (
                <p className="text-xs text-red-500 mt-1">
                  {fieldErrors.email}
                </p>
              )}
            </div>

            {/* PASSWORD */}
            <div>
              <input
                type="password"
                value={mode === "signin" ? loginPassword : password}
                onChange={(e) =>
                  mode === "signin"
                    ? onLoginPasswordChange(e.target.value)
                    : onPasswordChange(e.target.value)
                }
                placeholder="Password"
                autoComplete="current-password"
                className={`h-11 w-full px-4 rounded-lg border bg-gray-50
                focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#1e40af]/20 transition
                ${fieldErrors.password ? "border-red-400" : "border-gray-300"}`}
              />

              {fieldErrors.password && (
                <p className="text-xs text-red-500 mt-1">
                  {fieldErrors.password}
                </p>
              )}
            </div>

            {/* ERROR */}
            {error && (
              <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2">
                {error}
              </div>
            )}

            {/* BUTTON */}
            <button
              onClick={onSubmit}
              disabled={loading}
              className="
                h-11
                rounded-lg
                bg-primary
                text-white
                font-medium
                hover:opacity-95
                active:scale-[0.99]
                transition
                disabled:opacity-60
                disabled:cursor-not-allowed
                flex
                items-center
                justify-center
                gap-2
              "
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
                onSwitchMode(mode === "signin" ? "signup" : "signin")
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