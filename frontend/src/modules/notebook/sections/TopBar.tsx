import { Plus } from "lucide-react";
import { useAuth } from "@/lib/hooks/useAuth";
import SearchInput from "../components/SearchInput";
import { useState } from "react";

type Props = {
  onCreateWorkspace: () => void;
  searchQuery: string;
  onSearchChange: (value: string) => void;
};

const TopBar = ({
  onCreateWorkspace,
  searchQuery,
  onSearchChange,
}: Props) => {
  const { isDemoUser } = useAuth();

  // ✅ ONLY for mobile UI behavior
  const [mobileSearchOpen, setMobileSearchOpen] =
    useState(false);

  return (
    <div className="flex items-center justify-between mb-8 md:mb-10 gap-3">

      {/* LEFT SIDE */}
      <div
        className={`
          items-center gap-6 transition-all duration-300

          ${
            mobileSearchOpen
              ? "hidden md:flex"
              : "flex"
          }
        `}
      >
        <button className="px-4 py-2 rounded-full bg-gray-200 text-sm font-medium whitespace-nowrap">
          All
        </button>
      </div>

      {/* RIGHT SIDE */}
      <div
        className={`
          flex items-center gap-3

          ${
            mobileSearchOpen
              ? "flex-1 md:flex-none"
              : ""
          }
        `}
      >

        {/* SEARCH */}
        <div
          className={`
            transition-all duration-300

            ${
              mobileSearchOpen
                ? "flex-1 md:flex-none"
                : ""
            }
          `}
        >
          <SearchInput
            value={searchQuery}
            onChange={onSearchChange}
            placeholder="Search workspaces..."
            onOpenChange={setMobileSearchOpen}
          />
        </div>

        {/* CREATE BUTTON */}
        {!isDemoUser && (
          <button
            onClick={onCreateWorkspace}
            className="
              flex items-center gap-2
              bg-blue-600 text-white
              px-4 md:px-5
              py-2
              rounded-full
              text-sm font-medium
              hover:bg-blue-700
              transition
              whitespace-nowrap
              shrink-0
            "
          >
            <Plus size={16} />

            <span className="hidden sm:inline">
              Create Workspace
            </span>

            <span className="sm:hidden">
              Create
            </span>
          </button>
        )}

      </div>
    </div>
  );
};

export default TopBar;