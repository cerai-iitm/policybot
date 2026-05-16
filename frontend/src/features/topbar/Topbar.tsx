"use client";

import { useAuth } from "@/lib/hooks/useAuth";
import Link from "next/link";

import Header from "./components/Header";
import TopBrandBar from "./components/TopBrandBar";
import ProfileDropdown from "./components/ProfileDropdown";

export default function Topbar() {
  const { isDemoUser } = useAuth();

  const handleCollapse = () => {
    // reserved for sidebar collapse if needed later
  };

  return (
    <header
      className="
        w-full
        bg-[#F1F5F9]
        flex items-center justify-between
        px-12 py-2
      "
    >
      {/* Left side - Logo / Brand */}
      <div className="flex items-center">
        <Header onCollapse={handleCollapse} />
      </div>

      {/* Right side */}
      <div className="flex items-center gap-2">
        <TopBrandBar />

        {isDemoUser ? (
          <Link
            href="/login"
            className="
              inline-flex items-center justify-center
              px-4 py-2
              rounded-full
              border border-gray-400
              text-sm font-medium
              hover:bg-gray-100
              transition
              cursor-pointer
            "
          >
            Login
          </Link>
        ) : (
          <ProfileDropdown />
        )}
      </div>
    </header>
  );
}