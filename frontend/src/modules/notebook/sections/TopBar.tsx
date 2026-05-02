import { Search, Plus } from "lucide-react";
import { useAuth } from "@/lib/hooks/useAuth";
import SearchInput from "../components/SearchInput";
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

  return (
    <div className="flex items-center justify-between mb-10">
      
      <div className="flex items-center gap-6">
        <button className="px-4 py-2 rounded-full bg-gray-200 text-sm font-medium">
          All
        </button>
      </div>

      <div className="flex items-center gap-3">

        {/* 🔍 Search Input */}
      <SearchInput
  value={searchQuery}
  onChange={onSearchChange}
  placeholder="Search workspaces..."
/>

        {!isDemoUser && (
          <button
            onClick={onCreateWorkspace}
            className="flex items-center gap-2 bg-blue-600 text-white px-5 py-2 rounded-full text-sm font-medium hover:bg-blue-700 transition"
          >
            <Plus size={16} />
            Create Workspace
          </button>
        )}

      </div>
    </div>
  );
};

export default TopBar;