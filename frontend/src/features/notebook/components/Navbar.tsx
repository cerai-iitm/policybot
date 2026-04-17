"use client";

import { useState, useEffect } from "react";
import { FaGithub, FaBars, FaTimes } from "react-icons/fa";
import logo from "@/assets/logo/logo.png";
import Link from "next/link";
import cerailogo from "@/assets/logo/cerai.png";
import iitmlogo from "@/assets/logo/iiit.png";
import wsailogo from "@/assets/logo/wsai.png";

import { getMe } from "@/lib/api";
import { User } from "@/lib/types/auth";
import { useAuth } from "@/lib/hooks/useAuth";



const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loadingUser, setLoadingUser] = useState(true);

  const { logout } = useAuth();

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
      <nav className="sticky top-0 z-50 flex justify-between items-center px-12 py-6 bg-white/90 backdrop-blur-md">

        {/* Logo */}
        <Link
            href="/"
           
          >
        <img
          src={logo.src}
          alt="PolicyBot"
          className="h-6 w-auto"
        />
</Link>
        {/* Desktop Links */}
        <div className="hidden md:flex items-center gap-4">

         

          <a
            href="https://github.com/cerai-iitm/policybot.git"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Open PolicyBot GitHub repository"
            title="GitHub"
          >
            <FaGithub className="text-xl text-gray-700 cursor-pointer transition duration-300 hover:scale-125 hover:text-primary" />
          </a>
<div className="ml-2">
  <div className="flex items-center justify-center gap-6 h-10.75 px-5 rounded-[10px] border border-black/20 bg-white">

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
        className="h-5 w-auto object-contain cursor-pointer transition duration-300 hover:scale-110"
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
        className="h-5 w-auto object-contain cursor-pointer transition duration-300 hover:scale-110"
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
        className="h-5 w-auto object-contain cursor-pointer transition duration-300 hover:scale-110"
      />
    </a>

  </div>
</div>

         
          
     {/* ✅ Profile */}
        <div className="relative group ml-2">

          {/* Avatar */}
          <button className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-sm font-semibold text-gray-700 hover:scale-105 transition">
            {user?.username?.charAt(0).toUpperCase() || "?"}
          </button>

          {/* ✅ Hover Dropdown */}
          <div className="absolute right-0 mt-3 w-56 bg-white border border-gray-200 rounded-xl shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">

            <div className="p-4">
              {loadingUser ? (
                <p className="text-sm text-gray-500">Loading...</p>
              ) : user ? (
                <>
                  <p className="text-sm font-semibold text-gray-800">
                    {user.full_name}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    @{user.username}
                  </p>
                </>
              ) : (
                <p className="text-sm text-red-500">Failed to load</p>
              )}
            </div>

            <div className="border-t">
              <button
                onClick={logout}
                className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100 rounded-b-xl"
              >
                Logout
              </button>
            </div>

          </div>
        </div>


        </div>

        {/* Mobile Hamburger */}
        <button
        type="button"
        aria-label="Open mobile menu"
          className="md:hidden text-2xl text-gray-800"
          onClick={() => setIsOpen(true)}
        >
          <FaBars />
        </button>
      </nav>

      {/* Mobile Fullscreen Menu */}
      <div
        className={`fixed inset-0 bg-white z-50 transform transition-transform duration-300 ease-in-out ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="flex justify-between items-center px-6 py-6 border-b">
          <img src={logo.src} alt="PolicyBot" className="h-6 w-auto" />
          <button
          type="button"          aria-label="Close mobile menu"
            onClick={() => setIsOpen(false)}
            className="text-2xl text-gray-800"
          >
            <FaTimes />
          </button>
        </div>

       <div className="flex flex-col gap-8 px-6 pt-12 text-left h-full">

  <Link
    href="/"
    onClick={() => setIsOpen(false)}
    className="text-xl font-medium text-gray-800"
  >
    Overview
  </Link>

  <Link
    href="/notebook"
    onClick={() => setIsOpen(false)}
    className="text-xl font-medium text-gray-800"
  >
    Policy Notebooks
  </Link>

  <a
    href="https://github.com/cerai-iitm/policybot.git"
    target="_blank"
    rel="noopener noreferrer"
    className="flex items-center gap-3 text-xl font-medium text-gray-800"
  >
    <FaGithub />
    GitHub
  </a>

  {/* Partner Logos Section */}
  <div className="pt-8 mt-6 border-t border-gray-200">
    <p className="text-sm text-gray-500 mb-4 tracking-wide">
      In Collaboration With
    </p>

    <div className="flex items-center gap-8">

      <a
        href="https://cerai.iitm.ac.in/"
        target="_blank"
        rel="noopener noreferrer"
        onClick={() => setIsOpen(false)}
      >
        <img
          src={cerailogo.src}
          alt="CeRAI"
          className="h-7 w-auto object-contain transition duration-300 hover:scale-110"
        />
      </a>

      <a
        href="https://www.iitm.ac.in/"
        target="_blank"
        rel="noopener noreferrer"
        onClick={() => setIsOpen(false)}
      >
        <img
          src={iitmlogo.src}
          alt="IITM"
          className="h-7 w-auto object-contain transition duration-300 hover:scale-110"
        />
      </a>

      <a
        href="https://wsai.iitm.ac.in/"
        target="_blank"
        rel="noopener noreferrer"
        onClick={() => setIsOpen(false)}
      >
        <img
          src={wsailogo.src}
          alt="WSAI"
          className="h-7 w-auto object-contain transition duration-300 hover:scale-110"
        />
      </a>

    </div>
  </div>

  <Link
    href="/notebook"
    onClick={() => setIsOpen(false)}
  >
    <button className="mt-8 w-full border border-gray-400 px-6 py-3 rounded-xl transition duration-300 hover:bg-primary hover:text-white">
      Get Started
    </button>
  </Link>

</div>

      </div>
    </>
  )
}

export default Navbar
