"use client";

import { useState, useEffect } from "react";
import { FaGithub } from "react-icons/fa";

import logo from "@/assets/logo/logo.png";
import cerailogo from "@/assets/logo/cerai.png";
import iitmlogo from "@/assets/logo/iiit.png";
import wsailogo from "@/assets/logo/wsai.png";

import Link from "next/link";

import { getMe } from "@/lib/api";
import { User } from "@/lib/types/auth";
import { useAuth } from "@/lib/hooks/useAuth";

import ProfileDropdown from "./ProfileDropdown";

const Navbar = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loadingUser, setLoadingUser] = useState(true);

  const { isDemoUser } = useAuth();

  // ✅ Fetch user once
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const data = await getMe();
        setUser(data);
      } catch (err) {
        console.error("Failed to fetch user");
      } finally {
        setLoadingUser(false);
      }
    };

    fetchUser();
  }, []);

  return (
    <>
      <nav className="sticky top-0 z-50 flex items-center justify-between bg-white/90 backdrop-blur-md px-4 py-4 md:px-12 md:py-6">

        {/* LEFT - LOGO */}
        <Link href="/" className="flex-shrink-0">
          <img
            src={logo.src}
            alt="PolicyBot"
            className="h-5 w-auto md:h-6"
          />
        </Link>

        {/* RIGHT SIDE */}
        <div className="flex items-center gap-2 md:gap-4">

          {/* GitHub */}
          <a
            href="https://github.com/cerai-iitm/policybot.git"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Open PolicyBot GitHub repository"
            title="GitHub"
          >
            <FaGithub className="text-lg md:text-xl text-gray-700 cursor-pointer transition duration-300 hover:scale-125 hover:text-primary" />
          </a>

          {/* Logos Container */}
          <div className="flex items-center justify-center gap-2 md:gap-6 h-9 md:h-10.75 px-3 md:px-5 rounded-[10px] border border-black/20 bg-white">

            <a
              href="https://cerai.iitm.ac.in/"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Open CeRAI website"
              title="CeRAI"
            >
              <img
                src={cerailogo.src}
                alt="CeRAI"
                className="h-4 md:h-5 w-auto object-contain cursor-pointer transition duration-300 hover:scale-110"
              />
            </a>

            <a
              href="https://www.iitm.ac.in/"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Open IITM website"
              title="IITM"
            >
              <img
                src={iitmlogo.src}
                alt="IITM"
                className="h-4 md:h-5 w-auto object-contain cursor-pointer transition duration-300 hover:scale-110"
              />
            </a>

            <a
              href="https://wsai.iitm.ac.in/"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Open WSAI website"
              title="WSAI"
            >
              <img
                src={wsailogo.src}
                alt="WSAI"
                className="h-4 md:h-5 w-auto object-contain cursor-pointer transition duration-300 hover:scale-110"
              />
            </a>

          </div>

          {/* Login / Profile */}
          {isDemoUser ? (
            <Link href="/login">
              <button className="px-3 md:px-4 py-1.5 md:py-2 rounded-full border border-gray-300 text-xs md:text-sm font-medium hover:bg-gray-100 transition cursor-pointer whitespace-nowrap">
                Login
              </button>
            </Link>
          ) : (
            <ProfileDropdown />
          )}

        </div>

      </nav>
    </>
  );
};

export default Navbar;