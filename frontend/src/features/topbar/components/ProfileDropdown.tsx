"use client";

import { useEffect, useState } from "react";
import { getMe } from "@/lib/api";
import { User } from "@/lib/types/auth";
import { useAuth } from "@/lib/hooks/useAuth";

const ProfileDropdown = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loadingUser, setLoadingUser] = useState(true);

  const { logout } = useAuth();

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
    <div className="relative group ml-1 md:ml-2">

      {/* Avatar */}
      <button
        className="
          w-8 h-8 md:w-10 md:h-10
          rounded-full
          bg-gray-300
          flex items-center justify-center
          text-xs md:text-sm
          font-medium
          text-gray-700
          hover:bg-gray-200
          transition
        "
      >
        {user?.username?.charAt(0).toUpperCase() || "?"}
      </button>

      {/* Dropdown */}
      <div
        className="
          absolute right-0 mt-2 md:mt-3
          w-56 md:w-64
          bg-white rounded-xl
          shadow-lg shadow-black/10
          border border-gray-100
          opacity-0 invisible
          group-hover:opacity-100 group-hover:visible
          transition-all duration-200
          overflow-hidden
          z-50
        "
      >

        {/* Header */}
        <div className="px-4 py-3 md:py-4">
          {loadingUser ? (
            <div className="text-sm text-gray-400">
              Loading...
            </div>
          ) : user ? (
            <>
              <div className="text-sm font-semibold text-gray-900 truncate">
                {user.full_name}
              </div>

              <div className="text-xs text-gray-500 mt-0.5 truncate">
                {user.username}
              </div>
            </>
          ) : (
            <div className="text-sm text-red-500">
              Failed to load user
            </div>
          )}
        </div>

        {/* Divider */}
        <div className="h-px bg-gray-100" />

        {/* Divider */}
        <div className="h-px bg-gray-100" />

        {/* Logout */}
        <div className="py-2">
          <button
            onClick={logout}
            className="
              w-full text-left
              px-4 py-2
              text-sm
              text-red-600
              hover:bg-red-50
              transition
            "
          >
            Sign out
          </button>
        </div>

      </div>
    </div>
  );
};

export default ProfileDropdown;