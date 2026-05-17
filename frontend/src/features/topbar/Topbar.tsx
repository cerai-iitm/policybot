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

        bg-white md:bg-[#F1F5F9]

        flex items-center justify-between

        px-4 md:px-12
        py-3 md:py-2

        md:border-none
      "
    >
      {/* Left side - Logo / Brand */}
      <div className="flex items-center shrink-0">
        <Header onCollapse={handleCollapse} />
      </div>

      {/* Right side */}
      <div
        className="
          flex items-center
          gap-3 md:gap-2
          shrink-0
        "
      >
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
              whitespace-nowrap
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