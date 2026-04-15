import { useState } from "react";
import logo from "@/assets/logo.png";
import { useRouter } from "next/navigation";

export default function AuthPage() {
  const [activeTab, setActiveTab] = useState<"signin" | "signup">("signin");

  // Signin state
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  // Signup state
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const router = useRouter();

  return (
    <div className="h-screen w-screen bg-white flex flex-col">

      {/* 🔹 TOP LEFT LOGO */}
      <div className="absolute top-6 left-8">
        <img src={logo.src} alt="Logo" className="w-24" />
      </div>

      {/* 🔹 CENTER FORM */}
      <div className="flex flex-1 items-center justify-center">
        <div className="w-100 bg-white shadow-xl rounded-2xl p-10">

          {/* 🔹 HEADING */}
          <h1 className="text-[26px] font-semibold font-poppins leading-tight  text-center mb-6">
            {activeTab === "signin" ? "Welcome Back" : "Create Account"}
          </h1>

          {/* 🔹 TAB SWITCH */}
          <div className="relative flex bg-[#f1f3f6] rounded-full p-1 mb-8">
            <div
              className={`absolute top-1 bottom-1 w-1/2 rounded-full bg-[#1b78ff] transition-all duration-300 ${
                activeTab === "signin" ? "translate-x-0" : "translate-x-full"
              }`}
            />

            <div
              onClick={() => setActiveTab("signin")}
              className={`flex-1 text-center py-2 cursor-pointer relative z-10 font-medium ${
                activeTab === "signin" ? "text-white" : "text-gray-600"
              }`}
            >
              Sign In
            </div>

            <div
              onClick={() => setActiveTab("signup")}
              className={`flex-1 text-center py-2 cursor-pointer relative z-10 font-medium ${
                activeTab === "signup" ? "text-white" : "text-gray-600"
              }`}
            >
              Sign Up
            </div>
          </div>

          {/* 🔹 SIGN IN FORM */}
          {activeTab === "signin" && (
            <>
                  {/* EMAIL */}
              <div className="flex flex-col mb-4">
                <label className="mb-1 text-sm text-[#434a54]">Email</label>
                <input
                  type="email"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  placeholder="Enter your email"
                  className="px-4 py-3 rounded-xl border border-[#e5e8ec] focus:outline-none 
                    focus:border-[#1b78ff] focus:ring-4 focus:ring-blue-300/20 transition"
                />
              </div>

              {/* PASSWORD */}
              <div className="flex flex-col mb-6">
                <label className="mb-1 text-sm text-[#434a54]">Password</label>
                <input
                  type="password"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="px-4 py-3 rounded-xl border border-[#e5e8ec] focus:outline-none 
                    focus:border-[#1b78ff] focus:ring-4 focus:ring-blue-300/20 transition"
                />
              </div>

              <button
              onClick={() => router.push("/notebook")}
               className="w-full h-12 bg-[#1b78ff] text-white rounded-xl font-medium hover:shadow-lg transition">
                Sign In
              </button>

              <p className="text-center text-sm text-gray-500 mt-5">
                Don’t have an account?{" "}
                <span
                  onClick={() => setActiveTab("signup")}
                  className="text-blue-600 cursor-pointer font-medium"
                >
                  Sign up
                </span>
              </p>
            </>
          )}

          {/* 🔹 SIGN UP FORM */}
          {activeTab === "signup" && (
            <>
               {/* NAME */}
              <div className="flex flex-col mb-4">
                <label className="mb-1 text-sm text-[#434a54]">Full Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Your name"
                  className="px-4 py-3 rounded-xl border border-[#e5e8ec] focus:outline-none 
                    focus:border-[#1b78ff] focus:ring-4 focus:ring-blue-300/20 transition"
                />
              </div>

              {/* EMAIL */}
              <div className="flex flex-col mb-4">
                <label className="mb-1 text-sm text-[#434a54]">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  className="px-4 py-3 rounded-xl border border-[#e5e8ec] focus:outline-none 
                    focus:border-[#1b78ff] focus:ring-4 focus:ring-blue-300/20 transition"
                />
              </div>

              {/* PASSWORD */}
              <div className="flex flex-col mb-6">
                <label className="mb-1 text-sm text-[#434a54]">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Create password"
                  className="px-4 py-3 rounded-xl border border-[#e5e8ec] focus:outline-none 
                    focus:border-[#1b78ff] focus:ring-4 focus:ring-blue-300/20 transition"
                />
              </div>

              <button onClick={() => router.push("/notebook")}
              className="w-full h-12 bg-[#1b78ff] text-white rounded-xl font-medium hover:shadow-lg transition">
                Create Account
              </button>

              <p className="text-center text-sm text-gray-500 mt-5">
                Already have an account?{" "}
                <span
                  onClick={() => setActiveTab("signin")}
                  className="text-blue-600 cursor-pointer font-medium"
                >
                  Sign in
                </span>
              </p>
            </>
          )}

        

        </div>
      </div>
    </div>
  );
}