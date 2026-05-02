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
import ProfileDropdown from "./ProfileDropdown";



const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loadingUser, setLoadingUser] = useState(true);

  const { logout, isDemoUser } = useAuth();

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
     {isDemoUser ? (
  <Link href="/login">
    <button className="px-4 py-2 rounded-full border border-gray-300 text-sm font-medium hover:bg-gray-100 transition cursor-pointer">
      Login
    </button>
  </Link>
) : (
  <ProfileDropdown />
)}


        </div>

        
       
      </nav>

    
    
    </>
  )
}

export default Navbar
